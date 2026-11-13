"""Appel local v16 et garde anti-boucle ajouté par SCRUM-63."""
import math
import re


def repetition_errors(text, new_tokens, max_tokens=800):
    """Rejette six répétitions consécutives ou une sortie à au moins 95 % du budget.

    Les références normalement réutilisées entre champs ne sont pas comptées
    ensemble : seule une boucle contiguë est rejetée. Ne change aucun prompt.
    """
    errors = []
    if new_tokens >= math.ceil(max_tokens * 0.95):
        errors.append(f'budget de réponse presque épuisé : {new_tokens}/{max_tokens} tokens (seuil 95 %)')
    match = re.search(r'\b([FTLE]\d+)\b(?:[\s,;\[\]"\-]*\1\b){5,}', text)
    if match:
        errors.append(f'référence répétée en boucle : {match[1]} (au moins 6 fois consécutives)')
    words = re.findall(r'\w+|[^\w\s]', text.casefold())
    for width in range(1, len(words) // 6 + 1):
        for start in range(len(words) - 6 * width + 1):
            segment = words[start:start + width]
            if not any(re.search(r'\w', word) for word in segment):
                continue
            if all(words[start + k * width:start + (k + 1) * width] == segment for k in range(1, 6)):
                errors.append('segment répété en boucle (au moins 6 fois) : ' + ' '.join(segment))
                return errors
    return errors


def explain_block(block, adapter=None):
    """Explique un bloc préparé, conserve les deux réponses et corrige au plus une fois.

    Les réponses restent dans le dictionnaire rendu, à enregistrer par l'appelant.
    Aucun label ni document externe n'est ajouté au prompt v16.
    """
    from volet_b.slm.generate import generate, load_backend, load_config, v16_context_error
    from volet_b.slm.v16.runtime import evaluate_response, run_block, schema

    def infer(current, prompt, attempt):
        """Transmet le schéma fermé à l'interface unique du SLM."""
        out = generate([{'role': 'user', 'content': prompt}], adapter=adapter,
                       backend='llamacpp', max_new_tokens=800, do_sample=False,
                       repetition_penalty=1.0, seed=42, enable_thinking=False,
                       response_format={'type': 'json_object', 'schema': schema(current)},
                       return_metadata=True, enforce_v16_context=True)
        response = {'choices': [{'message': {'content': out['text']},
                                 'finish_reason': out['finish_reason']}],
                    'usage': {'prompt_tokens': out['prompt_tokens'], 'completion_tokens': out['new_tokens']}}
        return evaluate_response(response, current, prompt, out['seconds'], attempt)

    def persist(response):
        """Les tentatives sont conservées par run_block dans le résultat rendu."""

    def can_retry(prompt):
        """Le backend vérifie le contexte de la correction avant tout appel modèle."""
        cfg = {**load_config(), 'backend': 'llamacpp', 'max_new_tokens': 800}
        return v16_context_error(load_backend(cfg, adapter), [{'role': 'user', 'content': prompt}], cfg)

    return run_block(block, infer, persist, can_retry)
