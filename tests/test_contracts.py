"""Validateur du format C5 (exemples d'explication et réponses du SLM)."""
import json

import pytest

from teamai.contracts import leaked_blocks, load_jsonl, validate_answer, validate_example


def test_reponse_valide(valid_answer):
    assert validate_answer(valid_answer) == []


def test_abstention_sans_source_est_valide(valid_answer):
    answer = {**valid_answer, "sources": [], "abstention": True}
    assert validate_answer(answer) == []


@pytest.mark.parametrize(
    "change, attendu",
    [
        ({"resume_evenements": ""}, "resume_evenements"),
        ({"faits_observes": "E4"}, "faits_observes"),
        ({"abstention": "non"}, "abstention"),
        ({"sources": []}, "sources"),  # réponse sans abstention ni source
    ],
)
def test_reponse_invalide(valid_answer, change, attendu):
    errors = validate_answer({**valid_answer, **change})
    assert any(e.startswith(attendu) for e in errors), errors


def test_reponse_non_json_objet():
    assert validate_answer(["pas", "un", "objet"])


def test_exemple_valide(valid_example):
    assert validate_example(valid_example) == []


@pytest.mark.parametrize(
    "change, attendu",
    [
        ({"block_id": "8362325295506522506"}, "block_id"),
        ({"split": "validation"}, "split"),
        ({"label": "anomalie"}, "label"),
        ({"events": []}, "events"),
        ({"annotator": ""}, "annotator"),
    ],
)
def test_exemple_invalide(valid_example, change, attendu):
    errors = validate_example({**valid_example, **change})
    assert any(e.startswith(attendu) for e in errors), errors


def test_erreur_dans_expected_est_prefixee(valid_example):
    example = {**valid_example, "expected": {**valid_example["expected"], "abstention": None}}
    assert "expected.abstention : booléen attendu" in validate_example(example)


def test_load_jsonl_signale_la_ligne_fautive(tmp_path, valid_example):
    path = tmp_path / "lot.jsonl"
    path.write_text(json.dumps(valid_example) + "\n{pas du json\n", encoding="utf-8")
    with pytest.raises(ValueError, match="lot.jsonl:2"):
        load_jsonl(path)


def test_detection_de_fuite_vers_le_test(valid_example):
    train = [valid_example, {**valid_example, "block_id": "blk_1"}]
    test = [{**valid_example, "split": "test"}]
    assert leaked_blocks(train, test) == {"blk_8362325295506522506"}
    assert leaked_blocks(train[1:], test) == set()
