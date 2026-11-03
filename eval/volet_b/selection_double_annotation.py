
import json
import random
import csv
from pathlib import Path

base = Path("eval/volet_b")

rows = [
    json.loads(line)
    for line in (base / "annotations_travail.jsonl")
    .read_text(encoding="utf-8").splitlines()
    if line.strip()
]

rng = random.Random(35)

normales = [r for r in rows if r["label"] == 0]
anomalies = [r for r in rows if r["label"] == 1]

selection = (
    rng.sample(normales, 15)
    + rng.sample(anomalies, 15)
)

selection.sort(key=lambda r: r["id"])

output = base / "double_annotation.csv"

with output.open("w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "id",
        "block_id",
        "label",
        "annotateur_1",
        "annotateur_2",
        "annotation_1_terminee",
        "annotation_2_terminee",
        "accord",
        "arbitrage"
    ])

    for row in selection:
        writer.writerow([
            row["id"],
            row["block_id"],
            row["label"],
            "", "", "", "", "", ""
        ])

print("Traces sélectionnées :", len(selection))
print("Normales :", sum(r["label"] == 0 for r in selection))
print("Anomalies :", sum(r["label"] == 1 for r in selection))
print("Fichier créé :", output)
print("Annotations existantes modifiées : 0")
