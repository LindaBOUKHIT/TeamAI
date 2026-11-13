"""SCRUM-62 : export de cas de validation proches du seuil pour le navigateur."""

import hashlib
import json

import numpy as np
import pandas as pd

from teamai.data.loader import encode
from teamai.data.splits import load_split
from teamai.paths import ROOT, WEB_PUBLIC


def main():
    """Exporte cinq cas de chaque côté du seuil, sans consulter le test."""
    analysis_path = (
        ROOT / "eval/results/SCRUM-62_20261023T153242Z_690fcb/analysis.json"
    )
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    meta = json.loads(
        (WEB_PUBLIC / "model/detector.meta.json").read_text(encoding="utf-8")
    )
    predictions_path = (
        ROOT / "eval/runs" / meta["run_id"] / "predictions.jsonl"
    )

    actual_hash = hashlib.sha256(predictions_path.read_bytes()).hexdigest()
    if actual_hash != analysis["predictions_sha256"]:
        raise ValueError("Les prédictions ont changé depuis l'analyse.")
    if meta["model_sha256"] != analysis["model_sha256"]:
        raise ValueError("Le modèle ne correspond pas à l'analyse.")

    frame = pd.read_json(
        predictions_path, lines=True, precise_float=True
    )
    if not frame["split"].eq("val").all():
        raise ValueError("Uniquement la validation est autorisée.")

    threshold = meta["threshold"]
    below = frame.loc[frame["p_anomaly"] < threshold].nlargest(
        5, "p_anomaly"
    )
    above = frame.loc[frame["p_anomaly"] >= threshold].nsmallest(
        5, "p_anomaly"
    )
    selected = pd.concat([above, below], ignore_index=True)
    if len(selected) != 10:
        raise ValueError("Dix cas sont nécessaires.")

    val = load_split("val").set_index("BlockId")
    vocab = json.loads(
        (WEB_PUBLIC / "vocab.json").read_text(encoding="utf-8")
    )
    ids = {
        event: specification["id"]
        for event, specification in vocab["events"].items()
    }

    rows = []
    for block_id in selected["BlockId"]:
        rows.append(encode(val.loc[block_id, "events"], ids, max_len=50))

    scores = selected["p_anomaly"].to_numpy(dtype=float)
    cases = {
        "split": "val",
        "model_sha256": meta["model_sha256"],
        "threshold": threshold,
        "tolerance": 1e-4,
        "block_ids": selected["BlockId"].tolist(),
        "event_ids": rows,
        "p_anomaly": scores.tolist(),
        "expected_labels": (scores >= threshold).astype(int).tolist(),
    }

    output = WEB_PUBLIC / "model/threshold_cases.json"
    if output.exists():
        raise FileExistsError("Les cas existent déjà ; aucun écrasement.")

    output.write_text(
        json.dumps(cases, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(f"Cas exportés : {output}")
    print(f"Seuil : {threshold}")
    print("Classes attendues :", cases["expected_labels"])
    print("Distance minimale au seuil :", float(np.min(abs(scores - threshold))))


if __name__ == "__main__":
    main()