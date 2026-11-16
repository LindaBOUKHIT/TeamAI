"""Contrôles déterministes puis revue sémantique du dernier texte brut."""
import json

from teamai.contracts import validate_answer
from teamai.paths import PROMPTS
from volet_b.slm.v16.explain import repetition_errors
from volet_b.slm.v16.runtime import INSTRUCTION, build_prompt, validate

PROMPT = PROMPTS / 'checker.txt'


def code_checks(out, block, passages):
    """Contrôle une copie sans sources avec v16, puis les citations réelles avec C5."""
    try:
        answer = json.loads(out['text'])
    except (ValueError, TypeError):
        answer = None
    ids = [p['id'] for p in passages]
    errors = validate_answer(answer, allowed_sources=ids)
    copy = {**answer, 'sources': []} if isinstance(answer, dict) else answer
    try:
        contract, factual, review = validate(json.dumps(copy, ensure_ascii=False), block)
        errors.extend(contract + factual)
    except (TypeError, ValueError, KeyError) as exc:
        errors.append('réponse incompatible avec v16 : ' + str(exc))
        review = []
    if isinstance(answer, dict) and isinstance(answer.get('sources'), list):
        sources = answer['sources']
        if all(isinstance(s, str) for s in sources) and len(sources) != len(set(sources)):
            errors.append('sources : doublons interdits')
    errors.extend(repetition_errors(out['text'], out['new_tokens'], 800))
    if out['finish_reason'] != 'stop':
        errors.append('génération tronquée ou arrêt inattendu : ' + str(out['finish_reason']))
    return answer, list(dict.fromkeys(errors)), review


def check(out, block, passages, call_slm, checks=None):
    """Demande une revue au SLM uniquement lorsque tous les contrôles code passent."""
    answer, errors, review = checks if checks is not None else code_checks(out, block, passages)
    result = dict(answer=answer, errors=errors, code_errors=errors, review=review, verdict='corriger', motifs=errors)
    if errors:
        return result
    spec = {'type': 'object', 'additionalProperties': False, 'required': ['verdict', 'motifs'],
            'properties': {'verdict': {'type': 'string', 'enum': ['accepte', 'corriger', 'abstention']},
                           'motifs': {'type': 'array', 'maxItems': 3,
                                      'items': {'type': 'string', 'maxLength': 240}}}}
    shown = list(passages)
    guard = getattr(call_slm, 'context_error', None)
    while True:
        prompt = (PROMPT.read_text(encoding='utf-8').strip() + '\n\nPREUVES DU BLOC :\n'
                  + build_prompt(block).removeprefix(INSTRUCTION) + '\n\nDOCUMENTATION :\n'
                  + ('\n\n'.join(f"[{p['id']}]\n{p['text']}" for p in shown) or '(aucun passage fourni)')
                  + '\n\nREPONSE A CONTROLER :\n' + out['text'])
        problem = guard(prompt) if guard else None
        if not problem:
            break
        if not shown:
            # Aucun appel : le contrôle sémantique est impossible, la réponse n'est pas acceptée.
            result.update(verdict='non_controle', errors=['contrôle SLM impossible : ' + str(problem)], motifs=[])
            return result
        result.setdefault('adjustments', []).append({'reason': 'context_checker', 'id': shown[-1]['id'],
                                                     'error': problem})
        shown.pop()
    response = call_slm(prompt, {'type': 'json_object', 'schema': spec})
    try:
        verdict = json.loads(response['text'])
    except (ValueError, TypeError):
        verdict = None
    if (not isinstance(verdict, dict) or set(verdict) != {'verdict', 'motifs'}
            or verdict.get('verdict') not in ('accepte', 'corriger', 'abstention')
            or not isinstance(verdict.get('motifs'), list) or len(verdict['motifs']) > 3
            or any(not isinstance(m, str) or len(m) > 240 for m in verdict['motifs'])
            or response['finish_reason'] != 'stop'):
        result.update(errors=['verdict de contrôle invalide'], motifs=['verdict de contrôle invalide'])
    else:
        result.update(verdict)
    return result
