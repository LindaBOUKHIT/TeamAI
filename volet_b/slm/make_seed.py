"""SCRUM-29 — Pré-génère ~20 exemples C5 provisoires pour l'essai LoRA, à partir de l'échantillon versionné.

    python -m volet_b.slm.make_seed        # écrit volet_b/annotations/seed_alain.jsonl

Les blocs viennent du split **train** (C4) présents dans `data/sample/` ; le bloc inspecté par SCRUM-28 et
ceux de la calibration SCRUM-31 sont exclus. Les réponses attendues sont produites par des règles fixes
à partir des EventId : faits comptés dans l'ordre d'apparition, hypothèses seulement pour des motifs
connus, abstention quand la trace s'arrête sans erreur visible. Elles ne citent aucun passage C6
(`sources: []`). Ces exemples servent à tester la faisabilité matérielle, pas la qualité :
`reviewed_by` reste vide jusqu'à la relecture humaine (C5).
"""
import json
import re
from collections import Counter

import pandas as pd

from teamai.paths import ANNOTATIONS, SAMPLE, SPLITS

OUTPUT = ANNOTATIONS / "seed_alain.jsonl"
EXCLUDED = {
    "blk_8362325295506522506",  # inspecté par SCRUM-28
    "blk_7815531973893896934", "blk_4971154345890344", "blk_-8431991883875585441",  # calibration SCRUM-31
}

# Description courte et factuelle de chaque événement (templates Loghub E1–E29).
EVENTS = {
    "E1": "ajout d'un bloc déjà présent", "E2": "vérification réussie du bloc",
    "E3": "bloc servi à un client", "E4": "exception pendant le service du bloc",
    "E5": "début de réception du bloc", "E6": "bloc reçu avec sa taille",
    "E7": "exception reçue par writeBlock", "E8": "interruption d'un PacketResponder",
    "E9": "bloc reçu en entier", "E10": "exception d'un PacketResponder",
    "E11": "fin d'un PacketResponder", "E12": "exception d'écriture vers un miroir",
    "E13": "paquet vide reçu", "E14": "exception dans receiveBlock",
    "E15": "décalage du fichier de bloc modifié", "E16": "bloc transmis à un autre DataNode",
    "E17": "échec de transfert du bloc", "E18": "démarrage d'un transfert du bloc",
    "E19": "réouverture du bloc", "E20": "erreur volumeMap lors de la suppression",
    "E21": "suppression d'un fichier du bloc", "E22": "allocation du bloc par le NameNode",
    "E23": "ajout à l'invalidSet", "E24": "retrait de neededReplications",
    "E25": "demande de réplication", "E26": "réplique enregistrée dans le blockMap",
    "E27": "addStoredBlock redondant", "E28": "addStoredBlock pour un bloc sans fichier",
    "E29": "délai de réplication en attente expiré",
}
ERRORS = {"E4", "E7", "E8", "E10", "E12", "E14", "E17", "E20", "E28", "E29"}
HYPOTHESES = {
    "E7": "L'exception de writeBlock est compatible avec une écriture interrompue en amont du pipeline",
    "E20": "L'erreur volumeMap est compatible avec la suppression d'une réplique déjà absente du DataNode",
    "E28": "Le bloc semble avoir été rattaché trop tard, alors que son fichier n'existait plus",
    "E4": "Les exceptions de service sont compatibles avec des lectures interrompues côté client",
}


def stamp(line: str) -> str:
    """Horodatage lisible d'une ligne HDFS (`081109 213445` → `09/11 21:34:45`), date incluse pour les traces qui passent minuit."""
    date, time = line.split()[:2]
    return f"{date[4:]}/{date[2:4]} {time[:2]}:{time[2:4]}:{time[4:]}"


def build_expected(events: list[str], lines: list[str]) -> dict:
    """Réponse C5 attendue, calculée par règles à partir des EventId et des horodatages."""
    counts = Counter(events)
    order = list(dict.fromkeys(events))
    facts = [f"{e}{' ×' + str(counts[e]) if counts[e] > 1 else ''} : {EVENTS[e]}" for e in order]
    errors = [e for e in order if e in ERRORS]
    if "E5" in counts and "E9" not in counts:
        facts.append("Aucune réception complète du bloc (E9) dans la trace")
    if "E26" not in counts:
        facts.append("Aucune réplique enregistrée (E26) dans la trace")
    period = f"entre {stamp(lines[0])} et {stamp(lines[-1])}"
    summary = f"{len(events)} événements {period} : " + ", ".join(EVENTS[e] for e in order[:4])
    summary += "…" if len(order) > 4 else "."
    if errors:
        summary += " Erreur(s) visible(s) : " + ", ".join(f"{e} ({EVENTS[e]})" for e in errors) + "."

    truncated = "E9" not in counts and "E26" not in counts and not errors
    if truncated:
        return {"resume_evenements": summary + " La trace s'arrête sans fin de transfert ni erreur.",
                "faits_observes": facts, "hypotheses": [],
                "infos_manquantes": ["La trace ne permet pas de distinguer un échec d'écriture, un abandon "
                                     "par le client ou des lignes absentes du journal",
                                     "Logs du client et des DataNodes après la dernière ligne"],
                "sources": [], "abstention": True}
    hypotheses = [HYPOTHESES[e] for e in errors if e in HYPOTHESES]
    missing = ["Logs du client ou des DataNodes concernés au moment de l'erreur"] if errors else []
    return {"resume_evenements": summary, "faits_observes": facts, "hypotheses": hypotheses,
            "infos_manquantes": missing, "sources": [], "abstention": False}


def pick_blocks(traces: pd.DataFrame) -> pd.DataFrame:
    """10 normaux et 10 anomalies du train, en couvrant les motifs d'anomalie fréquents."""
    normal = traces[(traces["label"] == 0) & traces["n"].between(13, 19)].head(10)
    fail = traces[traces["label"] == 1]
    picks = [fail[fail["events"].map(lambda ev, e=e: e in ev)].head(k) for e, k in (("E7", 3), ("E20", 3), ("E28", 2))]
    picks.append(fail[fail["events"].map(lambda ev: set(ev) <= {"E5", "E22"})].head(2))
    return pd.concat([normal, *picks]).drop_duplicates("BlockId")


def main():
    """Sélectionne les blocs, retrouve leurs lignes brutes et écrit le fichier JSONL."""
    traces = pd.read_csv(SAMPLE / "Event_traces.csv")
    split = pd.read_csv(SPLITS / "splits.csv", usecols=["BlockId", "split"]).set_index("BlockId")["split"]
    traces["split"] = traces["BlockId"].map(split)
    traces["label"] = (traces["Label"] == "Fail").astype(int)
    traces["events"] = traces["Features"].str.strip("[]").str.split(",")
    traces["n"] = traces["events"].str.len()
    traces = traces[(traces["split"] == "train") & ~traces["BlockId"].isin(EXCLUDED)]
    chosen = pick_blocks(traces)

    wanted = set(chosen["BlockId"])
    lines: dict[str, list[str]] = {b: [] for b in wanted}
    block_re = re.compile(r"blk_-?\d+")
    with open(SAMPLE / "HDFS_sample.log", encoding="utf-8") as f:
        for line in f:
            for b in set(block_re.findall(line)) & wanted:
                lines[b].append(line.rstrip("\r\n"))

    rows = []
    for n, rec in enumerate(chosen.itertuples(), start=1):
        if len(lines[rec.BlockId]) != len(rec.events):
            raise ValueError(f"{rec.BlockId} : {len(lines[rec.BlockId])} lignes pour {len(rec.events)} événements")
        rows.append({"id": f"seed-{n:04d}", "block_id": rec.BlockId, "split": "train",
                     "trace_lines": lines[rec.BlockId], "events": rec.events, "label": int(rec.label),
                     "expected": build_expected(rec.events, lines[rec.BlockId]),
                     "annotator": "alain", "reviewed_by": ""})
    OUTPUT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    print(f"{len(rows)} exemples ({sum(r['label'] for r in rows)} anomalies) écrits dans {OUTPUT}")


if __name__ == "__main__":
    main()
