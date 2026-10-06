"""SCRUM-28 — Première inférence locale du SLM sur une vraie trace HDFS anormale.

    python -m volet_b.slm.first_inference          (depuis la racine du dépôt, HF_HOME conseillé sur D:)

Mesure le temps de chargement, la mémoire (RSS) avant/après chargement et au pic de génération,
le débit en tokens/s, puis enregistre tout dans eval/runs/<date>_first_inference/ (format C7).
"""
import json
import platform
import re
import subprocess
import threading
import time
from datetime import datetime

import psutil

from teamai.data.loader import load_traces
from teamai.paths import RAW_HDFS, RUNS
from volet_b.slm.generate import generate, load_config, load_model

PROMPT = """Voici les lignes de log HDFS concernant un seul bloc de données.

{lines}

Résume en français, en 5 phrases maximum, ce qui arrive à ce bloc, puis indique si le comportement semble normal ou anormal et pourquoi. N'invente aucune information absente des logs."""


def pick_block(min_len: int = 12, max_len: int = 25) -> str:
    """Premier bloc anormal de longueur moyenne (assez court pour tenir dans le prompt)."""
    traces = load_traces()
    lengths = traces["events"].str.len()
    candidates = traces[(traces["label"] == 1) & lengths.between(min_len, max_len)]
    return candidates.iloc[0]["BlockId"]


def raw_lines(block_id: str) -> list[str]:
    """Lignes brutes de HDFS.log qui mentionnent le bloc (parcours complet du fichier, ~1,5 Go)."""
    pattern = re.compile(re.escape(block_id) + r"(?!\d)")
    with open(RAW_HDFS / "HDFS.log", encoding="utf-8", errors="replace") as f:
        return [line.rstrip() for line in f if pattern.search(line)]


class PeakMemory:
    """Échantillonne la mémoire résidente du processus toutes les 0,2 s pour en garder le maximum."""

    def __init__(self):
        self.peak = 0
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        proc = psutil.Process()
        while not self._stop.is_set():
            self.peak = max(self.peak, proc.memory_info().rss)
            time.sleep(0.2)

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        self._thread.join()


def gb(n_bytes: int) -> float:
    return round(n_bytes / 1024**3, 2)


def main():
    proc = psutil.Process()
    block_id = pick_block()
    lines = raw_lines(block_id)
    print(f"Bloc {block_id} : {len(lines)} lignes brutes")

    rss_before = proc.memory_info().rss
    start = time.perf_counter()
    load_model()
    load_seconds = time.perf_counter() - start
    rss_loaded = proc.memory_info().rss
    print(f"Modèle chargé en {load_seconds:.1f} s — RSS {gb(rss_loaded)} Go")

    messages = [{"role": "user", "content": PROMPT.format(lines="\n".join(lines))}]
    with PeakMemory() as peak:
        out = generate(messages)

    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    metrics = {
        "block_id": block_id,
        "label": "anomalie",
        "raw_lines": len(lines),
        "load_seconds": round(load_seconds, 1),
        "rss_before_gb": gb(rss_before),
        "rss_after_load_gb": gb(rss_loaded),
        "rss_peak_generation_gb": gb(peak.peak),
        "new_tokens": out["new_tokens"],
        "generation_seconds": out["seconds"],
        "tokens_per_second": round(out["new_tokens"] / out["seconds"], 2) if out["seconds"] else None,
    }
    config = {
        **load_config(),
        "commit": commit,
        "machine": f"{platform.processor()} · {gb(psutil.virtual_memory().total)} Go RAM",
        "torch_threads": __import__("torch").get_num_threads(),
    }

    run_dir = RUNS / f"{datetime.now():%Y-%m-%d}_first_inference"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    (run_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    (run_dir / "prompt.txt").write_text(messages[0]["content"], encoding="utf-8")
    (run_dir / "output.txt").write_text(out["text"], encoding="utf-8")

    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    print("\n--- Réponse du modèle ---\n" + out["text"])
    print(f"\nRésultats enregistrés dans {run_dir}")


if __name__ == "__main__":
    main()
