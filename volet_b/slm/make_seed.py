"""SCRUM-29 : régénération déterministe de vingt brouillons v16, train uniquement."""
import argparse
import csv
import json
import re
from pathlib import Path

from data.parse_hdfs import compile_templates
from teamai.paths import ANNOTATIONS, SAMPLE
from volet_b.slm.lora_data import read_splits, prepare_examples
from volet_b.slm.v16.facts import GLOSSARY, prepare_block
from volet_b.slm.v16.policy import allowed_hypotheses, ATTENTION_CODES
from volet_b.slm.v16.runtime import build_prompt

OUTPUT = ANNOTATIONS / "seed_alain.jsonl"
EXCLUDED = {"blk_8362325295506522506", "blk_7815531973893896934",
            "blk_4971154345890344", "blk_-8431991883875585441"}


def build_expected(block):
    """Copie les faits v16, cite les preuves et n'utilise que les causes autorisées."""
    by_code = {}
    for fact in block["facts"]:
        match = re.match(r"\[F\d+\] (E\d+) :", fact)
        if match:
            by_code[match[1]] = fact
    priority = sorted(by_code, key=lambda c: (c not in {"E24", "E27", "E28"},
                                             c not in ATTENTION_CODES, int(c[1:])))
    selected = [by_code[c] for c in priority[:5]]
    if len(selected) < 2:
        selected.append(block["facts"][0])
    # Deux phrases sans ordre temporel ni conclusion globale ; les définitions
    # du glossaire sont celles fournies par le prompt, sans paraphrase causale.
    ordinary = next((c for c in priority if c not in ATTENTION_CODES), priority[0])
    notable = [c for c in priority if c in ATTENTION_CODES]
    first_ref = by_code[ordinary].split("]", 1)[0] + "]"
    summary = "La trace journalise : " + GLOSSARY[ordinary].rstrip(".") + " " + first_ref + "."
    if notable:
        parts = [GLOSSARY[c].rstrip(".") + " " + by_code[c].split("]", 1)[0] + "]" for c in notable]
        summary += " Événements atypiques observés : " + " ; ".join(parts) + "."
        unknown = [row["code"] for row in block["cause_catalog"] if row["unknown_cause"]]
        if unknown:
            refs = ", ".join(by_code[c].split("]", 1)[0][1:] for c in unknown)
            summary += " Cause indéterminée pour ces événements [" + refs + "]."
    else:
        summary += " L'intervalle et le nombre de lignes sont ceux calculés pour ce bloc [F01]."
    if len(summary) > 750:
        raise ValueError("Résumé trop long : choisir un bloc plus court, sans tronquer les preuves")
    return {"resume_evenements": summary, "faits_observes": selected,
            "hypotheses": allowed_hypotheses(block)[:2], "infos_manquantes": [],
            "sources": [], "abstention": False}


def pick_blocks(traces):
    """Privilégie E24/E27/E28 puis complète à vingt avec des motifs variés et courts."""
    picked = []
    for code in ("E24", "E27", "E28", "E7", "E20"):
        candidates = [r for r in traces if code in r["events"]]
        candidates.sort(key=lambda r: (len(r["events"]), r["BlockId"]))
        for row in candidates[:2]:
            if row not in picked:
                picked.append(row)
    for row in sorted(traces, key=lambda r: (r["Label"] != "Success", abs(len(r["events"])-16), r["BlockId"])):
        if row not in picked:
            picked.append(row)
        if len(picked) == 20:
            break
    if len(picked) != 20:
        raise ValueError("Vingt blocs train requis")
    return picked


def main(argv=None):
    """Sélectionne les blocs train, reconstruit v16, valide et écrit les brouillons sans relecteur."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--splits", type=Path, help="CSV C4 officiel ou sous-ensemble sample versionné")
    args = parser.parse_args(argv)
    splits = read_splits(args.splits)
    with (SAMPLE / "Event_traces.csv").open(encoding="utf-8", newline="") as stream:
        traces = list(csv.DictReader(stream))
    for row in traces:
        row["events"] = row["Features"].strip("[]").split(",")
    train = [r for r in traces if splits.get(r["BlockId"]) == "train" and r["BlockId"] not in EXCLUDED]
    chosen = pick_blocks(train)
    lines = {r["BlockId"]: [] for r in chosen}
    with (SAMPLE / "HDFS_sample.log").open(encoding="utf-8") as stream:
        for number, raw in enumerate(stream, 1):
            for bid in set(re.findall(r"blk_-?\d+", raw)) & lines.keys():
                lines[bid].append((number, raw.rstrip("\r\n")))
    templates = compile_templates(SAMPLE / "HDFS.log_templates.csv")
    rows = []
    for index, rec in enumerate(chosen, 1):
        block = prepare_block(rec["BlockId"], lines[rec["BlockId"]], templates, split="train")
        rows.append({"id": f"seed-{index:04d}", "block_id": rec["BlockId"], "split": "train",
                     "trace_lines": [raw for _, raw in lines[rec["BlockId"]]], "events": rec["events"],
                     "label": int(rec["Label"] == "Fail"), "prompt": build_prompt(block),
                     "expected": build_expected(block), "annotator": "alain", "reviewed_by": ""})
    prepare_examples(rows, args.splits)
    OUTPUT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    coverage = {code: sum(code in r["events"] for r in rows) for code in ("E24", "E27", "E28")}
    available = {code: sum(code in r["events"] for r in train) for code in coverage}
    print(json.dumps({"examples": len(rows), "coverage": coverage, "available_train": available,
                      "reviewed_by": "", "output": str(OUTPUT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
