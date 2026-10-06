"""Vérification des formats d'échange de docs/contrats.md (C5 : exemple d'explication et réponse du SLM).

    from teamai.contracts import validate_answer, validate_example, load_jsonl, leaked_blocks
    errors = validate_answer(json.loads(out["text"]))      # [] si la réponse du SLM respecte C5
    errors = validate_example(ligne_jsonl)                  # [] si l'exemple annoté est complet

Chaque fonction renvoie la liste des problèmes trouvés plutôt que de lever une exception :
on peut ainsi compter le taux de sorties conformes (critère d'évaluation du volet B).
"""
import json
from pathlib import Path

ANSWER_LISTS = ("faits_observes", "hypotheses", "infos_manquantes", "sources")
SPLITS = {"train", "val", "test"}


def validate_answer(answer: object) -> list[str]:
    """Réponse du SLM / bloc `expected` d'un exemple (C5)."""
    if not isinstance(answer, dict):
        return [f"la réponse doit être un objet JSON, reçu {type(answer).__name__}"]
    errors = []
    if not isinstance(answer.get("resume_evenements"), str) or not answer.get("resume_evenements", "").strip():
        errors.append("resume_evenements : texte non vide attendu")
    for key in ANSWER_LISTS:
        value = answer.get(key)
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            errors.append(f"{key} : liste de textes attendue")
    if not isinstance(answer.get("abstention"), bool):
        errors.append("abstention : booléen attendu")
    elif answer["abstention"] is False and not answer.get("sources"):
        errors.append("sources : au moins une source attendue quand le modèle ne s'abstient pas")
    return errors


def validate_example(example: object) -> list[str]:
    """Ligne d'un fichier volet_b/annotations/*.jsonl ou eval/volet_b/test.jsonl (C5)."""
    if not isinstance(example, dict):
        return [f"l'exemple doit être un objet JSON, reçu {type(example).__name__}"]
    errors = []
    for key in ("id", "block_id", "annotator"):
        if not isinstance(example.get(key), str) or not example.get(key):
            errors.append(f"{key} : texte non vide attendu")
    if not str(example.get("block_id", "")).startswith("blk_"):
        errors.append("block_id : doit commencer par blk_")
    if example.get("split") not in SPLITS:
        errors.append(f"split : une valeur parmi {sorted(SPLITS)} attendue")
    if example.get("label") not in (0, 1):
        errors.append("label : 0 (normal) ou 1 (anomalie) attendu")
    for key in ("trace_lines", "events"):
        value = example.get(key)
        if not isinstance(value, list) or not value or not all(isinstance(v, str) for v in value):
            errors.append(f"{key} : liste de textes non vide attendue")
    errors += [f"expected.{e}" for e in validate_answer(example.get("expected"))]
    return errors


def load_jsonl(path: Path) -> list[dict]:
    """Lit un fichier JSONL ; une ligne illisible lève une erreur indiquant son numéro."""
    rows = []
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, start=1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as e:
                    raise ValueError(f"{path}:{n} : JSON invalide ({e.msg})") from e
    return rows


def leaked_blocks(training: list[dict], test: list[dict]) -> set[str]:
    """Blocs présents à la fois dans des données d'adaptation et dans le test réservé (doit être vide)."""
    return {r["block_id"] for r in training} & {r["block_id"] for r in test}
