
import json
from collections import Counter
from pathlib import Path

base = Path("eval/volet_b")
path = base / "annotations_travail.jsonl"
corpus = Path("volet_b/rag/corpus/chunks.jsonl")

rows = [
    json.loads(line)
    for line in path.read_text(encoding="utf-8").splitlines()
    if line.strip()
]

chunks = [
    json.loads(line)
    for line in corpus.read_text(encoding="utf-8").splitlines()
    if line.strip()
]

valid_sources = {c["id"] for c in chunks}
errors = []
warnings = []

required = [
    "resume_evenements",
    "faits_observes",
    "hypotheses",
    "infos_manquantes",
    "sources",
    "abstention",
]

ids = [r.get("id") for r in rows]
blocks = [r.get("block_id") for r in rows]

for value, count in Counter(ids).items():
    if count > 1:
        errors.append(f"ID dupliqué : {value}")

for value, count in Counter(blocks).items():
    if count > 1:
        errors.append(f"Bloc dupliqué : {value}")

for row in rows:
    rid = row.get("id", "?")
    answer = row.get("expected", {})

    if row.get("split") != "test":
        errors.append(f"{rid}: split différent de test")

    if row.get("label") not in (0, 1):
        errors.append(f"{rid}: label invalide")

    if not row.get("trace_lines"):
        errors.append(f"{rid}: trace vide")

    if len(row.get("events", [])) != len(row.get("trace_lines", [])):
        errors.append(f"{rid}: événements et lignes non alignés")

    for field in required:
        if field not in answer:
            errors.append(f"{rid}: champ manquant {field}")

    if not isinstance(answer.get("resume_evenements"), str) or not answer.get("resume_evenements", "").strip():
        errors.append(f"{rid}: résumé vide")

    for field in ("faits_observes", "hypotheses", "infos_manquantes", "sources"):
        value = answer.get(field)
        if not isinstance(value, list) or any(
            not isinstance(x, str) or not x.strip() for x in value
        ):
            errors.append(f"{rid}: liste invalide {field}")

    abstention = answer.get("abstention")
    if not isinstance(abstention, bool):
        errors.append(f"{rid}: abstention non booléenne")

    if abstention is True:
        if answer.get("hypotheses"):
            errors.append(f"{rid}: hypothèses présentes malgré abstention")
        if not answer.get("infos_manquantes"):
            errors.append(f"{rid}: abstention sans informations manquantes")

    for source in answer.get("sources", []):
        if source not in valid_sources:
            errors.append(f"{rid}: source C6 inconnue : {source}")

    if not row.get("annotator"):
        warnings.append(f"{rid}: annotateur non renseigné")

    if not row.get("reviewed_by"):
        warnings.append(f"{rid}: relecteur non renseigné")

print("=== CONTRÔLE SCRUM-35 ===")
print("Fiches :", len(rows))
print("Normales :", sum(r.get("label") == 0 for r in rows))
print("Anomalies :", sum(r.get("label") == 1 for r in rows))
print("Abstentions :", sum(r["expected"].get("abstention") is True for r in rows))
print("Sources C6 disponibles :", len(valid_sources))
print("Erreurs :", len(errors))
print("Avertissements :", len(warnings))

for err in errors[:30]:
    print("ERREUR :", err)

for warning in warnings[:5]:
    print("AVERTISSEMENT :", warning)

if len(rows) != 80:
    print("ATTENTION : nombre de fiches différent de 80")

print("Contrôle terminé — aucune validation humaine implicite.")
