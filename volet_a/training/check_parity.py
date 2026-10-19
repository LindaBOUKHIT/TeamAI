"""SCRUM-25 : parité PyTorch / ONNX sur la validation officielle."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import onnxruntime as ort
import torch

from teamai.paths import SPLITS, WEB_PUBLIC
from volet_a.training.bilstm import BiLSTM
from volet_a.training.dataset import load_datasets


def file_hash(path):
    """Calcule le SHA-256 d'un fichier."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """Vérifie C3, les scores et les décisions, sans utiliser le test."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    torch.set_num_threads(4)

    run = args.run.resolve()
    export = run / "export"
    report_path = export / "parity.json"

    if report_path.exists():
        raise FileExistsError("Ce rapport existe déjà ; il ne sera pas écrasé.")

    meta = json.loads(
        (export / "detector.meta.json").read_text(encoding="utf-8")
    )
    for path, key in (
        (export / "detector.onnx", "model_sha256"),
        (WEB_PUBLIC / "vocab.json", "vocab_sha256"),
        (SPLITS / "splits.csv", "splits_sha256"),
        (run / "best.pt", "checkpoint_sha256"),
    ):
        if file_hash(path) != meta[key]:
            raise ValueError(f"Empreinte incorrecte : {path.name}")

    checkpoint = torch.load(
        run / "best.pt", map_location="cpu", weights_only=True
    )
    model = BiLSTM(
        checkpoint["embedding_dim"], checkpoint["hidden_size"]
    )
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()

    options = ort.SessionOptions()
    options.intra_op_num_threads = 4
    session = ort.InferenceSession(
        str(export / "detector.onnx"),
        sess_options=options,
        providers=["CPUExecutionProvider"],
    )

    inputs = session.get_inputs()
    outputs = session.get_outputs()

    if (
        len(inputs) != 1
        or inputs[0].name != "event_ids"
        or inputs[0].type != "tensor(int64)"
        or len(inputs[0].shape) != 2
        or inputs[0].shape[1] != 50
        or isinstance(inputs[0].shape[0], int)
        or len(outputs) != 1
        or outputs[0].name != "p_anomaly"
        or outputs[0].type != "tensor(float)"
        or len(outputs[0].shape) != 1
        or isinstance(outputs[0].shape[0], int)
    ):
        raise ValueError("Entrée ou sortie incompatible avec C3.")

    datasets = load_datasets()
    x = datasets["val"]["x"]
    del datasets

    maximum_error = 0.0
    disagreements = 0
    threshold = meta["threshold"]
    tolerance = 1e-4

    with torch.inference_mode():
        # Vérification explicite du batch dynamique.
        for size in (1, 3, 10):
            batch = x[:size]
            expected = model(batch).numpy()
            actual = session.run(
                ["p_anomaly"], {"event_ids": batch.numpy()}
            )[0]
            if actual.shape != (size,):
                raise ValueError(f"Forme incorrecte pour le batch {size}.")
            np.testing.assert_allclose(
                actual, expected, rtol=0, atol=tolerance
            )
            print(f"Batch {size} : OK", flush=True)

        # Comparaison sur toute la validation.
        for start in range(0, len(x), 512):
            batch = x[start:start + 512]
            expected = model(batch).numpy()
            actual = session.run(
                ["p_anomaly"], {"event_ids": batch.numpy()}
            )[0]

            if actual.shape != expected.shape:
                raise ValueError("Forme de sortie incorrecte.")
            if not np.isfinite(actual).all():
                raise ValueError("Scores ONNX non finis.")
            if np.any((actual < 0) | (actual > 1)):
                raise ValueError("Scores ONNX hors de [0, 1].")

            maximum_error = max(
                maximum_error,
                float(np.max(np.abs(actual - expected))),
            )
            disagreements += int(np.sum(
                (actual >= threshold) != (expected >= threshold)
            ))

            if start % 10240 == 0:
                print(f"Parité : {start:,}/{len(x):,}", flush=True)

        # Dix entrées réelles de validation pour le futur test navigateur.
        sample = x[:10]
        reference = model(sample).numpy().tolist()

    report = {
        "split": "val",
        "test_used": False,
        "n_blocks": len(x),
        "batch_sizes_checked": [1, 3, 10, 512],
        "max_absolute_error": maximum_error,
        "tolerance": tolerance,
        "threshold": threshold,
        "label_disagreements": disagreements,
        "model_sha256": meta["model_sha256"],
        "passed": maximum_error < tolerance and disagreements == 0,
    }

    report_path.write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    (export / "parity_cases.json").write_text(
        json.dumps({
            "event_ids": sample.tolist(),
            "p_anomaly": reference,
            "tolerance": tolerance,
            "model_sha256": meta["model_sha256"],
            "split": "val",
        }, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2))
    if not report["passed"]:
        raise RuntimeError("Parité insuffisante : ne pas publier le modèle.")

    print("Parité validée. Le modèle du site reste inchangé.")


if __name__ == "__main__":
    main()