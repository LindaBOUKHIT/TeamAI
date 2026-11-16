"""SCRUM-37 — Recherche des passages documentaires (C6) les plus proches d'une trace HDFS.

    from volet_b.rag.retriever import load_retriever, query_for_events
    retriever = load_retriever()                         # index construit par build_index.py
    query = query_for_events(["E22", "E5", "E5", "E7"])  # paraphrases anglaises des événements
    passages = retriever.search(query, k=3)              # [{id, doc, section, text, source_url, version, score, …}]

La requête décrit les événements distincts de la trace, dans leur ordre d'apparition, avec la
paraphrase anglaise de chaque template (event_descriptions.json) : les templates bruts (« allocateBlock »,
« Receiving block src dest ») sont trop courts. Elle ne contient jamais le label ni une réponse attendue.

Trois méthodes (`method`) : `dense` (embeddings BGE + index FAISS, cosinus), `bm25` (mots-clés) et
`hybrid` (défaut : fusion des deux classements par Reciprocal Rank Fusion). Le choix est mesuré sur
la validation par evaluate_retrieval.py. Les passages sont rendus par score décroissant ; avec
`min_score`, une liste vide signale qu'aucun passage n'est assez proche (réponse avec `sources: []`).
"""
import json
import re
from functools import lru_cache

import numpy as np

from teamai.data.preprocess import load_vocab_json
from teamai.paths import CORPUS, RAG, RAG_INDEX

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
# Préfixe recommandé par les auteurs de BGE pour les requêtes (les passages sont encodés sans préfixe).
QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "
DEFAULT_K = 3
DEFAULT_METHOD = "hybrid"
METHODS = ("dense", "bm25", "hybrid")
RRF_K = 60  # constante usuelle de la Reciprocal Rank Fusion
CHUNKS = CORPUS / "chunks.jsonl"
INDEX_FILE = RAG_INDEX / "index.faiss"
META_FILE = RAG_INDEX / "meta.json"
EVENT_DESCRIPTIONS = RAG / "event_descriptions.json"

_NOISE = re.compile(r"\[\*\]|BLOCK\*|NameSystem|[^\w\s.'-]")
_WORD = re.compile(r"[a-z]+")


def load_passages(path=CHUNKS) -> list[dict]:
    """Passages C6 du corpus, dans l'ordre du fichier (cet ordre fixe les positions dans l'index)."""
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def passage_text(passage: dict) -> str:
    """Texte indexé pour un passage : titre du guide et de la section, puis contenu."""
    return f"{passage['doc']}, {passage['section']}. {passage['text']}"


def tokenize(text: str) -> list[str]:
    """Mots en minuscules pour BM25."""
    return _WORD.findall(text.lower())


def load_event_descriptions(path=EVENT_DESCRIPTIONS) -> dict[str, str]:
    """Paraphrase anglaise de chaque EventId (E1…E29)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if not k.startswith("_")}


def query_for_events(events: list[str], mode: str = "description", vocab: dict | None = None) -> str:
    """Requête en anglais pour les événements distincts de la trace, dans leur ordre d'apparition.

    `mode="description"` (défaut) utilise event_descriptions.json ; `mode="template"` le template brut,
    gardé pour la comparaison de evaluate_retrieval.py.
    """
    if mode == "description":
        descriptions = load_event_descriptions()
        return ". ".join(descriptions[e] for e in dict.fromkeys(events) if e in descriptions)
    if mode != "template":
        raise ValueError(f"mode inconnu : {mode!r}")
    vocab = vocab or load_vocab_json()
    templates = []
    for event_id in dict.fromkeys(events):
        spec = vocab["events"].get(event_id)
        if spec:
            templates.append(" ".join(_NOISE.sub(" ", spec["template"]).split()))
    return "; ".join(templates)


class Retriever:
    """Recherche exacte sur les passages C6 : embeddings (cosinus), BM25, ou fusion des deux.

    `vectors` sont les embeddings des passages (même ordre), `encode_query` encode une requête ;
    `index` est un index FAISS facultatif (sinon numpy, avec le même résultat sur 51 passages).
    """

    def __init__(self, passages: list[dict], vectors, encode_query, index=None, method: str = DEFAULT_METHOD):
        """Associe chaque passage à son vecteur et prépare l'index BM25."""
        if method not in METHODS:
            raise ValueError(f"méthode inconnue : {method!r} (attendu : {METHODS})")
        self.passages = list(passages)
        self.vectors = _normalize(np.asarray(vectors, dtype="float32"))
        if len(self.passages) != len(self.vectors):
            raise ValueError(f"{len(self.passages)} passages pour {len(self.vectors)} vecteurs")
        self.encode_query = encode_query
        self.index = index
        self.method = method
        self._bm25 = None

    def dense_ranking(self, query: str) -> list[tuple[int, float]]:
        """Tous les passages, du plus proche au plus lointain, avec leur cosinus."""
        q = _normalize(np.asarray(self.encode_query(query), dtype="float32").reshape(1, -1))
        if self.index is not None:
            scores, positions = self.index.search(q, len(self.passages))
            return list(zip(positions[0].tolist(), scores[0].tolist()))
        scores = self.vectors @ q[0]
        return [(int(i), float(scores[i])) for i in np.argsort(-scores, kind="stable")]

    def bm25_ranking(self, query: str) -> list[tuple[int, float]]:
        """Tous les passages classés par score BM25 sur les mots de la requête."""
        if self._bm25 is None:
            from rank_bm25 import BM25Okapi

            self._bm25 = BM25Okapi([tokenize(passage_text(p)) for p in self.passages])
        scores = self._bm25.get_scores(tokenize(query))
        return [(int(i), float(scores[i])) for i in np.argsort(-scores, kind="stable")]

    def search(self, query: str, k: int = DEFAULT_K, min_score: float | None = None,
               method: str | None = None) -> list[dict]:
        """Les k passages C6 les plus proches de `query`, avec `score` (4 décimales) et le détail par méthode."""
        method = method or self.method
        if not query.strip():
            return []
        if method == "dense":
            ranked = [(i, s, {"dense": s}) for i, s in self.dense_ranking(query)]
        elif method == "bm25":
            ranked = [(i, s, {"bm25": s}) for i, s in self.bm25_ranking(query)]
        else:
            dense, bm25 = self.dense_ranking(query), self.bm25_ranking(query)
            fused, detail = {}, {}
            for name, ranking in (("dense", dense), ("bm25", bm25)):
                for rank, (i, s) in enumerate(ranking):
                    fused[i] = fused.get(i, 0.0) + 1.0 / (RRF_K + rank + 1)
                    detail.setdefault(i, {})[name] = s
            order = sorted(fused, key=lambda i: (-fused[i], i))
            ranked = [(i, fused[i], detail[i]) for i in order]
        results = [
            {**self.passages[i], "score": round(s, 4), "scores": {m: round(v, 4) for m, v in d.items()}}
            for i, s, d in ranked[:k]
        ]
        if min_score is not None:
            results = [p for p in results if p["score"] >= min_score]
        return results


def _normalize(matrix: np.ndarray) -> np.ndarray:
    """Normalise chaque ligne (norme 1) pour que le produit scalaire soit un cosinus."""
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix / np.where(norms == 0, 1, norms)


def load_encoder(model_id: str = EMBEDDING_MODEL, revision: str | None = None, local_files_only: bool = False):
    """Modèle d'embeddings sentence-transformers (téléchargé une fois dans le cache Hugging Face)."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_id, revision=revision, local_files_only=local_files_only, device="cpu")


@lru_cache(maxsize=2)
def load_retriever(method: str = DEFAULT_METHOD, local_files_only: bool = False) -> Retriever:
    """Retriever prêt à l'emploi, à partir de l'index de build_index.py (même modèle et même révision)."""
    import faiss

    if not INDEX_FILE.exists():
        raise FileNotFoundError(f"Index absent : lancer d'abord `python -m volet_b.rag.build_index` ({INDEX_FILE})")
    meta = json.loads(META_FILE.read_text(encoding="utf-8"))
    passages = load_passages()
    if [p["id"] for p in passages] != meta["ids"]:
        raise ValueError("chunks.jsonl a changé depuis la construction de l'index : relancer build_index")
    index = faiss.read_index(str(INDEX_FILE))
    encoder = load_encoder(meta["model"], meta["revision"], local_files_only)

    def encode_query(text: str):
        """Encode une requête avec le préfixe BGE."""
        return encoder.encode(meta["query_instruction"] + text, normalize_embeddings=True)

    return Retriever(passages, index.reconstruct_n(0, index.ntotal), encode_query, index=index, method=method)
