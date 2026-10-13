"""SCRUM-22 : BiLSTM jouet, export ONNX et vérification Python."""

import json
from pathlib import Path

import numpy as np
import onnx
import onnxruntime as ort
import torch
from torch import nn


ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / "volet_a/web/public/model"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

torch.manual_seed(22)


class ToyBiLSTM(nn.Module):
    def __init__(self):
        super().__init__()
        # C2 : 0 = padding, 1..29 = événements, 30 = inconnu.
        self.embedding = nn.Embedding(31, 8, padding_idx=0)
        self.lstm = nn.LSTM(
            input_size=8,
            hidden_size=8,
            batch_first=True,
            bidirectional=True,
        )
        self.classifier = nn.Linear(16, 1)

    def forward(self, event_ids):
        embeddings = self.embedding(event_ids)
        _, (hidden, _) = self.lstm(embeddings)
        # Derniers états des deux directions du BiLSTM.
        features = torch.cat((hidden[-2], hidden[-1]), dim=1)
        return torch.sigmoid(self.classifier(features)).squeeze(1)


model = ToyBiLSTM().eval()

# Dix séquences factices reproductibles, avec padding à droite.
inputs = torch.zeros((10, 50), dtype=torch.int64)
for index in range(10):
    length = 5 + index * 4
    inputs[index, :length] = torch.randint(1, 31, (length,))

with torch.no_grad():
    expected = model(inputs).numpy()

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
session = ort.InferenceSession(
    str(model_path),
    providers=["CPUExecutionProvider"],
)

# Vérifie que plusieurs tailles de batch fonctionnent.
for batch_size in (1, 3, 10):
    actual = session.run(
        ["p_anomaly"],
        {"event_ids": inputs[:batch_size].numpy()},
    )[0]
    assert actual.shape == (batch_size,)
    error = float(np.max(np.abs(actual - expected[:batch_size])))
    print(f"Batch {batch_size} : écart maximal = {error:.8f}")
    assert error < 1e-4, f"Écart trop élevé : {error}"

# Ces mêmes entrées et résultats serviront au test navigateur.
fixtures = {
    "event_ids": inputs.tolist(),
    "p_anomaly": expected.tolist(),
    "tolerance": 1e-4,
}

(MODEL_DIR / "spike_cases.json").write_text(
    json.dumps(fixtures, indent=2),
    encoding="utf-8",
)

metadata = {
    "threshold": 0.5,
    "model": "bilstm",
    "version": "spike",
    "trained_on": "none-random-weights",
    "val_macro_f1": None,
}

(MODEL_DIR / "detector.meta.json").write_text(
    json.dumps(metadata, indent=2),
    encoding="utf-8",
)

print(f"Modèle exporté : {model_path}")
print(f"Taille : {model_path.stat().st_size / 1024:.1f} Ko")
print("Parité PyTorch / ONNX Runtime Python : OK")
print("Modèle jouet non entraîné : scores sans valeur prédictive.")