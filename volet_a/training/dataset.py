"""SCRUM-25 : préparation des splits officiels pour le BiLSTM."""

import json

import torch

from teamai.data.loader import encode
from teamai.data.splits import load_split
from teamai.paths import WEB_PUBLIC


def load_datasets():
    """Charge train et validation, encode selon C2 et repère les séquences inédites."""
    vocab_path = WEB_PUBLIC / "vocab.json"
    vocab = json.loads(vocab_path.read_text(encoding="utf-8"))

    if (
        vocab["max_len"] != 50
        or vocab["pad_id"] != 0
        or vocab["unk_id"] != 30
    ):
        raise ValueError("Vocabulaire incompatible avec le contrat C2.")

    event_ids = {
        event: specification["id"]
        for event, specification in vocab["events"].items()
    }

    if event_ids != {f"E{i}": i for i in range(1, 30)}:
        raise ValueError("Les indices E1 à E29 ne respectent pas C2.")

    datasets = {}

    for name in ("train", "val"):
        print(f"Chargement de {name}...", flush=True)
        frame = load_split(name)

        if frame.empty:
            raise ValueError(f"Le split {name} est vide.")

        encoded = [
            encode(events, event_ids, max_len=50)
            for events in frame["events"]
        ]

        datasets[name] = {
            "frame": frame,
            "x": torch.tensor(encoded, dtype=torch.int64),
            "y": torch.tensor(
                frame["label"].to_numpy(),
                dtype=torch.float32,
            ),
        }

        truncated = sum(len(events) > 50 for events in frame["events"])
        print(
            f"{name} : {len(frame):,} blocs ; "
            f"{int(frame['label'].sum()):,} anomalies ; "
            f"{truncated:,} séquences tronquées.",
            flush=True,
        )

    train_sequences = set(
        datasets["train"]["frame"]["events"].map(tuple)
    )

    datasets["val"]["unseen"] = (
        ~datasets["val"]["frame"]["events"].map(tuple).isin(train_sequences)
    ).to_numpy()

    print(
        "Séquences de validation absentes du train :",
        int(datasets["val"]["unseen"].sum()),
        flush=True,
    )

    return datasets


if __name__ == "__main__":
    load_datasets()