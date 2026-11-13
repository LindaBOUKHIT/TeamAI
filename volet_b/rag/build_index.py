"""SCRUM-37 — Encode les passages C6 du corpus et construit l'index FAISS du RAG.

    python -m volet_b.rag.build_index            # → volet_b/rag/index/index.faiss + meta.json (non versionnés)

L'index est exact (IndexFlatIP sur vecteurs normalisés = similarité cosinus). `meta.json` garde le
modèle d'embeddings et sa révision figée, l'empreinte de chunks.jsonl et l'ordre des identifiants :
le retriever refuse un index qui ne correspond plus au corpus.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone

import numpy as np

from teamai.paths import RAG_INDEX
from volet_b.rag.retriever import (
    CHUNKS, EMBEDDING_MODEL, INDEX_FILE, META_FILE, QUERY_INSTRUCTION, load_encoder, load_passages, passage_text,
)


def model_revision(model_id: str) -> str | None:
    """Commit Hugging Face du modèle d'embeddings, pour pouvoir le recharger à l'identique."""
    try:
        from huggingface_hub import HfApi

        return HfApi().model_info(model_id).sha
    except Exception:  # hors ligne : la révision du cache local reste utilisable, mais n'est pas figée
        return None


def build(model_id: str = EMBEDDING_MODEL) -> dict:
    """Encode les passages, écrit index.faiss et meta.json, et rend les métadonnées."""
    import faiss

    passages = load_passages()
    revision = model_revision(model_id)
    encoder = load_encoder(model_id, revision)
    vectors = encoder.encode([passage_text(p) for p in passages], normalize_embeddings=True, batch_size=16)
    vectors = np.asarray(vectors, dtype="float32")
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    RAG_INDEX.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_FILE))
    meta = {
        "model": model_id,
        "revision": revision,
        "query_instruction": QUERY_INSTRUCTION,
        "dimension": int(vectors.shape[1]),
        "similarity": "cosine (IndexFlatIP, vecteurs normalisés)",
        "chunks_sha256": hashlib.sha256(CHUNKS.read_bytes()).hexdigest(),
        "ids": [p["id"] for p in passages],
        "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    META_FILE.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return meta


def main(argv=None):
    """Ligne de commande : construit l'index et affiche un résumé."""
    parser = argparse.ArgumentParser(description="SCRUM-37 : index FAISS des passages C6.")
    parser.add_argument("--model", default=EMBEDDING_MODEL)
    args = parser.parse_args(argv)
    meta = build(args.model)
    print(f"{len(meta['ids'])} passages encodés ({meta['model']}@{meta['revision']}, dim {meta['dimension']})")
    print(f"Index : {INDEX_FILE}")


if __name__ == "__main__":
    main()
