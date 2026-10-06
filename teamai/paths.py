"""Chemins centralisés : toujours importer d'ici plutôt que d'écrire des chemins en dur."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATA = ROOT / "data"
RAW_HDFS = DATA / "raw" / "HDFS_v1"
PREPROCESSED = RAW_HDFS / "preprocessed"
SAMPLE = DATA / "sample"
SPLITS = DATA / "splits"

VOLET_A = ROOT / "volet_a"
WEB_PUBLIC = VOLET_A / "web" / "public"

VOLET_B = ROOT / "volet_b"
RAG = VOLET_B / "rag"
ANNOTATIONS = VOLET_B / "annotations"

EVAL = ROOT / "eval"
RESULTS = EVAL / "results"
RUNS = EVAL / "runs"
