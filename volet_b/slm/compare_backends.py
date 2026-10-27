"""SCRUM-57 : diagnostic float32 / Q4_K_M sur la validation, sans téléchargement."""
import argparse
import csv
import json
import os
import platform
import random
import re
import statistics
import subprocess
import sys
import time

from teamai.contracts import validate_answer
from teamai.paths import ROOT, SAMPLE, SPLITS, resolve_path
from volet_b.slm.first_inference import PeakMemory, new_run_directory, package_versions, sha256_file
from volet_b.slm.generate import generate, load_backend, load_config
from volet_b.slm.bench_gguf import _version
from volet_b.slm.convert_gguf import source_hash

PROMPT = """Analyse les logs HDFS ci-dessous en français, sans inventer d'information. Réponds uniquement par un objet JSON avec les six clés : resume_evenements (texte), faits_observes, hypotheses, infos_manquantes, sources (listes de textes), abstention (booléen). Distingue les faits des hypothèses. Aucun document n'est fourni : sources doit être vide. Si les informations ne suffisent pas, abstiens-toi : hypotheses vide et infos_manquantes non vide.

Logs du bloc :
{lines}"""


def select_blocks(n, seed=42, split="val", sample=SAMPLE, splits=SPLITS):
    """Tire sans label N blocs du sample appartenant à C4 val ; refuse tout autre split."""
    if split != "val":
        raise ValueError("Seul le split val est autorisé ; le split test est réservé.")
    if n < 1:
        raise ValueError("N doit être positif.")
    split_path = splits / "splits.csv"
    if not split_path.is_file():
        raise FileNotFoundError("splits.csv C4 requis : aucune affectation de split ne sera inventée.")
    meta = splits / "splits_meta.json"
    if meta.is_file():
        expected = json.loads(meta.read_text(encoding="utf-8")).get("splits_csv_sha256")
        if expected and expected != sha256_file(split_path):
            raise ValueError("Hash de splits.csv différent de splits_meta.json.")
    with split_path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assignments = {}
    for row in rows:
        block = row["BlockId"]
        if block in assignments or row["split"] not in {"train", "val", "test"}:
            raise ValueError("Affectations C4 dupliquées ou invalides.")
        assignments[block] = row["split"]
    with (sample / "Event_traces.csv").open(encoding="utf-8", newline="") as stream:
        ids = {row["BlockId"] for row in csv.DictReader(stream)}
    candidates = sorted(block for block in ids if assignments.get(block) == "val")
    if len(candidates) < n:
        raise ValueError(f"Seulement {len(candidates)} blocs val dans le sample pour N={n}.")
    selected = random.Random(seed).sample(candidates, n)
    lines = {block: [] for block in selected}
    with (sample / "HDFS_sample.log").open(encoding="utf-8") as stream:
        for line in stream:
            for block in set(re.findall(r"(?<!\w)blk_-?\d+(?!\w)", line)) & lines.keys():
                lines[block].append(line.rstrip("\r\n"))
    if any(not lines[block] for block in selected):
        raise ValueError("Bloc val sans lignes brutes dans HDFS_sample.log.")
    return [{"block_id": block, "split": "val", "messages": [
        {"role": "user", "content": PROMPT.format(lines="\n".join(lines[block]))}]} for block in selected]


def write_json(path, value):
    """Écrit du JSON UTF-8 strict, sans NaN ni valeurs implicites."""
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")


def reject_constant(value):
    """Refuse NaN et Infinity dans la réponse, conformément au JSON strict de C5."""
    raise ValueError(f"Constante JSON interdite : {value}")


def measure_backend(config, backend):
    """Mesure un backend dans son processus dédié ; conserve aussi les échecs au dénominateur."""
    if not config["blocks"] or any(block.get("split") != "val" for block in config["blocks"]):
        raise ValueError("Bloc hors validation : test interdit.")
    cfg = {**config["generation"], "backend": backend, "local_files_only": True, "do_sample": False}
    adapter = config["adapters"][backend]
    predictions = []
    load_error = None
    start = time.perf_counter()
    with PeakMemory() as peak:
        try:
            load_backend(cfg, adapter)
        except Exception as exc:
            load_error = f"load_error: {type(exc).__name__}: {exc}"
        load_seconds = time.perf_counter() - start
        for block in config["blocks"]:
            if block["split"] != "val":
                raise ValueError("Bloc hors validation : test interdit.")
            result = {"text": "", "new_tokens": None, "seconds": None}
            parsed = None
            errors = [load_error] if load_error else []
            if not errors:
                try:
                    result = generate(block["messages"], adapter=adapter, **cfg)
                except Exception as exc:
                    errors.append(f"generation_error: {type(exc).__name__}: {exc}")
                else:
                    try:
                        parsed = json.loads(result["text"], parse_constant=reject_constant)
                    except (ValueError, TypeError):
                        errors.append("invalid_json")
                    else:
                        try:
                            errors += validate_answer(parsed, allowed_sources=[])
                        except Exception as exc:  # une sortie imprévue reste un échec compté, pas un arrêt du banc
                            errors.append(f"validation_error: {type(exc).__name__}: {exc}")
            seconds = result["seconds"]
            predictions.append({"id": block["block_id"], "block_id": block["block_id"], "split": "val",
                                "backend": backend, "raw_text": result["text"], "parsed_response": parsed,
                                "errors": errors, "conformity": not errors, "seconds": seconds,
                                "new_tokens": result["new_tokens"], "mock": False,
                                "tokens_per_second": result["new_tokens"] / seconds if seconds else None})
    n = len(predictions)
    rates = [row["tokens_per_second"] for row in predictions if row["tokens_per_second"] is not None]
    metrics = {"n": n, "conformity": sum(row["conformity"] for row in predictions) / n,
               "failures": sum(bool(row["errors"]) for row in predictions),
               "abstention": sum(isinstance(row["parsed_response"], dict) and
                                  row["parsed_response"].get("abstention") is True for row in predictions) / n,
               "mean_tokens_per_second": statistics.mean(rates) if rates else None,
               "throughput_measured_n": len(rates), "peak_rss_bytes": peak.peak,
               "load_seconds": load_seconds, "load_error": load_error,
               "quantization": "Q4_K_M" if backend == "llamacpp" else None,
               "dtype": "GGUF" if backend == "llamacpp" else "float32"}
    return predictions, metrics


def main(argv=None):
    """Crée un dossier C7 puis lance chaque backend dans un processus CPU indépendant."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=5)
    parser.add_argument("--split", default="val", choices=["val"])
    parser.add_argument("--backends", nargs="+", choices=["transformers", "llamacpp"],
                        default=["transformers", "llamacpp"])
    parser.add_argument("--adapter-hf")
    parser.add_argument("--adapter-gguf")
    parser.add_argument("--worker", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if os.environ.get("TEAMAI_SLM_MOCK") == "1":
        parser.error("Retirer TEAMAI_SLM_MOCK : les mesures factices sont interdites.")
    if args.worker:
        run = resolve_path(args.worker)
        config = json.loads((run / "config.json").read_text(encoding="utf-8"))
        predictions, metrics = measure_backend(config, args.backends[0])
        write_json(run / f"{args.backends[0]}.json", {"predictions": predictions, "metrics": metrics})
        return
    if len(args.backends) != len(set(args.backends)):
        parser.error("Un backend ne doit apparaître qu'une fois.")
    if len(args.backends) == 2 and bool(args.adapter_hf) != bool(args.adapter_gguf):
        parser.error("Fournir les deux adaptateurs pour comparer les mêmes configurations adaptées.")
    cfg = load_config()
    if cfg["dtype"] != "float32":
        parser.error("La comparaison exige dtype: float32 dans generation.yaml.")
    blocks = select_blocks(args.n, cfg["seed"], args.split)
    adapters = {"transformers": str(resolve_path(args.adapter_hf)) if args.adapter_hf else None,
                "llamacpp": str(resolve_path(args.adapter_gguf)) if args.adapter_gguf else None}
    for backend in args.backends:
        if adapters[backend] and not resolve_path(adapters[backend]).exists():
            parser.error(f"Adaptateur introuvable : {adapters[backend]}")
        if adapters[backend]:
            path = resolve_path(adapters[backend])
            if backend == "llamacpp" and (not path.is_file() or path.suffix.lower() != ".gguf"):
                parser.error("--adapter-gguf doit être un fichier GGUF d'adaptateur.")
            if backend == "transformers" and not (path / "adapter_config.json").is_file():
                parser.error("--adapter-hf doit contenir adapter_config.json.")
    adapter_hashes = {}
    for backend in args.backends:
        if adapters[backend]:
            path = resolve_path(adapters[backend])
            adapter_hashes[backend] = source_hash(path) if path.is_dir() else sha256_file(path)
    run = new_run_directory(name="compare_backends")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
                            capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, check=True,
                           capture_output=True, text=True).stdout.strip()
    config = {"generation": {**cfg, "do_sample": False, "local_files_only": True}, "blocks": blocks,
              "split": "val", "split_sha256": sha256_file(SPLITS / "splits.csv"),
              "sample_sha256": sha256_file(SAMPLE / "Event_traces.csv"),
              "log_sha256": sha256_file(SAMPLE / "HDFS_sample.log"), "seed": cfg["seed"],
              "backends": args.backends, "adapters": adapters, "adapter_sha256": adapter_hashes,
              "commit": commit, "git_dirty": bool(dirty),
              "machine": platform.platform(), "python": platform.python_version(),
              "packages": {**package_versions(), "llama-cpp-python": _version("llama-cpp-python"),
                           "peft": _version("peft"), "gguf": _version("gguf")},
              "quantization": {"transformers": None, "llamacpp": "Q4_K_M"},
              "mock": False, "device": "cpu", "rag": None,
              "agents": 1, "calls_per_block": 1,
              "memory": "RSS processus indépendant par backend ; octets ; pic échantillonné à 0,2 s, chargement inclus",
              "timing": "Chargement : imports et poids. Génération : prompt inclus ; Transformers hors tokenisation/décodage, llama.cpp chat complet.",
              "purpose": "diagnostic backend + quantification ; aucun score de justesse sémantique"}
    write_json(run / "config.json", config)
    predictions, metrics = [], {}
    for backend in args.backends:
        command = [sys.executable, "-m", "volet_b.slm.compare_backends", "--worker", str(run), "--backends", backend]
        try:
            subprocess.run(command, cwd=ROOT, check=True,
                           env={**os.environ, "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"})
            measured = json.loads((run / f"{backend}.json").read_text(encoding="utf-8"))
        except (OSError, subprocess.CalledProcessError) as exc:
            error = f"worker_error: {exc}"
            measured = {"predictions": [{"id": block["block_id"], "block_id": block["block_id"],
                        "split": "val", "backend": backend, "raw_text": "", "parsed_response": None,
                        "errors": [error], "conformity": False, "seconds": None, "new_tokens": None,
                        "tokens_per_second": None, "mock": False} for block in blocks],
                        "metrics": {"n": args.n, "conformity": 0.0, "abstention": 0.0,
                        "failures": args.n, "mean_tokens_per_second": None, "throughput_measured_n": 0,
                        "peak_rss_bytes": None, "load_seconds": None, "load_error": error,
                        "quantization": config["quantization"][backend]}}
        predictions.extend(measured["predictions"])
        metrics[backend] = measured["metrics"]
    (run / "predictions.jsonl").write_text("".join(
        json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n" for row in predictions), encoding="utf-8")
    write_json(run / "metrics.json", {"by_backend": metrics, "protocol": config["purpose"],
                                      "memory": config["memory"], "denominator": args.n})
    report = ["# Comparaison de validation", "", config["purpose"], "",
              "Conformité C5 et abstention ne mesurent pas la justesse des explications. Relecture humaine nécessaire.",
              "L'effet du backend et celui de la quantification ne sont pas séparés. Aucun résultat de test.", "",
              "| Backend | N | Conformité | Abstention | Tokens/s moyen | Pic RSS (octets) | Chargement (s) |",
              "|---|---:|---:|---:|---:|---:|---:|"]
    for backend, values in metrics.items():
        report.append(f"| {backend} | {values['n']} | {values['conformity']:.1%} | {values['abstention']:.1%} | "
                      f"{values['mean_tokens_per_second']} | {values['peak_rss_bytes']} | {values['load_seconds']} |")
    report += ["", "Sorties brutes et erreurs par bloc : `predictions.jsonl`. Prompts exacts : `config.json`."]
    (run / "comparison.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(run)


if __name__ == "__main__":
    main()
