"""SCRUM-36 : fusion des lots corrigés en train.jsonl et val.jsonl (contrat C5).

Chaque exemple garde le split C4 de son lot. Les deux fichiers sont triés par id,
écrits en UTF-8 avec des fins de ligne LF, une ligne JSON par exemple. Les
contrôles v16 de `prepare_examples` s'appliquent à chaque split, et aucun bloc
du split test des manifestes officiel ou sample n'est admis.
"""
import argparse
import csv
import json

from teamai.paths import ANNOTATIONS, SAMPLE, SPLITS
from volet_b.slm.lora_data import prepare_examples
from volet_b.slm.make_lots import ANNOTATORS, DRAFTS

OUTPUTS = {"train": ANNOTATIONS / "train.jsonl", "val": ANNOTATIONS / "val.jsonl"}
MANIFESTS = (SPLITS / "splits.csv", SAMPLE / "splits.csv")


def load_lots(drafts=DRAFTS):
    """Lit les quatre lots dans l'ordre de `ANNOTATORS`."""
    examples = []
    for lot in ANNOTATORS:
        text = (drafts / f"lot_{lot}.jsonl").read_text(encoding="utf-8")
        examples += [json.loads(line) for line in text.splitlines() if line.strip()]
    return examples


def banned_blocks(manifests=MANIFESTS):
    """Blocs du split test dans chaque manifeste C4 présent."""
    banned = set()
    for path in manifests:
        if path.is_file():
            with path.open(encoding="utf-8-sig", newline="") as stream:
                banned |= {row["BlockId"] for row in csv.DictReader(stream) if row["split"] == "test"}
    return banned


def merge(examples, banned):
    """Répartit les exemples par split, triés par id, après les contrôles de provenance."""
    ids = [ex["id"] for ex in examples]
    blocks = [ex["block_id"] for ex in examples]
    if len(set(ids)) != len(ids) or len(set(blocks)) != len(blocks):
        raise ValueError("id ou block_id dupliqué entre les lots")
    result = {split: [] for split in OUTPUTS}
    for ex in examples:
        if ex["block_id"] in banned or ex.get("split") not in result:
            raise ValueError(f"{ex['id']} : bloc ou split interdit pour l'adaptation")
        if not ex.get("annotator"):
            raise ValueError(f"{ex['id']} : annotateur absent")
        result[ex["split"]].append(ex)
    return {split: sorted(rows, key=lambda ex: ex["id"]) for split, rows in result.items()}


def serialize(rows):
    """Une ligne JSON par exemple, UTF-8 sans échappement, fin de ligne LF."""
    return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode("utf-8")


def main(argv=None):
    """Écrit train.jsonl et val.jsonl, ou vérifie avec --check qu'ils sont à jour."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare sans écrire ; code 1 si différent")
    args = parser.parse_args(argv)
    examples = load_lots()
    splits = merge(examples, banned_blocks())
    stale = []
    for split, rows in splits.items():
        prepare_examples(rows, split=split)
        payload = serialize(rows)
        path = OUTPUTS[split]
        if args.check:
            if not path.is_file() or path.read_bytes() != payload:
                stale.append(path.name)
        else:
            path.write_bytes(payload)
    summary = {split: len(rows) for split, rows in splits.items()}
    if stale:
        summary["a_regenerer"] = stale
    print(json.dumps(summary, ensure_ascii=False))
    raise SystemExit(1 if stale else 0)


if __name__ == "__main__":
    main()
