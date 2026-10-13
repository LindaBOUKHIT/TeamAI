"""Garde-fous sur les fichiers réellement présents dans le dépôt.

Ces tests ne font rien tant que les fichiers n'existent pas, puis protègent automatiquement
le travail de chacun dès qu'ils sont ajoutés (annotations, jeu de test réservé).
"""
import pytest

from teamai import paths
from teamai.contracts import leaked_blocks, load_jsonl, validate_example

ANNOTATIONS = sorted(paths.ANNOTATIONS.glob("*.jsonl"))
TEST_SET = paths.EVAL / "volet_b" / "test.jsonl"


@pytest.mark.parametrize("path", ANNOTATIONS, ids=lambda p: p.name)
def test_annotations_respectent_C5(path):
    """Chaque exemple de volet_b/annotations/*.jsonl respecte C5."""
    for n, example in enumerate(load_jsonl(path), start=1):
        assert validate_example(example) == [], f"{path.name}, exemple n°{n} ({example.get('id')})"


@pytest.mark.parametrize("path", ANNOTATIONS, ids=lambda p: p.name)
def test_sources_des_annotations_existent_dans_le_corpus(path):
    """Chaque source citée est un identifiant existant de volet_b/rag/corpus/chunks.jsonl (C6)."""
    corpus_ids = {passage["id"] for passage in load_jsonl(paths.RAG / "corpus" / "chunks.jsonl")}
    for example in load_jsonl(path):
        unknown = set(example["expected"]["sources"]) - corpus_ids
        assert not unknown, f"{path.name}, {example['id']} : sources absentes du corpus {sorted(unknown)}"


@pytest.mark.parametrize("path", ANNOTATIONS, ids=lambda p: p.name)
def test_annotations_hors_test_et_split_conforme(path):
    """Chaque exemple d'adaptation vient de train ou val, conformément à data/splits/splits.csv (C4)."""
    import pandas as pd

    official = pd.read_csv(paths.SPLITS / "splits.csv", usecols=["BlockId", "split"]).set_index("BlockId")["split"]
    for example in load_jsonl(path):
        assert example["split"] in ("train", "val"), f"{path.name}, {example['id']} : split {example['split']}"
        assert official.get(example["block_id"]) == example["split"], f"{path.name}, {example['id']}"


@pytest.mark.skipif(not TEST_SET.exists(), reason="jeu de test réservé pas encore constitué (SCRUM-35)")
def test_jeu_de_test_respecte_C5():
    """Le test réservé respecte C5 et ne contient que des exemples du split test."""
    for example in load_jsonl(TEST_SET):
        assert validate_example(example) == [], example.get("id")
        assert example["split"] == "test"


@pytest.mark.skipif(not TEST_SET.exists() or not ANNOTATIONS, reason="annotations ou test absents")
def test_aucune_trace_du_test_dans_les_annotations():
    """Aucun bloc du test réservé ne sert à l'adaptation."""
    training = [row for path in ANNOTATIONS for row in load_jsonl(path)]
    assert leaked_blocks(training, load_jsonl(TEST_SET)) == set()
