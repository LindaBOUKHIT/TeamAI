"""SCRUM-42 : trois rôles successifs, sans modèle, index ou split réservé."""
import json
from pathlib import Path

import pandas as pd
import pytest

from data.parse_hdfs import compile_templates
from teamai.contracts import validate_answer
from teamai.paths import SAMPLE
from volet_b.agents import orchestrator as orchestration
from volet_b.agents.roles import checker, search, writer
from volet_b.slm.v16.facts import prepare_block
from volet_b.slm.v16.runtime import build_prompt

FIXTURES = Path(__file__).parent / 'fixtures'
PASSAGES = [dict(id=f'doc#section#{i}', text=f'Documentation officielle HDFS, passage {i}.',
                 score=1.0 / i, scores={'fake': 1.0 / i}) for i in (1, 2, 3)]


@pytest.fixture
def block():
    """Prépare deux événements reconnus sans incident, avec leurs numéros source."""
    lines = [(10, '081109 203518 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /f. blk_1'),
             (20, '081109 203519 143 INFO dfs.DataNode$DataXceiver: Receiving block blk_1 src: /a:1 dest: /a:2')]
    return prepare_block('blk_1', lines, compile_templates(FIXTURES / 'preprocessed/HDFS.log_templates.csv'), split='val')


class FakeRetriever:
    """Rend des passages fixes et mémorise la requête effectivement exécutée."""

    def __init__(self, passages=PASSAGES):
        """Associe la liste de candidats sans construire d'index."""
        self.passages, self.queries = passages, []

    def search(self, query, k):
        """Enregistre le texte et k puis renvoie les premiers candidats."""
        self.queries.append((query, k))
        return self.passages[:k]


class FakeSLM:
    """Appels déterministes, avec verdicts ou corruptions de rédaction configurables."""

    def __init__(self, verdict='accepte', corrupt=None, selected=None):
        """Prépare le journal et les comportements nécessaires aux cas limites."""
        self.verdict, self.corrupt, self.selected = verdict, corrupt, selected
        self.calls, self.writings = [], []

    def __call__(self, prompt, response_format):
        """Simule le rôle indiqué par le schéma sans lire de réponse attendue."""
        self.calls.append((prompt, response_format))
        out = orchestration.mock_call_slm(prompt, response_format)
        properties = response_format['schema']['properties']
        answer = json.loads(out['text'])
        if 'verdict' in properties:
            answer = {'verdict': self.verdict, 'motifs': ['Affirmation à vérifier.'] if self.verdict != 'accepte' else []}
        elif 'passages' in properties and self.selected is not None:
            answer['passages'] = self.selected
        elif 'resume_evenements' in properties:
            if self.corrupt:
                answer = self.corrupt(answer, len(self.writings))
            # Les espaces du brut doivent survivre, même au dernier contrôle.
            out['text'] = ' \n' + json.dumps(answer, ensure_ascii=False) + '\n '
            self.writings.append(out['text'])
            return out
        out['text'] = json.dumps(answer, ensure_ascii=False)
        return {**out, 'seconds': 0.25, 'prompt_tokens': 123, 'new_tokens': 40}


def test_nominal_three_calls(block):
    """Le chemin nominal exécute recherche, rédaction et contrôle, en trois appels."""
    slm, retriever = FakeSLM(), FakeRetriever()
    record = orchestration.explain_block_three_agents(block, retriever, slm)
    assert record['statut'] == 'accepte' and record['errors'] == []
    assert record['n_calls'] == 3 and record['n_retries'] == 0
    assert [s['agent'] for s in record['steps']] == ['search', 'writer', 'checker']
    assert retriever.queries == [(record['query'], 5)]
    assert record['parsed_response']['sources'] == [PASSAGES[0]['id']]
    assert record['candidates'][0]['scores'] == PASSAGES[0]['scores']
    assert all(s['prompt_chars'] > 0 and s['prompt_tokens'] is not None for s in record['steps'])
    assert record['raw_text'] == slm.writings[-1]


def test_code_error_skips_checker_then_retries(block):
    """Une source inconnue déclenche une reprise sans appel de contrôle sur le texte fautif."""
    def corrupt(answer, index):
        """Introduit une source invalide dans la première rédaction seulement."""
        return {**answer, 'sources': ['absent']} if index == 0 else answer

    slm = FakeSLM(corrupt=corrupt)
    record = orchestration.explain_block_three_agents(block, FakeRetriever(), slm)
    assert record['statut'] == 'accepte' and record['n_retries'] == 1
    assert record['n_calls'] == 4
    assert [s['agent'] for s in record['steps']] == ['search', 'writer', 'writer', 'checker']
    assert any('sources' in error for error in record['steps'][1]['errors'])
    assert 'CORRECTION UNIQUE' in slm.calls[2][0]


def test_always_correct_stops_at_five_calls(block):
    """Un contrôleur qui refuse les deux rédactions ne provoque jamais de troisième essai."""
    slm = FakeSLM(verdict='corriger')
    record = orchestration.explain_block_three_agents(block, FakeRetriever(), slm)
    assert record['statut'] == 'rejete' and record['n_calls'] == len(slm.calls) == 5
    assert record['n_retries'] == 1 and record['errors']
    assert record['raw_text'] == slm.writings[-1]


@pytest.mark.parametrize('limit', [0, 1, 2, 3, 4])
def test_strict_call_limit(block, limit):
    """Le plafond est vérifié avant chaque appel, y compris pendant la correction."""
    slm = FakeSLM(verdict='corriger')
    record = orchestration.explain_block_three_agents(block, FakeRetriever(), slm, max_calls=limit)
    assert len(slm.calls) == record['n_calls'] == limit
    assert record['statut'] == 'rejete'
    assert any('limite' in e for e in record['errors'])
    if slm.writings:
        assert record['raw_text'] == slm.writings[-1]


@pytest.mark.parametrize('sources', [['doc#section#2'], ['doc#section#1', 'doc#section#1'], [{}]])
def test_sources_must_be_selected_and_unique(block, sources):
    """Les sources hors sélection, dupliquées ou non textuelles sont refusées sans crash."""
    slm = FakeSLM(corrupt=lambda answer, index: {**answer, 'sources': sources})
    record = orchestration.explain_block_three_agents(block, FakeRetriever(), slm)
    assert record['statut'] == 'rejete' and record['n_calls'] == 3
    assert any('sources' in e for e in record['errors'])
    assert not record['c5_valid']


def test_abstention_verdict_preserves_writing(block):
    """Le verdict d'abstention change le statut sans réécrire la réponse de rédaction."""
    slm = FakeSLM(verdict='abstention')
    record = orchestration.explain_block_three_agents(block, FakeRetriever(), slm)
    assert record['statut'] == 'abstention_demandee' and record['n_calls'] == 3
    assert record['raw_text'] == slm.writings[-1]
    assert record['parsed_response']['abstention'] is False


def test_no_candidates_preserves_v16_prompt(block):
    """Sans candidats, la recherche ne génère rien et la rédaction garde le prompt v16 exact."""
    slm = FakeSLM()
    record = orchestration.explain_block_three_agents(block, FakeRetriever([]), slm)
    assert record['n_calls'] == 2 and record['statut'] == 'accepte'
    assert slm.calls[0][0] == build_prompt(block)
    assert record['parsed_response']['sources'] == []


def test_prompts_exclude_metadata(block):
    """Les métadonnées arbitraires ne se retrouvent dans aucun prompt d'agent."""
    slm = FakeSLM(verdict='corriger')
    block.update(label='SECRET_ANNOTATION', split='SECRET_SPLIT', expected='SECRET_EXPECTED')
    orchestration.explain_block_three_agents(block, FakeRetriever(), slm)
    assert len(slm.calls) == 5
    for prompt, _ in slm.calls:
        assert 'label' not in prompt.lower() and 'split' not in prompt.lower()
        assert 'SECRET_' not in prompt


def test_writer_detects_prompt_drift(block, monkeypatch):
    """Une chaîne v16 modifiée provoque une erreur explicite avant toute inférence."""
    monkeypatch.setattr(writer, 'build_prompt', lambda block: 'instruction modifiée')
    with pytest.raises(ValueError, match='chaîne v16'):
        writer.build_request(block, PASSAGES[:1])


def test_passage_budget_and_candidate_truncation(block):
    """Le sélecteur voit 500 caractères par candidat et conserve au plus 3000 caractères."""
    passages = [{**p, 'text': char * 2500} for p, char in zip(PASSAGES, 'XYZ')]
    slm = FakeSLM(selected=[p['id'] for p in passages[:2]])
    record = orchestration.explain_block_three_agents(block, FakeRetriever(passages), slm)
    assert record['statut'] == 'accepte'
    assert 'X' * 500 in slm.calls[0][0] and 'X' * 501 not in slm.calls[0][0]
    assert sum(len(p['text']) for p in record['passages']) == search.PASSAGE_CHAR_BUDGET
    assert record['passages'][-1]['text'] == 'Y' * 500
    assert record['adjustments'][-1]['reason'] == 'passage_char_budget'


def test_context_drops_last_passages_before_writing(block):
    """Le garde retire les passages avant l'appel et adapte les sources du schéma."""
    slm = FakeSLM(selected=[p['id'] for p in PASSAGES[:2]])
    slm.context_error = lambda prompt: 'contexte insuffisant' if 'DOCUMENTATION (' in prompt else None
    record = orchestration.explain_block_three_agents(block, FakeRetriever(), slm)
    assert record['statut'] == 'accepte' and record['passages'] == []
    assert slm.calls[1][0] == build_prompt(block)
    assert [note['id'] for note in record['adjustments']] == [PASSAGES[1]['id'], PASSAGES[0]['id']]
    assert record['parsed_response']['sources'] == []


def test_context_failure_without_passages_does_not_generate(block):
    """Un prompt v16 trop long est rejeté et ne consomme aucun appel de rédaction."""
    slm = FakeSLM()
    slm.context_error = lambda prompt: 'contexte insuffisant'
    record = orchestration.explain_block_three_agents(block, FakeRetriever([]), slm)
    assert record['statut'] == 'rejete' and record['n_calls'] == 0
    assert any('contexte' in e for e in record['errors'])


def test_invalid_json_is_never_repaired_by_code(block):
    """Deux sorties JSON invalides sont conservées telles quelles et rejetées sans contrôleur SLM."""
    texts = iter(['{invalide premier', '{invalide dernier'])

    def call_slm(prompt, response_format):
        """Simule seulement les deux rédactions, sans passages."""
        return dict(text=next(texts), new_tokens=5, seconds=0.1, prompt_tokens=20, finish_reason='stop')

    record = orchestration.explain_block_three_agents(block, FakeRetriever([]), call_slm)
    assert record['raw_text'] == '{invalide dernier' and record['parsed_response'] is None
    assert record['statut'] == 'rejete' and record['n_calls'] == 2


def test_generation_parameters_match_v16(monkeypatch):
    """Un seul modèle chargé sert au garde et generate reçoit les paramètres v16."""
    model, calls, loads, guards = object(), [], [], []
    monkeypatch.setattr(orchestration, 'load_config', lambda: {'local_files_only': False})
    monkeypatch.setattr(orchestration, 'load_backend', lambda cfg, adapter: loads.append((cfg, adapter)) or model)
    monkeypatch.setattr(orchestration, 'generate', lambda messages, **options: calls.append((messages, options)) or {})
    monkeypatch.setattr(orchestration, 'v16_context_error', lambda llm, messages, cfg: guards.append(llm))
    call_slm = orchestration.make_call_slm('adapter', offline=True)
    call_slm.context_error('prompt')
    call_slm('prompt', {'type': 'json_object', 'schema': {}})
    call_slm('autre prompt', {'type': 'json_object', 'schema': {}})
    assert len(loads) == 1 and guards == [model]
    options = calls[0][1]
    assert options == dict(adapter='adapter', backend='llamacpp', max_new_tokens=800, do_sample=False,
                           repetition_penalty=1.0, seed=42, enable_thinking=False,
                           response_format={'type': 'json_object', 'schema': {}}, return_metadata=True,
                           enforce_v16_context=True, local_files_only=True)


def test_cli_refuses_reserved_split_and_blocks(monkeypatch, tmp_path):
    """La CLI refuse le nom du split et un identifiant artificiel marqué réservé."""
    with pytest.raises(SystemExit):
        orchestration.main(['--split', 'test', '--mock'])
    monkeypatch.setattr(orchestration, 'official_split', lambda: pd.Series({'blk_1': 'test'}))
    monkeypatch.setattr(orchestration, 'select_blocks', lambda args: {'blk_1': []})
    # Force uniquement la branche de sélection officielle, sans lire de bloc réservé.
    (tmp_path / 'splits.csv').write_text('BlockId,split\nblk_1,test\n', encoding='utf-8')
    monkeypatch.setattr(orchestration, 'SPLITS', tmp_path)
    with pytest.raises(SystemExit, match='split test'):
        orchestration.main(['--block', 'blk_1', '--mock'])


def test_cli_mock_five_validation_blocks(tmp_path, monkeypatch):
    """Exécute cinq vrais blocs val en mode factice et isole les sorties C7 sous tmp_path."""
    if not (SAMPLE / 'HDFS_sample.log').exists():
        pytest.skip('data/sample absent')
    monkeypatch.setattr(orchestration, 'RUNS', tmp_path / 'runs')
    monkeypatch.setattr(orchestration, 'load_backend', lambda *args: pytest.fail('chargement SLM en mode mock'))
    monkeypatch.setattr(orchestration, 'load_retriever', lambda *args, **kwargs: pytest.fail('index en mode mock'))
    run = orchestration.main(['--split', 'val', '--n', '5', '--mock'])
    records = [json.loads(line) for line in (run / 'predictions.jsonl').read_text(encoding='utf-8').splitlines()]
    config = json.loads((run / 'config.json').read_text(encoding='utf-8'))
    summary = json.loads((run / 'metrics.json').read_text(encoding='utf-8'))
    assert run.parent == tmp_path / 'runs'
    assert len(records) == summary['n_blocks'] == summary['c5_valid'] == 5
    assert all(r['statut'] == 'accepte' and r['split'] == 'val' and r['mock'] for r in records)
    assert all(r['n_calls'] == 3 and not r['errors'] for r in records)
    assert all(validate_answer(r['parsed_response'], [p['id'] for p in r['passages']]) == [] for r in records)
    assert summary['calls_mean'] == summary['calls_max'] == 3
    assert config['ticket'] == 'SCRUM-42' and config['agents'] == 3 and config['max_calls'] == 5
    assert set(config['prompts_sha256']) == {'search', 'writer', 'checker'}
    assert config['source']['split'] == 'val' and config['mock']
