
import csv
import json
from pathlib import Path

base = Path("eval/volet_b")
output_dir = base / "double_annotation"
output_dir.mkdir(exist_ok=True)

with (base / "double_annotation.csv").open(
    encoding="utf-8", newline=""
) as f:
    selection = list(csv.DictReader(f))

with (base / "annotations_travail.jsonl").open(
    encoding="utf-8"
) as f:
    annotations = {
        row["id"]: row
        for line in f
        if (row := json.loads(line.strip()))
    }

for numero in (1, 2):
    output = output_dir / f"annotateur_{numero}.jsonl"

    with output.open("w", encoding="utf-8") as f:
        for selected in selection:
            original = annotations[selected["id"]]

            fiche = {
                "id": original["id"],
                "block_id": original["block_id"],
                "split": original["split"],
                "trace_lines": original["trace_lines"],
                "events": original["events"],
                "expected": {
                    "resume_evenements": "",
                    "faits_observes": [],
                    "hypotheses": [],
                    "infos_manquantes": [],
                    "sources": [],
                    "abstention": False
                },
                "annotator": ""
            }

            f.write(
                json.dumps(fiche, ensure_ascii=False) + "\n"
            )

    print("Fichier créé :", output)

print("Traces par annotateur :", len(selection))
print("Explications préremplies : 0")
print("Labels officiels exposés : 0")
print("Annotations originales modifiées : 0")
