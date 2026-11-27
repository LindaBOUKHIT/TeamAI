"""Chemins centralisés : toujours importer d'ici plutôt que d'écrire des chemins en dur.

Tous les chemins partent de la racine du dépôt, quel que soit le dossier courant.
Les scripts se lancent depuis la racine avec `python -m paquet.module`.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATA = ROOT / "data"
RAW = DATA / "raw"
RAW_HDFS = RAW / "HDFS_v1"
PREPROCESSED = RAW_HDFS / "preprocessed"
PARSED = DATA / "parsed"
SAMPLE = DATA / "sample"
SPLITS = DATA / "splits"

VOLET_A = ROOT / "volet_a"
TRAINING = VOLET_A / "training"
VOLET_A_RESULTS = VOLET_A / "results"
WEB_PUBLIC = VOLET_A / "web" / "public"
MODEL_DIR = WEB_PUBLIC / "model"

VOLET_B = ROOT / "volet_b"
RAG = VOLET_B / "rag"
CORPUS = RAG / "corpus"
RAG_INDEX = RAG / "index"
AGENTS = VOLET_B / "agents"
APP_ASSETS = VOLET_B / "app" / "assets"
PROMPTS = AGENTS / "prompts"
SLM = VOLET_B / "slm"
SLM_CONFIGS = SLM / "configs"
SLM_ADAPTERS = SLM / "adapters"
ANNOTATIONS = VOLET_B / "annotations"

DOCS = ROOT / "docs"
RAPPORT = DOCS / "rapport"
RAPPORT_FINAL = RAPPORT / "final"

EVAL = ROOT / "eval"
EVAL_VOLET_B = EVAL / "volet_b"
VOLET_B_TEST = EVAL_VOLET_B / "test.jsonl"
VOLET_B_TEST_SHA256 = EVAL_VOLET_B / "test.sha256"
VOLET_B_TEST_INPUTS = EVAL_VOLET_B / "test_inputs.jsonl"
VOLET_B_TEST_INPUTS_SHA256 = EVAL_VOLET_B / "test_inputs.sha256"
VOLET_B_DOUBLE_ANNOTATION = EVAL_VOLET_B / "double_annotation.csv"
VOLET_B_BLIND = EVAL_VOLET_B / "double_annotation"
RESULTS = EVAL / "results"
VOLET_B_SUMMARY = RESULTS / "volet_b.md"
VOLET_B_PROMPT_FREEZE = RESULTS / "SCRUM-63" / "prompt_freeze.json"
RUNS = EVAL / "runs"


def resolve_path(value: str | Path) -> Path:
    """Résout un chemin fourni par l'utilisateur, relatif à la racine du dépôt."""
    path = Path(value).expanduser()
    return (ROOT / path).resolve() if not path.is_absolute() else path.resolve()
