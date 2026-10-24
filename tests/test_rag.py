"""SCRUM-37 : retriever, requête, contrôle des réponses et agent unique, sans modèle (CI)."""
import hashlib
import json
import re

import numpy as np
import pytest

from teamai.data.preprocess import load_vocab_json
from volet_b.agents.single_agent import build_messages, explain_block, lines_by_block
from volet_b.agents.validate import check_answer
from volet_b.rag.evaluate_retrieval import reference_passages
from volet_b.rag.retriever import Retriever, load_event_descriptions, load_passages, query_for_events
from volet_b.slm.generate import MOCK_ANSWER

PASSAGES = [
    {"id": "doc#staging#1", "doc": "Guide", "section": "Staging", "text": "The NameNode allocates a data block for the file",
     "source_url": "https://example.org/a", "version": "test"},
    {"id": "doc#pipeline#1", "doc": "Guide", "section": "Pipeline", "text": "A DataNode receives the block and forwards it to the next DataNode",
     "source_url": "https://example.org/b", "version": "test"},
    {"id": "doc#trash#1", "doc": "Guide", "section": "Trash", "text": "A deleted file goes to the trash directory",
     "source_url": "https://example.org/c", "version": "test"},
]


def fake_encode(text: str) -> np.ndarray:
    """Encodeur de test déterministe : sac de mots haché sur 64 dimensions."""
    vector = np.zeros(64, dtype="float32")
    for word in re.findall(r"[a-z]+", text.lower()):
        vector[int(hashlib.md5(word.encode()).hexdigest(), 16) % 64] += 1
    return vector


def fake_retriever(method: str = "dense") -> Retriever:
    """Retriever sur les 3 passages de test, avec l'encodeur haché."""
    vectors = [fake_encode(f"{p['doc']}, {p['section']}. {p['text']}") for p in PASSAGES]
    return Retriever(PASSAGES, vectors, fake_encode, method=method)


def test_descriptions_couvrent_les_29_evenements():
    """Chaque EventId du vocabulaire C2 a une paraphrase anglaise non vide."""
    descriptions = load_event_descriptions()
    assert set(descriptions) == set(load_vocab_json()["events"])
    assert all(text.strip() for text in descriptions.values())


def test_requete_evenements_distincts_dans_l_ordre():
    """La requête cite chaque événement une fois, dans l'ordre d'apparition, sans label."""
    descriptions = load_event_descriptions()
    query = query_for_events(["E22", "E5", "E5", "E7"])
    assert query == ". ".join(descriptions[e] for e in ("E22", "E5", "E7"))
    assert query_for_events(["E22"], mode="template") == "allocateBlock"


def test_recherche_dense_classe_et_garde_le_format_c6():
    """Les k passages sont rendus au format C6 avec un score, du plus proche au plus lointain."""
    results = fake_retriever().search("NameNode allocates a block", k=2)
    assert [p["id"] for p in results][0] == "doc#staging#1"
    assert len(results) == 2
    assert {"id", "doc", "section", "text", "source_url", "version", "score", "scores"} <= set(results[0])
    assert results[0]["score"] >= results[1]["score"]


def test_min_score_et_requete_vide_donnent_une_liste_vide():
    """Sans passage assez proche (ou sans requête), la liste est vide : la réponse garde sources: []."""
    retriever = fake_retriever()
    assert retriever.search("zzz qqq", k=3, min_score=0.5) == []
    assert retriever.search("   ") == []


def test_recherche_hybride_fusionne_dense_et_bm25():
    """La fusion RRF rend un score par passage et le détail des deux méthodes."""
    pytest.importorskip("rank_bm25")
    results = fake_retriever("hybrid").search("deleted file trash", k=3)
    assert results[0]["id"] == "doc#trash#1"
    assert set(results[0]["scores"]) == {"dense", "bm25"}


def test_references_de_la_table_de_couverture_existent_dans_le_corpus():
    """Les passages de référence de corpus_rag.md (rappel@k) sont des identifiants C6 réels."""
    reference = reference_passages()
    assert len(reference) >= 10
    assert set(reference.values()) <= {p["id"] for p in load_passages()}


@pytest.mark.parametrize("text, erreur", [
    ("pas de json", "invalid_json"),
    ('{"resume_evenements": ', "invalid_json"),
    ("[1, 2]", "invalid_json"),
])
def test_sortie_non_json_est_signalee_sans_reparation(text, erreur):
    """Une sortie illisible donne answer = None et une erreur invalid_json."""
    answer, errors = check_answer(text, [])
    assert answer is None and errors[0].startswith(erreur)


def test_source_hors_des_passages_fournis_est_une_erreur():
    """Citer un passage que le retriever n'a pas fourni est refusé par validate_answer."""
    answer = {**MOCK_ANSWER, "abstention": False, "hypotheses": ["h"], "sources": ["doc#inconnu#1"]}
    parsed, errors = check_answer("Voici : " + json.dumps(answer), ["doc#staging#1"])
    assert parsed is not None
    assert any(e.startswith("sources") for e in errors)


def test_prompt_consigne_avant_les_donnees_et_sans_label():
    """La consigne précède la trace et les passages ; les lignes au-delà de la limite sont signalées."""
    lines = [f"081109 2035{i:02d} 1 INFO dfs.DataNode$DataXceiver: Receiving block blk_1 src: /a dest: /b" for i in range(5)]
    content = build_messages(lines, PASSAGES[:1], max_lines=3)[0]["content"]
    assert content.index("Réponds uniquement") < content.index("Trace :") < content.index("[doc#staging#1]")
    assert "(… 2 lignes suivantes omises)" in content
    assert "label" not in content.lower()


def test_agent_en_mode_factice_produit_une_ligne_c7(monkeypatch):
    """Sans modèle, l'agent trace toutes les étapes et rend une réponse C5 valide."""
    monkeypatch.setenv("TEAMAI_SLM_MOCK", "1")
    lines = ["081109 203518 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /f. blk_1",
             "081109 203519 143 INFO dfs.DataNode$DataXceiver: Receiving block blk_1 src: /a:1 dest: /a:2"]
    record = explain_block("blk_1", lines, fake_retriever(), k=2)
    assert {"id", "raw_text", "parsed_response", "errors", "new_tokens", "seconds", "mock", "steps"} <= set(record)
    assert record["mock"] is True and record["errors"] == []
    assert record["steps"]["events"] == ["E22", "E5"]
    assert len(record["steps"]["retrieved"]) == 2


def test_lignes_regroupees_par_bloc():
    """Une ligne qui cite deux blocs est rattachée aux deux."""
    lines = ["a blk_1 x", "b blk_2 y", "c blk_1 blk_2 z"]
    assert lines_by_block(lines) == {"blk_1": ["a blk_1 x", "c blk_1 blk_2 z"], "blk_2": ["b blk_2 y", "c blk_1 blk_2 z"]}
