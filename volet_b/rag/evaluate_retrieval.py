"""SCRUM-37 — Rappel@k du retrieval sur la validation, pour choisir la méthode et la requête.

    python -m volet_b.rag.evaluate_retrieval      # → eval/results/SCRUM-37/retrieval_val.json

Référence : la table « template E1–E29 → passage C6 ou aucun » de docs/volet_b/corpus_rag.md
(SCRUM-30). Deux niveaux :
- templates : pour chacun des événements qui ont un passage de référence, la requête construite pour
  cet événement seul retrouve-t-elle ce passage dans le top k ?
- traces : sur les blocs du split `val` de data/sample/, part des passages de référence de la trace
  (union sur ses événements) présents dans le top k, en moyenne sur les traces qui en ont au moins un.

Limite : la référence et les paraphrases d'événements ont été écrites par l'équipe ; ce n'est pas un
jugement indépendant de la pertinence. Le test n'est jamais utilisé.
"""
import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone

import pandas as pd

from teamai.data.loader import load_traces
from teamai.paths import DOCS, RESULTS, SPLITS
from volet_b.rag.retriever import DEFAULT_K, load_retriever, query_for_events

COVERAGE_TABLE = DOCS / "volet_b" / "corpus_rag.md"
OUTPUT = RESULTS / "SCRUM-37" / "retrieval_val.json"
VARIANTS = [("dense", "template"), ("dense", "description"), ("bm25", "description"), ("hybrid", "description")]


def reference_passages(path=COVERAGE_TABLE) -> dict[str, str]:
    """EventId → identifiant C6 du passage de référence (lignes « aucun » exclues)."""
    reference = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\| (E\d+) .*?\| `([^`]+)`", line)
        if match:
            reference[match.group(1)] = match.group(2)
    return reference


def val_sequences() -> Counter:
    """Séquences d'événements des blocs `val` de l'échantillon, avec leur nombre d'occurrences."""
    split = pd.read_csv(SPLITS / "splits.csv", usecols=["BlockId", "split"]).set_index("BlockId")["split"]
    traces = load_traces(sample=True)
    traces = traces[traces["BlockId"].map(split) == "val"]
    return Counter(tuple(events) for events in traces["events"])


def evaluate(retriever, reference: dict, sequences: Counter, method: str, mode: str, k: int) -> dict:
    """Mesures au niveau des templates et des traces pour une méthode et un type de requête."""
    template_hits = {}
    for event_id, passage_id in reference.items():
        top = [p["id"] for p in retriever.search(query_for_events([event_id], mode), k, method=method)]
        template_hits[event_id] = {"expected": passage_id, "rank": top.index(passage_id) + 1 if passage_id in top else None,
                                   "top": top}
    recall_sum, complete, n_traces, n_without = 0.0, 0, 0, 0
    for sequence, count in sequences.items():
        expected = {reference[e] for e in sequence if e in reference}
        if not expected:
            n_without += count
            continue
        top = {p["id"] for p in retriever.search(query_for_events(list(sequence), mode), k, method=method)}
        recall_sum += count * len(expected & top) / len(expected)
        complete += count * (expected <= top)
        n_traces += count
    hits = sum(h["rank"] is not None for h in template_hits.values())
    return {
        "method": method, "query": mode, "k": k,
        "templates_hit_at_k": f"{hits}/{len(template_hits)}",
        "traces_recall_at_k": round(recall_sum / n_traces, 4) if n_traces else None,
        "traces_all_expected_at_k": round(complete / n_traces, 4) if n_traces else None,
        "n_traces": n_traces, "n_traces_without_reference": n_without,
        "templates": template_hits,
    }


def main(argv=None):
    """Évalue les variantes de VARIANTS et écrit le résumé versionné."""
    parser = argparse.ArgumentParser(description="SCRUM-37 : rappel@k du retrieval sur la validation.")
    parser.add_argument("--k", type=int, default=DEFAULT_K)
    parser.add_argument("--offline", action="store_true", help="Modèle d'embeddings déjà en cache uniquement.")
    args = parser.parse_args(argv)
    retriever = load_retriever(local_files_only=args.offline)
    reference, sequences = reference_passages(), val_sequences()
    results = [evaluate(retriever, reference, sequences, method, mode, args.k) for method, mode in VARIANTS]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({
        "ticket": "SCRUM-37", "split": "val (data/sample)", "reference": str(COVERAGE_TABLE.relative_to(DOCS.parent)),
        "evaluated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "variants": results,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for r in results:
        print(f"{r['method']:7s} {r['query']:12s} templates {r['templates_hit_at_k']:>5s} | "
              f"rappel@{r['k']} traces {r['traces_recall_at_k']} | tous trouvés {r['traces_all_expected_at_k']} "
              f"(n={r['n_traces']}, sans référence : {r['n_traces_without_reference']})")
    print(f"Résultats : {OUTPUT}")


if __name__ == "__main__":
    main()
