"""SCRUM-25 : export du meilleur BiLSTM vers un dossier candidat."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import onnx
import torch

from bilstm import BiLSTM
from teamai.paths import ROOT, SPLITS, WEB_PUBLIC


def file_hash(path):
    """Calcule l'empreinte SHA-256 d'un fichier."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """Exporte le checkpoint sélectionné sans modifier le modèle du site."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()

    run = args.run.resolve()
    config = json.loads((run / "config.json").read_text(encoding="utf-8"))
    vocab_path = WEB_PUBLIC / "vocab.json"

    if file_hash(vocab_path) != config["vocab_sha256"]:
        raise ValueError("Le vocabulaire a changé depuis l'entraînement.")

    if file_hash(SPLITS / "splits.csv") != config["splits_sha256"]:
        raise ValueError("Les splits ont changé depuis l'entraînement.")

    checkpoint = torch.load(
        run / "best.pt",
        map_location="cpu",
        weights_only=True,
    )

    model = BiLSTM(
        embedding_dim=checkpoint["embedding_dim"],
        hidden_size=checkpoint["hidden_size"],
    )
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()

    # Un dossier neuf empêche d'écraser un export précédent.
    output = run / "export"
    output.mkdir(exist_ok=False)
    model_path = output / "detector.onnx"

    example = torch.zeros((1, 50), dtype=torch.int64)
    example[:, :4] = torch.tensor([5, 22, 5, 11])

    torch.onnx.export(
        model,
        example,
        str(model_path),
        input_names=["event_ids"],
        output_names=["p_anomaly"],
        dynamic_axes={
            "event_ids": {0: "batch"},
            "p_anomaly": {0: "batch"},
        },
        opset_version=17,
        dynamo=False,
    )

    onnx.checker.check_model(onnx.load(str(model_path)))

    metadata = {
        "contract_version": "v1",
        "model": "bilstm",
        "version": "v1",
        "threshold": checkpoint["threshold"],
        "max_len": 50,
        "pad_id": 0,
        "unk_id": 30,
        "vocab_sha256": config["vocab_sha256"],
        "model_sha256": file_hash(model_path),
        "splits_sha256": config["splits_sha256"],
        "val_macro_f1": checkpoint["val_macro_f1"],
        "epoch": checkpoint["epoch"],
        "run_id": run.name,
        "checkpoint_sha256": file_hash(run / "best.pt"),
        "training_git_commit": config["git_commit"],
    }

    (output / "detector.meta.json").write_text(
        json.dumps(metadata, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )

    print(f"Export candidat : {model_path}")
    print(f"Taille : {model_path.stat().st_size / 1024:.1f} Ko")
    print("Structure ONNX vérifiée.")
    print("Parité numérique à vérifier avant installation dans le site.")


if __name__ == "__main__":
    main()
