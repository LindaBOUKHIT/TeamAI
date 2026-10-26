
import json
import csv
from pathlib import Path

annotations_path = Path("eval/volet_b/annotations_travail.jsonl")
corpus_path = Path("volet_b/rag/corpus/chunks.jsonl")
output_path = Path("eval/volet_b/suggestions_sources.csv")

rows = [
    json.loads(line)
    for line in annotations_path.open(encoding="utf-8")
]

chunks = [
    json.loads(line)
    for line in corpus_path.open(encoding="utf-8")
]

valid_ids = {chunk["id"] for chunk in chunks}

prefix = "hdfs-architecture-1.2.1#"

rules = {
    "E22": prefix + "namenode-and-datanodes#1",
    "E5": prefix + "replication-pipelining#1",
    "E9": prefix + "replication-pipelining#1",
    "E26": prefix + "namenode-and-datanodes#1",
    "E25": prefix + "data-replication#1",
    "E18": prefix + "data-replication#1",
    "E6": prefix + "data-replication#1",
    "E16": prefix + "data-replication#1",
    "E23": prefix + "file-deletes-and-undeletes#1",
    "E21": prefix + "file-deletes-and-undeletes#1"
}

suggestions = []

for row in rows:
    ids = sorted({
        rules[event]
        for event in row["events"]
        if event in rules and rules[event] in valid_ids
    })

    suggestions.append({
        "id": row["id"],
        "block_id": row["block_id"],
        "sources_candidates": ";".join(ids),
        "verification": "a_verifier"
    })

with output_path.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "id",
            "block_id",
            "sources_candidates",
            "verification"
        ]
    )
    writer.writeheader()
    writer.writerows(suggestions)

print("Fiches analysées :", len(rows))
print("Suggestions créées :", output_path)
print("Sources C6 valides :", len(valid_ids))
print("Annotations C5 modifiées : 0")
