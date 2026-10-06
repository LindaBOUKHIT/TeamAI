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
    for n, example in enumerate(load_jsonl(path), start=1):
        assert validate_example(example) == [], f"{path.name}, exemple n°{n} ({example.get('id')})"


@pytest.mark.skipif(not TEST_SET.exists(), reason="jeu de test réservé pas encore constitué (SCRUM-35)")
def test_jeu_de_test_respecte_C5():
    for example in load_jsonl(TEST_SET):
        assert validate_example(example) == [], example.get("id")
        assert example["split"] == "test"


@pytest.mark.skipif(not TEST_SET.exists() or not ANNOTATIONS, reason="annotations ou test absents")
def test_aucune_trace_du_test_dans_les_annotations():
    training = [row for path in ANNOTATIONS for row in load_jsonl(path)]
    assert leaked_blocks(training, load_jsonl(TEST_SET)) == set()
