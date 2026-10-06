"""Configuration commune des tests.

Les tests tournent sur de petites données d'exemple (tests/fixtures/, ~5 Ko extraits de HDFS_v1)
pour être rapides et exécutables partout, y compris sur GitHub Actions. Les tests qui ont besoin
du corpus complet (data/raw/, 1,5 Go) sont marqués `full_data` et sautés s'il est absent.
"""
from pathlib import Path

import pytest

from teamai import paths

FIXTURES = Path(__file__).parent / "fixtures"
HAS_FULL_DATA = (paths.PREPROCESSED / "Event_traces.csv").exists()


def pytest_collection_modifyitems(config, items):
    skip = pytest.mark.skip(reason="corpus complet absent : lancer python data/download_hdfs.py")
    for item in items:
        if "full_data" in item.keywords and not HAS_FULL_DATA:
            item.add_marker(skip)


@pytest.fixture
def fixture_data(monkeypatch):
    """Redirige le chargeur vers tests/fixtures/ (12 traces dont 4 anomalies, 29 templates)."""
    from teamai.data import loader

    monkeypatch.setattr(loader, "PREPROCESSED", FIXTURES / "preprocessed")
    return loader


@pytest.fixture
def valid_answer():
    return {
        "resume_evenements": "Le bloc est alloué puis reçu par 3 DataNodes ; deux exceptions surviennent en lecture.",
        "faits_observes": ["E4 : exception en servant le bloc à un client"],
        "hypotheses": ["DataNode surchargé ou client déconnecté"],
        "infos_manquantes": ["État réseau au moment de l'erreur"],
        "sources": ["hdfs-design#data-replication#2"],
        "abstention": False,
    }


@pytest.fixture
def valid_example(valid_answer):
    return {
        "id": "ex-0001",
        "block_id": "blk_8362325295506522506",
        "split": "train",
        "trace_lines": ["081109 203958 309 INFO dfs.DataNode$DataXceiver: Receiving block blk_8362325295506522506"],
        "events": ["E5", "E22", "E4"],
        "label": 1,
        "expected": valid_answer,
        "annotator": "linda",
        "reviewed_by": "alain",
    }
