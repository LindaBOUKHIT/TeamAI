"""SCRUM-28 — Première inférence locale du SLM sur une vraie trace HDFS anormale.

    python -m volet_b.slm.first_inference          (depuis la racine du dépôt, HF_HOME conseillé sur D:)

Mesure le temps de chargement, la mémoire (RSS) avant/après chargement et au pic de génération,
le débit en tokens/s, puis conserve un dossier distinct par exécution dans eval/runs/.
"""
import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import threading
import time
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from uuid import uuid4

import psutil

from teamai.data.loader import load_traces
from teamai.paths import RAW_HDFS, ROOT, RUNS
from volet_b.slm.generate import CONFIG, generate, load_config, load_model

PROMPT = """Voici les lignes de log HDFS concernant un seul bloc de données.

{lines}

Résume en français, en 5 phrases maximum, ce qui arrive à ce bloc, puis indique si le comportement semble normal ou anormal et pourquoi. N'invente aucune information absente des logs."""


def pick_block(min_len: int = 12, max_len: int = 25) -> str:
    """Premier bloc anormal de longueur moyenne (assez court pour tenir dans le prompt)."""
    traces = load_traces()
    lengths = traces["events"].str.len()
    candidates = traces[(traces["label"] == 1) & lengths.between(min_len, max_len)]
    if candidates.empty:
        raise ValueError("Aucun bloc anormal dans l'intervalle de longueurs demandé.")
    return candidates.iloc[0]["BlockId"]


def raw_lines(block_id: str, path: Path | None = None) -> list[str]:
    """Lignes brutes de HDFS.log qui mentionnent le bloc (parcours complet du fichier, ~1,5 Go)."""
    if not re.fullmatch(r"blk_-?\d+", block_id):
        raise ValueError("Identifiant attendu : blk_ suivi d'un entier signé.")
    pattern = re.compile(r"(?<!\w)" + re.escape(block_id) + r"(?!\d)")
    path = path or RAW_HDFS / "HDFS.log"
    with path.open(encoding="utf-8", errors="strict") as f:
        lines = [line.rstrip("\r\n") for line in f if block_id in line and pattern.search(line)]
    if not lines:
        raise ValueError(f"Aucune ligne trouvée pour {block_id} dans {path}.")
    return lines


class PeakMemory:
    """Échantillonne la mémoire résidente du processus toutes les 0,2 s pour en garder le maximum."""

    def __init__(self):
        self.peak = 0
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        proc = psutil.Process()
        while not self._stop.wait(0.2):
            self.peak = max(self.peak, proc.memory_info().rss)

    def __enter__(self):
        self.peak = psutil.Process().memory_info().rss
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        self._thread.join()
        self.peak = max(self.peak, psutil.Process().memory_info().rss)


def gb(n_bytes: int) -> float:
    return round(n_bytes / 1024**3, 2)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def new_run_directory(root: Path = RUNS) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S_%fZ")
    path = root / f"{stamp}_{uuid4().hex[:8]}_first_inference"
    path.mkdir(parents=True, exist_ok=False)
    return path


def package_versions() -> dict:
    versions = {}
    for name in ("torch", "transformers", "pandas", "PyYAML", "psutil", "hf-xet"):
        try:
            versions[name] = version(name)
        except PackageNotFoundError:
            versions[name] = None
    return versions


def main(argv=None):
    parser = argparse.ArgumentParser(description="Première inférence CPU sur une trace HDFS.")
    parser.add_argument("--block-id", help="Bloc précis à reproduire ; sinon sélection automatique.")
    parser.add_argument("--offline", action="store_true", help="Poids déjà en cache uniquement.")
    parser.add_argument("--torch-threads", type=int, default=12)
    args = parser.parse_args(argv)
    if args.torch_threads < 1:
        parser.error("--torch-threads doit être positif.")
    if os.environ.get("TEAMAI_SLM_MOCK") == "1":
        parser.error("Retirer TEAMAI_SLM_MOCK pour une vraie mesure ; tester le mode factice via generate().")

    proc = psutil.Process()
    block_id = args.block_id or pick_block()
    lines = raw_lines(block_id)
    print(f"Bloc {block_id} : {len(lines)} lignes brutes", flush=True)

    rss_before = proc.memory_info().rss
    start = time.perf_counter()
    import torch
    torch.set_num_threads(args.torch_threads)
    with PeakMemory() as loading_peak:
        load_model(local_files_only=args.offline)
    load_seconds = time.perf_counter() - start
    rss_loaded = proc.memory_info().rss
    print(f"Modèle chargé en {load_seconds:.1f} s — RSS {gb(rss_loaded)} GiB", flush=True)

    messages = [{"role": "user", "content": PROMPT.format(lines="\n".join(lines))}]
    with PeakMemory() as peak:
        out = generate(messages, local_files_only=args.offline)

    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    metrics = {
        "block_id": block_id,
        "raw_lines": len(lines),
        "load_seconds": round(load_seconds, 1),
        "rss_before_gb": gb(rss_before),
        "rss_after_load_gb": gb(rss_loaded),
        "rss_peak_load_gb": gb(loading_peak.peak),
        "rss_peak_generation_gb": gb(peak.peak),
        "vram_peak_gb": None,
        "new_tokens": out["new_tokens"],
        "generation_seconds": out["seconds"],
        "tokens_per_second": round(out["new_tokens"] / out["seconds"], 2) if out["seconds"] else None,
    }
    config = {
        **load_config(),
        "commit": commit,
        "git_dirty": bool(dirty),
        "mock": False,
        "offline": args.offline,
        "backend": "transformers",
        "device": "cpu",
        "python": platform.python_version(),
        "packages": package_versions(),
        "source_sha256": {str(path.relative_to(ROOT)): sha256_file(path) for path in
                          (Path(__file__), CONFIG, Path(__file__).with_name("generate.py"))},
        "prompt_sha256": hashlib.sha256(messages[0]["content"].encode("utf-8")).hexdigest(),
        "raw_log_sha256": sha256_file(RAW_HDFS / "HDFS.log"),
        "purpose": "technical_smoke_test_not_final_evaluation",
        "timing": "load includes imports and tokenizer/model; generation is model.generate including prompt processing",
        "memory": "process RSS sampled at 0.2s; fields ending _gb use GiB; no GPU used, VRAM not measured",
        "machine": f"{platform.processor()} · {gb(psutil.virtual_memory().total)} GiB RAM",
        "torch_threads": __import__("torch").get_num_threads(),
    }

    run_dir = new_run_directory()
    prediction = {"id": block_id, "raw_text": out["text"], "parsed_response": None,
                  "errors": ["unstructured_smoke_output"], "new_tokens": out["new_tokens"],
                  "seconds": out["seconds"], "mock": False}
    (run_dir / "predictions.jsonl").write_text(json.dumps(prediction, ensure_ascii=False) + "\n", encoding="utf-8")
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    (run_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    (run_dir / "prompt.txt").write_text(messages[0]["content"], encoding="utf-8")
    (run_dir / "output.txt").write_text(out["text"], encoding="utf-8")

    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    print("\n--- Réponse du modèle ---\n" + out["text"])
    print(f"\nRésultats enregistrés dans {run_dir}")


if __name__ == "__main__":
    main()
