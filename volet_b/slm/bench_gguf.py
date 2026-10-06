"""SCRUM-57 — Compare le modèle complet (float32, Transformers) et la version 4 bits officielle (GGUF Q4_K_M, llama.cpp).

    python -m volet_b.slm.bench_gguf --backend llamacpp
    python -m volet_b.slm.bench_gguf --backend transformers

Même bloc que SCRUM-28 et mêmes paramètres de génération (configs/generation.yaml) pour les deux.
Le prompt place la consigne AVANT les logs : avec la consigne à la fin (prompt de SCRUM-28), la version
4 bits recopie les logs au lieu de les résumer, même sur 5 lignes (observé le 06/10, voir le journal).
Résultats dans eval/runs/<date>_bench_<backend>/ (format C7).
"""
import argparse
import json
import subprocess
import time
from datetime import datetime

import psutil

from teamai.paths import RUNS
from volet_b.slm.first_inference import PeakMemory, gb, pick_block, raw_lines
from volet_b.slm.generate import generate, load_config, load_model

GGUF_REPO = "HuggingFaceTB/SmolLM2-1.7B-Instruct-GGUF"
GGUF_FILE = "smollm2-1.7b-instruct-q4_k_m.gguf"

PROMPT_CONSIGNE_AVANT = """Résume en français, en 5 phrases maximum, ce qui arrive au bloc HDFS ci-dessous, puis indique si le comportement semble normal ou anormal et pourquoi. N'invente aucune information absente des logs.

Logs du bloc :
{lines}"""


def load_llamacpp(cfg):
    from huggingface_hub import hf_hub_download
    from llama_cpp import Llama

    # last_n_tokens_size = n_ctx : pénalité de répétition sur tout le contexte, comme dans Transformers.
    return Llama(
        model_path=hf_hub_download(GGUF_REPO, GGUF_FILE),
        n_ctx=4096,
        last_n_tokens_size=4096,
        seed=cfg["seed"],
        verbose=False,
    )


def generate_llamacpp(llm, messages, cfg) -> dict:
    start = time.perf_counter()
    out = llm.create_chat_completion(
        messages=messages,
        max_tokens=cfg["max_new_tokens"],
        temperature=0.0,  # équivalent du décodage glouton (do_sample: false)
        repeat_penalty=cfg["repetition_penalty"],
    )
    return {
        "text": out["choices"][0]["message"]["content"],
        "new_tokens": out["usage"]["completion_tokens"],
        "seconds": round(time.perf_counter() - start, 2),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=["llamacpp", "transformers"], default="llamacpp")
    backend = parser.parse_args().backend

    cfg = load_config()
    proc = psutil.Process()
    block_id = pick_block()
    lines = raw_lines(block_id)
    messages = [{"role": "user", "content": PROMPT_CONSIGNE_AVANT.format(lines="\n".join(lines))}]
    print(f"Bloc {block_id} : {len(lines)} lignes brutes — backend {backend}")

    start = time.perf_counter()
    llm = load_llamacpp(cfg) if backend == "llamacpp" else load_model()
    load_seconds = time.perf_counter() - start
    rss_loaded = proc.memory_info().rss

    with PeakMemory() as peak:
        out = generate_llamacpp(llm, messages, cfg) if backend == "llamacpp" else generate(messages)

    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    metrics = {
        "backend": backend,
        "block_id": block_id,
        "load_seconds": round(load_seconds, 1),
        "rss_after_load_gb": gb(rss_loaded),
        "rss_peak_generation_gb": gb(peak.peak),
        "new_tokens": out["new_tokens"],
        "generation_seconds": out["seconds"],
        "tokens_per_second": round(out["new_tokens"] / out["seconds"], 2),
    }
    config = {**cfg, "backend": backend, "prompt": "consigne_avant", "commit": commit}
    if backend == "llamacpp":
        config |= {"gguf": f"{GGUF_REPO}/{GGUF_FILE}", "n_ctx": 4096, "repeat_last_n": 4096}

    run_dir = RUNS / f"{datetime.now():%Y-%m-%d}_bench_{backend}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    (run_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    (run_dir / "prompt.txt").write_text(messages[0]["content"], encoding="utf-8")
    (run_dir / "output.txt").write_text(out["text"], encoding="utf-8")

    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    print(f"\n--- Réponse ({backend}) ---\n" + out["text"])


if __name__ == "__main__":
    main()
