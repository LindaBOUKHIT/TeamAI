"""SCRUM-38 : mesures v16 fabriquées, sans modèle, téléchargement ni test réservé."""
import json
import subprocess
from unittest.mock import Mock

import pytest

from eval.volet_b import run_config as runner
from eval.volet_b.gpu_memory import PeakVRAM
from volet_b.slm import generate as slm
from volet_b.slm.generate import MOCK_ANSWER


@pytest.fixture
def examples(tmp_path, monkeypatch):
    """Fabrique deux C5 train à partir du sample, avec annotations sentinelles."""
    monkeypatch.setenv('TEAMAI_SLM_MOCK', '1')
    monkeypatch.setattr(slm, 'load_backend', lambda *args: None)
    monkeypatch.setattr(slm, 'v16_context_error', lambda *args: None)
    monkeypatch.setattr(runner.PeakVRAM, 'sample', lambda self: None)
    bid = 'blk_4971154345890344'
    lines = [line.rstrip() for line in (runner.SAMPLE / 'HDFS_sample.log').read_text(encoding='utf-8').splitlines() if bid in line]
    rows = [dict(id=f'factice-{i}', block_id=bid, split='train', trace_lines=lines,
                 events=['ANNOTATION_EVENTS_INTERDITE'], label=1,
                 expected={**MOCK_ANSWER, 'resume_evenements': 'ANNOTATION_EXPECTED_INTERDITE'},
                 annotator='ANNOTATEUR_INTERDIT', reviewed_by='RELECTEUR_INTERDIT',
                 extra_annotation='ANNOTATION_SUPPLEMENTAIRE_INTERDITE') for i in range(2)]
    path = tmp_path / 'exemples.jsonl'
    path.write_text(''.join(json.dumps(row) + '\n' for row in rows), encoding='utf-8')
    return path


def read_records(run_dir):
    """Lit les seules prédictions fabriquées pour le test courant."""
    return [json.loads(line) for line in (run_dir / 'predictions.jsonl').read_text(encoding='utf-8').splitlines()]


def fabricated(messages, adapter=None, **options):
    """Rend une réponse v16 conforme en recopiant les faits du schéma transmis."""
    facts = options['response_format']['schema']['properties']['faits_observes']['items']['enum']
    answer = dict(resume_evenements='Les opérations du bloc sont journalisées dans cet intervalle [F01]. Le nombre de WARN est fourni [F02].',
                  faits_observes=facts[:2], hypotheses=[], infos_manquantes=[], sources=[], abstention=False)
    return dict(text=json.dumps(answer), new_tokens=100, seconds=0.25, prompt_tokens=1200, finish_reason='stop')


def test_base_pipeline_and_no_annotation(examples, tmp_path, monkeypatch):
    """Base traverse réellement explain_block et generate avec schéma, sans annotations."""
    spy = Mock(wraps=runner.explain.explain_block)
    generator = Mock(side_effect=fabricated)
    monkeypatch.setattr(runner.explain, 'explain_block', spy)
    monkeypatch.setattr(slm, '_generate', generator)
    first = runner.run_config('base', examples, run_root=tmp_path / 'runs')
    second = runner.run_config('base', examples, limit=1, run_root=tmp_path / 'runs')
    assert first != second and spy.call_count == 3
    assert {p.name for p in first.iterdir()} == {'predictions.jsonl', 'config.json', 'metrics.json'}
    text = str(generator.call_args_list)
    for forbidden in ('label', 'expected', 'ANNOTATION_', 'ANNOTATEUR_INTERDIT', 'RELECTEUR_INTERDIT'):
        assert forbidden not in text
    records = read_records(first)
    assert len(records) == 2 and all(r['slm_calls'] == 1 for r in records)
    assert all(r['attempts'][0]['finish_reason'] == 'stop' for r in records)
    cfg = json.loads((first / 'config.json').read_text(encoding='utf-8'))
    freeze = json.loads(runner.PROMPT_FREEZE.read_text(encoding='utf-8'))
    assert cfg['instruction_sha256'] == freeze['instruction_sha256']
    assert cfg['policy_sha256'] == freeze['policy_sha256']
    assert cfg['gguf_revision'] == runner.load_config()['gguf_revision']
    assert cfg['n_ctx'] == 4096 and cfg['max_new_tokens'] == 800
    assert cfg['slm_calls_actual'] == 2 and 'Nassim' in cfg['target_machine']
    values = json.loads((first / 'metrics.json').read_text(encoding='utf-8'))
    assert values['conformity_rate'] == values['v16_contract_valid_rate'] == values['facts_copied_exactly_rate'] == 1
    assert values['process_peak_rss_bytes'] > 0 and values['process_peak_vram_bytes'] is None


@pytest.mark.parametrize('failure', ['invalid_json', 'exception', 'invalid_input', 'correction_exception'])
def test_failures_and_attempts(examples, tmp_path, monkeypatch, failure):
    """Échecs et correction interrompue restent au dénominateur et conservent chaque appel."""
    calls = 0

    def mixed(messages, adapter=None, **options):
        """Rend une réussite puis un échec déterministe à l'interface du SLM."""
        nonlocal calls
        calls += 1
        out = fabricated(messages, adapter, **options)
        if (calls >= 2 and failure == 'exception') or (calls == 3 and failure == 'correction_exception'):
            raise RuntimeError('échec factice')
        if calls == 2 and failure == 'invalid_json':
            out['text'] = 'pas de JSON'
        if calls == 2 and failure == 'correction_exception':
            out.update(text='F09 ' * 6, new_tokens=783)
        return out

    monkeypatch.setattr(slm, '_generate', mixed)
    if failure == 'invalid_input':
        with examples.open('a', encoding='utf-8') as output:
            output.write('JSON mal formé\n')
    run = runner.run_config('base', examples, run_root=tmp_path / 'runs')
    records = read_records(run)
    values = json.loads((run / 'metrics.json').read_text(encoding='utf-8'))
    n = 3 if failure == 'invalid_input' else 2
    valid = 2 if failure == 'invalid_input' else 1
    assert values['n'] == n and values['c5_valid'] == valid
    assert values['conformity_rate'] == valid / n
    assert values['v16_contract_valid_rate'] == valid / n
    if failure == 'correction_exception':
        assert records[1]['slm_calls'] == 2 and len(records[1]['attempts']) == 2
        assert records[1]['attempts'][0]['text'] == 'F09 ' * 6
        assert records[1]['attempts'][1]['errors'] and records[1]['attempts'][1]['new_tokens'] is None


def test_loop_corrected_and_alert_metrics(examples, tmp_path, monkeypatch):
    """Une boucle corrigée et des alertes fabriquées passent par les contrôles v16 existants."""
    calls = 0

    def responses(messages, adapter=None, **options):
        """Produit boucle, correction réussie, puis références et cause réseau sans appui."""
        nonlocal calls
        calls += 1
        out = fabricated(messages, adapter, **options)
        if calls == 1:
            out.update(text='F09 ' * 6, new_tokens=783)
        elif calls >= 3:
            answer = json.loads(out['text'])
            answer.update(hypotheses=['Une panne réseau pourrait expliquer ceci [L99].'],
                          infos_manquantes=['Quel incident vérifier [L99] ?'])
            out['text'] = json.dumps(answer)
        return out

    monkeypatch.setattr(slm, '_generate', responses)
    run = runner.run_config('base', examples, run_root=tmp_path / 'runs')
    records = read_records(run)
    values = json.loads((run / 'metrics.json').read_text(encoding='utf-8'))
    assert records[0]['v16']['retry_all_checks_success']
    assert values['loop_responses'] == 1 and values['corrections_succeeded'] == 1
    assert values['corrections_triggered'] == values['corrections_attempted'] == 2
    assert values['unknown_references_rate'] == values['unsupported_network_rate'] == 0.5
    assert values['hypotheses_per_block_with_incident'] == 0.5
    assert values['hypotheses_per_block_without_incident'] is None
    assert values['slm_calls'] == 4
    assert records[0]['generation_seconds'] == 0.5 and records[0]['new_tokens'] == 883


def test_investigation_without_incident_and_abstention(examples, tmp_path, monkeypatch):
    """Le groupe sans incident dépend des faits bruts ; une abstention C5 reste au dénominateur."""
    rows = [json.loads(line) for line in examples.read_text(encoding='utf-8').splitlines()]
    rows[0]['trace_lines'] = rows[0]['trace_lines'][:3]
    # label=1 est laissé volontairement en contradiction avec les preuves sans incident.
    examples.write_text(''.join(json.dumps(row) + '\n' for row in rows) + 'invalide\n', encoding='utf-8')

    def answer(messages, adapter=None, **options):
        """Ajoute une demande d'enquête et une abstention aux réponses fabriquées."""
        out = fabricated(messages, adapter, **options)
        parsed = json.loads(out['text'])
        parsed.update(infos_manquantes=['Quel état vérifier pour ce bloc [F01] ?'], abstention=True)
        out['text'] = json.dumps(parsed)
        return out

    monkeypatch.setattr(slm, '_generate', answer)
    run = runner.run_config('base', examples, run_root=tmp_path / 'runs')
    records = read_records(run)
    values = json.loads((run / 'metrics.json').read_text(encoding='utf-8'))
    assert records[0]['attention'] is False and records[1]['attention'] is True
    assert values['blocks_with_incident'] == values['blocks_without_incident'] == 1
    assert values['investigation_without_incident_rate'] == 1 / 3
    assert values['abstention_rate'] == 2 / 3 and values['v16_contract_valid_rate'] == 1 / 3


def test_facts_copy_and_finish_reason(examples, tmp_path, monkeypatch):
    """Une copie modifiée et un arrêt length sont signalés par les contrôles de production."""
    calls = 0

    def changed(messages, adapter=None, **options):
        """Modifie un fait sur le premier exemple et tronque le second."""
        nonlocal calls
        calls += 1
        out = fabricated(messages, adapter, **options)
        if calls == 1:
            answer = json.loads(out['text'])
            answer['faits_observes'][0] += ' texte inventé'
            out['text'] = json.dumps(answer)
        else:
            out['finish_reason'] = 'length'
        return out

    monkeypatch.setattr(slm, '_generate', changed)
    run = runner.run_config('base', examples, run_root=tmp_path / 'runs')
    records = read_records(run)
    values = json.loads((run / 'metrics.json').read_text(encoding='utf-8'))
    assert values['facts_copied_exactly'] == 0
    assert 'fait non conforme aux valeurs calculées' in records[0]['attempts'][0]['factual_errors']
    assert records[1]['finish_reason'] == 'length' and records[1]['attempts'][0]['errors']
    assert values['v16_contract_valid_rate'] == 0.5


def test_missing_and_rag_refused(tmp_path, monkeypatch, capsys):
    """Entrée absente et rag1 sont refusés avant tout modèle et tout dossier de run."""
    forbidden = Mock(side_effect=AssertionError('Aucun appel modèle'))
    monkeypatch.setattr(runner.explain, 'explain_block', forbidden)
    with pytest.raises(SystemExit):
        runner.main(['--config', 'base', '--data', str(tmp_path / 'absent')])
    assert "Fichier d'exemples C5 absent" in capsys.readouterr().err
    with pytest.raises(ValueError, match='SCRUM-42/SCRUM-45'):
        runner.run_config('rag1', tmp_path / 'absent', run_root=tmp_path / 'runs')
    assert not list(tmp_path.iterdir()) and not forbidden.called
    from volet_b.agents.single_agent import retrieve_for_trace
    assert callable(retrieve_for_trace)


def test_official_hash_refusal(examples, tmp_path, monkeypatch):
    """Une empreinte officielle divergente refuse le lancement sur des données fabriquées."""
    reference = tmp_path / 'reference.sha256'
    monkeypatch.setattr(runner, 'VOLET_B_TEST', examples)
    monkeypatch.setattr(runner, 'VOLET_B_TEST_SHA256', reference)
    reference.write_text('0' * 64, encoding='utf-8')
    with pytest.raises(ValueError, match='SHA-256'):
        runner.run_config('base', examples, run_root=tmp_path / 'runs')
    assert not (tmp_path / 'runs').exists()


@pytest.mark.parametrize('change', [{'config': 'rag1'}, {'mock': True}, {'limit': 1}, {'complete': False},
                                    {'official_test': False}, {'adapter': 'lora'}, {'n': 0}])
def test_summary_refuses_ineligible(tmp_path, change):
    """Refuse RAG, factice, partiel, hors test, vide ou adapté sans altérer le résumé."""
    path, output = tmp_path / 'metrics.json', tmp_path / 'resultats.md'
    output.write_text('# Résultats\n\n## Après adaptation\n\nÀ venir.\n', encoding='utf-8')
    values = dict(config='base', mock=False, adapter=None, official_test=True, limit=None, complete=True,
                  n=2, input_sha256='factice', conformity_rate=1, sources_valid_rate=1, abstention_rate=0,
                  latency_mean_seconds=1, latency_median_seconds=1, process_peak_rss_bytes=1024)
    runner.write_json(path, values)
    runner.update_summary([path], output)
    first = output.read_text(encoding='utf-8')
    runner.update_summary([path], output)
    assert output.read_text(encoding='utf-8') == first and first.count('| base |') == 1
    assert '## Après adaptation\n\nÀ venir.' in first
    runner.write_json(path, {**values, **change})
    with pytest.raises(ValueError):
        runner.update_summary([path], output)
    assert output.read_text(encoding='utf-8') == first


def test_gpu_fallback(monkeypatch):
    """Le fallback nvidia-smi ne compte que le PID courant et rend null si absent."""
    import os
    from eval.volet_b import gpu_memory
    sampler = PeakVRAM()
    monkeypatch.setattr(gpu_memory.subprocess, 'run', lambda *a, **k: subprocess.CompletedProcess(a, 0, f'{os.getpid()}, 12\n999999, 80\n'))
    assert sampler.sample() == 12 * 1024**2

    def absent(*args, **kwargs):
        """Simule l'absence du binaire sans dépendance ni matériel GPU."""
        raise FileNotFoundError('nvidia-smi')

    monkeypatch.setattr(gpu_memory.subprocess, 'run', absent)
    assert sampler.sample() is None


def test_gpu_nvml_pid_and_unavailable():
    """NVML additionne le PID courant sur deux GPU et respecte la valeur indisponible."""
    import os
    from types import SimpleNamespace
    sampler = PeakVRAM()
    fake = SimpleNamespace(nvmlDeviceGetCount=lambda: 2, nvmlDeviceGetHandleByIndex=lambda i: i,
        nvmlDeviceGetComputeRunningProcesses=lambda handle: [SimpleNamespace(pid=os.getpid(), usedGpuMemory=1024),
                                                              SimpleNamespace(pid=999999, usedGpuMemory=9999)])
    sampler._nvml = fake
    assert sampler.sample() == 2048
    fake.nvmlDeviceGetComputeRunningProcesses = lambda handle: [SimpleNamespace(pid=os.getpid(), usedGpuMemory=None)]
    assert sampler.sample() is None


@pytest.mark.parametrize('incident', [True, False])
@pytest.mark.parametrize('invalid_response', [None, {'hypotheses': ['à ignorer']}])
def test_hypotheses_per_group_includes_failures(incident, invalid_response):
    """Trois blocs : deux du même groupe dont un échec, même si le JSON est parsé."""
    records = [
        dict(attention=incident, parsed_response={'hypotheses': ['H1', 'H2', 'H3']}, errors=[]),
        dict(attention=incident, parsed_response=invalid_response, errors=['réponse invalide']),
        dict(attention=not incident, parsed_response={'hypotheses': ['H4', 'H5']}, errors=[]),
    ]
    for record in records:
        record.update(seconds=1, sources_valid=False, slm_calls=0, attempts=[])
    values = runner.metrics(records, peak_bytes=0)
    group = 'with_incident' if incident else 'without_incident'
    other = 'without_incident' if incident else 'with_incident'
    assert values['n'] == 3 and values['failures'] == 1
    assert values['blocks_' + group] == 2
    assert values['hypotheses_' + group] == 3
    assert values['hypotheses_per_block_' + group] == 3 / 2
    assert values['blocks_' + other] == 1
    assert values['hypotheses_per_block_' + other] == 2 / 1


@pytest.mark.parametrize('attention', [True, False, None])
def test_hypotheses_empty_group(attention):
    """Un groupe absent vaut None ; un échec connu seul donne zéro dans son groupe."""
    record = dict(attention=attention, parsed_response=None, errors=['échec'],
                  seconds=1, sources_valid=False, slm_calls=0, attempts=[])
    values = runner.metrics([record], peak_bytes=0)
    for group, signal in [('with_incident', True), ('without_incident', False)]:
        assert values['blocks_' + group] == int(attention is signal)
        expected = 0 if attention is signal else None
        assert values['hypotheses_per_block_' + group] == expected
    empty = runner.metrics([], peak_bytes=0)
    assert empty['hypotheses_per_block_with_incident'] is None
    assert empty['hypotheses_per_block_without_incident'] is None
