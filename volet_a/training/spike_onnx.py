"""SCRUM-22 : BiLSTM jouet, export ONNX et vérification Python.

    python volet_a/training/spike_onnx.py      (depuis la racine du dépôt)

Le BiLSTM ignore le padding (C2 : 0 à droite) : chaque direction lit seulement les vrais événements.
Le script vérifie la parité PyTorch / ONNX Runtime et l'invariance au padding, puis écrit le modèle,
ses métadonnées et les cas de test du navigateur dans volet_a/web/public/model/.
"""

import json
from pathlib import Path

import numpy as np
import onnx
import onnxruntime as ort
import torch
from torch import nn


ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / "volet_a/web/public/model"
MAX_LEN = 50  # C2


class ToyBiLSTM(nn.Module):
    """BiLSTM minuscule non entraîné, servant seulement à valider la chaîne d'export ONNX.

    Les deux directions sont deux LSTM simples : l'un lit la séquence dans l'ordre, l'autre la lit
    retournée à l'intérieur de sa vraie longueur. On garde l'état de chacun au dernier vrai événement,
    si bien que le padding n'influence pas le score. Ces opérations (gather) s'exportent en ONNX,
    contrairement à `pack_padded_sequence`.
    """

    def __init__(self):
        """Plongement des 31 identifiants C2 (dim 8), deux LSTM de 8, couche linéaire vers 1 logit."""
        super().__init__()
        # C2 : 0 = padding, 1..29 = événements, 30 = inconnu.
        self.embedding = nn.Embedding(31, 8, padding_idx=0)
        self.forward_lstm = nn.LSTM(input_size=8, hidden_size=8, batch_first=True)
        self.backward_lstm = nn.LSTM(input_size=8, hidden_size=8, batch_first=True)
        self.classifier = nn.Linear(16, 1)

    def forward(self, event_ids):
        """Rend la probabilité d'anomalie de chaque séquence (`event_ids` : batch × 50 entiers C2)."""
        lengths = (event_ids != 0).sum(dim=1).clamp(min=1)  # padding à droite (C2)
        positions = torch.arange(event_ids.shape[1], device=event_ids.device).unsqueeze(0)
        # Indices qui retournent chaque séquence dans sa vraie longueur ; le padding reste à droite.
        reverse = torch.where(positions < lengths.unsqueeze(1), lengths.unsqueeze(1) - 1 - positions, positions)

        embeddings = self.embedding(event_ids)
        reversed_embeddings = torch.gather(embeddings, 1, reverse.unsqueeze(2).expand_as(embeddings))
        forward_out, _ = self.forward_lstm(embeddings)
        backward_out, _ = self.backward_lstm(reversed_embeddings)

        # État de chaque direction au dernier vrai événement.
        last = (lengths - 1).view(-1, 1, 1).expand(-1, 1, forward_out.shape[2])
        features = torch.cat((forward_out.gather(1, last).squeeze(1), backward_out.gather(1, last).squeeze(1)), dim=1)
        return torch.sigmoid(self.classifier(features)).squeeze(1)


def make_inputs(count: int = 10) -> torch.Tensor:
    """Séquences factices reproductibles de longueurs variées, avec padding à droite."""
    inputs = torch.zeros((count, MAX_LEN), dtype=torch.int64)
    for index in range(count):
        length = 5 + index * 4
        inputs[index, :length] = torch.randint(1, 31, (length,))
    return inputs


def check_padding_invariance(model: nn.Module, inputs: torch.Tensor) -> float:
    """Écart maximal entre le score d'une séquence paddée à 50 et celui de la même séquence sans padding."""
    worst = 0.0
    with torch.no_grad():
        for row in inputs:
            length = int((row != 0).sum())
            padded = model(row.unsqueeze(0)).item()
            alone = model(row[:length].unsqueeze(0)).item()
            worst = max(worst, abs(padded - alone))
    return worst


def main():
    """Exporte le modèle jouet, vérifie parité et invariance au padding, écrit les fichiers du navigateur."""
    torch.manual_seed(22)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model = ToyBiLSTM().eval()
    inputs = make_inputs()

    with torch.no_grad():
        expected = model(inputs).numpy()

    padding_error = check_padding_invariance(model, inputs)
    print(f"Invariance au padding : écart maximal = {padding_error:.8f}")
    assert padding_error < 1e-6, f"Le padding influence le score : {padding_error}"

    model_path = MODEL_DIR / "detector.onnx"
    torch.onnx.export(
        model,
        inputs[:1],
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
    session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])

    # Vérifie que plusieurs tailles de batch fonctionnent.
    for batch_size in (1, 3, 10):
        actual = session.run(["p_anomaly"], {"event_ids": inputs[:batch_size].numpy()})[0]
        assert actual.shape == (batch_size,)
        error = float(np.max(np.abs(actual - expected[:batch_size])))
        print(f"Batch {batch_size} : écart maximal = {error:.8f}")
        assert error < 1e-4, f"Écart trop élevé : {error}"

    # Ces mêmes entrées et résultats servent au test navigateur.
    fixtures = {"event_ids": inputs.tolist(), "p_anomaly": expected.tolist(), "tolerance": 1e-4}
    (MODEL_DIR / "spike_cases.json").write_text(json.dumps(fixtures, indent=2), encoding="utf-8")

    metadata = {
        "threshold": 0.5,
        "model": "bilstm",
        "version": "spike",
        "trained_on": "none-random-weights",
        "val_macro_f1": None,
    }
    (MODEL_DIR / "detector.meta.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Modèle exporté : {model_path}")
    print(f"Taille : {model_path.stat().st_size / 1024:.1f} Ko")
    print("Parité PyTorch / ONNX Runtime Python : OK")
    print("Modèle jouet non entraîné : scores sans valeur prédictive.")


if __name__ == "__main__":
    main()
