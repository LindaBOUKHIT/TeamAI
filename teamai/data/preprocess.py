"""SCRUM-26 — Vocabulaire C2 et prétraitement des logs bruts, partagés entre Python et JavaScript.

    python -m teamai.data.preprocess                  # écrit volet_a/web/public/vocab.json (C2)

    from teamai.data.preprocess import load_vocab_json, parse_lines
    vocab = load_vocab_json()
    result = parse_lines(open("HDFS.log", encoding="utf-8"), vocab)
    result["sequences"]["blk_…"]                      # ["E5", "E22", …] dans l'ordre du fichier

Les regex de `vocab.json` sont la seule source de vérité du parsing : `volet_a/web/src/preprocess.js`
applique exactement les mêmes, avec la même priorité (premier EventId qui correspond, dans l'ordre
numérique). `HEADER_REGEX` et `BLOCK_REGEX` sont recopiés à l'identique dans `preprocess.js` ;
les tests de parité (tests/test_preprocess.py, volet_a/web/tests/parity.test.js) vérifient l'accord.
"""
import argparse
import csv
import json
import re
from pathlib import Path

from teamai.data.loader import MAX_LEN, PAD_ID, UNK_ID
from teamai.paths import PREPROCESSED, WEB_PUBLIC

CONTRACT_VERSION = "v1"
UNKNOWN_EVENT = "UNK"
VOCAB_JSON = WEB_PUBLIC / "vocab.json"

# En-tête HDFS : date (6 chiffres), heure (6), PID, niveau, composant, puis « : » et le message.
HEADER_REGEX = r"^\d{6}\s+\d{6}\s+\d+\s+\w+\s+[^:]+:\s*(.*)$"
BLOCK_REGEX = r"blk_-?\d+"

# Caractères spéciaux à échapper pour que la regex soit lue de la même façon par Python et JavaScript.
_SPECIAL = set("\\^$.|?*+()[]{}/")


def template_to_regex(template: str) -> str:
    """Convertit un template Loghub (`[*]` = partie variable) en regex ancrée, compatible Python et JavaScript."""
    parts = ("".join("\\" + c if c in _SPECIAL else c for c in part) for part in template.split("[*]"))
    return "^" + ".*?".join(parts) + "$"


def build_vocab(templates_csv: Path) -> dict:
    """Construit le vocabulaire C2 (ids, templates, regex) à partir de HDFS.log_templates.csv."""
    with open(templates_csv, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 29:
        raise ValueError(f"29 templates attendus, {len(rows)} trouvés dans {templates_csv}")
    rows.sort(key=lambda r: int(r["EventId"].strip()[1:]))
    events = {}
    for row in rows:
        event_id, template = row["EventId"].strip(), row["EventTemplate"].strip()
        events[event_id] = {"id": int(event_id[1:]), "template": template, "regex": template_to_regex(template)}
    return {"contract_version": CONTRACT_VERSION, "pad_id": PAD_ID, "unk_id": UNK_ID, "max_len": MAX_LEN,
            "events": events}


def load_vocab_json(path: Path = VOCAB_JSON) -> dict:
    """Lit le vocabulaire C2 publié avec le site."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def compile_vocab(vocab: dict) -> list[tuple[str, re.Pattern]]:
    """Regex compilées, triées par id : la première qui correspond donne l'EventId (priorité C2)."""
    items = sorted(vocab["events"].items(), key=lambda item: item[1]["id"])
    return [(event_id, re.compile(spec["regex"])) for event_id, spec in items]


def parse_lines(lines, vocab: dict) -> dict:
    """Lignes brutes HDFS → séquences d'EventId par bloc, dans l'ordre d'apparition.

    Une ligne d'en-tête invalide ou sans identifiant de bloc est comptée puis ignorée ; une ligne
    valide qu'aucun template ne reconnaît donne `UNKNOWN_EVENT` (encodé `unk_id`). Une ligne qui
    cite plusieurs blocs ajoute l'événement à chacun d'eux.
    """
    header, block = re.compile(HEADER_REGEX), re.compile(BLOCK_REGEX)
    patterns = compile_vocab(vocab)
    sequences: dict[str, list[str]] = {}
    stats = {"lines": 0, "empty": 0, "invalid_header": 0, "without_block": 0, "matched": 0, "unknown": 0}
    for line in lines:
        line = line.rstrip("\r\n")
        if not line.strip():
            stats["empty"] += 1
            continue
        stats["lines"] += 1
        match = header.match(line)
        if not match:
            stats["invalid_header"] += 1
            continue
        message = match.group(1)
        block_ids = list(dict.fromkeys(block.findall(message)))
        if not block_ids:
            stats["without_block"] += 1
            continue
        event = next((event_id for event_id, pattern in patterns if pattern.search(message)), UNKNOWN_EVENT)
        stats["unknown" if event == UNKNOWN_EVENT else "matched"] += 1
        for block_id in block_ids:
            sequences.setdefault(block_id, []).append(event)
    return {"sequences": sequences, "stats": stats}


def main(argv=None):
    """Ligne de commande : écrit vocab.json (C2) à partir des 29 templates Loghub."""
    parser = argparse.ArgumentParser(description="SCRUM-26 : exporte le vocabulaire C2 pour le site.")
    parser.add_argument("--templates", type=Path, default=PREPROCESSED / "HDFS.log_templates.csv")
    parser.add_argument("--output", type=Path, default=VOCAB_JSON)
    args = parser.parse_args(argv)
    vocab = build_vocab(args.templates)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(vocab, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(vocab['events'])} événements écrits dans {args.output}")


if __name__ == "__main__":
    main()
