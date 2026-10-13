
"""SCRUM-20 : splits HDFS reproductibles, conformes au contrat C4."""

import argparse
import hashlib
import json

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from teamai.data.loader import load_traces
from teamai.paths import SPLITS


def main():
    """Découpe les blocs en train/val/test stratifiés et écrit splits.csv et splits_meta.json (contrat C4).

    Le test porte en plus le drapeau `unseen_seq` : séquence absente du train.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--train-ratio", type=float, default=0.70)
    parser.add_argument("--val-ratio", type=float, default=0.15)
    parser.add_argument("--test-ratio", type=float, default=0.15)
    args = parser.parse_args()

    if any(
        ratio <= 0
        for ratio in (
            args.train_ratio,
            args.val_ratio,
            args.test_ratio,
        )
    ):
        parser.error("Les trois proportions doivent être positives.")

    if not np.isclose(
        args.train_ratio + args.val_ratio + args.test_ratio,
        1.0,
    ):
        parser.error("La somme des proportions doit être égale à 1.")

    print("Chargement des traces HDFS...")
    df = load_traces()

    if df["BlockId"].duplicated().any():
        raise ValueError("BlockId dupliqués dans le dataset.")

    # Représentation stable des séquences complètes.
    df["sequence_key"] = df["events"].map(
        lambda events: ",".join(events)
    )

    # Tri stable pour garantir la reproductibilité.
    df = df.sort_values("BlockId").reset_index(drop=True)

    # Premier découpage : train / reste.
    train, remaining = train_test_split(
        df,
        train_size=args.train_ratio,
        random_state=args.seed,
        stratify=df["label"],
    )

    # Deuxième découpage : validation / test.
    val_fraction = (
        args.val_ratio / (args.val_ratio + args.test_ratio)
    )

    val, test = train_test_split(
        remaining,
        train_size=val_fraction,
        random_state=args.seed,
        stratify=remaining["label"],
    )

    # Les séquences inédites sont celles absentes du train.
    train_sequences = set(train["sequence_key"])

    test = test.copy()
    test["unseen_seq"] = ~test["sequence_key"].isin(
        train_sequences
    )

    # Hors test, ce drapeau n'est pas applicable.
    train = train.copy()
    val = val.copy()

    train["unseen_seq"] = False
    val["unseen_seq"] = False

    train["split"] = "train"
    val["split"] = "val"
    test["split"] = "test"

    result = pd.concat(
        [train, val, test],
        ignore_index=True,
    )

    result = result[
        ["BlockId", "split", "unseen_seq"]
    ].sort_values("BlockId").reset_index(drop=True)

    # Vérification des contraintes C4.
    assert len(result) == len(df)
    assert result["BlockId"].is_unique
    assert result["split"].isin(
        ["train", "val", "test"]
    ).all()

    SPLITS.mkdir(parents=True, exist_ok=True)
    output = SPLITS / "splits.csv"

    result.to_csv(output, index=False)

    # Hash SHA-256 du CSV réellement enregistré.
    sha256 = hashlib.sha256(output.read_bytes()).hexdigest()

    stats = {}
    for name, subset in (
        ("train", train),
        ("val", val),
        ("test", test),
    ):
        stats[name] = {
            "size": int(len(subset)),
            "normal": int((subset["label"] == 0).sum()),
            "anomaly": int((subset["label"] == 1).sum()),
            "anomaly_rate": float(subset["label"].mean()),
        }

    stats["test"]["unseen_seq_count"] = int(
        test["unseen_seq"].sum()
    )

    stats["test"]["unseen_seq_rate"] = float(
        test["unseen_seq"].mean()
    )

    metadata = {
        "protocol": "C4",
        "source": "Loghub HDFS_v1/Event_traces.csv",
        "method": "stratified_random_by_BlockId",
        "seed": args.seed,
        "ratios": {
            "train": args.train_ratio,
            "val": args.val_ratio,
            "test": args.test_ratio,
        },
        "normal_undersampling": False,
        "hash_algorithm": "sha256",
        "splits_csv_sha256": sha256,
        "total_blocks": int(len(result)),
        "splits": stats,
    }

    metadata_path = SPLITS / "splits_meta.json"

    metadata_path.write_text(
        json.dumps(
            metadata,
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )

    print("\n=== SCRUM-20 : SPLITS HDFS ===")
    print(f"Total : {len(result):,} blocs")

    for name, info in stats.items():
        print(
            f"{name:5s} : {info['size']:,} blocs "
            f"| anomalies : {info['anomaly']:,} "
            f"({info['anomaly_rate']:.2%})"
        )

    print(
        "Séquences inédites dans le test :",
        stats["test"]["unseen_seq_count"],
    )
    print("SHA-256 :", sha256)
    print("CSV :", output)
    print("Métadonnées :", metadata_path)


if __name__ == "__main__":
    main()
