"""SCRUM-38 : mesures base avant adaptation via le pipeline v16 figé."""
import argparse
import json
import os
import platform
import re
import statistics
import time
from pathlib import Path

from data.parse_hdfs import compile_templates
from teamai.contracts import validate_example
from teamai.paths import ROOT, RUNS, SAMPLE, PREPROCESSED, VOLET_B_SUMMARY, VOLET_B_TEST, VOLET_B_TEST_SHA256
from volet_b.agents.validate import check_answer
from volet_b.slm.first_inference import PeakMemory, new_run_directory, sha256_file
from volet_b.slm.generate import GENERATION_OBSERVER, load_config
from volet_b.slm.v16 import explain, runtime
from volet_b.slm.v16.facts import prepare_block
from volet_b.slm.v16.policy import unknown_reference_errors, network_alert_details
from eval.volet_b.gpu_memory import PeakVRAM

RAG_DEFERRED = 'rag1 reporté : pas de variante v16 + RAG figée ; voir SCRUM-42/SCRUM-45'
PROMPT_FREEZE = ROOT / 'eval/results/SCRUM-63/prompt_freeze.json'
TEMPLATES = PREPROCESSED / 'HDFS.log_templates.csv'
if not TEMPLATES.is_file():
    TEMPLATES = ROOT / 'tests/fixtures/preprocessed/HDFS.log_templates.csv'


def write_json(path: Path, value: dict) -> None:
    """Écrit un objet JSON strict en UTF-8."""
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def require_base(config):
    """Refuse RAG avant toute lecture de données ou création de run."""
    if config == 'rag1':
        raise ValueError(RAG_DEFERRED)
    if config != 'base':
        raise ValueError('Configuration attendue : base.')


def input_hash(path: Path) -> str:
    """Vérifie l'entrée et l'empreinte de référence du test officiel si présente."""
    if not path.is_file():
        raise FileNotFoundError(f"Fichier d'exemples C5 absent : {path}. Fournir --data ou attendre SCRUM-35.")
    digest = sha256_file(path)
    if path.resolve() == VOLET_B_TEST.resolve() and VOLET_B_TEST_SHA256.exists():
        reference = VOLET_B_TEST_SHA256.read_text(encoding='utf-8').split()
        if not reference or not re.fullmatch(r'[0-9a-fA-F]{64}', reference[0]):
            raise ValueError('test.sha256 : empreinte SHA-256 invalide.')
        if reference[0].lower() != digest:
            raise ValueError('SHA-256 du test officiel différent de test.sha256 : exécution refusée.')
    return digest


def predict(example: dict, config: str, retriever=None, adapter: str | None = None) -> dict:
    """Construit les preuves brutes, appelle explain_block et conserve chaque tentative, même échouée."""
    require_base(config)
    record = dict(id=example.get('id'), block_id=example.get('block_id'), split=example.get('split'),
                  raw_text=None, parsed_response=None, errors=[], passages=[], seconds=None,
                  generation_seconds=None, new_tokens=None, prompt_tokens=None, finish_reason=None,
                  mock=os.environ.get('TEAMAI_SLM_MOCK') == '1', sources_valid=False,
                  attempts=[], slm_calls=0, v16=None, attention=None)
    start = time.perf_counter()
    block = None

    def observe(messages, out, error, elapsed):
        """Compte chaque appel effectif et contrôle sa réponse avec les fonctions v16."""
        record['slm_calls'] += 1
        if error is not None:
            attempt = dict(attempt=record['slm_calls'], text=None, prompt=messages[0]['content'],
                           finish=None, finish_reason=None, seconds=elapsed, prompt_tokens=None, new_tokens=None,
                           errors=[f'execution : {type(error).__name__} : {error}'])
        else:
            attempt = dict(attempt=record['slm_calls'], text=out['text'], prompt=messages[0]['content'],
                           finish=out['finish_reason'], finish_reason=out['finish_reason'],
                           seconds=out['seconds'], prompt_tokens=out['prompt_tokens'], new_tokens=out['new_tokens'],
                           errors=['Contrôles v16 interrompus.'])
            record['attempts'].append(attempt)
            response = {'choices': [{'message': {'content': out['text']}, 'finish_reason': out['finish_reason']}],
                        'usage': {'prompt_tokens': out['prompt_tokens'], 'completion_tokens': out['new_tokens']}}
            attempt.update(runtime.evaluate_response(response, block, messages[0]['content'], out['seconds'], record['slm_calls']))
            attempt['finish_reason'] = attempt['finish']
            return
        record['attempts'].append(attempt)

    token = GENERATION_OBSERVER.set(observe)
    try:
        errors = validate_example(example)
        if errors:
            record['errors'] = [f'input : {error}' for error in errors]
            return record
        # C5 ne fournit pas les numéros du journal global : références locales, à partir de 1.
        block = prepare_block(example['block_id'], list(enumerate(example['trace_lines'], 1)),
                              compile_templates(TEMPLATES), split=example['split'])
        record['attention'] = block['attention']
        result = explain.explain_block(block, adapter=adapter)
        record['v16'] = result
    except Exception as error:
        record['errors'].append(f'execution : {type(error).__name__} : {error}')
    finally:
        GENERATION_OBSERVER.reset(token)
        if record['attempts']:
            final = record['attempts'][-1]
            record.update(raw_text=final['text'], finish_reason=final['finish'],
                          new_tokens=(sum(a['new_tokens'] or 0 for a in record['attempts'])
                                      if any(a['new_tokens'] is not None for a in record['attempts']) else None),
                          prompt_tokens=(sum(a['prompt_tokens'] or 0 for a in record['attempts'])
                                         if any(a['prompt_tokens'] is not None for a in record['attempts']) else None),
                          generation_seconds=sum(a['seconds'] for a in record['attempts']))
            if final['text'] is not None:
                answer, c5_errors = check_answer(final['text'], allowed_sources=[])
                record['parsed_response'] = answer
                record['c5_errors'] = c5_errors
                record['errors'].extend(c5_errors)
                record['sources_valid'] = isinstance(answer, dict) and answer.get('sources') == []
                contract = final['errors']
                factual = final.get('factual_errors', [])
                review = final.get('review_flags', [])
                record['checks'] = dict(contract_errors=final['errors'], factual_errors=factual, review_flags=review,
                    facts_copied_exactly=not contract and not any(e in factual for e in
                        ('faits dupliqués', 'fait non conforme aux valeurs calculées')),
                    unknown_references=bool(unknown_reference_errors(answer, block)) if isinstance(answer, dict) else False,
                    unsupported_network=bool(network_alert_details(answer, block)) if isinstance(answer, dict) else False,
                    investigation_without_incident=(
                        'enquete_demandee_sans_indice_incident' in runtime.targeted_review(answer, block)
                        if answer is not None and not c5_errors else False))
        record['seconds'] = time.perf_counter() - start
    return record


def metrics(records: list[dict], peak_bytes: int, peak_vram_bytes=None) -> dict:
    """Agrège les contrôles v16 ; tous les taux et moyennes par bloc incluent les échecs."""
    n = len(records)
    valid = sum(not r['errors'] and r['parsed_response'] is not None for r in records)
    sources = sum(r['sources_valid'] for r in records)
    abstentions = sum(not r['errors'] and bool((r['parsed_response'] or {}).get('abstention')) for r in records)
    seconds = [r['seconds'] for r in records]
    values = dict(n=n, c5_valid=valid, failures=n-valid, sources_valid=sources, abstentions=abstentions,
                  latency_mean_seconds=statistics.mean(seconds) if seconds else None,
                  latency_median_seconds=statistics.median(seconds) if seconds else None,
                  process_peak_rss_bytes=peak_bytes, process_peak_vram_bytes=peak_vram_bytes,
                  slm_calls=sum(r['slm_calls'] for r in records))
    counts = dict(v16_contract_valid=0, facts_copied_exactly=0, unknown_references=0,
                  unsupported_network=0, investigation_without_incident=0, loop_responses=0,
                  corrections_triggered=0, corrections_attempted=0, corrections_succeeded=0,
                  blocks_with_incident=0, blocks_without_incident=0,
                  hypotheses_with_incident=0, hypotheses_without_incident=0)
    for r in records:
        checks = r.get('checks', {})
        counts['v16_contract_valid'] += bool(checks) and not checks['contract_errors']
        for key in ('facts_copied_exactly', 'unknown_references', 'unsupported_network', 'investigation_without_incident'):
            counts[key] += bool(checks.get(key))
        counts['loop_responses'] += any(runtime.repetition_errors(a['text'], a['new_tokens'], 800)
                                       for a in r['attempts'] if a['text'] is not None)
        attempts = r['attempts']
        counts['corrections_triggered'] += bool(attempts and attempts[0].get('retry_errors'))
        counts['corrections_attempted'] += r['slm_calls'] == 2
        counts['corrections_succeeded'] += bool((r.get('v16') or {}).get('retry_all_checks_success'))
        if r['attention'] is not None:
            group = 'with_incident' if r['attention'] else 'without_incident'
            counts['blocks_' + group] += 1
            hypotheses = (r['parsed_response'] or {}).get('hypotheses', [])
            counts['hypotheses_' + group] += len(hypotheses) if not r['errors'] and isinstance(hypotheses, list) else 0
    values.update(counts)
    for key in counts:
        values[key + '_rate'] = counts[key] / n if n else None
    for name, count in [('conformity', valid), ('sources_valid', sources), ('abstention', abstentions)]:
        values[name + '_rate'] = count / n if n else None
    for group in ('with_incident', 'without_incident'):
        # Chaque bloc du groupe reste au dénominateur, même en échec.
        blocks = counts['blocks_' + group]
        values['hypotheses_per_block_' + group] = counts['hypotheses_' + group] / blocks if blocks else None
    values['protocol'] = {
        'denominator': 'Taux sur tous les exemples lus, échecs compris ; hypotheses_per_block par groupe = somme des hypothèses valides / nombre de blocs du groupe avec attention connu, échecs compris (réponse invalide = 0 hypothèse) ; None si groupe vide.',
        'incident': 'Indice attention calculé par facts.prepare_block, jamais label annoté.',
        'v16': 'Contrat final ; faits exacts évaluables si structure valide ; alertes lexicales, pas vérité sémantique.',
        'loops': 'Exemples avec au moins une tentative rejetée par repetition_errors, budget 95 % compris.',
        'corrections': 'Déclenchées = retry_errors initiales ; tentées = deux appels ; réussies = retry_all_checks_success.',
        'memory': 'Pics RSS et VRAM du PID échantillonnés à 0,2 s, chargement inclus ; VRAM null si indisponible.',
        'latency': 'Temps mural par exemple ; génération séparée, somme de toutes les tentatives.'}
    return values


def run_config(config: str, data: Path = VOLET_B_TEST, limit: int | None = None,
               adapter: str | None = None, run_root: Path = RUNS) -> Path:
    """Exécute uniquement base v16 et écrit un C7 neuf sans commande git ni publication."""
    require_base(config)
    if limit is not None and limit < 1:
        raise ValueError('--limit doit être strictement positif.')
    data = Path(data)
    digest = input_hash(data)
    generation = load_config()
    mock = os.environ.get('TEAMAI_SLM_MOCK') == '1'
    freeze = json.loads(PROMPT_FREEZE.read_text(encoding='utf-8'))
    run_dir = new_run_directory(root=run_root, name=config)
    metadata = {
        'ticket': 'SCRUM-38', 'config': config, 'adapter': adapter, 'mock': mock,
        'input': str(data.resolve()), 'input_sha256': digest,
        'official_test': data.resolve() == VOLET_B_TEST.resolve(), 'limit': limit,
        'model_id': generation['model_id'], 'model_revision': generation['revision'],
        'gguf_repo': generation['gguf_repo'], 'gguf_file': generation['gguf_file'],
        'gguf_revision': generation['gguf_revision'], 'n_ctx': generation['n_ctx'], 'max_new_tokens': 800,
        'generation': generation, 'commit': None, 'commit_note': 'Aucune opération git ; à renseigner hors script.',
        'agents': 0, 'slm_calls_per_example': '1 ou 2 (correction unique v16)',
        'backend': 'mock' if mock else 'llamacpp', 'quantification': 'Q4_0', 'seed': 42,
        'prompt': 'volet_b/slm/v16/runtime.py::build_prompt', 'prompt_freeze': str(PROMPT_FREEZE.relative_to(ROOT)),
        'instruction_sha256': freeze['instruction_sha256'], 'policy_sha256': freeze['policy_sha256'],
        'runtime_sha256': freeze['runtime_sha256'], 'prompt_freeze_sha256': sha256_file(PROMPT_FREEZE),
        'templates': str(TEMPLATES.relative_to(ROOT)), 'templates_sha256': sha256_file(TEMPLATES),
        'retrieval': None, 'splits': [], 'line_numbering': 'local to trace_lines, starts at 1',
        'target_machine': 'Portable de Nassim (Ryzen 5 8645HS, 32 Go RAM, RTX 3050 Laptop 6 Go)',
        'machine': {'python': platform.python_version(), 'platform': platform.platform()},
    }
    write_json(run_dir / 'config.json', metadata)
    records = []
    with PeakMemory() as peak, PeakVRAM() as gpu:
        with data.open(encoding='utf-8') as source, (run_dir / 'predictions.jsonl').open('w', encoding='utf-8') as output:
            for line in source:
                if not line.strip():
                    continue
                try:
                    example = json.loads(line)
                except json.JSONDecodeError:
                    example = {}
                if not isinstance(example, dict):
                    example = {}
                record = predict(example, config, adapter=adapter)
                output.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + '\n')
                output.flush()
                records.append(record)
                split = example.get('split')
                if split in ('train', 'val', 'test') and split not in metadata['splits']:
                    metadata['splits'].append(split)
                if limit is not None and len(records) >= limit:
                    break
    summary = {**metrics(records, peak.peak, gpu.peak), 'config': config, 'mock': mock, 'adapter': adapter,
               'input_sha256': digest, 'official_test': metadata['official_test'], 'limit': limit, 'complete': limit is None}
    metadata['slm_calls_actual'] = summary['slm_calls']
    write_json(run_dir / 'config.json', metadata)
    write_json(run_dir / 'metrics.json', summary)
    return run_dir


def update_summary(metric_paths, output: Path = VOLET_B_SUMMARY) -> None:
    """Publie base seulement, pour un test officiel complet, non vide, réel et sans adaptateur."""
    text = output.read_text(encoding='utf-8') if output.exists() else '# Résultats du volet B\n'
    pattern = re.compile(r'^## Avant adaptation\s*\n.*?(?=^## |\Z)', re.M | re.S)
    match = pattern.search(text)
    row = ''
    if match:
        row = next((line for line in match.group().splitlines() if line.startswith('| base |')), '')
    for path in metric_paths:
        values = json.loads(Path(path).read_text(encoding='utf-8'))
        require_base(values['config'])
        if (values['mock'] or values['adapter'] or not values['official_test'] or values['limit'] is not None
                or not values.get('complete') or values['n'] < 1):
            raise ValueError('Le résumé avant adaptation exige le test officiel complet, sans mock ni adaptateur.')
        fields = ['base', str(values['n'])]
        for key in ('conformity_rate', 'sources_valid_rate', 'abstention_rate', 'latency_mean_seconds',
                    'latency_median_seconds', 'process_peak_rss_bytes'):
            value = values[key]
            fields.append('non mesuré' if value is None else str(round(value, 6)))
        fields.append(values['input_sha256'])
        row = '| ' + ' | '.join(fields) + ' |'
    section = ('## Avant adaptation\n\nBase v16 seulement ; rag1 reporté à SCRUM-42/SCRUM-45. '
               'Tous les exemples au dénominateur, échecs compris.\n\n'
               '| Configuration | n | Conformité C5 | Sources valides | Abstention | Latence moyenne (s) | Médiane (s) | RSS max (octets) | SHA-256 entrée |\n'
               '|---|---:|---:|---:|---:|---:|---:|---:|---|\n' + row + '\n\n')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text[:match.start()] + section + text[match.end():] if match else text.rstrip() + '\n\n' + section,
                      encoding='utf-8')


def main(argv=None) -> None:
    """Lance base v16 ; rag1 reste une option reconnue pour afficher son report explicite."""
    parser = argparse.ArgumentParser(description='SCRUM-38 : mesures base v16 avant adaptation.')
    parser.add_argument('--config', required=True, choices=('base', 'rag1'))
    parser.add_argument('--data', type=Path, default=VOLET_B_TEST)
    parser.add_argument('--limit', type=int)
    parser.add_argument('--adapter', help='Adaptateur GGUF éventuel ; exclu du résumé avant adaptation.')
    args = parser.parse_args(argv)
    try:
        run_dir = run_config(args.config, args.data, args.limit, args.adapter)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(f'Run : {run_dir}')


if __name__ == '__main__':
    main()
