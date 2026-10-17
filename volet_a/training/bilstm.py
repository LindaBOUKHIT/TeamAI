"""SCRUM-25 : BiLSTM binaire compatible avec l'export ONNX C3."""

import torch
from torch import nn


class BiLSTM(nn.Module):
    """Encode les événements et classe une séquence HDFS."""

    def __init__(self, embedding_dim=16, hidden_size=32):
        """Initialise l'embedding, le BiLSTM et la couche de classification."""
        super().__init__()
        self.embedding = nn.Embedding(
            num_embeddings=31,
            embedding_dim=embedding_dim,
            padding_idx=0,
        )
        self.lstm = nn.LSTM(
            input_size=embedding_dim,
            hidden_size=hidden_size,
            batch_first=True,
            bidirectional=True,
        )
        self.classifier = nn.Linear(hidden_size * 2, 1)

    def logits(self, event_ids):
        """Retourne les logits en ignorant le padding lors de l'agrégation."""
        embedded = self.embedding(event_ids)
        outputs, _ = self.lstm(embedded)

        # Agrégation des positions contenant de vrais événements.
        mask = (event_ids != 0).unsqueeze(-1).to(outputs.dtype)
        pooled = (outputs * mask).sum(dim=1)
        pooled = pooled / mask.sum(dim=1).clamp(min=1)

        return self.classifier(pooled).squeeze(-1)

    def forward(self, event_ids):
        """Retourne p_anomaly float32 de forme [batch], conformément à C3."""
        return torch.sigmoid(self.logits(event_ids))


if __name__ == "__main__":
    model = BiLSTM().eval()

    example = torch.zeros((3, 50), dtype=torch.int64)
    example[:, :4] = torch.tensor([5, 22, 5, 11])

    with torch.no_grad():
        scores = model(example)

    assert scores.shape == (3,)
    assert torch.isfinite(scores).all()
    assert ((scores >= 0) & (scores <= 1)).all()

    print("Architecture OK : entrée [3, 50], sortie [3].")
    print("Nombre de paramètres :", sum(p.numel() for p in model.parameters()))
    print("Poids initialisés ; entraînement pas encore lancé.")