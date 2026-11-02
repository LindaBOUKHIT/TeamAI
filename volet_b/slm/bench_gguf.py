"""SCRUM-57 — Compare le modèle complet (float32, Transformers) et la version 4 bits officielle (GGUF Q4_K_M, llama.cpp).

    python -m volet_b.slm.bench_gguf --backend llamacpp [--block-id blk_…] [--offline]
    python -m volet_b.slm.bench_gguf --backend transformers [--block-id blk_…] [--offline]

Banc de mesure expérimental : le backend llama.cpp n'est pas encore branché derrière `generate()`.
Même bloc que SCRUM-28 et mêmes paramètres de génération (configs/generation.yaml) pour les deux.
Le prompt place la consigne AVANT les logs : avec la consigne à la fin (prompt de SCRUM-28), la version
4 bits recopie les logs au lieu de les résumer, même sur 5 lignes (observé le 06/10, voir le journal).
Chaque exécution écrit un dossier neuf dans eval/runs/ (format C7), sans jamais écraser un run précédent.
"""
import argparse
import hashlib
import json
import os
import platform
import subprocess
import time

import psutil

from teamai.paths import ROOT
from volet_b.slm.first_inference import PeakMemory, gb, new_run_directory, package_versions, pick_block, raw_lines
from volet_b.slm.generate import generate, load_config, load_model

GGUF_REPO = "HuggingFaceTB/SmolLM2-1.7B-Instruct-GGUF"
GGUF_FILE = "smollm2-1.7b-instruct-q4_k_m.gguf"
GGUF_REVISION = "2d4a76a30b4af41ecd395c35725ac11688d4cfe4"  # snapshot vérifié le 06/10
N_CTX = 4096

PROMPT_CONSIGNE_AVANT = """Résume en français, en 5 phrases maximum, ce qui arrive au bloc HDFS ci-dessous, puis indique si le comportement semble normal ou anormal et pourquoi. N'invente aucune information absente des logs.

Logs du bloc :
{lines}"""


def load_llamacpp(cfg: dict, local_files_only: bool = False):
    """Charge le GGUF Q4_K_M (révision figée) avec llama.cpp, contexte de 4 096 tokens.

    `last_n_tokens_size = n_ctx` applique la pénalité de répétition sur tout le contexte, comme Transformers.
    """
    from huggingface_hub import hf_hub_download
    from llama_cpp import Llama

    path = hf_hub_download(GGUF_REPO, GGUF_FILE, revision=GGUF_REVISION, local_files_only=local_files_only)
    return Llama(model_path=path, n_ctx=N_CTX, last_n_tokens_size=N_CTX, seed=cfg["seed"],
                 verbose=False, n_gpu_layers=cfg.get("n_gpu_layers", 0))


def generate_llamacpp(llm, messages: list[dict], cfg: dict) -> dict:
    """Génère avec llama.cpp au format de `generate()` : {text, new_tokens, seconds}.

    Température 0 = décodage glouton, comme `do_sample: false` côté Transformers.
    """
    start = time.perf_counter()
    out = llm.create_chat_completion(
        messages=messages,
        max_tokens=cfg["max_new_tokens"],
        temperature=0.0,
        repeat_penalty=cfg["repetition_penalty"],
    )
    return {
        "text": out["choices"][0]["message"]["content"],
        "new_tokens": out["usage"]["completion_tokens"],
        "seconds": round(time.perf_counter() - start, 2),
    }


def main(argv=None):
    """Mesure chargement, mémoire et débit d'un backend sur un bloc, puis écrit les artefacts C7 du run.

    Refuse de tourner avec TEAMAI_SLM_MOCK=1 : une mesure factice n'a pas de sens.
    """
    parser = argparse.ArgumentParser(description="Banc float32 / GGUF 4 bits sur une trace HDFS.")
    parser.add_argument("--backend", choices=["llamacpp", "transformers"], default="llamacpp")
    parser.add_argument("--block-id", help="Bloc précis à reproduire ; sinon le bloc de SCRUM-28.")
    parser.add_argument("--offline", action="store_true", help="Poids déjà en cache uniquement.")
    args = parser.parse_args(argv)
    if os.environ.get("TEAMAI_SLM_MOCK") == "1":
        parser.error("Retirer TEAMAI_SLM_MOCK pour une vraie mesure.")

    cfg = load_config()
    proc = psutil.Process()
    block_id = args.block_id or pick_block()
    lines = raw_lines(block_id)
    messages = [{"role": "user", "content": PROMPT_CONSIGNE_AVANT.format(lines="\n".join(lines))}]
    print(f"Bloc {block_id} : {len(lines)} lignes brutes — backend {args.backend}", flush=True)

    start = time.perf_counter()
    if args.backend == "llamacpp":
        llm = load_llamacpp(cfg, local_files_only=args.offline)
    else:
        load_model(local_files_only=args.offline)
    load_seconds = time.perf_counter() - start
    rss_loaded = proc.memory_info().rss

    with PeakMemory() as peak:
        if args.backend == "llamacpp":
            out = generate_llamacpp(llm, messages, cfg)
        else:
            out = generate(messages, local_files_only=args.offline)

    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT,
                           capture_output=True, text=True).stdout.strip()
    metrics = {
        "backend": args.backend,
        "block_id": block_id,
        "raw_lines": len(lines),
        "load_seconds": round(load_seconds, 1),
        "rss_after_load_gb": gb(rss_loaded),
        "rss_peak_generation_gb": gb(peak.peak),
        "new_tokens": out["new_tokens"],
        "generation_seconds": out["seconds"],
        "tokens_per_second": round(out["new_tokens"] / out["seconds"], 2) if out["seconds"] else None,
    }
    config = {
        **cfg,
        "backend": args.backend,
        "prompt": "consigne_avant",
        "prompt_sha256": hashlib.sha256(messages[0]["content"].encode("utf-8")).hexdigest(),
        "commit": commit,
        "git_dirty": bool(dirty),
        "mock": False,
        "offline": args.offline,
        "device": "cpu",
        "python": platform.python_version(),
        "packages": {**package_versions(), "llama-cpp-python": _version("llama_cpp_python")},
        "purpose": "benchmark_observation_not_final_evaluation",
        "memory": "process RSS sampled at 0.2s; GiB",
    }
    if args.backend == "llamacpp":
        config |= {"gguf": f"{GGUF_REPO}/{GGUF_FILE}", "gguf_revision": GGUF_REVISION,
                   "quantization": "Q4_K_M", "n_ctx": N_CTX, "repeat_last_n": N_CTX}
    else:
        config |= {"quantization": None}

    run_dir = new_run_directory(name=f"bench_{args.backend}")
    prediction = {"id": block_id, "raw_text": out["text"], "parsed_response": None,
                  "errors": ["unstructured_benchmark_output"], "new_tokens": out["new_tokens"],
                  "seconds": out["seconds"], "mock": False}
    (run_dir / "predictions.jsonl").write_text(json.dumps(prediction, ensure_ascii=False) + "\n", encoding="utf-8")
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    (run_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    (run_dir / "prompt.txt").write_text(messages[0]["content"], encoding="utf-8")
    (run_dir / "output.txt").write_text(out["text"], encoding="utf-8")

    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    print(f"\n--- Réponse ({args.backend}) ---\n" + out["text"])
    print(f"\nRésultats enregistrés dans {run_dir}")


def _version(dist: str) -> str | None:
    """Version installée d'un paquet, ou None s'il est absent."""
    from importlib.metadata import PackageNotFoundError, version

    try:
        return version(dist)
    except PackageNotFoundError:
        return None


if __name__ == "__main__":
    main()
