"""SCRUM-36 : tirage stratifié des blocs train/val et lots à annoter au format v16.

Chaque lot contient les prompts v16 reconstruits par le code ; `expected` est
laissé vide pour le brouillon puis la correction humaine. Aucun bloc du split
test, aucun bloc des 20 brouillons SCRUM-29 ni des blocs de mise au point v16.
"""
import argparse
import csv
import json
import random
import re

from data.parse_hdfs import compile_templates
from teamai.paths import ANNOTATIONS, ROOT, SAMPLE
from volet_b.slm.lora_data import read_splits
from volet_b.slm.v16.facts import prepare_block
from volet_b.slm.v16.policy import ATTENTION_CODES
from volet_b.slm.v16.runtime import build_prompt

DRAFTS = ANNOTATIONS / "brouillons"
ANNOTATORS = ("linda", "alain", "nassim", "bachar")
# Fichiers où figurent les blocs déjà vus pendant la mise au point du prompt v16.
TUNING_FILES = ("eval/results/SCRUM-63/revue_qualitative_validation.json",
                "eval/results/SCRUM-63/comparaison_v16_validation.json",
                "tests/fixtures/v16/blocks.json")
# Strates (nom, filtre, quota train, quota val) : les codes rares sont pris en entier.
STRATA = (
    ("E27", lambda r: "E27" in r["events"], 99, 99),
    ("E28", lambda r: "E28" in r["events"], 99, 99),
    ("rares", lambda r: r["att"] & {"E1", "E8", "E10", "E12", "E13", "E14", "E17", "E29"}, 99, 99),
    ("E20+E4", lambda r: r["att"] == {"E20", "E4"}, 10, 3),
    ("E7", lambda r: r["att"] == {"E7"}, 25, 5),
    ("E20", lambda r: r["att"] == {"E20"}, 25, 5),
    ("E4 anomalie", lambda r: r["att"] == {"E4"} and r["label"] == 1, 12, 3),
    ("anomalie sans indice", lambda r: not r["att"] and r["label"] == 1, 25, 6),
    ("E4 normal", lambda r: r["att"] == {"E4"} and r["label"] == 0, 15, 4),
    ("normal", lambda r: not r["att"] and r["label"] == 0, 30, 6),
)


def excluded_blocks():
    """Blocs interdits : brouillons SCRUM-29 et blocs vus pendant la mise au point v16."""
    text = "".join((ROOT / path).read_text(encoding="utf-8") for path in TUNING_FILES)
    seeds = (ANNOTATIONS / "seed_alain.jsonl").read_text(encoding="utf-8")
    return set(re.findall(r"blk_-?\d+", text + seeds))


def select(rows, seed):
    """Tire chaque strate dans l'ordre, sans doublon, avec un générateur seedé."""
    rng = random.Random(seed)
    picked, taken = [], set()
    for name, keep, quota_train, quota_val in STRATA:
        for split, quota in (("train", quota_train), ("val", quota_val)):
            pool = sorted((r for r in rows if r["split"] == split and r["id"] not in taken and keep(r)),
                          key=lambda r: r["id"])
            rng.shuffle(pool)
            for row in pool[:quota]:
                row["strate"] = name
                picked.append(row)
                taken.add(row["id"])
    return picked


def main(argv=None):
    """Écrit lot_<prénom>.jsonl : prompts v16, expected vide, sans annotateur ni relecteur."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=36)
    args = parser.parse_args(argv)
    splits = read_splits()
    banned = excluded_blocks()
    with (SAMPLE / "Event_traces.csv").open(encoding="utf-8", newline="") as stream:
        traces = list(csv.DictReader(stream))
    rows = []
    for t in traces:
        split = splits.get(t["BlockId"])
        if split not in ("train", "val") or t["BlockId"] in banned:
            continue
        events = t["Features"].strip("[]").split(",")
        rows.append({"id": t["BlockId"], "split": split, "events": events,
                     "label": int(t["Label"] == "Fail"), "att": set(events) & ATTENTION_CODES})
    picked = select(rows, args.seed)
    lines = {r["id"]: [] for r in picked}
    with (SAMPLE / "HDFS_sample.log").open(encoding="utf-8") as stream:
        for number, raw in enumerate(stream, 1):
            for bid in set(re.findall(r"blk_-?\d+", raw)) & lines.keys():
                lines[bid].append((number, raw.rstrip("\r\n")))
    templates = compile_templates(SAMPLE / "HDFS.log_templates.csv")
    lots = {name: [] for name in ANNOTATORS}
    for index, rec in enumerate(sorted(picked, key=lambda r: (r["split"], r["strate"], r["id"]))):
        block = prepare_block(rec["id"], lines[rec["id"]], templates, split=rec["split"])
        if [e["event"] for e in block["raw_events"]] != rec["events"]:
            raise ValueError(f"{rec['id']} : codes différents du sample")
        lot = ANNOTATORS[index % len(ANNOTATORS)]
        lots[lot].append({"block_id": rec["id"], "split": rec["split"], "strate": rec["strate"],
                          "trace_lines": [raw for _, raw in lines[rec["id"]]], "events": rec["events"],
                          "label": rec["label"], "prompt": build_prompt(block), "expected": None,
                          "annotator": "", "reviewed_by": ""})
    DRAFTS.mkdir(parents=True, exist_ok=True)
    for lot, items in lots.items():
        for number, item in enumerate(items, 1):
            item["id"] = f"{lot}-{number:03d}"
        path = DRAFTS / f"lot_{lot}.jsonl"
        path.write_text("".join(json.dumps({"id": i.pop("id"), **i}, ensure_ascii=False) + "\n" for i in items),
                        encoding="utf-8")
    summary = {lot: {"n": len(items), "val": sum(i["split"] == "val" for i in items)} for lot, items in lots.items()}
    strata = {}
    for rec in picked:
        strata.setdefault(rec["strate"], {"train": 0, "val": 0})[rec["split"]] += 1
    print(json.dumps({"total": len(picked), "excluded": len(banned), "lots": summary, "strates": strata},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
