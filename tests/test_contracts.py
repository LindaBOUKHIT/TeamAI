"""Validateur du format C5 (exemples d'explication et réponses du SLM)."""
import json

import pytest

from teamai.contracts import leaked_blocks, load_jsonl, validate_answer, validate_example


def test_reponse_valide(valid_answer):
    """Une réponse complète et sourcée ne produit aucune erreur."""
    assert validate_answer(valid_answer) == []


def test_reponse_sans_source_est_valide(valid_answer):
    """Configuration sans RAG : une réponse sans source reste conforme."""
    assert validate_answer({**valid_answer, "sources": []}) == []


def test_abstention_valide(valid_answer):
    """Abstention conforme : aucune hypothèse, une raison dans infos_manquantes."""
    answer = {**valid_answer, "hypotheses": [], "sources": [], "abstention": True}
    assert validate_answer(answer) == []


@pytest.mark.parametrize(
    "change, attendu",
    [
        ({"resume_evenements": ""}, "resume_evenements"),
        ({"faits_observes": "E4"}, "faits_observes"),
        ({"abstention": "non"}, "abstention"),
        ({"abstention": True}, "hypotheses"),  # abstention qui garde des hypothèses
        ({"abstention": True, "hypotheses": [], "infos_manquantes": []}, "infos_manquantes"),
    ],
)
def test_reponse_invalide(valid_answer, change, attendu):
    """Chaque écart au format C5 est signalé par une erreur préfixée par le champ fautif."""
    errors = validate_answer({**valid_answer, **change})
    assert any(e.startswith(attendu) for e in errors), errors


def test_sources_limitees_aux_passages_fournis(valid_answer):
    """Une citation absente des passages C6 fournis au modèle est une erreur."""
    assert validate_answer(valid_answer, allowed_sources=["hdfs-design#data-replication#2"]) == []
    errors = validate_answer(valid_answer, allowed_sources=["autre#passage#1"])
    assert any(e.startswith("sources") for e in errors), errors


def test_reponse_non_json_objet():
    """Une réponse qui n'est pas un objet JSON est refusée."""
    assert validate_answer(["pas", "un", "objet"])


def test_exemple_valide(valid_example):
    """Un exemple annoté complet ne produit aucune erreur."""
    assert validate_example(valid_example) == []


@pytest.mark.parametrize(
    "change, attendu",
    [
        ({"block_id": "8362325295506522506"}, "block_id"),
        ({"split": "validation"}, "split"),
        ({"label": "anomalie"}, "label"),
        ({"events": []}, "events"),
        ({"annotator": ""}, "annotator"),
        ({"reviewed_by": ""}, "reviewed_by"),
        ({"reviewed_by": "linda"}, "reviewed_by"),  # relecteur = annotateur
    ],
)
def test_exemple_invalide(valid_example, change, attendu):
    """Chaque champ d'exemple manquant ou mal typé est signalé."""
    errors = validate_example({**valid_example, **change})
    assert any(e.startswith(attendu) for e in errors), errors


def test_erreur_dans_expected_est_prefixee(valid_example):
    """Les erreurs du bloc expected sont préfixées par « expected. »."""
    example = {**valid_example, "expected": {**valid_example["expected"], "abstention": None}}
    assert "expected.abstention : booléen attendu" in validate_example(example)


def test_load_jsonl_signale_la_ligne_fautive(tmp_path, valid_example):
    """Une ligne JSONL illisible lève une erreur qui cite le fichier et le numéro de ligne."""
    path = tmp_path / "lot.jsonl"
    path.write_text(json.dumps(valid_example) + "\n{pas du json\n", encoding="utf-8")
    with pytest.raises(ValueError, match="lot.jsonl:2"):
        load_jsonl(path)


def test_detection_de_fuite_vers_le_test(valid_example):
    """leaked_blocks repère un bloc présent à la fois en adaptation et dans le test."""
    train = [valid_example, {**valid_example, "block_id": "blk_1"}]
    test = [{**valid_example, "split": "test"}]
    assert leaked_blocks(train, test) == {"blk_8362325295506522506"}
    assert leaked_blocks(train[1:], test) == set()


def test_validate_answer_sources_non_textuelles():
    """Une source qui n'est pas un texte (ex. un objet) est une erreur, jamais une exception."""
    answer = {"resume_evenements": "r", "faits_observes": [], "hypotheses": [], "infos_manquantes": [],
              "sources": [{"id": "x"}], "abstention": False}
    errors = validate_answer(answer, allowed_sources=[])
    assert any(e.startswith("sources") for e in errors)
