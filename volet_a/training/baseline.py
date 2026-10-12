
import json
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from eval.metrics import evaluate_binary
from teamai.data.splits import load_split
from teamai.paths import PREPROCESSED


FEATURES = [f"E{i}" for i in range(1, 30)]
RESULTS_DIR = Path("volet_a/results")
RESULTS_FILE = RESULTS_DIR / "SCRUM-24-baseline-results.json"


def load_dataset():
    """Charge les splits officiels et les comptages HDFS."""
    print("Chargement des splits officiels SCRUM-20...")

    splits = {
        name: load_split(name)
        for name in ("train", "val", "test")
    }

    print("Chargement des comptages d'événements...")
    counts = pd.read_csv(
        PREPROCESSED / "Event_occurrence_matrix.csv",
        usecols=["BlockId"] + FEATURES,
    )

    if counts["BlockId"].duplicated().any():
        raise ValueError("BlockId dupliqués dans la matrice.")

    for name, split in splits.items():
        merged = split.merge(
            counts,
            on="BlockId",
            how="left",
            validate="one_to_one",
        )

        if merged[FEATURES].isna().any().any():
            raise ValueError(
                f"Comptages manquants dans le split {name}."
            )

        splits[name] = merged
        print(f"{name} : {len(merged):,} blocs")

    return splits


def evaluate_unseen(model, train, dataset, split_name):
    """Évalue les séquences inédites et connues."""

    train_sequences = {
        tuple(events) for events in train["events"]
    }

    unseen_mask = ~dataset["events"].apply(
        lambda events: tuple(events) in train_sequences
    )

    print(f"\n{split_name} - Séquences inédites : "
          f"{unseen_mask.sum():,}")
    print(f"{split_name} - Séquences connues : "
          f"{(~unseen_mask).sum():,}")

    y_true = dataset["label"].astype(int)
    y_pred = model.predict(dataset[FEATURES])

    results = {}

    for name, mask in (
        ("unseen", unseen_mask),
        ("known", ~unseen_mask),
    ):
        if mask.any():
            results[name] = evaluate_binary(
                y_true[mask],
                y_pred[mask.to_numpy()],
                name=f"{split_name} - {name}",
            )
            results[name]["n_blocks"] = int(mask.sum())

    return results


def main():
    splits = load_dataset()

    train = splits["train"]
    val = splits["val"]
    test = splits["test"]

    X_train = train[FEATURES]
    y_train = train["label"].astype(int)

    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(
            class_weight="balanced",
            max_iter=1000,
            random_state=42,
        ),
    )

    print("\nEntraînement de la régression logistique...")
    model.fit(X_train, y_train)

    results = {
        "ticket": "SCRUM-24",
        "model": "LogisticRegression",
        "class_weight": "balanced",
        "max_iter": 1000,
        "random_state": 42,
        "features": FEATURES,
        "n_train": len(train),
        "n_val": len(val),
        "n_test": len(test),
    }

    # Validation officielle
    print("\n========== VALIDATION ==========")

    val_predictions = model.predict(val[FEATURES])

    results["validation"] = evaluate_binary(
        val["label"].astype(int),
        val_predictions,
        name="Validation officielle SCRUM-20",
    )

    results["validation_by_sequence"] = evaluate_unseen(
        model, train, val, "Validation"
    )

    # Test officiel : évaluation uniquement, sans réentraînement
    print("\n========== TEST FINAL ==========")

    test_predictions = model.predict(test[FEATURES])

    results["test"] = evaluate_binary(
        test["label"].astype(int),
        test_predictions,
        name="Test officiel SCRUM-20",
    )

    results["test_by_sequence"] = evaluate_unseen(
        model, train, test, "Test"
    )

    # Enregistrement automatique des résultats
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nRésultats enregistrés : {RESULTS_FILE}")
    print("\nSCRUM-24 : exécution terminée.")


if __name__ == "__main__":
    main()
