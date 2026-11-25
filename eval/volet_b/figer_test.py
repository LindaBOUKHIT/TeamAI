"""Fige le jeu de test réservé du volet B (SCRUM-35) : test.jsonl et test.sha256.

Le fichier est construit à partir de annotations_travail.jsonl, une fois chaque cas vérifié
et relu dans validation_humaine.csv. Rien n'est écrit si un cas reste sans vérification ou
sans relecture, si un nom manque ou si validate_example (C5) signale une erreur.

    python -m eval.volet_b.figer_test              # contrôle puis écrit test.jsonl et test.sha256
    python -m eval.volet_b.figer_test --controler  # contrôle seulement, n'écrit rien

Le jeu de test ne sert jamais à l'entraînement ni au réglage.
"""
import argparse
import csv
import hashlib
import json

from teamai.contracts import validate_example
from teamai.paths import EVAL_VOLET_B, VOLET_B_TEST, VOLET_B_TEST_SHA256

SOURCE = EVAL_VOLET_B / "annotations_travail.jsonl"
VALIDATION = EVAL_VOLET_B / "validation_humaine.csv"


def problems(rows, validation):
    """Liste des obstacles au gel : contrat C5, effectifs et état de la validation humaine."""
    found = []
    ids = [r.get("id") for r in rows]
    if len(rows) != 80 or ids != sorted(ids) or len(set(ids)) != 80:
        found.append("80 identifiants distincts, dans l'ordre, attendus")
    if [r.get("label") for r in rows].count(0) != 40:
        found.append("40 cas normaux et 40 anomalies attendus")
    if len({r.get("block_id") for r in rows}) != len(rows):
        found.append("bloc présent deux fois")
    for r in rows:
        rid = r.get("id")
        found += [f"{rid} : {e}" for e in validate_example(r)]
        if r.get("split") != "test":
            found.append(f"{rid} : split différent de test")
        v = validation.get(rid)
        if v is None:
            found.append(f"{rid} : absent de validation_humaine.csv")
            continue
        if v["block_id"] != r.get("block_id"):
            found.append(f"{rid} : bloc différent dans validation_humaine.csv")
        if v["annotator"] != r.get("annotator") or v["reviewed_by"] != r.get("reviewed_by"):
            found.append(f"{rid} : noms différents dans validation_humaine.csv")
        if v["annotation_verifiee"] != "oui" or v["relecture_validee"] != "oui":
            found.append(f"{rid} : vérification ou relecture non validée")
    return found


def main(argv=None):
    """Contrôle les annotations et, sauf --controler, écrit le jeu figé et son empreinte."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--controler", action="store_true", help="contrôle sans écrire")
    args = parser.parse_args(argv)
    rows = [json.loads(line) for line in SOURCE.read_text(encoding="utf-8").splitlines() if line.strip()]
    with VALIDATION.open(encoding="utf-8", newline="") as f:
        validation = {row["id"]: row for row in csv.DictReader(f)}
    found = problems(rows, validation)
    for p in found:
        print("BLOQUANT :", p)
    if found:
        print(f"{len(found)} obstacle(s) : test.jsonl n'est pas écrit.")
        return 1
    content = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows).encode("utf-8")
    digest = hashlib.sha256(content).hexdigest()
    if args.controler:
        print(f"Contrôle réussi : 80 cas prêts, SHA-256 attendu {digest}.")
        return 0
    VOLET_B_TEST.write_bytes(content)
    VOLET_B_TEST_SHA256.write_text(f"{digest}  {VOLET_B_TEST.name}\n", encoding="utf-8", newline="\n")
    print(f"{VOLET_B_TEST.name} écrit : 80 cas, SHA-256 {digest}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
