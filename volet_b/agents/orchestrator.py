"""SCRUM-42 : recherche, rédaction et contrôle successifs sur une instance SLM."""
import argparse
from collections import Counter
import hashlib
import json
import platform
import time

import pandas as pd

from data.parse_hdfs import compile_templates
from teamai.paths import PROMPTS, RUNS, SAMPLE, SPLITS, resolve_path
from volet_b.agents.roles import checker, search, writer
from volet_b.agents.single_agent import (git_commit, lines_by_block, official_split,
                                         refuse_test_blocks, select_blocks)
from volet_b.rag.retriever import (CHUNKS, DEFAULT_METHOD, METHODS, META_FILE,
                                   load_passages, load_retriever)
from volet_b.slm.first_inference import new_run_directory
from volet_b.slm.generate import generate, load_backend, load_config, v16_context_error
from volet_b.slm.v16.facts import prepare_block


class CallLimitReached(RuntimeError):
    """Signale une limite atteinte avant tout appel supplémentaire."""


def explain_block_three_agents(block, retriever, call_slm, k=5, max_calls=5):
    """Explique un bloc préparé, conserve les appels bruts et autorise une seule reprise."""
    if block.get('split') == 'test':
        raise ValueError('split test réservé à l’évaluation finale')
    if k < 1 or max_calls < 0:
        raise ValueError('k doit être positif et max_calls non négatif')
    steps, errors = [], []
    retrieval = dict(events=[], query=None, candidates=[], passages=[], adjustments=[])
    final, parsed, c5_valid, status = None, None, False, 'rejete'

    def caller(agent, attempt):
        """Enveloppe chaque rôle avec le même compteur et le même journal des appels."""
        def invoke(prompt, response_format):
            """Réserve une place avant l'appel et conserve aussi les échecs du backend."""
            if len(steps) >= min(max_calls, 5):
                raise CallLimitReached('limite d’appels SLM atteinte')
            step = dict(agent=agent, tentative=attempt, prompt_chars=len(prompt), prompt_tokens=None,
                        new_tokens=None, seconds=None, raw_text=None, errors=[], verdict=None)
            steps.append(step)
            started = time.perf_counter()
            try:
                out = call_slm(prompt, response_format)
            except Exception as exc:
                step.update(seconds=time.perf_counter() - started, errors=[f'{type(exc).__name__}: {exc}'])
                raise
            step.update({key: out[key] for key in ('prompt_tokens', 'new_tokens', 'seconds')})
            step['raw_text'] = out['text']
            step['finish_reason'] = out['finish_reason']
            return out
        invoke.context_error = getattr(call_slm, 'context_error', None)
        return invoke

    try:
        retrieval = search.select_passages(block, retriever, caller('search', 1), k)
        if steps:
            steps[-1].update(errors=retrieval['errors'], manque=retrieval.get('manque'))
        if retrieval['errors']:
            raise ValueError('; '.join(retrieval['errors']))
        motifs = None
        for attempt in (1, 2):
            passages = list(retrieval['passages'])
            final = writer.write(block, passages, caller('writer', attempt),
                                 retrieval['adjustments'], motifs)
            retrieval['passages'] = passages
            # La dernière rédaction devient immédiatement la sortie, même si le contrôle échoue.
            writing_step = steps[-1]
            checks = checker.code_checks(final, block, retrieval['passages'])
            parsed, errors, review = checks
            c5_valid = not [e for e in errors if e != checker.ORDER_ERROR]
            writing_step.update(errors=errors, review_flags=review)
            checked = checker.check(final, block, retrieval['passages'], caller('checker', attempt), checks)
            retrieval['adjustments'].extend(checked.get('adjustments', []))
            parsed, errors = checked['answer'], checked['errors']
            c5_valid = not [e for e in checked['code_errors'] if e != checker.ORDER_ERROR]
            writing_step.update(errors=checked['code_errors'], review_flags=checked['review'])
            steps[-1].update(verdict=checked['verdict'])
            if steps[-1]['agent'] == 'checker':
                steps[-1].update(errors=errors, motifs=checked['motifs'])
            if checked['verdict'] == 'accepte':
                status = 'accepte'
                break
            if checked['verdict'] == 'abstention':
                status = 'abstention_demandee'
                break
            if checked['verdict'] == 'non_controle':
                break
            motifs = checked['motifs'] or ['le contrôle demande une correction']
            errors = errors or motifs
    except (CallLimitReached, ValueError, RuntimeError, OSError) as exc:
        errors = list(dict.fromkeys(errors + [f'{type(exc).__name__}: {exc}']))
    return dict(id=block['block_id'], split=block.get('split'), raw_text=final['text'] if final else '',
                parsed_response=parsed, errors=errors, statut=status, n_calls=len(steps),
                n_retries=sum(s['agent'] == 'writer' and s['tentative'] == 2 for s in steps),
                seconds=sum(s['seconds'] for s in steps if s['seconds'] is not None),
                new_tokens=sum(s['new_tokens'] for s in steps if s['new_tokens'] is not None),
                c5_valid=c5_valid, steps=steps, **{key: retrieval[key] for key in
                ('events', 'query', 'candidates', 'passages', 'adjustments')})


def make_call_slm(adapter=None, offline=False):
    """Fournit generate avec les paramètres llama.cpp exacts de v16 et son garde de contexte."""
    cfg = load_config()
    cfg = {**cfg, 'backend': 'llamacpp', 'max_new_tokens': 800,
           'do_sample': False, 'repetition_penalty': 1.0, 'seed': 42, 'enable_thinking': False,
           'local_files_only': offline or cfg.get('local_files_only', False)}
    llm = load_backend(cfg, adapter)

    def call_slm(prompt, response_format):
        """Appelle l'interface unique sans réflexion et renvoie les mesures v16."""
        return generate([{'role': 'user', 'content': prompt}], adapter=adapter,
                        backend='llamacpp', max_new_tokens=800, do_sample=False,
                        repetition_penalty=1.0, seed=42, enable_thinking=False,
                        response_format=response_format, return_metadata=True,
                        enforce_v16_context=True, local_files_only=cfg['local_files_only'])

    def context_error(prompt):
        """Vérifie le contexte avec l'unique instance chargée, sans inférence."""
        return v16_context_error(llm, [{'role': 'user', 'content': prompt}], cfg)

    call_slm.context_error = context_error
    return call_slm


def mock_call_slm(prompt, response_format):
    """Produit des réponses déterministes depuis le schéma et les références du prompt."""
    properties = response_format['schema']['properties']
    if 'passages' in properties:
        answer = {'passages': properties['passages']['items']['enum'][:1], 'manque': ''}
    elif 'verdict' in properties:
        answer = {'verdict': 'accepte', 'motifs': []}
    else:
        facts = properties['faits_observes']['items']['enum']
        # Les mentions obligatoires v16 complètent les deux premiers faits, sans les remplacer.
        selected = facts[:2] + [f for f in facts[2:] if any(f'] {c} :' in f for c in ('E24', 'E27', 'E28'))]
        answer = dict(resume_evenements='Les compteurs et les bornes temporelles du bloc sont fournis [F01]. '
                      'Le nombre total de lignes WARN est indiqué dans les faits calculés [F02].',
                      faits_observes=selected, hypotheses=[],
                      infos_manquantes=['Quel contexte opérationnel permet d’interpréter cet événement [L01] ?']
                      if properties['infos_manquantes']['maxItems'] else [],
                      sources=properties['sources']['items'].get('enum', [])[:1], abstention=False)
    return dict(text=json.dumps(answer, ensure_ascii=False), new_tokens=0, seconds=0.0,
                prompt_tokens=0, finish_reason='stop')


class MockRetriever:
    """Fournit des passages officiels sans index ni modèle, uniquement pour le mode factice."""

    def search(self, query, k):
        """Rend les premiers passages du corpus sans prétendre mesurer leur pertinence."""
        return [{**p, 'score': None, 'scores': {}} for p in load_passages()[:k]] if query else []


def select_inputs(args):
    """Réutilise la sélection existante, avec repli sur les splits livrés dans l'échantillon."""
    split_path = SPLITS / 'splits.csv'
    if split_path.exists():
        split = official_split()
        blocks = select_blocks(args)
    else:
        split_path = SAMPLE / 'splits.csv'
        split = pd.read_csv(split_path, usecols=['BlockId', 'split']).set_index('BlockId')['split']
        path = resolve_path(args.file) if args.file else SAMPLE / 'HDFS_sample.log'
        sample = lines_by_block(path.read_text(encoding='utf-8').splitlines())
        if args.block:
            refuse_test_blocks([args.block], split)
            if args.block not in sample:
                raise SystemExit(f'{args.block} absent de {path}')
            blocks = {args.block: sample[args.block]}
        elif args.file:
            blocks = sample
        else:
            eligible = pd.Series([bid for bid in sample if split.get(bid) == args.split], dtype=str)
            chosen = eligible.sample(n=args.n, random_state=args.seed)
            blocks = {bid: sample[bid] for bid in chosen}
    refuse_test_blocks(blocks, split)
    return blocks, split, split_path


def metrics(records):
    """Compte tous les blocs et précise le périmètre des durées et des réponses valides."""
    calls = [r['n_calls'] for r in records]
    return dict(n_blocks=len(records), statuts=dict(Counter(r['statut'] for r in records)),
                calls_mean=sum(calls) / len(calls) if calls else None, calls_max=max(calls, default=0),
                n_retries=sum(r['n_retries'] for r in records), c5_valid=sum(r['c5_valid'] for r in records),
                answers_with_sources=sum(bool(r['parsed_response'].get('sources')) for r in records
                                         if r['statut'] == 'accepte' and isinstance(r['parsed_response'], dict)),
                abstentions_effectives=sum(r['statut'] == 'abstention_demandee' or (
                    r['statut'] == 'accepte' and isinstance(r['parsed_response'], dict)
                    and r['parsed_response'].get('abstention') is True) for r in records),
                seconds_total=sum(r['seconds'] for r in records),
                units={'seconds': 'génération SLM, hors chargement, retrieval et contrôles',
                       'answers_with_sources': 'réponses au statut accepte citant au moins un passage',
                       'abstentions_effectives': 'statut abstention_demandee, ou réponse acceptée avec abstention C5 ; '
                                                 'parsed_response garde le texte du rédacteur sans réparation'},
                protocol='train/val uniquement ; mode mock exclu des mesures de qualité')


def main(argv=None):
    """Sélectionne les blocs autorisés et écrit un dossier C7 neuf pour les trois rôles."""
    parser = argparse.ArgumentParser(description='SCRUM-42 : orchestration à trois agents.')
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--block')
    source.add_argument('--file')
    source.add_argument('--split', choices=['train', 'val'])
    parser.add_argument('--n', type=int, default=5)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--k', type=int, default=5)
    parser.add_argument('--method', choices=METHODS, default=DEFAULT_METHOD)
    parser.add_argument('--adapter')
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--max-calls', type=int, default=5)
    parser.add_argument('--mock', action='store_true')
    args = parser.parse_args(argv)
    if args.k < 1 or not 1 <= args.max_calls <= 5 or args.n < 1:
        parser.error('--k et --n positifs ; --max-calls entre 1 et 5')
    if args.file:
        args.file = str(resolve_path(args.file))
    blocks, split, split_path = select_inputs(args)
    path = resolve_path(args.file) if args.file else SAMPLE / 'HDFS_sample.log'
    numbered = {bid: [] for bid in blocks}
    with path.open(encoding='utf-8') as stream:
        for number, line in enumerate(stream, 1):
            for bid in lines_by_block([line]):
                if bid in numbered:
                    numbered[bid].append((number, line.rstrip('\r\n')))
    templates = compile_templates(SAMPLE / 'HDFS.log_templates.csv')
    retriever = MockRetriever() if args.mock else load_retriever(args.method, local_files_only=args.offline)
    call_slm = mock_call_slm if args.mock else make_call_slm(args.adapter, args.offline)
    run_dir = new_run_directory(root=RUNS, name='three_agents')
    records = []
    with (run_dir / 'predictions.jsonl').open('w', encoding='utf-8') as stream:
        for index, bid in enumerate(blocks):
            block = prepare_block(bid, numbered[bid], templates, index=index, split=split.get(bid))
            record = explain_block_three_agents(block, retriever, call_slm, args.k, args.max_calls)
            record['mock'] = args.mock
            records.append(record)
            stream.write(json.dumps(record, ensure_ascii=False) + '\n')
            stream.flush()
            print(f"[{index + 1}/{len(blocks)}] {bid} : {record['statut']} ({record['n_calls']} appels)")
    generation = {**load_config(), 'backend': 'llamacpp', 'max_new_tokens': 800,
                  'do_sample': False, 'repetition_penalty': 1.0, 'seed': 42, 'enable_thinking': False}
    generation['local_files_only'] = args.offline or generation.get('local_files_only', False)
    config = dict(ticket='SCRUM-42', agents=3, max_calls=args.max_calls, k=args.k, method=args.method,
                  source=vars(args), split_sha256=hashlib.sha256(split_path.read_bytes()).hexdigest(),
                  prompts_sha256={role: hashlib.sha256((PROMPTS / f'{role}.txt').read_bytes()).hexdigest()
                                  for role in ('search', 'writer', 'checker')},
                  model=generation['model_id'], generation=generation, adapter=args.adapter, mock=args.mock,
                  corpus_sha256=hashlib.sha256(CHUNKS.read_bytes()).hexdigest(),
                  retrieval_metadata=json.loads(META_FILE.read_text(encoding='utf-8'))
                  if not args.mock and META_FILE.exists() else None,
                  commit=git_commit(), machine=dict(python=platform.python_version(), platform=platform.platform()),
                  timing='secondes de génération SLM ; chargement, retrieval et contrôles exclus')
    for name, content in (('config', config), ('metrics', metrics(records))):
        (run_dir / f'{name}.json').write_text(json.dumps(content, ensure_ascii=False, indent=2) + '\n',
                                            encoding='utf-8')
    print(f'Run : {run_dir}')
    return run_dir


if __name__ == '__main__':
    main()
