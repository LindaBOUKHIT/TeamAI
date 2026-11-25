"""SCRUM-45 : banc des 4 configurations en mode factice, sans modèle, index, GPU ni test réservé."""
import csv
import hashlib
import json
import os
from unittest.mock import Mock

import pytest

from eval.volet_b import blind_scores, blind_sheets, run_eval, summarize
from teamai.paths import SAMPLE
from volet_b.agents import orchestrator
from volet_b.agents.single_agent import lines_by_block
from volet_b.slm import generate as slm


def write_inputs(path, cases):
    """Écrit des entrées figées fabriquées et rend leur empreinte."""
    text = ''.join(json.dumps(case, ensure_ascii=False) + '\n' for case in cases)
    path.write_text(text, encoding='utf-8', newline='\n')
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


@pytest.fixture
def inputs(tmp_path, monkeypatch):
    """Trois cas fabriqués depuis data/sample (dont un sans incident), déclarés entrées officielles."""
    blocks = list(lines_by_block((SAMPLE / 'HDFS_sample.log').read_text(encoding='utf-8').splitlines()).items())
    cases = [dict(id=f'factice-{i:04d}', block_id=bid, split='test', label=1,
                  trace_lines=lines[:3] if i == 3 else lines, events=['ANNOTATION_EVENTS_INTERDITE'])
             for i, (bid, lines) in enumerate(blocks[:3], 1)]
    path, reference = tmp_path / 'test_inputs.jsonl', tmp_path / 'test_inputs.sha256'
    reference.write_text(write_inputs(path, cases) + '  test_inputs.jsonl\n', encoding='utf-8')
    monkeypatch.setattr(run_eval, 'VOLET_B_TEST_INPUTS', path)
    monkeypatch.setattr(run_eval, 'VOLET_B_TEST_INPUTS_SHA256', reference)
    monkeypatch.setattr(run_eval.run_config, 'git_metadata',
                        lambda: dict(commit='a' * 40, git_dirty=False, commit_note=None))
    monkeypatch.setattr(run_eval, 'gpu_names', lambda: None)
    monkeypatch.setattr(run_eval.platform, 'platform', lambda: 'test')
    monkeypatch.setattr(run_eval.PeakVRAM, 'sample', lambda self: None)
    monkeypatch.setattr(slm, 'load_backend', lambda *args: pytest.fail('chargement SLM en mode mock'))
    monkeypatch.setattr(slm, 'v16_context_error', lambda *args: None)
    monkeypatch.setattr(orchestrator, 'load_retriever', lambda *args, **kwargs: pytest.fail('index en mode mock'))
    monkeypatch.setattr(orchestrator, 'make_call_slm', lambda *args, **kwargs: pytest.fail('SLM réel en mode mock'))
    monkeypatch.delenv('TEAMAI_SLM_MOCK', raising=False)
    monkeypatch.setattr(run_eval, 'RUNS', tmp_path / 'runs')
    return path


@pytest.fixture
def adapter(tmp_path):
    """Adaptateur GGUF factice, seulement haché."""
    path = tmp_path / 'adapter.gguf'
    path.write_bytes(b'GGUF factice')
    return path


def read_run(run_dir):
    """Rend config, prédictions et métriques d'un run."""
    config = json.loads((run_dir / 'config.json').read_text(encoding='utf-8'))
    records = [json.loads(line) for line in (run_dir / 'predictions.jsonl').read_text(encoding='utf-8').splitlines()]
    return config, records, json.loads((run_dir / 'metrics.json').read_text(encoding='utf-8'))


@pytest.mark.parametrize('config', list(run_eval.CONFIGS))
def test_mock_end_to_end(inputs, adapter, tmp_path, monkeypatch, config):
    """Les 4 configurations traversent leur pipeline en mode factice et écrivent un C7 complet."""
    prompts, original = [], orchestrator.mock_call_slm

    def spy(prompt, response_format):
        """Conserve chaque prompt des 3 rôles avant la réponse factice."""
        prompts.append(prompt)
        return original(prompt, response_format)

    monkeypatch.setattr(orchestrator, 'mock_call_slm', spy)
    single = Mock(wraps=slm._generate)
    monkeypatch.setattr(slm, '_generate', single)
    lora = run_eval.CONFIGS[config]['lora']
    run = run_eval.main(['--config', config, '--mock', '--data', str(inputs)]
                        + (['--adapter', str(adapter)] if lora else []))
    cfg, records, values = read_run(run)
    assert run.parent == tmp_path / 'runs' and run.name.endswith(config)
    assert len(records) == values['n'] == 3 and values['complete'] and values['mock'] and cfg['mock']
    assert [r['id'] for r in records] == ['factice-0001', 'factice-0002', 'factice-0003']
    assert cfg['input_sha256'] == values['input_sha256'] == run_eval.expected_inputs_hash()
    assert cfg['official_input'] and cfg['commit'] == 'a' * 40 and cfg['git_dirty'] is False
    assert cfg['adapter_sha256'] == (hashlib.sha256(b'GGUF factice').hexdigest() if lora else None)
    assert set(cfg['prompts_sha256']) == {'search', 'writer', 'checker'}
    assert cfg['instruction_sha256'] and cfg['prompt_freeze_sha256'] and cfg['generation']['seed'] == 42
    assert records[2]['attention'] is False and records[0]['attention'] is True
    assert values['blocks_with_incident'] == 2 and values['blocks_without_incident'] == 1
    assert values['conformity_rate'] == 1 and values['process_peak_rss_bytes'] > 0
    assert values['process_peak_vram_bytes'] is None
    if run_eval.CONFIGS[config]['agents'] == 3:
        assert cfg['k'] == 5 and cfg['max_calls'] == 5 and cfg['rag_method'] == 'MockRetriever'
        assert values['accepted_rate'] == 1 and values['slm_calls_mean'] == values['slm_calls_max'] == 3
        assert values['mode_metrics']['n_blocks'] == 3 and not single.called
        assert all(r['statut'] == 'accepte' and r['split'] == 'test' for r in records)
        text = '\n'.join(prompts)
    else:
        assert cfg['k'] is None and cfg['rag_method'] is None and not prompts
        assert values['accepted'] == 0 and values['abstention_rate'] == 1 and values['slm_calls_mean'] == 1
        assert values['mode_metrics']['n'] == 3 and all(r['mock'] for r in records)
        text = str(single.call_args_list)
    assert text and 'ANNOTATION_' not in text and 'label' not in text
    assert 'TEAMAI_SLM_MOCK' not in os.environ


@pytest.mark.parametrize('agents', [1, 3])
def test_failure_stays_in_denominator(inputs, tmp_path, agents):
    """Un cas illisible et une trace étrangère au bloc comptent comme échecs au dénominateur."""
    rows = [json.loads(line) for line in inputs.read_text(encoding='utf-8').splitlines()]
    rows[1]['trace_lines'] = rows[0]['trace_lines']
    data = tmp_path / 'essai.jsonl'
    write_inputs(data, rows)
    with data.open('a', encoding='utf-8') as stream:
        stream.write('JSON mal formé\n')
    config = 'base_1agent' if agents == 1 else 'base_3agents'
    run = run_eval.run_eval(config, data, mock=True, run_root=tmp_path / 'runs')
    cfg, records, values = read_run(run)
    assert not cfg['official_input'] and values['n'] == values['n_inputs'] == 4
    assert values['c5_valid'] == 2 and values['failures'] == 2 and values['conformity_rate'] == 0.5
    assert [r['attention'] for r in records] == [True, None, False, None]
    assert values['blocks_with_incident'] == values['blocks_without_incident'] == 1
    assert records[1]['errors'] and records[3]['errors'] and not records[1]['final']['c5_valid']
    assert values['slm_calls'] == (2 if agents == 1 else 6)
    assert len([r['wall_seconds'] for r in records]) == 4


def test_ids_limit_and_unknown_id(inputs, tmp_path):
    """--ids et --limit gardent l'ordre du fichier et marquent le run incomplet."""
    run = run_eval.run_eval('base_3agents', inputs, ids=['factice-0003', 'factice-0001'], mock=True,
                            run_root=tmp_path / 'runs')
    _, records, values = read_run(run)
    assert [r['id'] for r in records] == ['factice-0001', 'factice-0003'] and not values['complete']
    run = run_eval.run_eval('base_1agent', inputs, limit=1, mock=True, run_root=tmp_path / 'runs')
    assert read_run(run)[2]['n'] == 1 and not read_run(run)[2]['complete']
    with pytest.raises(ValueError, match='factice-0099'):
        run_eval.run_eval('base_1agent', inputs, ids=['factice-0099'], mock=True, run_root=tmp_path / 'runs')


def test_hash_refusal_before_any_run(inputs, tmp_path, monkeypatch):
    """Une empreinte différente de test_inputs.sha256 arrête tout avant le chargement et le dossier C7."""
    run_eval.VOLET_B_TEST_INPUTS_SHA256.write_text('0' * 64 + '  test_inputs.jsonl\n', encoding='utf-8')
    forbidden = Mock(side_effect=AssertionError('aucun chargement'))
    monkeypatch.setattr(run_eval, 'describe', forbidden)
    with pytest.raises(ValueError, match='SHA-256'):
        run_eval.run_eval('base_3agents', inputs, mock=True, run_root=tmp_path / 'runs')
    run_eval.VOLET_B_TEST_INPUTS_SHA256.unlink()
    with pytest.raises(FileNotFoundError, match='test_inputs.sha256'):
        run_eval.run_eval('base_3agents', inputs, mock=True, run_root=tmp_path / 'runs')
    assert not (tmp_path / 'runs').exists() and not forbidden.called


@pytest.mark.parametrize('config, given, error', [
    ('lora_1agent', None, 'exige --adapter'), ('lora_3agents', None, 'exige --adapter'),
    ('base_1agent', 'adapter', 'interdit'), ('base_3agents', 'adapter', 'interdit'),
    ('lora_1agent', 'absent', 'introuvable')])
def test_adapter_required_or_forbidden(inputs, adapter, tmp_path, capsys, config, given, error):
    """L'adaptateur est obligatoire pour lora_*, interdit pour base_*, et doit exister."""
    value = {'adapter': str(adapter), 'absent': str(tmp_path / 'absent.gguf'), None: None}[given]
    with pytest.raises(SystemExit):
        run_eval.main(['--config', config, '--mock'] + (['--adapter', value] if value else []))
    assert error in capsys.readouterr().err and not (tmp_path / 'runs').exists()


def test_undeclared_mock_and_options_refused(inputs, tmp_path, monkeypatch):
    """TEAMAI_SLM_MOCK sans --mock et des limites incohérentes sont refusés."""
    monkeypatch.setenv('TEAMAI_SLM_MOCK', '1')
    with pytest.raises(ValueError, match='sans --mock'):
        run_eval.run_eval('base_1agent', inputs, run_root=tmp_path / 'runs')
    for options in (dict(k=0), dict(max_calls=6), dict(limit=0), dict(ids=['a', 'a'])):
        with pytest.raises(ValueError):
            run_eval.run_eval('base_3agents', inputs, mock=True, run_root=tmp_path / 'runs', **options)


def summary_values(config, **change):
    """Métriques minimales d'un run complet et réel."""
    values = dict(config=config, mock=False, limit=None, ids=None, complete=True, n=80, n_inputs=80,
                  official_input=True, input_sha256=run_eval.expected_inputs_hash(), conformity_rate=0.9875,
                  accepted_rate=0.5, abstention_rate=0.0, hypotheses_per_block_with_incident=4 / 21,
                  unknown_references_rate=0.025, unsupported_network_rate=0.0, loop_responses_rate=0.0,
                  slm_calls_mean=3.25, latency_mean_seconds=12.5, latency_median_seconds=11.0,
                  process_peak_vram_bytes=5 * 1024**3 if '3agents' in config else None)
    return {**values, **change}


def write_metrics(tmp_path, overrides=None):
    """Écrit les 4 metrics.json dans des dossiers de run fabriqués."""
    paths = []
    for config in run_eval.CONFIGS:
        path = tmp_path / f'run_{config}'
        path.mkdir()
        run_eval.run_config.write_json(path / 'metrics.json', summary_values(config, **(overrides or {}).get(config, {})))
        paths.append(path)
    return paths


def test_summary_section_replaced(inputs, tmp_path):
    """Le résumé écrit une seule section, la remplace ensuite et garde le reste du fichier."""
    output = tmp_path / 'volet_b.md'
    output.write_text('# Résultats du volet B\n\n## Avant adaptation\n\nInchangé.\n', encoding='utf-8')
    paths = write_metrics(tmp_path)
    summarize.update_summary(paths, output)
    first = output.read_text(encoding='utf-8')
    summarize.update_summary(list(reversed(paths)), output)
    assert output.read_text(encoding='utf-8') == first and first.count(summarize.TITLE) == 1
    assert '## Avant adaptation\n\nInchangé.' in first
    lines = [line for line in first.splitlines() if line.startswith('| base_') or line.startswith('| lora_')]
    assert [line.split(' | ')[0] for line in lines] == ['| ' + c for c in run_eval.CONFIGS]
    assert '| base_1agent | 80 | 98,8 % | 50,0 % | 0,0 % | 0,19 | 2,5 % |' in first
    assert lines[1].endswith('| 5120 |') and lines[0].endswith('| non mesuré |')


@pytest.mark.parametrize('change', [dict(mock=True), dict(limit=5), dict(ids=['test-0004']), dict(complete=False),
                                    dict(n=79), dict(input_sha256='0' * 64), dict(official_input=False)])
def test_summary_refuses_ineligible(inputs, tmp_path, change):
    """Un run factice, partiel ou sur d'autres entrées n'est jamais publié."""
    output = tmp_path / 'volet_b.md'
    output.write_text('# Résultats\n', encoding='utf-8')
    with pytest.raises(ValueError):
        summarize.update_summary(write_metrics(tmp_path, {'lora_3agents': change}), output)
    assert output.read_text(encoding='utf-8') == '# Résultats\n'


def test_summary_requires_the_four_configurations(inputs, tmp_path):
    """Une configuration manquante ou fournie deux fois est refusée."""
    paths = write_metrics(tmp_path)
    with pytest.raises(ValueError, match='deux fois'):
        summarize.load_runs(paths[:3] + paths[:1])
    with pytest.raises(SystemExit):
        summarize.main([str(p) for p in paths[:3]])


def fake_runs(tmp_path, inputs, mock=False):
    """Fabrique 4 runs réels minimaux dont les réponses nomment leur configuration."""
    cases = [json.loads(line) for line in inputs.read_text(encoding='utf-8').splitlines()]
    paths = []
    for config in run_eval.CONFIGS:
        path = tmp_path / f'run_{config}'
        path.mkdir()
        run_eval.run_config.write_json(path / 'config.json', dict(config=config, mock=mock,
                                                                  input_sha256=run_eval.expected_inputs_hash()))
        records = []
        for case in cases:
            answer = dict(resume_evenements=f'Réponse {config.upper()[::-1]} pour {case["id"]} [F01].',
                          faits_observes=['[F01] fait'], hypotheses=[], infos_manquantes=[],
                          sources=['doc#1'] if '3agents' in config else [], abstention=False)
            records.append(dict(id=case['id'], passages=[dict(id='doc#1', text='Passage officiel.')],
                                final=dict(text=json.dumps(answer, ensure_ascii=False), answer=answer)))
        (path / 'predictions.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in records),
                                                encoding='utf-8')
        paths.append(path)
    selection = tmp_path / 'double_annotation.csv'
    selection.write_text('id,block_id,label\nfactice-0003,blk,0\nfactice-0001,blk,1\n', encoding='utf-8')
    return paths, selection


def test_blind_sheets_and_reproducible_key(inputs, tmp_path):
    """Deux fiches identiques sans configuration visible, une clé séparée et un tirage reproductible."""
    paths, selection = fake_runs(tmp_path, inputs)
    out = tmp_path / 'aveugle'
    blind_sheets.build(paths, out, selection, inputs)
    sheets = [(out / name).read_text(encoding='utf-8') for name in blind_sheets.SHEETS]
    assert sheets[0] == sheets[1]
    rows = list(csv.DictReader((out / blind_sheets.SHEETS[0]).open(encoding='utf-8', newline='')))
    assert [(r['id'], r['etiquette']) for r in rows] == [(c, l) for c in ('factice-0003', 'factice-0001') for l in 'ABCD']
    assert all(r[c] == '' for r in rows for c in (*blind_sheets.CRITERIA, 'commentaire'))
    assert all(name not in sheets[0] for name in ('base_', 'lora_', '1agent', '3agents'))
    assert rows[0]['trace'].startswith('1: ') and '[F01]' in rows[0]['preuves']
    key = json.loads((out / blind_sheets.KEY).read_text(encoding='utf-8'))['cases']
    for row in rows:
        assert key[row['id']][row['etiquette']].upper()[::-1] in row['reponse']
    again = tmp_path / 'aveugle_bis'
    blind_sheets.build(paths, again, selection, inputs)
    assert json.loads((again / blind_sheets.KEY).read_text(encoding='utf-8'))['cases'] == key
    assert key == {case: blind_sheets.draw_order(case) for case in ('factice-0003', 'factice-0001')}
    orders = {tuple(blind_sheets.draw_order(f'test-{i:04d}').values()) for i in range(1, 31)}
    assert len(orders) > 1 and all(sorted(o) == sorted(run_eval.CONFIGS) for o in orders)
    with pytest.raises(FileExistsError):
        blind_sheets.build(paths, out, selection, inputs)


def test_blind_sheets_refuse_mock_runs(inputs, tmp_path):
    """Des réponses factices ne partent jamais en annotation humaine."""
    paths, selection = fake_runs(tmp_path, inputs, mock=True)
    with pytest.raises(ValueError, match='factice'):
        blind_sheets.build(paths, tmp_path / 'aveugle', selection, inputs)


def test_weighted_kappa_by_hand():
    """Exemple calculé à la main : observé 0,125, attendu 0,34375, kappa 7/11 ; accord exact 1/2."""
    first, second = [0, 1, 2, 2], [0, 2, 2, 1]
    assert blind_scores.weighted_kappa(first, second) == pytest.approx(7 / 11)
    assert blind_scores.exact_agreement(first, second) == 0.5
    assert blind_scores.weighted_kappa([0, 1, 2], [0, 1, 2]) == pytest.approx(1)
    assert blind_scores.weighted_kappa([2, 2], [2, 2]) is None


def test_scores_means_agreement_and_disagreements(inputs, tmp_path):
    """Le dépouillement donne moyennes par configuration, accord par critère et désaccords à arbitrer."""
    paths, selection = fake_runs(tmp_path, inputs)
    out = tmp_path / 'aveugle'
    blind_sheets.build(paths, out, selection, inputs)
    key = json.loads((out / blind_sheets.KEY).read_text(encoding='utf-8'))['cases']
    for number, name in enumerate(blind_sheets.SHEETS, 1):
        path = out / name
        rows = list(csv.DictReader(path.open(encoding='utf-8', newline='')))
        for row in rows:
            base = 2 if key[row['id']][row['etiquette']].startswith('lora') else 1
            row.update(F=str(base), S='2', A='2', U=str(base if number == 1 or row['id'] != 'factice-0001' else 0))
        with path.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=blind_sheets.COLUMNS, lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
    result = blind_scores.score(out)
    assert result['configurations']['lora_1agent']['moyennes']['F']['ensemble'] == 2
    assert result['configurations']['base_1agent']['total_sur_8'] == 5.75
    assert result['configurations']['lora_3agents']['moyennes']['U'] == dict(annotateur_1=2, annotateur_2=1, ensemble=1.5)
    assert result['accord']['F']['accord_exact'] == 1 and result['accord']['F']['kappa_quadratique'] == pytest.approx(1)
    assert result['accord']['S']['kappa_quadratique'] is None and result['accord']['U']['accord_exact'] == 0.5
    disagreements = list(csv.DictReader((out / blind_scores.DISAGREEMENTS).open(encoding='utf-8', newline='')))
    assert len(disagreements) == result['desaccords'] == 4
    assert all(d['id'] == 'factice-0001' and d['critere'] == 'U' and d['arbitrage'] == '' for d in disagreements)
    assert 'agent' not in (out / blind_scores.DISAGREEMENTS).read_text(encoding='utf-8')


def test_scores_refuse_missing_grade(inputs, tmp_path):
    """Une grille incomplète est refusée avec le cas et le critère manquants."""
    paths, selection = fake_runs(tmp_path, inputs)
    out = tmp_path / 'aveugle'
    blind_sheets.build(paths, out, selection, inputs)
    with pytest.raises(ValueError, match='factice-0003 A F'):
        blind_scores.score(out)
