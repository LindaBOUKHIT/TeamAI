"""SCRUM-26 : vocabulaire C2 et prétraitement Python, référence du prétraitement JavaScript."""
import json
import os

import pytest

from teamai import paths
from teamai.data.loader import load_traces
from teamai.data.preprocess import UNKNOWN_EVENT, build_vocab, load_vocab_json, parse_lines, template_to_regex

FIXTURE_TEMPLATES = paths.ROOT / "tests" / "fixtures" / "preprocessed" / "HDFS.log_templates.csv"
PARITY_CASES = json.loads((paths.WEB_PUBLIC.parent / "tests" / "parity_cases.json").read_text(encoding="utf-8"))["cases"]


def test_vocab_json_a_jour_avec_les_templates():
    """Le vocab.json publié correspond aux 29 templates : relancer `python -m teamai.data.preprocess` sinon."""
    assert load_vocab_json() == build_vocab(FIXTURE_TEMPLATES)


def test_vocab_json_respecte_C2():
    """Ids 1..29 dans l'ordre des EventId, padding 0, inconnu 30, longueur 50."""
    vocab = load_vocab_json()
    assert (vocab["pad_id"], vocab["unk_id"], vocab["max_len"]) == (0, 30, 50)
    assert [spec["id"] for spec in vocab["events"].values()] == list(range(1, 30))
    assert list(vocab["events"]) == [f"E{i}" for i in range(1, 30)]


def test_template_to_regex_echappe_et_ancre():
    """Les caractères spéciaux sont échappés, [*] devient une partie variable, la regex est ancrée."""
    regex = template_to_regex("[*]BLOCK* NameSystem[*]allocateBlock:[*]")
    assert regex == r"^.*?BLOCK\* NameSystem.*?allocateBlock:.*?$"


def test_echantillon_identique_a_loghub():
    """Sur les 2 000 blocs de data/sample/, les séquences reconstruites == Features de Event_traces.csv."""
    expected = load_traces(sample=True).set_index("BlockId")["events"].to_dict()
    with open(paths.SAMPLE / "HDFS_sample.log", encoding="utf-8") as f:
        result = parse_lines(f, load_vocab_json())
    assert result["stats"]["unknown"] == 0
    assert result["sequences"] == expected


@pytest.mark.parametrize("case", PARITY_CASES, ids=lambda c: c["name"])
def test_cas_de_parite_partages_avec_javascript(case):
    """Mêmes séquences et compteurs que ceux attendus par volet_a/web/tests/parity.test.js."""
    result = parse_lines(case["lines"], load_vocab_json())
    assert result["sequences"] == case["expected_sequences"]
    assert result["stats"] == case["expected_stats"]


def test_ligne_inconnue_donne_UNK():
    """Une ligne HDFS valide qu'aucun template ne reconnaît est gardée comme événement inconnu."""
    line = "081109 203600 143 INFO dfs.DataNode$DataXceiver: Unexpected message about blk_7"
    assert parse_lines([line], load_vocab_json())["sequences"] == {"blk_7": [UNKNOWN_EVENT]}


@pytest.mark.full_data
@pytest.mark.skipif(os.environ.get("TEAMAI_FULL_PARITY") != "1", reason="plusieurs minutes : TEAMAI_FULL_PARITY=1")
def test_corpus_complet_identique_a_loghub():
    """Sur les 575 061 blocs de HDFS_v1 : parité complète avec Event_traces.csv (plusieurs minutes)."""
    expected = load_traces().set_index("BlockId")["events"].to_dict()
    with open(paths.RAW_HDFS / "HDFS.log", encoding="utf-8", errors="replace") as f:
        result = parse_lines(f, load_vocab_json())
    assert result["stats"]["unknown"] == 0
    assert result["sequences"] == expected
