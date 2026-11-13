"""Mesure C7 sur validation ; --mock fonctionne sans modèle ni corpus.

Installation réelle facultative : ``pip install laya``. La RSS est échantillonnée.
"""
import argparse
import csv
import hashlib
from importlib.metadata import PackageNotFoundError, version
import json
import math
from pathlib import Path
import platform
import subprocess
import threading
from datetime import datetime, timezone
from uuid import uuid4

from teamai import paths
from teamai.contracts import validate_answer
from volet_b.agents.laya_gate import LayaGate, load_config


def checked_path(value, allow_test_name=False):
    """Refuse les chemins réservés avant ouverture, y compris leurs alias résolus."""
    resolved = paths.resolve_path(value)
    for candidate in (Path(value).expanduser(), resolved):
        parts = [part.casefold() for part in candidate.parts]
        if ".secrets" in parts or (not allow_test_name and "test" in candidate.name.casefold()) or any(
                a == "eval" and b == "volet_b" for a, b in zip(parts, parts[1:])):
            raise ValueError("Chemin réservé interdit : test, eval/volet_b ou .secrets.")
    if resolved == paths.EVAL_VOLET_B.resolve() or paths.EVAL_VOLET_B.resolve() in resolved.parents:
        raise ValueError("Chemin eval/volet_b réservé interdit.")
    return resolved


def read_responses(path):
    """Vérifie toutes les lignes avant sélection, même celles au-delà de --n."""
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict) or row.get("split") not in ("val", "validation"):
            raise ValueError(f"Ligne {number} : seul le split val/validation est autorisé.")
        if not isinstance(row.get("block_id"), str) or not row["block_id"]:
            raise ValueError(f"Ligne {number} : block_id non vide attendu.")
        if not isinstance(row.get("events"), list) or not all(isinstance(e, str) for e in row["events"]):
            raise ValueError(f"Ligne {number} : liste de codes events attendue.")
        errors = validate_answer(row.get("answer"))
        if errors:
            raise ValueError(f"Ligne {number} : réponse C5 invalide : {errors}")
        rows.append(row)
    if len({r["block_id"] for r in rows}) != len(rows):
        raise ValueError("Identifiants de blocs dupliqués dans les réponses.")
    return rows


def mock_predict(state, questions):
    """Produit des probabilités stables sans valeur scientifique et sans modèle."""
    answers = {}
    for name, question in questions.items():
        digest = hashlib.sha256((state + question["instructions"]).encode("utf-8")).digest()
        answers[name] = {"noul": (20, 50, 80)[digest[0] % 3] / 100}
    return {"answers": answers}


class PeakRSS:
    """Échantillonne la RSS du processus si psutil est disponible."""

    def __init__(self):
        """Prépare une sonde optionnelle et son signal d'arrêt."""
        try:
            import psutil
        except ImportError:
            self.process = None
        else:
            self.process = psutil.Process()
        self.peak = None
        self.stop = threading.Event()
        self.thread = None

    def sample(self):
        """Conserve la valeur maximale observée, en octets."""
        if self.process is not None:
            self.peak = max(self.peak or 0, self.process.memory_info().rss)

    def run(self):
        """Relève la mémoire toutes les vingt millisecondes."""
        while not self.stop.wait(0.02):
            self.sample()

    def __enter__(self):
        """Prend une mesure initiale puis lance le suivi optionnel."""
        self.sample()
        if self.process is not None:
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()
        return self

    def __exit__(self, *exc):
        """Arrête le suivi et prend une dernière mesure, même après erreur."""
        self.stop.set()
        if self.thread is not None:
            self.thread.join()
        self.sample()


def by_label(predictions):
    """Résume la probabilité d'anomalie de Laya par label officiel du bloc, s'il est fourni."""
    groups = {}
    for p in predictions:
        if p.get("label") is not None:
            groups.setdefault(str(p["label"]), []).append(p["info"]["anomaly_probability"])
    return {label: {"n": len(v), "mean": sum(v) / len(v), "min": min(v), "max": max(v)}
            for label, v in sorted(groups.items())}


def input_hash(path):
    """Calcule l'empreinte des octets d'une entrée."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_unsupported(path, rows):
    """Valide les annotations humaines selon les indices d'origine, base zéro."""
    annotations = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(annotations, list):
        raise ValueError("Les annotations humaines doivent former une liste.")
    blocks = {row["block_id"]: row for row in rows}
    result = set()
    for item in annotations:
        if not isinstance(item, dict):
            raise ValueError("Chaque annotation humaine doit être un objet.")
        block, index = item.get("block_id"), item.get("hypothesis_index")
        if (not isinstance(block, str) or block not in blocks or type(index) is not int
                or not 0 <= index < len(blocks[block]["answer"]["hypotheses"])):
            raise ValueError("Annotation humaine : bloc ou indice d'hypothèse invalide.")
        result.add((block, index))
    return result


def main(argv=None):
    """Mesure la validation et écrit trois artefacts dans un run C7 neuf."""
    parser = argparse.ArgumentParser(description="Porte Laya sur réponses de validation uniquement.")
    parser.add_argument("--responses", required=True)
    parser.add_argument("--unsupported")
    parser.add_argument("--n", type=int, default=30)
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--out", help="Racine des runs ; eval/runs par défaut.")
    parser.add_argument("--config", help="Configuration Laya (seuils) ; volet_b/agents/configs/laya.yaml par défaut.")
    args = parser.parse_args(argv)
    try:
        if args.n < 1:
            raise ValueError("--n doit être positif.")
        response_path = checked_path(args.responses)
        unsupported_path = checked_path(args.unsupported) if args.unsupported else None
        root = checked_path(args.out, allow_test_name=True) if args.out else paths.RUNS
        rows = read_responses(response_path)
        unsupported = load_unsupported(unsupported_path, rows) if unsupported_path else None
        selected = rows[:args.n]
        if not selected:
            raise ValueError("Aucun bloc de validation à mesurer.")
        # Source identique à loader.load_templates, sans importer pandas.
        template_path = None
        if args.mock:
            templates = {code: "Synthetic event template (mock mode)."
                         for row in selected for code in row["events"]}
        else:
            template_path = checked_path(paths.PREPROCESSED / "HDFS.log_templates.csv")
            with template_path.open(encoding="utf-8", newline="") as source:
                templates = {r["EventId"]: r["EventTemplate"] for r in csv.DictReader(source)}
        config = load_config(args.config)
        gate = LayaGate(config, predict=mock_predict if args.mock else None)
        predictions = []
        with PeakRSS() as memory:
            load_seconds = gate.load()
            for row in selected:
                after, info = gate.apply(row["answer"], row["events"], templates)
                predictions.append({"block_id": row["block_id"], "split": row["split"], "label": row.get("label"),
                                    "before": row["answer"], "after": after, "info": info})
        latencies = sorted(p["info"]["predict_seconds"] for p in predictions)
        metrics = {
            "blocks": len(predictions),
            "abstentions_before": sum(p["before"]["abstention"] for p in predictions),
            "abstentions_after": sum(p["after"]["abstention"] for p in predictions),
            "hypotheses_before": sum(len(p["before"]["hypotheses"]) for p in predictions),
            "hypotheses_after": sum(len(p["after"]["hypotheses"]) for p in predictions),
            "hypotheses_moved": sum(len(p["info"]["moved_indices"]) for p in predictions),
            "unsupported_before": None, "unsupported_after": None,
            "latency_mean_seconds": sum(latencies) / len(latencies),
            "latency_p95_seconds": latencies[math.ceil(0.95 * len(latencies)) - 1],
            "peak_rss_bytes": memory.peak,
            "load_seconds": load_seconds,
            "anomaly_probability_by_label": by_label(predictions),
        }
        if unsupported is not None:
            selected_ids = {p["block_id"] for p in predictions}
            moved = {(p["block_id"], i) for p in predictions for i in p["info"]["moved_indices"]}
            before = {(bid, i) for bid, i in unsupported if bid in selected_ids}
            metrics.update(unsupported_before=len(before), unsupported_after=len(before - moved))
        try:
            laya_version = version("laya")
        except PackageNotFoundError:
            laya_version = None
        hashes = {"responses": input_hash(response_path)}
        if unsupported_path:
            hashes["unsupported"] = input_hash(unsupported_path)
        if template_path:
            hashes["templates"] = input_hash(template_path)
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=paths.ROOT,
                                capture_output=True, text=True, check=True).stdout.strip()
        run_config = {"laya": config, "revision": config["revision"], "mock": args.mock,
                      "commit": commit, "split": "validation", "backend": "mock" if args.mock else "laya.Router",
                      "loaded_revision_verified": False, "agents": 1, "calls_per_block": 1,
                      "n": args.n, "laya_version": laya_version, "input_sha256": hashes,
                      "machine": {"platform": platform.platform(), "processor": platform.processor(),
                                  "python": platform.python_version()},
                      "templates": "synthetic" if args.mock else str(template_path),
                      "memory": "RSS échantillonnée toutes les 0,02 s ; octets",
                      "latency": "Appel groupé par bloc, après chargement et échauffement (load_seconds à part)",
                      "config_path": str(paths.resolve_path(args.config)) if args.config else "volet_b/agents/configs/laya.yaml",
                      "p95": "Rang supérieur (nearest rank)",
                      "purpose": "mock_sans_valeur_scientifique" if args.mock else "validation"}
        # Équivalent léger de new_run_directory : first_inference impose psutil
        # et importe les composants SLM, ici facultatifs.
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S_%fZ")
        run_dir = root / f"{stamp}_{uuid4().hex[:8]}_laya_C7"
        run_dir.mkdir(parents=True, exist_ok=False)
        (run_dir / "predictions.jsonl").write_text(
            "".join(json.dumps(p, ensure_ascii=False) + "\n" for p in predictions), encoding="utf-8")
        for name, data in (("config.json", run_config), ("metrics.json", metrics)):
            (run_dir / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except (ValueError, OSError, ImportError) as exc:
        parser.error(str(exc))
    print(f"Mesure C7 enregistrée dans {run_dir}")
    return run_dir


if __name__ == "__main__":
    main()
