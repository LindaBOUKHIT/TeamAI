"""Sélection documentaire bornée, depuis les seuls événements du bloc."""
import json

from teamai.paths import PROMPTS
from volet_b.rag.retriever import query_for_events

PROMPT = PROMPTS / 'search.txt'
PASSAGE_CHAR_BUDGET = 3000


def select_passages(block, retriever, call_slm, k=5):
    """Recherche les candidats, fait sélectionner leurs IDs puis borne leur texte."""
    events = [event['event'] for event in block['raw_events']]
    query = query_for_events(events)
    candidates = retriever.search(query, k)
    result = dict(events=events, query=query, candidates=candidates, passages=[], adjustments=[], errors=[])
    if not candidates:
        return result
    ids = [p['id'] for p in candidates]
    spec = {'type': 'object', 'additionalProperties': False, 'required': ['passages', 'manque'],
            'properties': {'passages': {'type': 'array', 'items': {'type': 'string', 'enum': ids},
                                        'maxItems': 2, 'uniqueItems': True},
                           'manque': {'type': 'string', 'maxLength': 240}}}
    guard = getattr(call_slm, 'context_error', None)
    shown = list(candidates)
    while True:
        prompt = (PROMPT.read_text(encoding='utf-8').strip() + '\n\nFAITS :\n' + '\n'.join(block['facts'])
                  + '\n\nCANDIDATS :\n' + '\n\n'.join(f"[{p['id']}]\n{p['text'][:500]}" for p in shown))
        problem = guard(prompt) if guard else None
        if not problem:
            break
        result['adjustments'].append({'reason': 'context_search', 'id': shown[-1]['id'], 'error': problem})
        shown.pop()
        if not shown:
            # Aucun appel : la rédaction se fera sans passage, comme v16.
            return result
    ids = [p['id'] for p in shown]
    spec['properties']['passages']['items']['enum'] = ids
    out = call_slm(prompt, {'type': 'json_object', 'schema': spec})
    try:
        answer = json.loads(out['text'])
    except (ValueError, TypeError):
        answer = None
    selected = answer.get('passages') if isinstance(answer, dict) else None
    if (not isinstance(answer, dict) or set(answer) != {'passages', 'manque'}
            or not isinstance(answer.get('manque'), str) or len(answer['manque']) > 240
            or not isinstance(selected, list) or len(selected) > 2
            or any(not isinstance(p, str) or p not in ids for p in selected)
            or len(set(selected)) != len(selected) or out['finish_reason'] != 'stop'):
        result['errors'] = ['sélection documentaire invalide']
        return result
    result['manque'] = answer['manque']
    remaining = PASSAGE_CHAR_BUDGET
    by_id = {p['id']: p for p in candidates}
    for pid in selected:
        passage = by_id[pid]
        text = passage['text'][:remaining]
        if len(text) < len(passage['text']):
            result['adjustments'].append({'reason': 'passage_char_budget', 'id': pid,
                                          'original_chars': len(passage['text']), 'kept_chars': len(text)})
        if text:
            result['passages'].append({**passage, 'text': text})
        remaining -= len(text)
    return result
