
"""SCRUM-20 — Chargement partagé des splits HDFS (contrat C4)."""

import hashlib
import json

import pandas as pd

from teamai.data.loader import load_traces
from teamai.paths import SPLITS


VALID_SPLITS = {"train", "val", "test"}


def load_split(name: str) -> pd.DataFrame:
    """Charge un split avec ses labels et ses séquences d'événements."""
    if name not in VALID_SPLITS:
        raise ValueError(
            f"Split inconnu : {name!r}. "
            f"Valeurs possibles : {sorted(VALID_SPLITS)}"
        )

    path = SPLITS / "splits.csv"

    if not path.exists():
        raise FileNotFoundError(
            "Fichier splits.csv introuvable. "
            "Exécuter : python data/make_splits.py"
        )

    splits = pd.read_csv(
        path,
        dtype={"BlockId": str, "split": str},
    )

    required = {"BlockId", "split", "unseen_seq"}

    if not required.issubset(splits.columns):
        raise ValueError("Format splits.csv non conforme au contrat C4.")

    if splits["BlockId"].duplicated().any():
        raise ValueError("BlockId dupliqués dans splits.csv.")

    if not splits["split"].isin(VALID_SPLITS).all():
        raise ValueError("Valeur de split invalide.")

    # Vérification du hash enregistré lors de la génération.
    meta_path = SPLITS / "splits_meta.json"

    if meta_path.exists():
        metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        expected_hash = metadata.get("splits_csv_sha256")

        if expected_hash:
            actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()

            if actual_hash != expected_hash:
                raise ValueError(
                    "Le hash de splits.csv ne correspond pas "
                    "à splits_meta.json. Régénérer les splits."
                )

    selected = splits.loc[
        splits["split"] == name
    ].copy()

    traces = load_traces()

    result = selected.merge(
        traces,
        on="BlockId",
        how="left",
        validate="one_to_one",
        indicator=True,
    )

    if (result["_merge"] != "both").any():
        raise ValueError(
            "Certains BlockId du split sont absents des traces HDFS."
        )

    result = result.drop(columns="_merge")

    if result["unseen_seq"].isna().any():
        raise ValueError("Valeurs unseen_seq manquantes.")

    return result.reset_index(drop=True)
