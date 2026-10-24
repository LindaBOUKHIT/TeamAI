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
PROMPTS = AGENTS / "prompts"
SLM = VOLET_B / "slm"
SLM_CONFIGS = SLM / "configs"
ANNOTATIONS = VOLET_B / "annotations"

DOCS = ROOT / "docs"

EVAL = ROOT / "eval"
RESULTS = EVAL / "results"
RUNS = EVAL / "runs"
