"""SCRUM-37 — RAG de référence à un agent : trace → requête → passages C6 → SLM → réponse C5 vérifiée.

    python -m volet_b.agents.single_agent --block blk_4971154345890344      # un bloc de data/sample/
    python -m volet_b.agents.single_agent --file mes_logs.txt                # chaque bloc d'un fichier de logs
    python -m volet_b.agents.single_agent --split val --n 5                  # 5 blocs de validation
    ajouter --mock pour développer sans modèle (TEAMAI_SLM_MOCK=1)

Chaque exécution écrit un dossier C7 neuf dans eval/runs/ : predictions.jsonl (une ligne par bloc, avec
les étapes : événements, requête, passages et scores, erreurs), config.json et metrics.json.
Le modèle ne reçoit que la consigne, les lignes de la trace et les passages : jamais le label, une
annotation ou une réponse attendue. Le split `test` est refusé : il est réservé à l'évaluation finale.
"""
import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
from collections import Counter

import pandas as pd

from teamai.data.loader import load_traces
from teamai.data.preprocess import load_vocab_json, parse_lines
from teamai.paths import PROMPTS, ROOT, SAMPLE, SPLITS
from volet_b.agents.validate import check_answer
from volet_b.rag.retriever import DEFAULT_K, DEFAULT_METHOD, METHODS, META_FILE, load_retriever, query_for_events
from volet_b.slm.first_inference import new_run_directory
from volet_b.slm.generate import generate, load_config

PROMPT = PROMPTS / "single_agent.txt"
SAMPLE_LOG = SAMPLE / "HDFS_sample.log"
MAX_LINES = 60  # au-delà, les lignes sont tronquées dans le prompt (le nombre omis est indiqué)


def build_messages(trace_lines: list[str], passages: list[dict], max_lines: int = MAX_LINES) -> list[dict]:
    """Prompt du volet B : consigne d'abord, puis la trace, puis les passages avec leur identifiant."""
    shown = trace_lines[:max_lines]
    if len(trace_lines) > max_lines:
        shown = shown + [f"(… {len(trace_lines) - max_lines} lignes suivantes omises)"]
    documentation = "\n\n".join(f"[{p['id']}]\n{p['text']}" for p in passages) or "(aucun passage pertinent trouvé)"
    content = PROMPT.read_text(encoding="utf-8").replace("<<TRACE>>", "\n".join(shown))
    return [{"role": "user", "content": content.replace("<<PASSAGES>>", documentation)}]


def explain_block(block_id: str, trace_lines: list[str], retriever, k: int = DEFAULT_K,
                  adapter: str | None = None) -> dict:
    """Une ligne C7 pour un bloc : sortie brute, réponse analysée, erreurs, mesures et étapes."""
    events = parse_lines(trace_lines, load_vocab_json())["sequences"].get(block_id, [])
    query = query_for_events(events)
    passages = retriever.search(query, k)
    messages = build_messages(trace_lines, passages)
    out = generate(messages, adapter=adapter)
    answer, errors = check_answer(out["text"], [p["id"] for p in passages])
    return {
        "id": block_id,
        "raw_text": out["text"],
        "parsed_response": answer,
        "errors": errors,
        "new_tokens": out["new_tokens"],
        "seconds": round(out["seconds"], 2),
        "mock": os.environ.get("TEAMAI_SLM_MOCK") == "1",
        "steps": {
            "events": events,
            "query": query,
            "retrieved": [{"id": p["id"], "score": p["score"], "scores": p["scores"]} for p in passages],
            "prompt_chars": len(messages[0]["content"]),
        },
    }


def lines_by_block(lines: list[str]) -> dict[str, list[str]]:
    """Regroupe des lignes brutes par bloc (une ligne qui cite plusieurs blocs va dans chacun)."""
    blocks: dict[str, list[str]] = {}
    for line in lines:
        for block_id in dict.fromkeys(re.findall(r"blk_-?\d+", line)):
            blocks.setdefault(block_id, []).append(line.rstrip("\r\n"))
    return blocks


def official_split() -> pd.Series:
    """BlockId → split officiel (C4), lu dans data/splits/splits.csv."""
    return pd.read_csv(SPLITS / "splits.csv", usecols=["BlockId", "split"]).set_index("BlockId")["split"]


def select_blocks(args) -> dict[str, list[str]]:
    """Blocs à traiter selon --block, --file ou --split, avec leurs lignes brutes."""
    if args.file:
        with open(args.file, encoding="utf-8", errors="replace") as f:
            return lines_by_block(f.readlines())
    with open(SAMPLE_LOG, encoding="utf-8") as f:
        sample = lines_by_block(f.readlines())
    split = official_split()
    if args.block:
        if split.get(args.block) == "test":
            raise SystemExit("Bloc du split test : réservé à l'évaluation finale (SCRUM-45).")
        if args.block not in sample:
            raise SystemExit(f"{args.block} absent de {SAMPLE_LOG} : utiliser --file avec ses lignes brutes.")
        return {args.block: sample[args.block]}
    traces = load_traces(sample=True)
    chosen = traces[traces["BlockId"].map(split) == args.split].sample(n=args.n, random_state=args.seed)
    return {b: sample[b] for b in chosen["BlockId"]}


def metrics(records: list[dict]) -> dict:
    """Effectifs et taux du run ; les échecs restent dans le dénominateur."""
    n = len(records)
    parsed = [r for r in records if r["parsed_response"] is not None]
    valid = [r for r in records if not r["errors"]]
    answers = [r["parsed_response"] for r in valid]
    return {
        "n_blocks": n,
        "json_valid": len(parsed),
        "c5_valid": len(valid),
        "abstentions": sum(a["abstention"] for a in answers),
        "answers_with_sources": sum(bool(a["sources"]) for a in answers),
        "errors": dict(Counter(e.split(" :")[0] for r in records for e in r["errors"])),
        "seconds_total": round(sum(r["seconds"] for r in records), 2),
        "new_tokens_total": sum(r["new_tokens"] for r in records),
        "units": {"seconds": "temps de génération du SLM (hors chargement et retrieval)"},
    }


def git_commit() -> str | None:
    """Commit courant du dépôt (None hors de Git)."""
    out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    return out.stdout.strip() or None


def main(argv=None):
    """Ligne de commande : explique les blocs choisis et écrit le dossier C7 du run."""
    parser = argparse.ArgumentParser(description="SCRUM-37 : RAG de référence à un agent.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--block", help="Identifiant d'un bloc présent dans data/sample/.")
    source.add_argument("--file", help="Fichier de logs HDFS bruts : chaque bloc est expliqué.")
    source.add_argument("--split", choices=["train", "val"], help="Tirer --n blocs de ce split dans data/sample/.")
    parser.add_argument("--n", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--k", type=int, default=DEFAULT_K, help="Nombre de passages donnés au modèle.")
    parser.add_argument("--method", choices=METHODS, default=DEFAULT_METHOD)
    parser.add_argument("--adapter", help="Adaptateur LoRA (dossier), sinon modèle de base.")
    parser.add_argument("--mock", action="store_true", help="Sans modèle : réponse factice (TEAMAI_SLM_MOCK=1).")
    parser.add_argument("--offline", action="store_true", help="Modèle d'embeddings déjà en cache uniquement.")
    args = parser.parse_args(argv)
    if args.mock:
        os.environ["TEAMAI_SLM_MOCK"] = "1"

    blocks = select_blocks(args)
    retriever = load_retriever(args.method, local_files_only=args.offline)
    run_dir = new_run_directory(name="single_agent")
    records = []
    with open(run_dir / "predictions.jsonl", "w", encoding="utf-8") as out:
        for i, (block_id, lines) in enumerate(blocks.items(), start=1):
            record = explain_block(block_id, lines, retriever, args.k, args.adapter)
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            out.flush()
            records.append(record)
            status = "OK" if not record["errors"] else f"{len(record['errors'])} erreur(s)"
            print(f"[{i}/{len(blocks)}] {block_id} : {status}, sources récupérées "
                  f"{[p['id'].split('#', 1)[1] for p in record['steps']['retrieved']]}", flush=True)

    index_meta = json.loads(META_FILE.read_text(encoding="utf-8"))
    config = {
        "ticket": "SCRUM-37", "agents": 1, "slm_calls_per_block": 1,
        "source": {"block": args.block, "file": args.file, "split": args.split, "n": args.n, "seed": args.seed},
        "retrieval": {"method": args.method, "k": args.k, "embedding_model": index_meta["model"],
                      "embedding_revision": index_meta["revision"], "chunks_sha256": index_meta["chunks_sha256"]},
        "prompt": PROMPT.name, "prompt_sha256": hashlib.sha256(PROMPT.read_bytes()).hexdigest(),
        "generation": load_config(), "adapter": args.adapter,
        "mock": os.environ.get("TEAMAI_SLM_MOCK") == "1", "commit": git_commit(),
        "machine": {"python": platform.python_version(), "platform": platform.platform()},
    }
    (run_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    summary = metrics(records)
    (run_dir / "metrics.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "units"}, ensure_ascii=False))
    print(f"Run : {run_dir}")


if __name__ == "__main__":
    main()
