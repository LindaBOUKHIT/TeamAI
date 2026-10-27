"""SCRUM-63 : équivalence v16 et contrôle anti-boucle, sans réseau ni GGUF."""
import ast
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from types import SimpleNamespace
import sys

from data.parse_hdfs import compile_templates
from volet_b.slm.v16 import policy, runtime
from volet_b.slm.v16.explain import repetition_errors
from volet_b.slm.v16.facts import prepare_block

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tests/fixtures/v16'
TRACE = ROOT / 'eval/results/SCRUM-63'


def load(path):
    """Lit un artefact JSON UTF-8 de référence."""
    return json.loads(path.read_text(encoding='utf-8'))


def digest(text):
    """Calcule l'empreinte UTF-8 avec la même convention que la v16."""
    return hashlib.sha256(text.encode()).hexdigest()


def without_docstrings(tree):
    """Retire les seules docstrings ajoutées au port pour comparer la politique exécutée."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef)) and ast.get_docstring(node):
            node.body.pop(0)
    return ast.dump(tree, include_attributes=False)


def prepared_blocks():
    """Reconstruit les 40 blocs val depuis leurs lignes brutes, sans faits précalculés."""
    templates = compile_templates(ROOT / 'tests/fixtures/preprocessed/HDFS.log_templates.csv')
    inputs = load(FIXTURES / 'blocks.json')
    assert len(inputs) == 40 and all(b['split'] == 'val' and 'label' not in b for b in inputs)
    return [prepare_block(b['block_id'], b['lines'], templates, i, b['split']) for i, b in enumerate(inputs)]


class FrozenV16Tests(unittest.TestCase):
    """Protège les empreintes originales, le schéma et la correction unique."""

    def test_frozen_prompts_instruction_policy_and_schemas(self):
        """Vérifie 40 prompts et schémas reconstruits ; aucune empreinte n'est recalculée en fixture."""
        freeze = load(TRACE / 'prompt_freeze.json')
        self.assertEqual(digest(runtime.INSTRUCTION), freeze['instruction_sha256'])
        frozen_policy = (TRACE / 'policy_v16.txt').read_bytes()
        self.assertEqual(hashlib.sha256(frozen_policy).hexdigest(), freeze['policy_sha256'])
        self.assertEqual(without_docstrings(ast.parse(frozen_policy)),
                         without_docstrings(ast.parse((ROOT / 'volet_b/slm/v16/policy.py').read_text(encoding='utf-8'))))
        blocks = prepared_blocks()
        self.assertEqual([digest(runtime.build_prompt(b)) for b in blocks], freeze['prompt_sha256'])
        self.assertEqual([digest(json.dumps(runtime.schema(b), ensure_ascii=False, sort_keys=True)) for b in blocks],
                         freeze['schema_sha256'])

    def test_loop_normal_and_budget(self):
        """Rejette la boucle F09 réelle et le budget quasi épuisé, accepte une vraie réponse normale."""
        loop, normal = load(FIXTURES / 'loop.json'), load(FIXTURES / 'normal.json')
        errors = repetition_errors(loop['text'], loop['new_tokens'])
        self.assertTrue(any('F09' in e for e in errors))
        self.assertTrue(any('783/800' in e for e in errors))
        self.assertEqual(repetition_errors(normal['text'], normal['new_tokens']), [])
        self.assertEqual(repetition_errors('texte normal', 759), [])
        self.assertTrue(repetition_errors('texte normal', 760))
        self.assertTrue(repetition_errors('même phrase. ' * 6, 60))
        self.assertTrue(repetition_errors(('une très longue phrase avec plus de seize mots qui décrit un événement sans jamais pouvoir terminer son explication. ' * 6), 150))
        self.assertEqual(repetition_errors('F09 puis F01. F09 puis F02. F09 puis F03.', 40), [])

    def test_single_correction_preserves_both_raw_responses(self):
        """Une boucle déclenche exactement un second appel et conserve les textes et erreurs."""
        block = prepared_blocks()[0]
        loop = load(FIXTURES / 'loop.json')
        prompts, saved = [], []

        def infer(current, prompt, attempt):
            """Simule la boucle réelle, y compris si la correction boucle encore."""
            prompts.append(prompt)
            return runtime.evaluate_response({'choices': [{'message': {'content': loop['text']}, 'finish_reason': 'stop'}],
                                              'usage': {'prompt_tokens': 2000, 'completion_tokens': 783}},
                                             current, prompt, 1.0, attempt)

        result = runtime.run_block(block, infer, saved.append, lambda prompt: None)
        self.assertEqual(result['attempt_count'], 2)
        self.assertEqual(len(saved), 2)
        self.assertEqual(result['first_response']['text'], loop['text'])
        self.assertEqual(result['second_response']['text'], loop['text'])
        self.assertFalse(result['ok'])
        self.assertEqual(prompts[0], runtime.build_prompt(block))
        self.assertIn('CORRECTION UNIQUE', prompts[1])
        self.assertIn('référence répétée en boucle : F09', prompts[1])

    def test_normal_does_not_retry(self):
        """Une réponse réelle normale ne déclenche pas le contrôle supplémentaire."""
        block = prepared_blocks()[0]
        normal = load(FIXTURES / 'normal.json')

        def infer(current, prompt, attempt):
            """Évalue la réponse normale avec les contrôles de production."""
            return runtime.evaluate_response({'choices': [{'message': {'content': normal['text']}, 'finish_reason': 'stop'}],
                                              'usage': {'prompt_tokens': 2000, 'completion_tokens': normal['new_tokens']}},
                                             current, prompt, 1.0, attempt)

        result = runtime.run_block(block, infer, lambda response: None, lambda prompt: None)
        self.assertEqual(result['attempt_count'], 1)
        self.assertTrue(result['ok'])

    def test_explain_uses_generate_and_recovers_once(self):
        """Le port complet envoie le schéma et garde la première boucle après correction réussie."""
        from volet_b.slm.v16.explain import explain_block

        block = prepared_blocks()[0]
        loop, normal = load(FIXTURES / 'loop.json'), load(FIXTURES / 'normal.json')
        calls = []

        def generate(messages, adapter=None, **options):
            """Simule seulement l'interface publique, sans importer ni charger un backend."""
            calls.append((messages, adapter, options))
            response = loop if len(calls) == 1 else normal
            return {**response, 'seconds': 1.0, 'finish_reason': 'stop', 'prompt_tokens': 2000}

        fake = SimpleNamespace(generate=generate, load_config=lambda: {}, load_backend=lambda *args: None,
                               v16_context_error=lambda *args: None)
        with patch.dict(sys.modules, {'volet_b.slm.generate': fake}):
            result = explain_block(block)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][0][0]['content'], runtime.build_prompt(block))
        self.assertEqual(calls[0][2]['response_format'], {'type': 'json_object', 'schema': runtime.schema(block)})
        self.assertEqual(calls[0][2]['enable_thinking'], False)
        self.assertEqual(result['first_response']['text'], loop['text'])
        self.assertEqual(result['second_response']['text'], normal['text'])
        self.assertTrue(result['ok'])
        self.assertTrue(result['retry_all_checks_success'])

    def test_context_guard_preserves_first_response(self):
        """Une correction trop longue est refusée sans perdre la première réponse."""
        block = prepared_blocks()[0]
        loop = load(FIXTURES / 'loop.json')

        def infer(current, prompt, attempt):
            """Rend la première boucle avec les mêmes mesures que le cas réel."""
            return runtime.evaluate_response({'choices': [{'message': {'content': loop['text']}, 'finish_reason': 'stop'}],
                                              'usage': {'prompt_tokens': 2000, 'completion_tokens': 783}},
                                             current, prompt, 1.0, attempt)

        result = runtime.run_block(block, infer, lambda response: None,
                                   lambda prompt: 'contexte insuffisant pour la réponse complète')
        self.assertEqual(result['attempt_count'], 1)
        self.assertEqual(result['first_response']['text'], loop['text'])
        self.assertIsNone(result['second_response'])
        self.assertIn('contexte insuffisant', result['retry_skipped_reason'])


def test_generate_schema_and_metadata(monkeypatch):
    """Le backend reçoit le schéma, désactive la réflexion et conserve son interface historique."""
    from unittest.mock import MagicMock
    from volet_b.slm import generate as slm

    monkeypatch.delenv('TEAMAI_SLM_MOCK', raising=False)
    llm = MagicMock()
    llm.create_chat_completion.return_value = {
        'choices': [{'message': {'content': '{}'}, 'finish_reason': 'stop'}],
        'usage': {'completion_tokens': 2, 'prompt_tokens': 123}}
    monkeypatch.setattr(slm, 'load_backend', lambda *args: llm)
    block = prepared_blocks()[0]
    response_format = {'type': 'json_object', 'schema': runtime.schema(block)}
    out = slm.generate('prompt', response_format=response_format, return_metadata=True)
    args = llm.create_chat_completion.call_args.kwargs
    assert args['response_format'] == response_format
    assert 'chat_template_kwargs' not in args
    assert args['max_tokens'] == 800 and args['temperature'] == 0.0 and args['repeat_penalty'] == 1.0
    assert out['finish_reason'] == 'stop' and out['prompt_tokens'] == 123
    assert set(slm.generate('prompt')) == {'text', 'new_tokens', 'seconds'}


if __name__ == '__main__':
    unittest.main()
