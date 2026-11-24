"""Reconstruit les entrées de la porte Laya depuis les sorties v16 de validation (SCRUM-63).

Entrées : le fichier JSON des blocs v16 et le dossier des sorties Kaggle
(resultats_worker_*.jsonl). Sortie : une réponse C5 par bloc, au format de
laya_measure.read_responses. Seul le split val est accepté.
"""
import argparse
import json
import sys

from teamai.contracts import validate_answer
from volet_b.agents.laya_measure import checked_path


def build_rows(blocks, results):
    """Associe chaque bloc val à sa réponse finale ; renvoie les lignes et le nombre écarté."""
    by_id = {r["block_id"]: r for r in results}
    rows, rejected = [], 0
    for block in sorted(blocks, key=lambda b: b["selection_index"]):
        if block.get("split") != "val":
            raise ValueError(f"Bloc hors validation refusé : {block.get('block_id')}.")
        result = by_id.get(block["block_id"])
        if result is None or result.get("split") != "val":
            raise ValueError(f"Sortie val absente pour {block['block_id']}.")
        try:
            answer = json.loads(result["text"])
        except (TypeError, ValueError):
            rejected += 1
            continue
        if validate_answer(answer):
            rejected += 1
            continue
        rows.append({"block_id": block["block_id"], "split": "val", "label": block["label"],
                     "selection_index": block["selection_index"],
                     "events": [e["event"] for e in block["raw_events"]], "answer": answer})
    return rows, rejected


def main(argv=None):
    """Lit les blocs et les sorties, puis écrit le fichier JSONL des réponses."""
    parser = argparse.ArgumentParser(description="Entrées Laya depuis les sorties v16 de validation.")
    parser.add_argument("--blocks", required=True)
    parser.add_argument("--outputs", required=True, help="Dossier contenant resultats_worker_*.jsonl.")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        blocks = json.loads(checked_path(args.blocks).read_text(encoding="utf-8"))
        results = [json.loads(line) for path in sorted(checked_path(args.outputs).glob("resultats_worker_*.jsonl"))
                   for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        rows, rejected = build_rows(blocks, results)
        target = checked_path(args.out)
        target.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    except (OSError, ValueError, KeyError) as exc:
        parser.error(str(exc))
    print(f"{len(rows)} réponses écrites, {rejected} écartées (non conformes à C5).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
