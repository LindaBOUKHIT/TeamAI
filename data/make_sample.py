
"""SCRUM-18 : échantillon reproductible de HDFS_v1."""

import argparse
import re
from pathlib import Path

import pandas as pd

from teamai.data.loader import load_traces
from teamai.paths import PREPROCESSED, SAMPLE

RAW_LOG = PREPROCESSED.parent / "HDFS.log"
BLOCK_PATTERN = re.compile(r"blk_-?\d+")


def make_sample(n_blocks=2000, anomaly_ratio=0.25, seed=42):
    """Tire `n_blocks` blocs (dont `anomaly_ratio` d'anomalies) et écrit l'échantillon dans data/sample/.

    Produit Event_traces.csv (colonnes d'origine) et HDFS_sample.log (lignes brutes des blocs tirés),
    puis vérifie le résultat avec le chargeur commun ; lève une erreur si un bloc n'a aucune ligne brute.
    """
    SAMPLE.mkdir(parents=True, exist_ok=True)

    # Utiliser le chargeur commun du projet.
    traces = load_traces()

    if traces["BlockId"].duplicated().any():
        raise ValueError("BlockId dupliqués dans le dataset source")

    n_anomaly = round(n_blocks * anomaly_ratio)
    n_normal = n_blocks - n_anomaly

    normal = traces[traces["label"] == 0]
    anomaly = traces[traces["label"] == 1]

    if n_normal > len(normal) or n_anomaly > len(anomaly):
        raise ValueError("Nombre de blocs demandé indisponible")

    selected = pd.concat([
        normal.sample(n=n_normal, random_state=seed),
        anomaly.sample(n=n_anomaly, random_state=seed),
    ]).sample(frac=1, random_state=seed).reset_index(drop=True)

    selected_ids = set(selected["BlockId"])

    # Conserver les colonnes originales attendues par le loader.
    original = pd.read_csv(PREPROCESSED / "Event_traces.csv")
    sample = original[original["BlockId"].isin(selected_ids)].copy()

    if len(sample) != n_blocks:
        raise ValueError("Nombre de blocs incorrect après sélection")

    sample.to_csv(SAMPLE / "Event_traces.csv", index=False)

    # Extraire les lignes brutes contenant au moins un bloc sélectionné.
    log_count = 0
    found_ids = set()

    with RAW_LOG.open("r", encoding="utf-8", errors="replace") as source:
        with (SAMPLE / "HDFS_sample.log").open(
            "w", encoding="utf-8"
        ) as destination:
            for line in source:
                ids = set(BLOCK_PATTERN.findall(line))
                matched = ids & selected_ids

                if matched:
                    destination.write(line)
                    log_count += 1
                    found_ids.update(matched)

    # Vérification avec le loader commun.
    loaded = load_traces(sample=True)

    assert len(loaded) == n_blocks
    assert loaded["BlockId"].nunique() == n_blocks
    assert int(loaded["label"].sum()) == n_anomaly

    missing = selected_ids - found_ids

    print(f"Blocs sélectionnés : {len(loaded)}")
    print(f"Normaux : {(loaded['label'] == 0).sum()}")
    print(f"Anomalies : {loaded['label'].sum()}")
    print(f"Proportion anomalies : {loaded['label'].mean():.2%}")
    print(f"Lignes brutes extraites : {log_count}")
    print(f"Blocs sans logs bruts retrouvés : {len(missing)}")

    if missing:
        raise RuntimeError(
            f"{len(missing)} blocs sans lignes brutes correspondantes"
        )

    print("Échantillon généré et validé.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-blocks", type=int, default=2000)
    parser.add_argument("--anomaly-ratio", type=float, default=0.25)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if args.n_blocks <= 0:
        parser.error("--n-blocks doit être positif")
    if not 0 <= args.anomaly_ratio <= 1:
        parser.error("--anomaly-ratio doit être entre 0 et 1")

    make_sample(args.n_blocks, args.anomaly_ratio, args.seed)
