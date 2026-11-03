
import json
import csv
from pathlib import Path

base = Path("eval/volet_b")

with (base / "annotations_travail.jsonl").open(encoding="utf-8") as f:
    rows = [json.loads(line) for line in f]

with (base / "suggestions_sources.csv").open(
    encoding="utf-8", newline=""
) as f:
    suggestions = {
        r["id"]: r
        for r in csv.DictReader(f)
    }

output = base / "relecture_annotations.md"

with output.open("w", encoding="utf-8") as f:
    f.write("# SCRUM-35 — Relecture des annotations C5\n\n")
    f.write(
        "> Document de travail : les réponses sont des brouillons "
        "non validés. Ne pas utiliser pour entraîner ou ajuster "
        "le modèle.\n\n"
    )

    for row in rows:
        expected = row["expected"]

        f.write(f"## {row['id']} — {row['block_id']}\n\n")
        f.write(f"**Label officiel :** {row['label']}\n\n")
        f.write(
            f"**Abstention proposée :** "
            f"{expected['abstention']}\n\n"
        )

        f.write("### Trace originale\n\n```text\n")
        for event, line in zip(row["events"], row["trace_lines"]):
            f.write(f"[{event}] {line}\n")
        f.write("```\n\n")

        f.write("### Résumé proposé\n\n")
        f.write(expected["resume_evenements"] + "\n\n")

        for field, title in [
            ("faits_observes", "Faits observés"),
            ("hypotheses", "Hypothèses"),
            ("infos_manquantes", "Informations manquantes")
        ]:
            f.write(f"### {title}\n\n")
            for item in expected[field]:
                f.write(f"- {item}\n")
            f.write("\n")

        source_ids = suggestions.get(
            row["id"], {}
        ).get("sources_candidates", "")

        f.write("### Sources C6 candidates\n\n")
        f.write((source_ids or "Aucune") + "\n\n")

        f.write("### Validation humaine\n\n")
        f.write("- [ ] Faits vérifiés dans les logs\n")
        f.write("- [ ] Résumé fidèle et chronologique\n")
        f.write("- [ ] Abstention justifiée\n")
        f.write("- [ ] Sources C6 vérifiées\n")
        f.write("- [ ] Relecture indépendante effectuée\n\n")
        f.write("---\n\n")

print("Dossier de relecture créé :", output)
print("Nombre de fiches :", len(rows))
