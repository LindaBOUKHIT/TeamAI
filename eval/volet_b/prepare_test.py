
"""SCRUM-35 : préparer 80 traces du test officiel pour annotation humaine.

Ne crée PAS le fichier final test.jsonl.
"""
import csv
import json
import random
import re
from pathlib import Path

from teamai.data.loader import load_traces
from teamai.data.preprocess import BLOCK_REGEX, HEADER_REGEX

ROOT = Path(__file__).resolve().parents[2]
SPLITS = ROOT / "data/splits/splits.csv"
LOGS = ROOT / "data/raw/HDFS_v1/HDFS.log"
OUTPUT = ROOT / "eval/volet_b/candidats_annotation.jsonl"

SEED = 35
N_NORMAL = 40
N_ANOMALY = 40

EXCLUDED = {
    "blk_8362325295506522506",
    "blk_-1000014584150379967",
    "blk_-100004553717737248",
    "blk_-1001299764911418845",
}


def main():
    # 1. Charger les identifiants du test officiel
    test_ids = set()
    with SPLITS.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row["split"] == "test" and row["BlockId"] not in EXCLUDED:
                test_ids.add(row["BlockId"])

    # 2. Charger les événements et les labels officiels
    traces = load_traces()
    traces = traces[traces["BlockId"].isin(test_ids)]

    normal = traces[traces["label"] == 0]
    anomaly = traces[traces["label"] == 1]

    rng = random.Random(SEED)
    normal_ids = rng.sample(sorted(normal["BlockId"].tolist()), N_NORMAL)
    anomaly_ids = rng.sample(sorted(anomaly["BlockId"].tolist()), N_ANOMALY)
    selected = set(normal_ids + anomaly_ids)

    # 3. Extraire les lignes brutes en une seule lecture
    lines_by_block = {block_id: [] for block_id in selected}
    header = re.compile(HEADER_REGEX)
    block_pattern = re.compile(BLOCK_REGEX)

    with LOGS.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            match = header.match(line)
            if not match:
                continue
            block_ids = set(block_pattern.findall(match.group(1)))
            for block_id in block_ids & selected:
                lines_by_block[block_id].append(line.rstrip("\r\n"))

    # 4. Préparer les candidats, sans inventer d'annotations
    indexed = traces.set_index("BlockId")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", encoding="utf-8") as f:
        for i, block_id in enumerate(normal_ids + anomaly_ids, 1):
            row = indexed.loc[block_id]
            example = {
                "id": f"candidate-{i:04d}",
                "block_id": block_id,
                "split": "test",
                "trace_lines": lines_by_block[block_id],
                "events": row["events"],
                "label": int(row["label"]),
                "annotation_status": "pending",
            }
            f.write(json.dumps(example, ensure_ascii=False) + "\n")

    missing = [bid for bid, lines in lines_by_block.items() if not lines]
    print(f"Candidats préparés : {len(selected)}")
    print(f"Normaux : {len(normal_ids)}")
    print(f"Anomalies : {len(anomaly_ids)}")
    print(f"Blocs sans lignes brutes : {len(missing)}")
    print(f"Fichier : {OUTPUT}")
    if missing:
        raise RuntimeError("Des blocs sélectionnés n'ont aucune ligne brute.")


if __name__ == "__main__":
    main()
