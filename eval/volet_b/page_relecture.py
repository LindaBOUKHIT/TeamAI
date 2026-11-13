"""Génère une page HTML locale pour vérifier les 80 annotations du jeu réservé (SCRUM-35).

La page affiche la trace et le corrigé proposé côte à côte, un pré-contrôle mécanique
(codes d'événement, effectifs, nombres retrouvés dans la trace) et exporte un CSV au
format de validation_humaine.csv. Le pré-contrôle est une aide : le verdict reste humain.

La page contient des données de test : elle est ignorée par git et ne doit pas être partagée.

    python -m eval.volet_b.page_relecture
puis ouvrir eval/volet_b/relecture_locale.html dans un navigateur.

Le bouton « Corriger ce corrigé » de la page produit corrections_<prénom>.jsonl.
Pour réintégrer ces corrections (contrôle C5, refus des conflits, journal) :

    python -m eval.volet_b.page_relecture --appliquer eval/volet_b/corrections_Alain.jsonl
"""
import csv
import json
import re
from pathlib import Path

from teamai.paths import EVAL_VOLET_B

SECTIONS = ["Trace originale", "Résumé proposé", "Faits observés", "Hypothèses",
            "Informations manquantes", "Sources C6 candidates", "Validation humaine"]


def parse(md_text):
    """Découpe relecture_annotations.md en cas : identifiants, métadonnées et sections."""
    cases = []
    blocks = re.split(r"^## (?=test-\d+)", md_text, flags=re.M)[1:]
    for block in blocks:
        head, _, body = block.partition("\n")
        m = re.match(r"(test-\d+)\s+—\s+(\S+)", head.strip())
        case = {"id": m.group(1), "block_id": m.group(2), "meta": {}, "sections": {}}
        pre, *rest = re.split(r"^### ", body, flags=re.M)
        for line in pre.splitlines():
            mm = re.match(r"\*\*(.+?)\s*:\*\*\s*(.*)", line.strip())
            if mm:
                case["meta"][mm.group(1)] = mm.group(2).strip()
        for sec in rest:
            title, _, content = sec.partition("\n")
            content = re.sub(r"\n---\s*$", "", content.strip()).strip()
            case["sections"][title.strip()] = content
        cases.append(case)
    return cases


NUM_WORDS = {"un": 1, "une": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5, "six": 6, "sept": 7,
             "huit": 8, "neuf": 9, "dix": 10, "onze": 11, "douze": 12, "treize": 13, "quatorze": 14,
             "quinze": 15, "seize": 16}


def precheck(rec):
    """Contrôles mécaniques d'un corrigé contre sa trace. Ne remplace pas la lecture humaine."""
    from collections import Counter
    events = Counter(rec["events"])
    trace = "\n".join(rec["trace_lines"])
    e = rec["expected"]
    alerts, ok = [], []

    def numbers_in_trace(text, where):
        """Signale les tailles et adresses citées qui n'apparaissent pas dans la trace."""
        for tok in re.findall(r"\d{1,3}(?:\.\d{1,3}){3}(?::\d+)?|\b\d{3,}\b", text):
            if tok not in trace:
                alerts.append(f"{where} : « {tok} » n'apparaît pas dans la trace.")

    for i, fact in enumerate(e["faits_observes"], 1):
        where = f"Fait {i}"
        codes = re.findall(r"\bE(\d{1,2})\b", fact.split(":")[0]) if ":" in fact else re.findall(r"\bE(\d{1,2})\b", fact)
        codes = [f"E{c}" for c in codes]
        missing = [c for c in codes if c not in events]
        if missing:
            alerts.append(f"{where} : code(s) {', '.join(missing)} absent(s) de la trace.")
        if not codes:
            alerts.append(f"{where} : aucun code d'événement cité, à vérifier à la main.")
        if len(codes) == 1 and codes[0] in events:
            body = fact.split(":", 1)[1] if ":" in fact else fact
            m = re.search(r"\b(" + "|".join(NUM_WORDS) + r"|\d{1,2})\b", body.lower())
            if m:
                n = NUM_WORDS.get(m.group(1)) or int(m.group(1))
                if n != events[codes[0]] and not (m.group(1) in ("un", "une") and events[codes[0]] >= 1 and "plusieurs" not in body):
                    alerts.append(f"{where} : annonce {n}, mais {codes[0]} apparaît {events[codes[0]]} fois dans la trace.")
                else:
                    ok.append(f"{where} : effectif {codes[0]} = {events[codes[0]]} cohérent.")
            elif "plusieurs" in body.lower() and events[codes[0]] < 2:
                alerts.append(f"{where} : « plusieurs » alors que {codes[0]} apparaît {events[codes[0]]} fois.")
        numbers_in_trace(fact, where)
    numbers_in_trace(e["resume_evenements"], "Résumé")
    if e["abstention"] and e["hypotheses"]:
        alerts.append("Abstention vraie mais hypothèses présentes (contraire à C5).")
    if e["abstention"] and not e["infos_manquantes"]:
        alerts.append("Abstention vraie sans information manquante (contraire à C5).")
    for i, h in enumerate(e["hypotheses"], 1):
        if not re.search(r"pourrai|compatible|possible|peut|suggèr|probabl|semble", h.lower()):
            alerts.append(f"Hypothèse {i} : pas formulée comme une hypothèse (conditionnel absent).")
    warn_lines = sum(1 for l in rec["trace_lines"] if re.search(r"\b(WARN|ERROR|FATAL)\b", l))
    if warn_lines and not any(w in (e["resume_evenements"] + " ".join(e["faits_observes"])).lower()
                              for w in ("avertissement", "warn", "exception", "erreur", "error")):
        alerts.append(f"La trace contient {warn_lines} ligne(s) WARN/ERROR non mentionnée(s) dans le résumé ni les faits.")
    return {"alerts": alerts, "ok": ok, "n_facts": len(e["faits_observes"])}


HERE = EVAL_VOLET_B
EXPECTED_KEYS = ["resume_evenements", "faits_observes", "hypotheses", "infos_manquantes", "sources", "abstention"]
CORRECTIONS_LOG_FIELDS = ["id", "block_id", "corrige_par", "date", "motif"]


def check_expected(expected, where):
    """Vérifie la forme d'un corrigé C5 et ses règles d'abstention ; lève ValueError sinon."""
    if list(expected) != EXPECTED_KEYS:
        raise ValueError(f"{where} : champs attendus {EXPECTED_KEYS}, reçus {list(expected)}")
    if not isinstance(expected["resume_evenements"], str) or not expected["resume_evenements"].strip():
        raise ValueError(f"{where} : résumé vide")
    for key in EXPECTED_KEYS[1:5]:
        if not isinstance(expected[key], list) or not all(isinstance(x, str) and x.strip() for x in expected[key]):
            raise ValueError(f"{where} : {key} doit être une liste de textes non vides")
    if not expected["faits_observes"]:
        raise ValueError(f"{where} : au moins un fait observé est requis")
    if not isinstance(expected["abstention"], bool):
        raise ValueError(f"{where} : abstention doit être un booléen")
    if expected["abstention"] and (expected["hypotheses"] or not expected["infos_manquantes"]):
        raise ValueError(f"{where} : abstention vraie impose hypotheses vide et au moins une info manquante (C5)")


def apply_corrections(paths, jsonl_path, log_path):
    """Réintègre les corrections exportées par la page dans le JSONL source et les journalise."""
    rows = [json.loads(l) for l in jsonl_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    by_id = {r["id"]: r for r in rows}
    seen, log = {}, []
    for path in paths:
        for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            corr = json.loads(line)
            where = f"{Path(path).name}:{n} ({corr.get('id')})"
            row = by_id.get(corr.get("id"))
            if row is None or row["block_id"] != corr.get("block_id"):
                raise ValueError(f"{where} : identifiant ou bloc inconnu")
            if corr["id"] in seen:
                raise ValueError(f"{where} : déjà corrigé dans {seen[corr['id']]}")
            if not str(corr.get("corrige_par", "")).strip():
                raise ValueError(f"{where} : auteur de la correction manquant")
            check_expected(corr["expected"], where)
            seen[corr["id"]] = where
            row["expected"] = corr["expected"]
            log.append({"id": corr["id"], "block_id": corr["block_id"], "corrige_par": corr["corrige_par"],
                        "date": corr.get("date", ""), "motif": corr.get("motif", "")})
    jsonl_path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8", newline="\n")
    new_log = not log_path.exists()
    with log_path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CORRECTIONS_LOG_FIELDS, lineterminator="\n")
        if new_log:
            writer.writeheader()
        writer.writerows(log)
    return len(log)


def main(argv=None):
    """Construit la page locale à partir du Markdown, du JSONL source et du CSV de validation."""
    import argparse
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--md", type=Path, default=HERE / "relecture_annotations.md")
    parser.add_argument("--csv", type=Path, default=HERE / "validation_humaine.csv")
    parser.add_argument("--sortie", type=Path, default=HERE / "relecture_locale.html")
    parser.add_argument("--appliquer", type=Path, nargs="+", metavar="corrections_<prénom>.jsonl",
                        help="réintègre des corrections exportées par la page dans annotations_travail.jsonl")
    args = parser.parse_args(argv)
    if args.appliquer:
        n = apply_corrections(args.appliquer, HERE / "annotations_travail.jsonl", HERE / "corrections_journal.csv")
        print(f"{n} correction(s) appliquée(s) ; journal : eval/volet_b/corrections_journal.csv."
              " Régénérer relecture_annotations.md avec preparer_relecture.py.")
        return
    md, csv_path, out = args.md, args.csv, args.sortie
    cases = parse(md.read_text(encoding="utf-8"))
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        rows = {r["id"]: r for r in csv.DictReader(f)}
    # Le .md a perdu des accents par endroits : le texte du corrigé et la trace viennent du JSONL source.
    jsonl = md.parent / "annotations_travail.jsonl"
    recs = {r["id"]: r for r in (json.loads(l) for l in jsonl.read_text(encoding="utf-8").splitlines() if l.strip())}
    def bullets(xs):
        """Met une liste au format Markdown."""
        return "\n".join(f"- {x}" for x in xs)

    mismatch = 0
    for c in cases:
        c["label"] = rows.get(c["id"], {}).get("label", c["meta"].get("Label officiel", ""))
        r = recs[c["id"]]
        assert r["block_id"] == c["block_id"]
        e = r["expected"]
        md_trace = [l for l in c["sections"]["Trace originale"].splitlines() if l.strip() and not l.startswith("```")]
        mismatch += len(md_trace) != len(r["trace_lines"])
        c["sections"]["Trace originale"] = "\n".join(f"[{ev}] {line}" for ev, line in zip(r["events"], r["trace_lines"]))
        c["sections"]["Résumé proposé"] = e["resume_evenements"]
        c["sections"]["Faits observés"] = bullets(e["faits_observes"])
        c["sections"]["Hypothèses"] = bullets(e["hypotheses"])
        c["sections"]["Informations manquantes"] = bullets(e["infos_manquantes"])
        c["meta"]["Abstention proposée"] = str(e["abstention"])
        src = c["sections"].get("Sources C6 candidates", "")
        if ";" in src and "\n" not in src.strip():
            c["sections"]["Sources C6 candidates"] = bullets(s.strip() for s in src.split(";") if s.strip())
        c["label"] = str(r["label"])
        c["checks"] = precheck(r)
        # Données brutes pour le mode « Corriger » (pré-contrôle recalculé dans la page).
        c["events"], c["trace_lines"], c["expected"] = r["events"], r["trace_lines"], r["expected"]
    print("traces de longueur différente md/jsonl:", mismatch)
    print("cas avec au moins une alerte de pré-contrôle:", sum(1 for c in cases if c["checks"]["alerts"]),
          "| alertes au total:", sum(len(c["checks"]["alerts"]) for c in cases))
    print("accents abîmés restants:", sum(len(re.findall(r"[a-zA-Z]\?[a-zA-Z]", json.dumps(c, ensure_ascii=False))) for c in cases))
    # Contrôles sans contenu
    missing = {s: sum(1 for c in cases if s not in c["sections"]) for s in SECTIONS}
    print("cas:", len(cases), "| ids csv:", len(rows), "| ids communs:", len(set(rows) & {c["id"] for c in cases}))
    print("sections manquantes:", {k: v for k, v in missing.items() if v})
    print("méta trouvées:", sorted({k for c in cases for k in c["meta"]}))
    template = (HERE / "page_relecture.html").read_text(encoding="utf-8")
    data = json.dumps(cases, ensure_ascii=False).replace("</", "<\\/")
    out.write_text(template.replace("/*__DATA__*/[]", data), encoding="utf-8")
    print("écrit :", out, f"({out.stat().st_size} octets) — ne pas partager, données de test")


if __name__ == "__main__":
    main()
