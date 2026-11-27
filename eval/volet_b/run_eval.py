"""SCRUM-45 : évaluation automatique des 4 configurations du volet B sur les entrées figées du test.

    python -m eval.volet_b.run_eval --config base_1agent
    python -m eval.volet_b.run_eval --config lora_3agents --adapter chemin/adapter.gguf

Les 4 configurations lisent les mêmes traces (test_inputs.jsonl, vérifié par SHA-256), le même corpus
et les mêmes paramètres de génération. Chaque run écrit un dossier C7 neuf dans eval/runs/.
"""
import argparse
import json
import os
import platform
import re
import statistics
import subprocess
import time
from pathlib import Path

from data.parse_hdfs import compile_templates
from eval.volet_b import run_config
from eval.volet_b.gpu_memory import PeakVRAM
from teamai.paths import (PROMPTS, ROOT, RUNS, VOLET_B_PROMPT_FREEZE, VOLET_B_TEST_INPUTS,
                          VOLET_B_TEST_INPUTS_SHA256, resolve_path)
from volet_b.agents import orchestrator
from volet_b.agents.validate import check_answer
from volet_b.rag.retriever import CHUNKS, DEFAULT_METHOD, META_FILE
from volet_b.slm import generate as slm
from volet_b.slm.first_inference import PeakMemory, new_run_directory, sha256_file
from volet_b.slm.v16.explain import repetition_errors
from volet_b.slm.v16.facts import prepare_block
from volet_b.slm.v16.policy import network_alert_details, unknown_reference_errors

CONFIGS = {'base_1agent': dict(agents=1, lora=False), 'base_3agents': dict(agents=3, lora=False),
           'lora_1agent': dict(agents=1, lora=True), 'lora_3agents': dict(agents=3, lora=True)}
GENERATION = dict(backend='llamacpp', max_new_tokens=800, do_sample=False, repetition_penalty=1.0,
                  seed=42, enable_thinking=False)
ROLES = ('search', 'writer', 'checker')
PROTOCOL = {
    'denominator': 'Tous les cas lus, échecs compris (réponse absente ou invalide = non conforme, non acceptée, '
                   '0 hypothèse). Hypothèses par bloc : somme / nombre de blocs du groupe dont attention est connu ; '
                   'None si groupe vide.',
    'final_answer': '1 agent : dernière tentative v16 ; 3 agents : dernière rédaction, même rejetée par le contrôle.',
    'c5': 'check_answer sur le texte final, sources limitées aux passages fournis (aucun pour 1 agent).',
    'accepted': '3 agents : statut accepte ; 1 agent : contrat v16 de la tentative finale sans erreur.',
    'abstention': 'Réponse finale conforme C5 avec abstention=true ; abstention_demandee du contrôle '
                  'comptée seulement dans mode_metrics.',
    'incident': 'Indice attention calculé par facts.prepare_block, jamais label annoté.',
    'references': 'unknown_reference_errors et network_alert_details v16 sur la réponse finale, sources exclues.',
    'loops': 'Réponse finale rejetée par repetition_errors (budget 800 tokens) ; None si tokens non mesurés.',
    'latency': 'Temps mural par cas : préparation, retrieval, génération et contrôles ; chargement exclu.',
    'memory': 'Pics RSS et VRAM du PID échantillonnés à 0,2 s, chargement inclus ; VRAM null si indisponible.'}


def check_options(config, adapter, k, max_calls, limit, ids) -> None:
    """Refuse une option incohérente avant toute lecture des entrées ou création de run."""
    if config not in CONFIGS:
        raise ValueError(f'Configuration inconnue : {config} ; attendues : {", ".join(CONFIGS)}.')
    if CONFIGS[config]['lora'] and not adapter:
        raise ValueError(f'{config} exige --adapter (adaptateur LoRA GGUF).')
    if not CONFIGS[config]['lora'] and adapter:
        raise ValueError(f'{config} utilise le modèle de base : --adapter interdit.')
    if adapter and not resolve_path(adapter).is_file():
        raise FileNotFoundError(f'Adaptateur GGUF introuvable : {adapter}')
    if k < 1 or not 1 <= max_calls <= 5:
        raise ValueError('--k doit être positif et --max-calls compris entre 1 et 5.')
    if limit is not None and limit < 1:
        raise ValueError('--limit doit être strictement positif.')
    if ids is not None and (not ids or not all(ids) or len(set(ids)) != len(ids)):
        raise ValueError('--ids : identifiants non vides et distincts attendus.')


def expected_inputs_hash() -> str:
    """Lit l'empreinte figée de test_inputs.jsonl."""
    if not VOLET_B_TEST_INPUTS_SHA256.is_file():
        raise FileNotFoundError('eval/volet_b/test_inputs.sha256 manquant : empreinte des entrées figées requise.')
    reference = VOLET_B_TEST_INPUTS_SHA256.read_text(encoding='utf-8').split()
    if not reference or not re.fullmatch(r'[0-9a-fA-F]{64}', reference[0]):
        raise ValueError('test_inputs.sha256 : empreinte SHA-256 invalide.')
    return reference[0].lower()


def inputs_hash(path: Path) -> tuple[str, bool]:
    """Rend l'empreinte et le caractère officiel ; les entrées officielles doivent correspondre à la référence."""
    if not path.is_file():
        raise FileNotFoundError(f'Entrées absentes : {path}')
    digest = sha256_file(path)
    official = path.resolve() == VOLET_B_TEST_INPUTS.resolve()
    if official and digest != expected_inputs_hash():
        raise ValueError('SHA-256 de test_inputs.jsonl différent de test_inputs.sha256 : exécution refusée.')
    return digest, official


def load_cases(path: Path, ids=None, limit=None) -> tuple[list[dict], int]:
    """Lit les cas dans l'ordre du fichier ; une ligne illisible reste un cas en échec."""
    cases = []
    with path.open(encoding='utf-8') as source:
        for line in source:
            if line.strip():
                try:
                    case = json.loads(line)
                except json.JSONDecodeError:
                    case = {}
                cases.append(case if isinstance(case, dict) else {})
    total = len(cases)
    if ids is not None:
        missing = sorted(set(ids) - {case.get('id') for case in cases})
        if missing:
            raise ValueError(f'--ids absents des entrées : {", ".join(missing)}')
        cases = [case for case in cases if case.get('id') in set(ids)]
    return (cases[:limit] if limit is not None else cases), total


def prepare_case(case: dict, index: int, templates) -> tuple[dict | None, str | None]:
    """Prépare les preuves v16 avec la numérotation locale de run_config, sans lire label ni events."""
    errors = run_config.input_errors(case)
    if errors:
        return None, 'input : ' + ' ; '.join(errors)
    try:
        return prepare_block(case['block_id'], list(enumerate(case['trace_lines'], 1)), templates,
                             index=index, split=case['split']), None
    except Exception as error:
        return None, f'execution : {type(error).__name__} : {error}'


def final_checks(text, new_tokens, block, sources, accepted, slm_calls) -> dict:
    """Mesures communes de la réponse finale, identiques pour les 4 configurations."""
    answer, errors = check_answer(text, allowed_sources=sources) if text and text.strip() else (None, ['aucune réponse finale'])
    valid = answer is not None and not errors
    evidence = {**answer, 'sources': []} if isinstance(answer, dict) and block is not None else None
    loop = False if not text else None if new_tokens is None else bool(repetition_errors(text, new_tokens, 800))
    return dict(text=text, answer=answer, c5_errors=errors, c5_valid=valid, accepted=accepted,
                abstention=valid and answer['abstention'] is True,
                hypotheses=len(answer['hypotheses']) if valid else 0,
                attention=None if block is None else block['attention'],
                unknown_references=evidence is not None and bool(unknown_reference_errors(evidence, block)),
                unsupported_network=evidence is not None and bool(network_alert_details(evidence, block)),
                loop=loop, slm_calls=slm_calls)


def predict_single(case: dict, block, adapter) -> dict:
    """Réutilise run_config.predict (v16, 1 agent) en ne contrôlant que les champs d'entrée."""
    record = run_config.predict(case, 'base', adapter=adapter, check_annotations=False)
    last = record['attempts'][-1] if record['attempts'] else None
    checks = record.get('checks')
    record['final'] = final_checks(record['raw_text'], last['new_tokens'] if last else None, block, [],
                                   bool(checks) and not checks['contract_errors'], record['slm_calls'])
    return record


def failed_three(case: dict, errors: list[str]) -> dict:
    """Enregistrement 3 agents d'un cas sans appel exécuté, au format de l'orchestrateur."""
    return dict(id=case.get('id'), block_id=case.get('block_id'), split=case.get('split'), raw_text='',
                parsed_response=None, errors=errors, statut='rejete', n_calls=0, n_retries=0, seconds=0.0,
                new_tokens=0, c5_valid=False, steps=[], events=[], query=None, candidates=[], passages=[],
                adjustments=[])


def predict_three(case: dict, block, problem, retriever, call_slm, k: int, max_calls: int) -> dict:
    """Appelle l'orchestrateur SCRUM-42 sur le bloc préparé ; un échec reste un cas évalué."""
    if block is None:
        record = failed_three(case, [problem])
    else:
        try:
            record = {**orchestrator.explain_block_three_agents(block, retriever, call_slm, k, max_calls,
                                                                 final_evaluation=True),
                      'id': case['id'], 'block_id': case['block_id']}
        except Exception as error:
            record = failed_three(case, [f'execution : {type(error).__name__} : {error}'])
    writings = [s for s in record['steps'] if s['agent'] == 'writer' and s['raw_text'] is not None]
    record['final'] = final_checks(record['raw_text'], writings[-1]['new_tokens'] if writings else None, block,
                                   [p['id'] for p in record['passages']], record['statut'] == 'accepte',
                                   record['n_calls'])
    return record


def metrics(records: list[dict], agents: int, peak_bytes: int, peak_vram_bytes=None) -> dict:
    """Agrège les mesures communes de la réponse finale, puis les mesures propres au mode."""
    n = len(records)
    finals = [r['final'] for r in records]
    counts = dict(c5_valid=sum(f['c5_valid'] for f in finals), accepted=sum(f['accepted'] for f in finals),
                  abstentions=sum(f['abstention'] for f in finals),
                  unknown_references=sum(f['unknown_references'] for f in finals),
                  unsupported_network=sum(f['unsupported_network'] for f in finals),
                  loop_responses=sum(f['loop'] is True for f in finals))
    values = dict(n=n, failures=n - counts['c5_valid'], **counts,
                  loops_not_measured=sum(f['loop'] is None for f in finals))
    rates = dict(conformity_rate='c5_valid', accepted_rate='accepted', abstention_rate='abstentions',
                 unknown_references_rate='unknown_references', unsupported_network_rate='unsupported_network',
                 loop_responses_rate='loop_responses')
    for name, key in rates.items():
        values[name] = counts[key] / n if n else None
    for group, flag in (('with_incident', True), ('without_incident', False)):
        members = [f for f in finals if f['attention'] is flag]
        values['blocks_' + group] = len(members)
        values['hypotheses_' + group] = sum(f['hypotheses'] for f in members)
        values['hypotheses_per_block_' + group] = values['hypotheses_' + group] / len(members) if members else None
    calls = [f['slm_calls'] for f in finals]
    seconds = [r['wall_seconds'] for r in records]
    values.update(slm_calls=sum(calls), slm_calls_mean=statistics.mean(calls) if calls else None,
                  slm_calls_max=max(calls) if calls else None,
                  latency_mean_seconds=statistics.mean(seconds) if seconds else None,
                  latency_median_seconds=statistics.median(seconds) if seconds else None,
                  process_peak_rss_bytes=peak_bytes, process_peak_vram_bytes=peak_vram_bytes, protocol=PROTOCOL)
    values['mode_metrics'] = (run_config.metrics(records, peak_bytes, peak_vram_bytes) if agents == 1
                              else orchestrator.metrics(records))
    return values


def gpu_names() -> list[str] | None:
    """Noms des GPU NVIDIA visibles, ou None si nvidia-smi est indisponible."""
    try:
        out = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
                             capture_output=True, text=True, timeout=5, check=True)
    except (OSError, subprocess.SubprocessError):
        return None
    return [line.strip() for line in out.stdout.splitlines() if line.strip()]


def describe(config, data, digest, official, total, adapter, limit, ids, k, max_calls, mock) -> dict:
    """Configuration C7 du run : entrées, modèle, prompts figés, RAG, Git et machine."""
    agents = CONFIGS[config]['agents']
    generation = {**slm.load_config(), **GENERATION}
    freeze = json.loads(VOLET_B_PROMPT_FREEZE.read_text(encoding='utf-8'))
    return {
        'ticket': 'SCRUM-45', 'config': config, 'agents': agents, 'mock': mock,
        'backend': 'mock' if mock else 'llamacpp', 'quantification': 'Q4_0',
        'adapter': adapter, 'adapter_sha256': sha256_file(resolve_path(adapter)) if adapter else None,
        'input': str(data.resolve()), 'input_sha256': digest, 'official_input': official,
        'input_fields': 'id, block_id, split, trace_lines transmis à prepare_block ; label et events jamais lus',
        'n_inputs': total, 'limit': limit, 'ids': ids,
        'model_id': generation['model_id'], 'gguf_repo': generation['gguf_repo'], 'gguf_file': generation['gguf_file'],
        'gguf_revision': generation['gguf_revision'], 'n_ctx': generation['n_ctx'], 'generation': generation,
        'k': k if agents == 3 else None, 'max_calls': max_calls if agents == 3 else None,
        'slm_calls_rule': ('recherche, rédaction, contrôle et une reprise, au plus max_calls' if agents == 3
                           else '1 ou 2 (correction unique v16)'),
        'rag_method': ('MockRetriever' if mock else DEFAULT_METHOD) if agents == 3 else None,
        'corpus': str(CHUNKS.relative_to(ROOT)), 'corpus_sha256': sha256_file(CHUNKS),
        'retrieval_metadata': (json.loads(META_FILE.read_text(encoding='utf-8'))
                               if agents == 3 and not mock else None),
        'prompts_sha256': {role: sha256_file(PROMPTS / f'{role}.txt') for role in ROLES},
        'prompt_freeze': str(VOLET_B_PROMPT_FREEZE.relative_to(ROOT)),
        'prompt_freeze_sha256': sha256_file(VOLET_B_PROMPT_FREEZE),
        'instruction_sha256': freeze['instruction_sha256'], 'policy_sha256': freeze['policy_sha256'],
        'runtime_sha256': freeze['runtime_sha256'],
        'templates': str(run_config.TEMPLATES.relative_to(ROOT)),
        'templates_sha256': sha256_file(run_config.TEMPLATES),
        'line_numbering': 'local to trace_lines, starts at 1', **run_config.git_metadata(),
        'machine': {'python': platform.python_version(), 'platform': platform.platform(),
                    'cpu_count': os.cpu_count(), 'gpu': gpu_names()},
        'timing': PROTOCOL['latency'],
    }


def run_eval(config: str, data: Path = VOLET_B_TEST_INPUTS, adapter: str | None = None, limit: int | None = None,
             ids: list[str] | None = None, k: int = 5, max_calls: int = 5, mock: bool = False,
             run_root: Path = RUNS) -> Path:
    """Vérifie les entrées, charge une seule fois modèle et retriever, puis écrit un C7 neuf."""
    check_options(config, adapter, k, max_calls, limit, ids)
    if os.environ.get('TEAMAI_SLM_MOCK') == '1' and not mock:
        raise ValueError('TEAMAI_SLM_MOCK=1 sans --mock : run factice non déclaré, refusé.')
    data = Path(data)
    digest, official = inputs_hash(data)
    cases, total = load_cases(data, ids, limit)
    agents = CONFIGS[config]['agents']
    templates = compile_templates(run_config.TEMPLATES)
    previous = os.environ.get('TEAMAI_SLM_MOCK')
    records = []
    try:
        if mock and agents == 1:
            os.environ['TEAMAI_SLM_MOCK'] = '1'
        with PeakMemory() as peak, PeakVRAM() as gpu:
            if agents == 3:
                retriever = orchestrator.MockRetriever() if mock else orchestrator.load_retriever(DEFAULT_METHOD)
                call_slm = orchestrator.mock_call_slm if mock else orchestrator.make_call_slm(adapter)
            elif not mock:
                # Même clé de cache que explain_block : le chargement reste hors de la latence du premier cas.
                slm.load_backend({**slm.load_config(), **GENERATION}, adapter)
            metadata = describe(config, data, digest, official, total, adapter, limit, ids, k, max_calls, mock)
            run_dir = new_run_directory(root=run_root, name=config)
            run_config.write_json(run_dir / 'config.json', metadata)
            with (run_dir / 'predictions.jsonl').open('w', encoding='utf-8') as output:
                for index, case in enumerate(cases):
                    started = time.perf_counter()
                    block, problem = prepare_case(case, index, templates)
                    record = (predict_single(case, block, adapter) if agents == 1
                              else predict_three(case, block, problem, retriever, call_slm, k, max_calls))
                    record.update(config=config, mock=mock, attention=record['final']['attention'],
                                  wall_seconds=time.perf_counter() - started)
                    output.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + '\n')
                    output.flush()
                    records.append(record)
                    print(f"[{index + 1}/{len(cases)}] {case.get('id')} : "
                          f"{'conforme' if record['final']['c5_valid'] else 'non conforme'}, "
                          f"{record['final']['slm_calls']} appel(s)")
    finally:
        if previous is None:
            os.environ.pop('TEAMAI_SLM_MOCK', None)
        else:
            os.environ['TEAMAI_SLM_MOCK'] = previous
    summary = {**metrics(records, agents, peak.peak, gpu.peak), 'config': config, 'agents': agents, 'mock': mock,
               'adapter': adapter, 'adapter_sha256': metadata['adapter_sha256'], 'input_sha256': digest,
               'official_input': official, 'n_inputs': total, 'limit': limit, 'ids': ids,
               'complete': limit is None and ids is None and len(records) == total}
    metadata['slm_calls_actual'] = summary['slm_calls']
    run_config.write_json(run_dir / 'config.json', metadata)
    run_config.write_json(run_dir / 'metrics.json', summary)
    return run_dir


def main(argv=None) -> Path:
    """Ligne de commande : une configuration par run, sur le GPU visé ou en mode factice."""
    parser = argparse.ArgumentParser(description='SCRUM-45 : évaluation automatique des 4 configurations du volet B.')
    parser.add_argument('--config', required=True, choices=tuple(CONFIGS))
    parser.add_argument('--data', type=Path, default=VOLET_B_TEST_INPUTS)
    parser.add_argument('--adapter', help='Adaptateur LoRA GGUF : obligatoire pour lora_*, interdit pour base_*.')
    parser.add_argument('--limit', type=int)
    parser.add_argument('--ids', help='Identifiants séparés par des virgules, par exemple test-0004,test-0009.')
    parser.add_argument('--k', type=int, default=5)
    parser.add_argument('--max-calls', type=int, default=5)
    parser.add_argument('--mock', action='store_true', help='Réponses factices, refusées par le résumé.')
    args = parser.parse_args(argv)
    ids = [value.strip() for value in args.ids.split(',')] if args.ids is not None else None
    try:
        run_dir = run_eval(args.config, resolve_path(args.data), args.adapter, args.limit, ids,
                           args.k, args.max_calls, args.mock, RUNS)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(f'Run : {run_dir}')
    return run_dir


if __name__ == '__main__':
    main()
