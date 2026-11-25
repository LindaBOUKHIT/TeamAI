"""SCRUM-68 : questions-réponses sourcées, avec appelants et retriever factices."""
import json

from volet_b.agents import doc_chat
from volet_b.app import app

PASSAGE = {"id": "hdfs-architecture-1.2.1#heartbeats#1", "doc": "HDFS Architecture Guide", "section": "Heartbeats",
           "text": "Each DataNode sends a Heartbeat message to the NameNode periodically.",
           "source_url": "https://hadoop.apache.org/docs/stable1/hdfs_design.html"}


class FixedRetriever:
    """Rend toujours les mêmes passages et garde la requête reçue."""

    def __init__(self, passages):
        """Fixe les passages renvoyés."""
        self.passages, self.queries = passages, []

    def search(self, query, k):
        """Mémorise la requête et rend au plus k passages."""
        self.queries.append(query)
        return self.passages[:k]


def caller(answer, query="datanode heartbeat failure detection"):
    """Appelant qui écrit la requête puis la réponse donnée, en gardant les prompts."""
    prompts = []

    def call(prompt, response_format):
        """Choisit la sortie selon le schéma demandé."""
        prompts.append(prompt)
        properties = response_format["schema"]["properties"]
        value = {"requete": query} if "requete" in properties else answer
        return {"text": json.dumps(value, ensure_ascii=False), "finish_reason": "stop"}

    call.prompts = prompts
    return call


def test_sourced_answer_maps_labels_to_ids():
    """La requête anglaise va au retriever et la source P1 devient l'identifiant C6."""
    retriever = FixedRetriever([PASSAGE])
    record = doc_chat.ask("Comment HDFS détecte une panne de DataNode ?", [], retriever,
                          caller({"reponse": "Par les heartbeats.", "sources": ["P1"], "abstention": False}))
    assert retriever.queries == ["datanode heartbeat failure detection"]
    assert record["status"] == "sourcée" and record["answer"]["sources"] == [PASSAGE["id"]]


def test_answer_without_source_is_refused():
    """Une réponse non abstenue sans source est refusée par le code."""
    record = doc_chat.ask("Question ?", [], FixedRetriever([PASSAGE]),
                          caller({"reponse": "Affirmation libre.", "sources": [], "abstention": False}))
    assert record["status"] == "refusée" and "réponse sans source" in record["errors"]


def test_unknown_source_and_cited_abstention_refused():
    """Une source hors passages ou une abstention qui cite sont des erreurs de contrat."""
    assert "sources hors des passages fournis" in doc_chat.check_reply(
        {"reponse": "x", "sources": ["P9"], "abstention": False}, ["P1"])
    assert doc_chat.check_reply({"reponse": "x", "sources": ["P1"], "abstention": True}, ["P1"]) == [
        "abstention avec sources"]


def test_no_passage_abstains_without_answer_call():
    """Sans passage, l'abstention est produite par le code, sans second appel au modèle."""
    call = caller({"reponse": "ne doit pas servir", "sources": [], "abstention": False})
    record = doc_chat.ask("Question hors corpus ?", [], FixedRetriever([]), call)
    assert record["status"] == "abstention" and record["answer"]["reponse"] == doc_chat.ABSTENTION
    assert len(call.prompts) == 1


def test_event_code_adds_loghub_template():
    """Un code Exx cité ajoute son template Loghub comme passage citable."""
    record = doc_chat.ask("Que signifie E23 ?", [], FixedRetriever([]),
                          caller({"reponse": "Inscription dans invalidSet.", "sources": ["P1"], "abstention": False}))
    assert record["passages"][0]["id"] == "loghub-templates#E23"
    assert "invalidSet" in record["passages"][0]["text"] and record["status"] == "sourcée"
    assert doc_chat.event_passages("E30 et E0 ne sont pas des codes") == []


def test_history_and_analysis_are_context_only():
    """Le fil récent et l'analyse vont dans le prompt de réponse, sans devenir des passages."""
    call = caller({"reponse": "Oui.", "sources": ["P1"], "abstention": False})
    history = [{"role": "user", "content": "Et E20 ?"},
               {"role": "assistant", "content": "Réponse précédente\n\n**Sources**\n- doc"}]
    record = doc_chat.ask("Et pour ce bloc ?", history, FixedRetriever([PASSAGE]), call, analysis="Bloc blk_1 : E20")
    assert "Question : Et E20 ?" in call.prompts[1] and "Bloc blk_1 : E20" in call.prompts[1]
    assert "**Sources**" not in call.prompts[1].split("FIL RÉCENT", 1)[1].split("PASSAGES", 1)[0]
    assert [p["id"] for p in record["passages"]] == [PASSAGE["id"]]


def test_invalid_query_falls_back_to_question():
    """Une requête illisible laisse la question brute partir au retriever, avec une erreur tracée."""
    retriever = FixedRetriever([PASSAGE])

    def call(prompt, response_format):
        """Sortie illisible pour la requête, réponse valide ensuite."""
        if "requete" in response_format["schema"]["properties"]:
            return {"text": "pas du JSON", "finish_reason": "stop"}
        return {"text": json.dumps({"reponse": "Oui.", "sources": ["P1"], "abstention": False}), "finish_reason": "stop"}

    record = doc_chat.ask("Heartbeat ?", [], retriever, call)
    assert retriever.queries == ["Heartbeat ?"] and record["errors"][0].startswith("requête de recherche invalide")


def test_app_chat_mock_cites_official_link():
    """En mode factice, l'onglet ajoute la question et une réponse sourcée avec lien officiel."""
    history, cleared = app.chat("Comment fonctionne la réplication ?", [], mock=True)
    assert cleared == "" and [m["role"] for m in history] == ["user", "assistant"]
    assert "**Sources**" in history[1]["content"] and "](https://hadoop.apache.org/" in history[1]["content"]
    assert app.chat("   ", history, mock=True) == (history, "")
