"""SCRUM-38 — Mesures avant adaptation, sans réglage sur les sorties du test."""
import argparse
import json
import os
import platform
import re
import statistics
import subprocess
import time
from pathlib import Path

from teamai.contracts import validate_example
from teamai.paths import ROOT, RUNS, VOLET_B_SUMMARY, VOLET_B_TEST, VOLET_B_TEST_SHA256
from volet_b.agents import single_agent
from volet_b.agents.validate import check_answer
from volet_b.slm.first_inference import PeakMemory, new_run_directory, sha256_file
from volet_b.slm.generate import generate, load_config


NO_RAG_NOTE = "(aucune documentation fournie dans cette configuration)"


def write_json(path: Path, value: dict) -> None:
    """Écrit un objet JSON strict en UTF-8."""
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def git_commit() -> str | None:
    """Renvoie le commit courant, ou None si Git est indisponible."""
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    except OSError:
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def input_hash(path: Path) -> str:
    """Vérifie l'entrée et, pour le test officiel, son empreinte de référence si elle existe."""
    if not path.is_file():
        raise FileNotFoundError(f"Fichier d'exemples C5 absent : {path}. Fournir --data ou attendre SCRUM-35.")
    digest = sha256_file(path)
    if path.resolve() == VOLET_B_TEST.resolve() and VOLET_B_TEST_SHA256.exists():
        reference = VOLET_B_TEST_SHA256.read_text(encoding="utf-8").split()
        if not reference or not re.fullmatch(r"[0-9a-fA-F]{64}", reference[0]):
            raise ValueError("test.sha256 : empreinte SHA-256 invalide.")
        if reference[0].lower() != digest:
            raise ValueError("SHA-256 du test officiel différent de test.sha256 : exécution refusée.")
    return digest


def predict(example: dict, config: str, retriever, adapter: str | None) -> dict:
    """Évalue un exemple ; conserve toute erreur sans envoyer ses annotations au pipeline."""
    record = {
        "id": example.get("id"), "block_id": example.get("block_id"),
        "raw_text": None, "parsed_response": None, "errors": [], "passages": [],
        "seconds": None, "generation_seconds": None, "new_tokens": None,
        "mock": os.environ.get("TEAMAI_SLM_MOCK") == "1", "sources_valid": False,
    }
    start = time.perf_counter()
    try:
        errors = validate_example(example)
        if errors:
            record["errors"] = [f"input : {error}" for error in errors]
            return record
        lines = example["trace_lines"]
        if config == "rag1":
            if retriever is None:
                retriever = single_agent.load_retriever(single_agent.DEFAULT_METHOD, local_files_only=True)
            _, _, record["passages"] = single_agent.retrieve_for_trace(example["block_id"], lines, retriever)
        note = None if config == "rag1" else NO_RAG_NOTE
        messages = single_agent.build_messages(lines, record["passages"], empty_note=note)
        out = generate(messages, adapter=adapter)
        record.update(raw_text=out["text"], generation_seconds=out["seconds"], new_tokens=out["new_tokens"])
        allowed = [p["id"] for p in record["passages"]]
        # Même contrôle que l'agent (SCRUM-37), pour que rag1 soit mesuré comme il s'exécute.
        answer, record["errors"] = check_answer(out["text"], allowed_sources=allowed)
        if answer is None:
            return record
        record["parsed_response"] = answer
        sources = answer.get("sources")
        record["sources_valid"] = (isinstance(sources, list)
                                   and all(isinstance(s, str) and s in allowed for s in sources))
    except Exception as error:
        record["errors"].append(f"execution : {type(error).__name__} : {error}")
    finally:
        record["seconds"] = time.perf_counter() - start
    return record


def metrics(records: list[dict], peak_bytes: int) -> dict:
    """Calcule les taux sur tous les exemples, échecs compris, et les latences en secondes."""
    n = len(records)
    valid = sum(not r["errors"] for r in records)
    sources = sum(r["sources_valid"] for r in records)
    abstentions = sum(not r["errors"] and r["parsed_response"]["abstention"] for r in records)
    seconds = [r["seconds"] for r in records]
    return {
        "n": n, "c5_valid": valid, "failures": n - valid,
        "conformity_rate": valid / n if n else None,
        "sources_valid": sources, "sources_valid_rate": sources / n if n else None,
        "abstentions": abstentions, "abstention_rate": abstentions / n if n else None,
        "latency_mean_seconds": statistics.mean(seconds) if seconds else None,
        "latency_median_seconds": statistics.median(seconds) if seconds else None,
        "process_peak_rss_bytes": peak_bytes,
        "protocol": {
            "denominator": "Tous les exemples lus, y compris les échecs ; abstention sur réponses C5 conformes.",
            "sources": "Liste de textes citant uniquement les passages fournis ; liste vide valide, y compris sans RAG.",
            "latency": "Temps mural par exemple : validation, retrieval, prompt, chargement éventuel et génération.",
            "generation_seconds": "Mesure renvoyée par generate, hors chargement et retrieval ; null en cas d'échec.",
            "memory": "RSS du processus, chargement inclus, échantillonnée toutes les 0,2 s ; ni GPU ni processus enfants.",
        },
    }


def run_config(config: str, data: Path = VOLET_B_TEST, limit: int | None = None,
               adapter: str | None = None, run_root: Path = RUNS) -> Path:
    """Exécute base ou rag1 et renvoie le dossier C7 neuf ; aucun résumé n'est publié automatiquement."""
    if config not in ("base", "rag1"):
        raise ValueError("Configuration attendue : base ou rag1.")
    if limit is not None and limit < 1:
        raise ValueError("--limit doit être strictement positif.")
    data = Path(data)
    digest = input_hash(data)
    generation = load_config()
    mock = os.environ.get("TEAMAI_SLM_MOCK") == "1"
    run_dir = new_run_directory(root=run_root, name=config)
    metadata = {
        "ticket": "SCRUM-38", "config": config, "adapter": adapter, "mock": mock,
        "input": str(data.resolve()), "input_sha256": digest,
        "official_test": data.resolve() == VOLET_B_TEST.resolve(), "limit": limit,
        "model_id": generation["model_id"], "model_revision": generation["revision"],
        "generation": generation, "commit": git_commit(), "agents": int(config == "rag1"),
        "slm_calls_per_example": 1, "backend": "mock" if mock else generation.get("backend", "transformers"),
        "quantification": None if mock else generation.get("quantification", generation.get("dtype")), "seed": generation["seed"],
        "prompt": single_agent.PROMPT.name, "prompt_sha256": sha256_file(single_agent.PROMPT),
        "retrieval": None, "splits": [],
        "machine": {"python": platform.python_version(), "platform": platform.platform()},
    }
    if config == "rag1":
        metadata["retrieval"] = {"method": single_agent.DEFAULT_METHOD, "k": single_agent.DEFAULT_K,
                                 "local_files_only": True, "index_metadata": None}
        if single_agent.META_FILE.exists():
            metadata["retrieval"]["index_metadata"] = json.loads(single_agent.META_FILE.read_text(encoding="utf-8"))
    write_json(run_dir / "config.json", metadata)
    records = []
    with PeakMemory() as peak:
        with data.open(encoding="utf-8") as source, (run_dir / "predictions.jsonl").open("w", encoding="utf-8") as output:
            for line in source:
                if not line.strip():
                    continue
                try:
                    example = json.loads(line)
                except json.JSONDecodeError:
                    example = {}
                if not isinstance(example, dict):
                    example = {}
                record = predict(example, config, None, adapter)
                output.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
                output.flush()
                records.append(record)
                split = example.get("split")
                if split in ("train", "val", "test") and split not in metadata["splits"]:
                    metadata["splits"].append(split)
                if limit is not None and len(records) >= limit:
                    break
    summary = {**metrics(records, peak.peak), "config": config, "mock": mock, "adapter": adapter,
               "input_sha256": digest, "official_test": metadata["official_test"], "limit": limit}
    write_json(run_dir / "config.json", metadata)
    write_json(run_dir / "metrics.json", summary)
    return run_dir


def update_summary(metric_paths, output: Path = VOLET_B_SUMMARY) -> None:
    """Actualise « Avant adaptation » depuis des mesures officielles complètes, réelles et sans adaptateur."""
    text = output.read_text(encoding="utf-8") if output.exists() else "# Résultats du volet B\n"
    pattern = re.compile(r"^## Avant adaptation\s*\n.*?(?=^## |\Z)", re.M | re.S)
    match = pattern.search(text)
    rows = {}
    if match:
        for line in match.group().splitlines():
            if line.startswith(("| base |", "| rag1 |")):
                rows[line.split("|")[1].strip()] = line
    for path in metric_paths:
        values = json.loads(Path(path).read_text(encoding="utf-8"))
        if (values["mock"] or values["adapter"] or not values["official_test"] or values["limit"] is not None):
            raise ValueError("Le résumé avant adaptation exige le test officiel complet, sans mock ni adaptateur.")
        name = values["config"]
        if name not in ("base", "rag1"):
            raise ValueError(f"Configuration inconnue : {name}")
        fields = [name, str(values["n"])]
        for key in ("conformity_rate", "sources_valid_rate", "abstention_rate", "latency_mean_seconds",
                    "latency_median_seconds", "process_peak_rss_bytes"):
            value = values[key]
            fields.append("non mesuré" if value is None else str(round(value, 6)))
        fields.append(values["input_sha256"])
        rows[name] = "| " + " | ".join(fields) + " |"
    section = ("## Avant adaptation\n\n"
               "Taux calculés sur tous les exemples, échecs compris. Mémoire RSS échantillonnée du processus.\n\n"
               "| Configuration | n | Conformité C5 | Sources valides | Abstention | Latence moyenne (s) | Médiane (s) | RSS max (octets) | SHA-256 entrée |\n"
               "|---|---:|---:|---:|---:|---:|---:|---:|---|\n"
               + "\n".join(rows[name] for name in ("base", "rag1") if name in rows) + "\n\n")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text[:match.start()] + section + text[match.end():] if match else text.rstrip() + "\n\n" + section,
                      encoding="utf-8")


def main(argv=None) -> None:
    """Lit les options et lance une configuration avec les paramètres de génération figés."""
    parser = argparse.ArgumentParser(description="SCRUM-38 : mesures avant adaptation du volet B.")
    parser.add_argument("--config", required=True, choices=("base", "rag1"))
    parser.add_argument("--data", type=Path, default=VOLET_B_TEST)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--adapter", help="Dossier d'un adaptateur LoRA, sinon modèle de base.")
    args = parser.parse_args(argv)
    try:
        run_dir = run_config(args.config, args.data, args.limit, args.adapter)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(f"Run : {run_dir}")


if __name__ == "__main__":
    main()
