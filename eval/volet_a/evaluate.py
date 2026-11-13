"""SCRUM-44 — evaluation C4/C7 du volet A.

Preparation (SANS ouvrir le test) :
    python -m eval.volet_a.evaluate --preflight

Campagne finale UNIQUE (apres revue des artefacts, du protocole et du navigateur) :
    python -m eval.volet_a.evaluate --run-final \
        --int8-model chemin/du/modele_int8.onnx \
        --confirm-test-once SCRUM-44-TEST-UNIQUE

Le mode --preflight n'appelle jamais load_split('test') et ne lit pas les
contenus de splits.csv. La campagne finale cree un marqueur irrevocable AVANT
l'ouverture du test, pour empecher toute reevaluation accidentelle.

IMPORTANT : la parite dans un VRAI navigateur (ONNX Runtime Web/WASM), les
mesures cache/reseau et le banc de latence navigateur demandent un harness JS
supplementaire. Ils NE SONT PAS simules par ce script Python.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import numpy as np

from teamai.paths import MODEL_DIR, PREPROCESSED, RESULTS, ROOT, RUNS, SPLITS, WEB_PUBLIC


EXPECTED_FP32_SHA = "ab98e8c45ef398c5c2ad13e05503fd94c5f13453daedda32d61c3ae43611a5ad"
EXPECTED_SPLITS_SHA = "f504592cb7ac13b8b7e5d532a336b4e3641ec441a863c5efafd164faa2a43f22"
EXPECTED_THRESHOLD = 0.40814146399497986
EXPOSED = {
    "blk_-1000014584150379967",
    "blk_-100004553717737248",
    "blk_-1001299764911418845",
}
FEATURES = [f"E{i}" for i in range(1, 30)]
MODEL_FP32 = MODEL_DIR / "detector.onnx"
MODEL_META = MODEL_DIR / "detector.meta.json"
VOCAB_PATH = WEB_PUBLIC / "vocab.json"
MARKER = RESULTS / "SCRUM-44-test-opened.json"
REPORT = RESULTS / "volet_a.md"
FIG_DIR = ROOT / "docs" / "rapport" / "figures"


def file_sha256(path: Path) -> str:
    """Calcule SHA-256 sans charger tout le fichier en memoire."""
    sha = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def read_json(path: Path) -> dict:
    """Charge un fichier JSON strict."""
    def reject_constant(value):
        """Refuse NaN et Infinity, absents du JSON strict."""
        raise ValueError(f"JSON non strict : {value}")
    return json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_constant)


def metadata_check() -> tuple[dict, dict]:
    """Verifie les artefacts figes SANS ouvrir les donnees de test."""
    for p in (MODEL_FP32, MODEL_META, VOCAB_PATH):
        if not p.is_file():
            raise FileNotFoundError(str(p))
    meta = read_json(MODEL_META)
    vocab = read_json(VOCAB_PATH)
    if file_sha256(MODEL_FP32) != EXPECTED_FP32_SHA:
        raise ValueError("Empreinte du modele FP32 differente du modele SCRUM-62 fige.")
    if meta.get("model_sha256") != EXPECTED_FP32_SHA:
        raise ValueError("SHA du modele incoherent dans detector.meta.json.")
    if file_sha256(VOCAB_PATH) != meta.get("vocab_sha256"):
        raise ValueError("Vocabulaire modifie depuis l'entrainement.")
    if meta.get("splits_sha256") != EXPECTED_SPLITS_SHA:
        raise ValueError("Empreinte C4 non conforme dans les metadonnees.")
    if meta.get("threshold") != EXPECTED_THRESHOLD:
        raise ValueError("Seuil SCRUM-62 modifie : evaluation interdite.")
    if any(vocab.get(k) != v for k, v in (("max_len", 50), ("pad_id", 0), ("unk_id", 30))):
        raise ValueError("Contrat C2 incompatible.")
    event_ids = {name: item["id"] for name, item in vocab["events"].items()}
    if event_ids != {f"E{i}": i for i in range(1, 30)}:
        raise ValueError("Mapping E1-E29 non conforme au contrat C2.")
    return meta, event_ids


def ort_session(path: Path):
    """Ouvre un modele ONNX et controle la signature C3 par un cas fictif."""
    import onnxruntime as ort
    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    inp = session.get_inputs()
    out = session.get_outputs()
    if len(inp) != 1 or inp[0].name != "event_ids" or inp[0].type != "tensor(int64)":
        raise ValueError(f"Entree C3 incorrecte : {path}")
    if len(out) != 1 or out[0].name != "p_anomaly" or out[0].type != "tensor(float)":
        raise ValueError(f"Sortie C3 incorrecte : {path}")
    if inp[0].shape[-1] != 50:
        raise ValueError(f"Sequence C2 incompatible : {path}")
    dummy = np.asarray([[5, 22, 5, 11] + [0] * 46], dtype=np.int64)
    score = np.asarray(session.run(["p_anomaly"], {"event_ids": dummy})[0]).reshape(-1)
    if len(score) != 1 or not np.isfinite(score).all() or not ((0 <= score) & (score <= 1)).all():
        raise ValueError(f"Predictions C3 invalides : {path}")
    return session


def preflight(int8_path: Path, *, require_all: bool = False) -> dict:
    """Verifie les prerequis en s'interdisant les donnees de test."""
    meta, events = metadata_check()
    fp32 = ort_session(MODEL_FP32)
    del fp32
    status = {
        "fp32_sha256": EXPECTED_FP32_SHA,
        "threshold": meta["threshold"],
        "vocab_events": len(events),
        "int8_path": str(int8_path),
        "int8_ready": False,
        "data_ready": False,
        "python_dependencies_ready": False,
    }
    if int8_path.is_file():
        if int8_path.resolve() == MODEL_FP32.resolve():
            raise ValueError("Le modele INT8 doit etre un artefact distinct du FP32.")
        import onnx
        model = onnx.load(str(int8_path))
        onnx.checker.check_model(model)
        quantized_ops = {n.op_type for n in model.graph.node if "Integer" in n.op_type or "Quant" in n.op_type or "QLinear" in n.op_type}
        if not quantized_ops:
            raise ValueError("Le modele INT8 ne contient aucune operation quantifiee identifiable.")
        int8 = ort_session(int8_path)
        del int8
        status["int8_ready"] = True
        status["int8_sha256"] = file_sha256(int8_path)
        status["quantized_ops"] = sorted(quantized_ops)
    paths = [SPLITS / "splits.csv", PREPROCESSED / "Event_traces.csv", PREPROCESSED / "Event_occurrence_matrix.csv"]
    status["missing_data_paths"] = [str(p) for p in paths if not p.is_file()]
    status["data_ready"] = not status["missing_data_paths"]
    status["missing_dependencies"] = [p for p in ("sklearn", "pandas", "matplotlib", "onnx", "onnxruntime") if importlib.util.find_spec(p) is None]
    status["python_dependencies_ready"] = not status["missing_dependencies"]
    status["old_run_marker_exists"] = MARKER.exists()
    status["old_report_exists"] = REPORT.exists()
    print(json.dumps(status, indent=2, ensure_ascii=False))
    if require_all and (not status["int8_ready"] or not status["data_ready"] or not status["python_dependencies_ready"] or status["old_run_marker_exists"] or status["old_report_exists"]):
        raise RuntimeError("Prerequis non satisfaits. Test NON ouvert.")
    return status


def encode_rows(frames, event_ids: dict) -> np.ndarray:
    """Applique exactement l'encodage Python C2 pour les trois modeles."""
    from teamai.data.loader import encode
    rows = [encode(events, event_ids, max_len=50) for events in frames["events"]]
    return np.asarray(rows, dtype=np.int64)


def infer_onnx(session, x: np.ndarray, batch_size: int = 512) -> tuple[np.ndarray, dict]:
    """Calcule les scores en lots et mesure le debit sur CPU."""
    results = []
    t0 = time.perf_counter()
    for offset in range(0, len(x), batch_size):
        batch = x[offset:offset + batch_size]
        result = np.asarray(session.run(["p_anomaly"], {"event_ids": batch})[0]).reshape(-1)
        if len(result) != len(batch) or not np.isfinite(result).all() or ((result < 0) | (result > 1)).any():
            raise RuntimeError("Prediction ONNX invalide ; evaluation interrompue.")
        results.append(result)
    seconds = time.perf_counter() - t0
    return np.concatenate(results), {"seconds_inference": seconds, "blocks_per_second": len(x) / seconds if seconds else None, "batch_size": batch_size}


def confusion(y: np.ndarray, scores: np.ndarray, threshold: float) -> dict:
    """Retourne les metriques de classification binaire (labels 0/1)."""
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
    predicted = (scores >= threshold).astype(np.int64)
    tn, fp, fn, tp = confusion_matrix(y, predicted, labels=[0, 1]).ravel()
    return {
        "n_blocks": int(len(y)), "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
        "accuracy": float(accuracy_score(y, predicted)),
        "precision_anomaly": float(precision_score(y, predicted, zero_division=0)),
        "recall_anomaly": float(recall_score(y, predicted, zero_division=0)),
        "macro_f1": float(f1_score(y, predicted, average="macro", zero_division=0)),
    }


def strict_unseen(series) -> np.ndarray:
    """Convertit le booleen C4 sans assimiler une valeur incorrecte a False."""
    value = series.astype(str).str.lower().str.strip()
    if not value.isin(("true", "false", "1", "0")).all():
        raise ValueError("Colonne unseen_seq invalide dans C4.")
    return value.isin(("true", "1")).to_numpy()


def git_commit() -> str:
    """Renvoie le commit local de l'evaluation."""
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip()


def new_run_dir(name: str) -> Path:
    """C7 : dossier neuf horodate, sans ecrasement."""
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S_%fZ")
    path = RUNS / f"{stamp}_{uuid4().hex[:8]}_{name}"
    path.mkdir(parents=True, exist_ok=False)
    return path


def write_json(path: Path, obj: dict) -> None:
    """Ecrit un JSON strict, lisible par les outils de suivi."""
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def run_model(name: str, test, scores: np.ndarray, threshold: float, details: dict, hashes: dict) -> tuple[dict, Path]:
    """Enregistre predictions et metriques C7 du modele sur trois sous-ensembles."""
    unseen = strict_unseen(test["unseen_seq"])
    not_exposed = ~test["BlockId"].isin(EXPOSED).to_numpy()
    groups = {"test_complet": np.ones(len(test), dtype=bool), "unseen_seq": unseen, "sans_3_blocs_exposes": not_exposed}
    y = test["label"].to_numpy(dtype=np.int64)
    metrics = {key: confusion(y[mask], scores[mask], threshold) for key, mask in groups.items()}
    run = new_run_dir(f"SCRUM-44_{name}")
    with (run / "predictions.jsonl").open("x", encoding="utf-8") as dest:
        for idx, row in enumerate(test.itertuples(index=False)):
            # C7 exige ces quatre champs ; les autres sont des informations de traçabilite.
            record = {"BlockId": str(row.BlockId), "label": int(row.label), "p_anomaly": float(scores[idx]), "split": "test", "unseen_seq": bool(unseen[idx])}
            dest.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
    config = {"ticket": "SCRUM-44", "model": name, "threshold": threshold, "commit": git_commit(), "python": platform.python_version(), **hashes, **details}
    write_json(run / "config.json", config)
    write_json(run / "metrics.json", metrics)
    return metrics, run



def write_browser_parity_inputs(run: Path, test, x: np.ndarray, fp32_scores: np.ndarray, int8_scores: np.ndarray) -> None:
    """Fige les entrees du test une fois pour le futur harness navigateur.

    Le navigateur consomme cet export C2, sans rappeler load_split('test').
    Les labels ne sont pas necessaires a la verification numerique.
    """
    if len(test) != len(x) or len(test) != len(fp32_scores) or len(test) != len(int8_scores):
        raise ValueError("Longueurs incompatibles pour la parite navigateur.")
    path = run / "browser_parity_inputs.jsonl"
    with path.open("x", encoding="utf-8") as dest:
        for block_id, ids, fp32, int8 in zip(test["BlockId"], x, fp32_scores, int8_scores):
            record = {
                "BlockId": str(block_id),
                "event_ids": ids.tolist(),
                "p_anomaly_fp32_python": float(fp32),
                "p_anomaly_int8_python": float(int8),
            }
            dest.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")


def save_figures(name: str, metrics: dict) -> None:
    """Dessine les matrices de confusion, sans alterer les predictions."""
    import matplotlib.pyplot as plt
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for group, m in metrics.items():
        fig_path = FIG_DIR / f"scrum44_{name}_{group}_confusion.png"
        if fig_path.exists():
            raise FileExistsError(f"Figure deja presente (run final unique) : {fig_path}")
        mat = np.array([[m["tn"], m["fp"]], [m["fn"], m["tp"]]])
        fig, ax = plt.subplots(figsize=(5.2, 4.6))
        ax.imshow(mat, cmap="Blues")
        for (i, j), val in np.ndenumerate(mat):
            ax.text(j, i, str(val), ha="center", va="center", color="black")
        ax.set_xticks([0, 1], ["Normal", "Anomalie"])
        ax.set_yticks([0, 1], ["Normal", "Anomalie"])
        ax.set_xlabel("Prediction")
        ax.set_ylabel("Verite")
        ax.set_title(f"{name} — {group}")
        fig.tight_layout()
        fig.savefig(fig_path, dpi=160)
        plt.close(fig)


def write_report(result: dict, runs: dict, details: dict) -> None:
    """Produit le resume versionne et marque les mesures non encore realisees."""
    lines = [
        "# SCRUM-44 — Evaluation finale du volet A",
        "",
        "**Protocole :** C4-bloc, test officiel (campagne unique), contrats C3/C7.",
        f"**Seuil BiLSTM figé SCRUM-62 :** `{EXPECTED_THRESHOLD}`.",
        "**Historique :** le fichier SCRUM-24-baseline-results.json contenait deja des resultats du test (commit b77b1a2, 12/10/2026). Ce precedent est declare et n'a pas servi au reglage de l'evaluation actuelle.",
        "",
        "## Metriques",
        "",
        "| Modele | Population | N | Precision anomalie | Rappel anomalie | Macro-F1 | TN | FP | FN | TP |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for model, per_group in result.items():
        for pop, m in per_group.items():
            lines.append(f"| {model} | {pop} | {m['n_blocks']} | {m['precision_anomaly']:.6f} | {m['recall_anomaly']:.6f} | {m['macro_f1']:.6f} | {m['tn']} | {m['fp']} | {m['fn']} | {m['tp']} |")
    lines += ["", "## Artefacts C7", ""]
    for model, path in runs.items():
        lines.append(f"- `{model}` : `{path.relative_to(ROOT).as_posix()}` (`predictions.jsonl`, `metrics.json`, `config.json`).")
    lines += [
        "", "## Performance CPU (ONNX Runtime Python)", "",
        f"- FP32 : {details['fp32_perf']}",
        f"- INT8 : {details['int8_perf']}",
        "", "## Parite navigateur et performance web — A COMPLETER", "",
        "- Les entrees figees `browser_parity_inputs.jsonl` sont disponibles dans le run FP32 pour effectuer la parite sur tout le test SANS le relire.",
        "- Parite **sur l'ensemble du test** entre ONNX Runtime Python et ONNX Runtime Web/WASM : **NON MESUREE** par ce script.",
        "- Temps de premier chargement, temps avec cache navigateur, taille des artefacts web, debit en lot navigateur : **NON MESURES**.",
        "- Le benchmark CPU Python ci-dessus ne peut pas etre presente comme une mesure navigateur.",
        "", "## Analyse d'erreurs — A COMMENTER", "",
        "- Selectionner et commenter au moins dix cas FP/FN, en recoupant les `predictions.jsonl` et les sequences brutes.",
        "- Ne pas inferer une cause de panne a partir d'un simple label d'anomalie.",
        "", "## Provenance et limitations", "",
        f"- Empreinte FP32 : `{EXPECTED_FP32_SHA}`.",
        f"- Empreinte des splits : `{EXPECTED_SPLITS_SHA}`.",
        "- Les trois blocs exposes historiquement ont ete exclus uniquement de la population `sans_3_blocs_exposes`.",
        "- L'etape navigateur et la revue Bachar restent indispensables avant de considerer SCRUM-44 termine.",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def run_final(int8_path: Path) -> None:
    """Execute une unique evaluation apres les controles, sans re-selection du seuil."""
    preflight(int8_path, require_all=True)
    if MARKER.exists() or REPORT.exists():
        raise RuntimeError("Campagne SCRUM-44 deja ouverte / rapport existant.")
    meta, events = metadata_check()
    # Verifier les splits par hash sans utiliser les labels du test pour ajuster quoi que ce soit.
    actual_splits_hash = file_sha256(SPLITS / "splits.csv")
    if actual_splits_hash != EXPECTED_SPLITS_SHA:
        raise ValueError("splits.csv non officiel. Test non ouvert pour evaluation.")

    # Preparations sans test AVANT le verrou irrevocable : toutes les
    # dependances, les donnees train et les comptages doivent etre valides.
    from teamai.data.splits import load_split
    import pandas as pd
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    import matplotlib
    matplotlib.use("Agg")

    train = load_split("train")
    if len(train) != 402542 or train["BlockId"].duplicated().any():
        raise RuntimeError("Split train non conforme. Test NON ouvert.")
    counts = pd.read_csv(PREPROCESSED / "Event_occurrence_matrix.csv", usecols=["BlockId", *FEATURES])
    if counts["BlockId"].duplicated().any():
        raise ValueError("BlockId dupliques dans les comptages. Test NON ouvert.")
    train_counts = train[["BlockId", "label"]].merge(counts, on="BlockId", how="left", validate="one_to_one")
    if train_counts[FEATURES].isna().any().any():
        raise ValueError("Comptages train manquants. Test NON ouvert.")
    baseline = make_pipeline(StandardScaler(), LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42))
    baseline.fit(train_counts[FEATURES], train_counts["label"].astype(int))
    fp32_session = ort_session(MODEL_FP32)
    int8_session = ort_session(int8_path)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for model_name in ("baseline", "bilstm_fp32", "bilstm_int8"):
        for group_name in ("test_complet", "unseen_seq", "sans_3_blocs_exposes"):
            fig_path = FIG_DIR / f"scrum44_{model_name}_{group_name}_confusion.png"
            if fig_path.exists():
                raise FileExistsError(f"Figure deja presente avant ouverture du test : {fig_path}")
    RESULTS.mkdir(parents=True, exist_ok=True)
    RUNS.mkdir(parents=True, exist_ok=True)
    # Le verrou est pose avant le SEUL appel a load_split('test').
    with MARKER.open("x", encoding="utf-8") as dest:
        json.dump({"ticket": "SCRUM-44", "opened_at_utc": datetime.now(timezone.utc).isoformat(), "git_commit": git_commit(), "fp32_sha256": EXPECTED_FP32_SHA, "int8_sha256": file_sha256(int8_path), "splits_sha256": actual_splits_hash}, dest, indent=2)
        dest.write("\n")

    test = load_split("test")  # POINT D'OUVERTURE UNIQUE DU TEST OFFICIEL
    if len(test) != 86260 or len(train) != 402542 or test["BlockId"].duplicated().any():
        raise RuntimeError("Effectifs C4 inattendus. Campagne interrompue, ne pas relancer sans revue.")
    test_counts = test[["BlockId"]].merge(counts, on="BlockId", how="left", validate="one_to_one")
    if test_counts[FEATURES].isna().any().any():
        raise ValueError("Comptages test manquants : evaluation interrompue sans nouvelle ouverture.")
    t0 = time.perf_counter()
    baseline_scores = baseline.predict_proba(test_counts[FEATURES])[:, 1]
    baseline_seconds = time.perf_counter() - t0

    x = encode_rows(test, events)
    fp32_scores, fp32_perf = infer_onnx(fp32_session, x)
    int8_scores, int8_perf = infer_onnx(int8_session, x)
    all_scores = {"baseline": (baseline_scores, 0.5), "bilstm_fp32": (fp32_scores, EXPECTED_THRESHOLD), "bilstm_int8": (int8_scores, EXPECTED_THRESHOLD)}
    results, run_paths = {}, {}
    for name, (scores, threshold) in all_scores.items():
        hashes = {"splits_sha256": actual_splits_hash, "fp32_sha256": EXPECTED_FP32_SHA, "int8_sha256": file_sha256(int8_path)}
        model_details = {"baseline": "StandardScaler + LogisticRegression(balanced, max_iter=1000, seed=42), features E1-E29", "bilstm_fp32": str(MODEL_FP32.relative_to(ROOT)), "bilstm_int8": str(int8_path)}
        metrics, path = run_model(name, test, np.asarray(scores), threshold, {"model_spec": model_details[name]}, hashes)
        save_figures(name, metrics)
        results[name] = metrics
        run_paths[name] = path
    write_browser_parity_inputs(run_paths["bilstm_fp32"], test, x, fp32_scores, int8_scores)
    write_report(results, run_paths, {"fp32_perf": fp32_perf, "int8_perf": int8_perf, "baseline_seconds": baseline_seconds})
    print(f"Campagne enregistree. Rapport : {REPORT}")
    print("ATTENTION : parite navigateur, latence cache/reseau et commentaires humains restent a completer.")


def main() -> None:
    """CLI securisee : preflight par defaut, test uniquement sur confirmation explicite."""
    parser = argparse.ArgumentParser(description="SCRUM-44 — evaluation finale du volet A")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preflight", action="store_true", help="Controle statique uniquement (defaut).")
    mode.add_argument("--run-final", action="store_true", help="Ouvre le test UNE seule fois.")
    parser.add_argument("--int8-model", type=Path, default=MODEL_DIR / "detector.int8.onnx")
    parser.add_argument("--confirm-test-once", default="", help="Confirmation obligatoire avant la campagne finale.")
    args = parser.parse_args()
    int8_path = args.int8_model.expanduser().resolve()
    if args.run_final:
        if args.confirm_test_once != "SCRUM-44-TEST-UNIQUE":
            parser.error("La campagne finale exige --confirm-test-once SCRUM-44-TEST-UNIQUE.")
        run_final(int8_path)
    else:
        if args.confirm_test_once:
            parser.error("--confirm-test-once est reserve a --run-final.")
        preflight(int8_path)


if __name__ == "__main__":
    main()
