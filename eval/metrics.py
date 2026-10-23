"""Métriques communes de classification binaire (normal / anomalie) pour comparer les modèles du volet A."""

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


def evaluate_binary(y_true, y_pred, name="Validation"):
    """Évalue un modèle de détection d'anomalies HDFS."""

    precision = precision_score(
        y_true, y_pred, zero_division=0
    )
    recall = recall_score(
        y_true, y_pred, zero_division=0
    )
    macro_f1 = f1_score(
        y_true, y_pred, average="macro",
        zero_division=0
    )
    accuracy = accuracy_score(y_true, y_pred)

    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    print(f"\n=== {name} ===")
    print(f"Accuracy           : {accuracy:.4f}")
    print(f"Precision anomalie : {precision:.4f}")
    print(f"Recall anomalie    : {recall:.4f}")
    print(f"Macro-F1           : {macro_f1:.4f}")

    print("\nMatrice de confusion :")
    print(cm)

    print("\nRapport de classification :")
    print(
        classification_report(
            y_true,
            y_pred,
            labels=[0, 1],
            target_names=["Normal", "Anomalie"],
            zero_division=0,
        )
    )

    return {
        "accuracy": float(accuracy),
        "precision_anomaly": float(precision),
        "recall_anomaly": float(recall),
        "macro_f1": float(macro_f1),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }
