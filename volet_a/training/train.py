"""SCRUM-25 : entraînement sur train et sélection sur validation uniquement."""

import argparse
import hashlib
import json
import platform
import random
import subprocess
import time
import uuid
from datetime import datetime, timezone
import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from eval.metrics import evaluate_binary
from teamai.paths import PREPROCESSED, RUNS, SPLITS, TRAINING, VOLET_A_RESULTS, WEB_PUBLIC
from volet_a.training.bilstm import BiLSTM
from volet_a.training.dataset import load_datasets


def write_json(path, value):
    """Écrit un JSON strict en UTF-8."""
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def file_hash(path):
    """Calcule l'empreinte SHA-256 d'un fichier."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_output(*args):
    """Capture une information Git pour tracer l'expérience."""
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True, encoding="utf-8"
    ).strip()


def select_threshold(labels, scores):
    """Choisit le seuil maximisant la macro-F1 sur la validation."""
    best = None
    for threshold in np.linspace(0.01, 0.99, 99):
        predicted = scores >= threshold
        positive = labels == 1

        tp = int(np.sum(predicted & positive))
        fp = int(np.sum(predicted & ~positive))
        fn = int(np.sum(~predicted & positive))
        tn = int(np.sum(~predicted & ~positive))

        positive_f1 = 2 * tp / max(2 * tp + fp + fn, 1)
        negative_f1 = 2 * tn / max(2 * tn + fp + fn, 1)
        macro_f1 = (positive_f1 + negative_f1) / 2

        # En cas d'égalité, préférer le seuil le plus proche de 0,5.
        candidate = (macro_f1, -abs(float(threshold) - 0.5))
        if best is None or candidate > best[0]:
            best = (candidate, float(threshold))

    return best[1], best[0][0]


def predict(model, inputs, batch_size):
    """Effectue l'inférence CPU sans gradients."""
    model.eval()
    outputs = []
    with torch.inference_mode():
        for batch in inputs.split(batch_size):
            outputs.append(model(batch).numpy())
    scores = np.concatenate(outputs)

    if not np.isfinite(scores).all():
        raise ValueError("Scores de validation non finis.")

    return scores


def main():
    """Entraîne, sélectionne et enregistre un run neuf sans consulter le test."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=["officiel"], default="officiel")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--lr", type=float, default=0.001)
    args = parser.parse_args()

    if min(args.epochs, args.batch_size, args.threads) < 1 or args.lr <= 0:
        parser.error("Les paramètres numériques doivent être positifs.")

    torch.set_num_threads(args.threads)
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.use_deterministic_algorithms(True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run = RUNS / f"{timestamp}_{uuid.uuid4().hex[:8]}_bilstm"
    run.mkdir(parents=True, exist_ok=False)

    config = {
        "ticket": "SCRUM-25",
        "model": "BiLSTM",
        "embedding_dim": 16,
        "hidden_size": 32,
        "device": "cpu",
        "machine": platform.platform(),
        "torch_version": str(torch.__version__),
        "parameters": vars(args),
        "git_commit": git_output("rev-parse", "HEAD"),
        "git_status": git_output("status", "--short"),
        "source_hashes": {
            name: file_hash(TRAINING / name)
            for name in ("dataset.py", "bilstm.py", "train.py")
        },
        "splits_sha256": file_hash(SPLITS / "splits.csv"),
        "data_sha256": file_hash(PREPROCESSED / "Event_traces.csv"),
        "vocab_sha256": file_hash(WEB_PUBLIC / "vocab.json"),
        "threshold_selection": "macro-F1 validation, grille 0.01 à 0.99",
        "test_used": False,
    }
    write_json(run / "config.json", config)
    print(f"Run : {run}", flush=True)

    datasets = load_datasets()
    train = datasets["train"]
    val = datasets["val"]

    positives = float(train["y"].sum())
    negatives = len(train["y"]) - positives
    if positives == 0 or negatives == 0:
        raise ValueError("Les deux classes doivent être présentes dans train.")

    model = BiLSTM()
    loss_function = nn.BCEWithLogitsLoss(
        pos_weight=torch.tensor(negatives / positives, dtype=torch.float32)
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    generator = torch.Generator().manual_seed(args.seed)
    batches = DataLoader(
        TensorDataset(train["x"], train["y"]),
        batch_size=args.batch_size,
        shuffle=True,
        generator=generator,
        num_workers=0,
    )

    labels = val["y"].numpy().astype(int)
    history = []
    best_f1 = -1.0
    started = time.perf_counter()

    for epoch in range(1, args.epochs + 1):
        model.train()
        total_loss = 0.0
        epoch_started = time.perf_counter()

        for step, (inputs, targets) in enumerate(batches, start=1):
            optimizer.zero_grad(set_to_none=True)
            loss = loss_function(model.logits(inputs), targets)

            if not torch.isfinite(loss):
                raise ValueError("Perte non finie : entraînement interrompu.")

            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            total_loss += loss.item() * len(inputs)

            if step % 100 == 0:
                print(
                    f"Époque {epoch}/{args.epochs} — "
                    f"batch {step}/{len(batches)}",
                    flush=True,
                )

        scores = predict(model, val["x"], args.batch_size)
        threshold, macro_f1 = select_threshold(labels, scores)

        record = {
            "epoch": epoch,
            "train_loss": total_loss / len(train["y"]),
            "val_macro_f1": macro_f1,
            "threshold": threshold,
            "seconds": time.perf_counter() - epoch_started,
        }
        history.append(record)
        write_json(run / "history.json", history)
        print(json.dumps(record), flush=True)

        if macro_f1 > best_f1:
            best_f1 = macro_f1
            torch.save(
                {
                    "state_dict": model.state_dict(),
                    "embedding_dim": 16,
                    "hidden_size": 32,
                    "epoch": epoch,
                    "threshold": threshold,
                    "val_macro_f1": macro_f1,
                },
                run / "best.pt",
            )

    checkpoint = torch.load(
        run / "best.pt", map_location="cpu", weights_only=True
    )
    model.load_state_dict(checkpoint["state_dict"])
    scores = predict(model, val["x"], args.batch_size)
    predictions = (scores >= checkpoint["threshold"]).astype(int)

    metrics = {
        "split": "val",
        "test_used": False,
        "n_blocks": len(labels),
        "best_epoch": checkpoint["epoch"],
        "threshold": checkpoint["threshold"],
        "training_and_validation_seconds": time.perf_counter() - started,
        "validation": evaluate_binary(labels, predictions),
    }

    for name, mask in (
        ("unseen", val["unseen"]),
        ("known", ~val["unseen"]),
    ):
        metrics[name] = (
            {
                "n_blocks": int(mask.sum()),
                **evaluate_binary(
                    labels[mask], predictions[mask], name=f"Validation {name}"
                ),
            }
            if mask.any()
            else None
        )

    baseline_path = VOLET_A_RESULTS / "SCRUM-24-baseline-results.json"
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    metrics["baseline_reference"] = {
        "file_sha256": file_hash(baseline_path),
        "validation": baseline["validation"],
        "unseen": baseline["validation_by_sequence"]["unseen"],
        "note": "Résultats publiés par Nassim ; baseline non réentraînée ici.",
    }
    write_json(run / "metrics.json", metrics)

    with (run / "predictions.jsonl").open("w", encoding="utf-8") as stream:
        for block_id, label, score in zip(
            val["frame"]["BlockId"], labels, scores
        ):
            stream.write(
                json.dumps(
                    {
                        "BlockId": str(block_id),
                        "label": int(label),
                        "p_anomaly": float(score),
                        "split": "val",
                    },
                    allow_nan=False,
                ) + "\n"
            )

    print(f"\nTerminé. Résultats et meilleur modèle : {run}", flush=True)
    print("Le test officiel n'a pas été évalué.")
    print("Le modèle du site n'a pas encore été remplacé.")


if __name__ == "__main__":
    main()