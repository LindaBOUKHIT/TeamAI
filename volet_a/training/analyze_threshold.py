"""SCRUM-62 : analyse du seuil sur la validation, sans accès au test."""

import argparse
import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from teamai.data.splits import load_split
from teamai.paths import ROOT, SPLITS, WEB_PUBLIC


def file_hash(path):
    """Retourne le SHA-256 d'un fichier."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    """Enregistre un JSON strict."""
    path.write_text(
        json.dumps(value, indent=2, allow_nan=False, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def calculate_curve(labels, scores, thresholds):
    """Calcule les métriques pour la règle score >= seuil, égalités incluses."""
    order = np.argsort(scores, kind="stable")
    sorted_scores = scores[order]
    sorted_labels = labels[order]

    positive_prefix = np.concatenate(([0], np.cumsum(sorted_labels)))
    below = np.searchsorted(sorted_scores, thresholds, side="left")

    fn = positive_prefix[below]
    tn = below - fn
    tp = int(labels.sum()) - fn
    fp = int((labels == 0).sum()) - tn

    precision = np.divide(
        tp, tp + fp, out=np.zeros(len(tp), dtype=float), where=(tp + fp) > 0
    )
    recall = tp / int(labels.sum())
    f1 = 2 * tp / np.maximum(2 * tp + fp + fn, 1)
    normal_f1 = 2 * tn / np.maximum(2 * tn + fp + fn, 1)

    return pd.DataFrame({
        "threshold": thresholds,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "tp": tp,
        "precision_anomaly": precision,
        "recall_anomaly": recall,
        "f1_anomaly": f1,
        "macro_f1": (f1 + normal_f1) / 2,
    })


def best_under_constraint(curve, max_fn):
    """Maximise le F1 anomalie, puis départage par FN, FP et seuil."""
    eligible = curve.loc[curve["fn"] <= max_fn]
    best = eligible.sort_values(
        ["f1_anomaly", "fn", "fp", "threshold"],
        ascending=[False, True, True, False],
    ).iloc[0]
    result = best.to_dict()
    for field in ("tn", "fp", "fn", "tp"):
        result[field] = int(result[field])
    return result


def main():
    """Vérifie les sources et produit résultats et courbes sans modifier le site."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    run = args.run.resolve()

    predictions_path = run / "predictions.jsonl"
    config_path = run / "config.json"
    meta_path = WEB_PUBLIC / "model/detector.meta.json"

    config = json.loads(config_path.read_text(encoding="utf-8"))
    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    if meta["run_id"] != run.name:
        raise ValueError("Le site ne référence pas ce run d'entraînement.")

    if file_hash(run / "best.pt") != meta["checkpoint_sha256"]:
        raise ValueError("Checkpoint différent de celui du modèle servi.")

    if file_hash(WEB_PUBLIC / "model/detector.onnx") != meta["model_sha256"]:
        raise ValueError("Hash du modèle servi incorrect.")

    splits_hash = file_hash(SPLITS / "splits.csv")
    if splits_hash != config["splits_sha256"] or splits_hash != meta["splits_sha256"]:
        raise ValueError("Splits différents de ceux de l'entraînement.")

    if file_hash(WEB_PUBLIC / "vocab.json") != config["vocab_sha256"]:
        raise ValueError("Le vocabulaire a changé depuis l'entraînement.")

    frame = pd.read_json(
        predictions_path, lines=True, precise_float=True
    )
    if frame.empty or not frame["split"].eq("val").all():
        raise ValueError("Le fichier doit contenir uniquement la validation.")
    if frame["BlockId"].duplicated().any():
        raise ValueError("Identifiants dupliqués.")

    labels = frame["label"].to_numpy()
    scores = frame["p_anomaly"].to_numpy(dtype=float)
    if not np.isin(labels, [0, 1]).all() or len(np.unique(labels)) != 2:
        raise ValueError("Labels binaires invalides.")
    if not np.isfinite(scores).all() or np.any((scores < 0) | (scores > 1)):
        raise ValueError("Scores invalides.")

    # Vérifie les identifiants et labels contre la validation officielle.
    print("Vérification de la validation officielle...", flush=True)
    val = load_split("val")
    expected = val.set_index("BlockId")["label"].sort_index()
    actual = frame.set_index("BlockId")["label"].sort_index()
    if not expected.index.equals(actual.index):
        raise ValueError("Les blocs ne correspondent pas à la validation.")
    if not np.array_equal(expected.to_numpy(), actual.to_numpy()):
        raise ValueError("Labels différents de la validation officielle.")

    # Séquences inédites calculées à partir des séquences complètes.
    train = load_split("train")
    train_sequences = set(train["events"].map(tuple))
    unseen_ids = set(
        val.loc[
            ~val["events"].map(tuple).isin(train_sequences), "BlockId"
        ]
    )
    unseen = frame["BlockId"].isin(unseen_ids).to_numpy()

    # Tous les changements possibles de classification, plus une grille
    # régulière pour les courbes, dont des seuils supérieurs à 0,99.
    thresholds = np.unique(np.concatenate((
        scores,
        np.linspace(0, 1, 1001),
        [float(meta["threshold"])],
    )))
    curve = calculate_curve(labels.astype(int), scores, thresholds)

    candidates = {
        f"max_fn_{limit}": best_under_constraint(curve, limit)
        for limit in (0, 1, 2)
    }

    evaluated = {"current": float(meta["threshold"])}
    evaluated.update({
        name: result["threshold"] for name, result in candidates.items()
    })

    comparisons = {}
    for name, threshold in evaluated.items():
        comparisons[name] = {}
        for subset, mask in (
            ("all_validation", np.ones(len(labels), dtype=bool)),
            ("unseen", unseen),
        ):
            if not mask.any():
                comparisons[name][subset] = None
                continue
            result = calculate_curve(
                labels[mask].astype(int), scores[mask], np.array([threshold])
            ).iloc[0].to_dict()
            for field in ("tn", "fp", "fn", "tp"):
                result[field] = int(result[field])
            result["n_blocks"] = int(mask.sum())
            comparisons[name][subset] = result

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = ROOT / "eval/results" / (
        f"SCRUM-62_{stamp}_{uuid.uuid4().hex[:6]}"
    )
    output.mkdir(parents=True, exist_ok=False)

    curve.to_csv(output / "threshold_curve.csv", index=False)

    missed = frame.loc[
        (labels == 1) & (scores < float(meta["threshold"]))
    ].sort_values("p_anomaly")
    missed.to_csv(output / "missed_at_original_threshold.csv", index=False)

    report = {
        "ticket": "SCRUM-62",
        "split": "val",
        "test_used": False,
        "model_sha256": meta["model_sha256"],
        "splits_sha256": splits_hash,
        "predictions_sha256": file_hash(predictions_path),
        "script_sha256": file_hash(ROOT / "volet_a/training/analyze_threshold.py"),
        "run_id": run.name,
        "n_blocks": len(frame),
        "n_unseen": int(unseen.sum()),
        "selection_objective": "maximum F1 anomalie sous contrainte de FN",
        "tie_break": "moins de FN, puis moins de FP, puis seuil le plus élevé",
        "candidates": comparisons,
        "metadata_updated": False,
    }
    write_json(output / "analysis.json", report)

    figure, axes = plt.subplots(1, 2, figsize=(12, 4))
    for axis in axes:
        for column, title in (
            ("precision_anomaly", "Précision"),
            ("recall_anomaly", "Rappel"),
            ("f1_anomaly", "F1 anomalie"),
        ):
            axis.plot(curve["threshold"], curve[column], label=title)
        axis.axvline(
            float(meta["threshold"]),
            color="grey", linestyle="--", label="Seuil actuel",
        )
        axis.set_xlabel("Seuil — anomalie si score ≥ seuil")
        axis.set_ylabel("Mesure sur la validation")
        axis.grid(alpha=0.3)

    axes[0].set_title("Vue complète")
    axes[1].set_title("Détail au-dessus de 0,99")
    axes[1].set_xlim(0.99, 1.0)
    axes[0].legend()
    figure.tight_layout()
    figure.savefig(output / "threshold_curves.png", dpi=180)
    plt.close(figure)

    for name, result in comparisons.items():
        item = result["all_validation"]
        print(
            f"{name} : seuil={item['threshold']:.17g} ; "
            f"FP={item['fp']} ; FN={item['fn']} ; "
            f"F1 anomalie={item['f1_anomaly']:.6f} ; "
            f"macro-F1={item['macro_f1']:.6f}",
            flush=True,
        )

    print(f"\nRésultats : {output}")
    print("Métadonnées inchangées. Aucun test officiel évalué.")


if __name__ == "__main__":
    main()