"""Contrôle par code de la sortie du SLM (SCRUM-37) : JSON valide, format C5, sources limitées aux passages fournis.

    from volet_b.agents.validate import check_answer
    answer, errors = check_answer(out["text"], allowed_sources=[p["id"] for p in passages])

La réponse n'est jamais réparée : une sortie invalide garde `answer = None` (ou la réponse analysée)
et la liste de ses erreurs, pour être comptée telle quelle dans l'évaluation (C7).
"""
import json

from teamai.contracts import validate_answer


def parse_json_answer(text: str) -> tuple[dict | None, list[str]]:
    """Extrait l'objet JSON de la sortie : du premier « { » au dernier « } » (texte autour toléré)."""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        return None, ["invalid_json : aucun objet JSON dans la sortie"]
    try:
        answer = json.loads(text[start:end + 1])
    except json.JSONDecodeError as error:
        return None, [f"invalid_json : {error.msg}"]
    if not isinstance(answer, dict):
        return None, ["invalid_json : la sortie n'est pas un objet JSON"]
    return answer, []


def check_answer(text: str, allowed_sources: list[str]) -> tuple[dict | None, list[str]]:
    """Réponse analysée (ou None) et erreurs : JSON, format C5 et sources hors des passages fournis."""
    answer, errors = parse_json_answer(text)
    if answer is None:
        return None, errors
    return answer, validate_answer(answer, allowed_sources=allowed_sources)
