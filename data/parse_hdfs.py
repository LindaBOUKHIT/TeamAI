
"""SCRUM-19 — Parser de référence HDFS_v1.

Transforme les lignes brutes HDFS en séquences ordonnées d'EventId
par BlockId, à partir des templates officiels Loghub.
"""

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

from teamai.paths import PARSED, PREPROCESSED


BLOCK_PATTERN = re.compile(r"blk_-?\d+")

HEADER_PATTERN = re.compile(
    r"^\d{6}\s+\d{6}\s+\d+\s+\w+\s+[^:]+:\s*(.*)$"
)


def compile_templates(template_path: Path):
    """Convertit les templates Loghub en expressions régulières."""
    templates = []

    with template_path.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            event_id = row["EventId"].strip()
            template = row["EventTemplate"].strip()

            # [*] représente une portion variable.
            expression = re.escape(template).replace(
                re.escape("[*]"), ".*?"
            )

            pattern = re.compile(rf"^{expression}$")
            templates.append((event_id, pattern))

    if len(templates) != 29:
        raise ValueError(
            f"29 templates attendus, {len(templates)} trouvés."
        )

    return templates


def extract_message(line: str):
    """Supprime l'en-tête pour récupérer le message HDFS."""
    match = HEADER_PATTERN.match(line.rstrip("\r\n"))
    return match.group(1) if match else None


def match_event(message: str, templates):
    """Retourne l'EventId si un template correspond."""
    matches = [
        event_id
        for event_id, pattern in templates
        if pattern.fullmatch(message)
    ]

    if len(matches) == 1:
        return matches[0], "matched"

    if len(matches) > 1:
        return None, "ambiguous"

    return None, "unmatched"


def parse_hdfs(
    log_path: Path,
    template_path: Path,
    limit: int | None = None,
):
    """Reconstruit les séquences d'événements par BlockId."""
    templates = compile_templates(template_path)

    sequences = defaultdict(list)

    stats = {
        "lines": 0,
        "matched": 0,
        "unmatched": 0,
        "ambiguous": 0,
        "without_block": 0,
        "invalid_header": 0,
    }

    examples = {
        "unmatched": [],
        "ambiguous": [],
        "invalid_header": [],
    }

    with log_path.open(
        "r", encoding="utf-8", errors="replace"
    ) as file:

        for line_number, line in enumerate(file, start=1):

            if limit is not None and line_number > limit:
                break

            stats["lines"] += 1

            message = extract_message(line)

            if message is None:
                stats["invalid_header"] += 1

                if len(examples["invalid_header"]) < 3:
                    examples["invalid_header"].append(
                        (line_number, line.strip()[:180])
                    )
                continue

            block_ids = list(
                dict.fromkeys(BLOCK_PATTERN.findall(message))
            )

            if not block_ids:
                stats["without_block"] += 1
                continue

            event_id, status = match_event(message, templates)

            if status != "matched":
                stats[status] += 1

                if len(examples[status]) < 3:
                    examples[status].append(
                        (line_number, message[:180])
                    )
                continue

            stats["matched"] += 1

            # Une ligne peut concerner plusieurs blocs.
            for block_id in block_ids:
                sequences[block_id].append(event_id)

    return sequences, stats, examples


def save_sequences(sequences, output_path: Path):
    """Enregistre les séquences reconstruites en CSV."""
    output_path.parent.mkdir(
        parents=True, exist_ok=True
    )

    with output_path.open(
        "w", encoding="utf-8", newline=""
    ) as file:
        writer = csv.writer(file)

        writer.writerow(["BlockId", "Features"])

        for block_id, events in sequences.items():
            writer.writerow([
                block_id,
                "[" + ",".join(events) + "]",
            ])


def main():
    """Ligne de commande : parse HDFS.log avec les 29 templates, écrit le CSV des séquences et affiche les statistiques."""
    parser = argparse.ArgumentParser(
        description="SCRUM-19 : parser HDFS_v1"
    )

    parser.add_argument(
        "--log",
        type=Path,
        default=PREPROCESSED.parent / "HDFS.log",
        help="Chemin du fichier HDFS.log",
    )

    parser.add_argument(
        "--templates",
        type=Path,
        default=PREPROCESSED / "HDFS.log_templates.csv",
        help="Chemin du fichier des 29 templates",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=PARSED / "Event_traces_parsed.csv",
        help="Chemin du CSV généré",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Nombre maximal de lignes à analyser",
    )

    args = parser.parse_args()

    if args.limit is not None and args.limit <= 0:
        parser.error("--limit doit être supérieur à 0")

    sequences, stats, examples = parse_hdfs(
        log_path=args.log,
        template_path=args.templates,
        limit=args.limit,
    )

    save_sequences(sequences, args.output)

    print("\n=== SCRUM-19 : PARSING HDFS ===")

    print(f"Lignes analysées      : {stats['lines']:,}")
    print(f"Lignes reconnues      : {stats['matched']:,}")
    print(f"Lignes non reconnues  : {stats['unmatched']:,}")
    print(f"Lignes ambiguës       : {stats['ambiguous']:,}")
    print(f"En-têtes invalides    : {stats['invalid_header']:,}")
    print(f"Lignes sans BlockId   : {stats['without_block']:,}")
    print(f"Blocs reconstruits    : {len(sequences):,}")

    eligible = (
        stats["matched"]
        + stats["unmatched"]
        + stats["ambiguous"]
    )

    if eligible:
        recognition_rate = stats["matched"] / eligible
        print(f"Taux de reconnaissance: {recognition_rate:.2%}")

    for category, items in examples.items():
        if items:
            print(f"\nExemples {category} :")

            for line_number, message in items:
                print(f"  Ligne {line_number}: {message}")

    print(f"\nCSV généré : {args.output}")


if __name__ == "__main__":
    main()
