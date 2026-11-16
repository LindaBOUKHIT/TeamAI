"""Vérifie la démo locale sans poids de modèle ni index RAG."""
import pytest

from teamai.paths import SAMPLE
from volet_b.app import app


def valid_record():
    """Fournit une réponse C5 avec sa provenance documentaire."""
    return dict(id="blk_1", raw_text="brut", parsed_response=dict(
        resume_evenements="Résumé sûr", faits_observes=["fait"], hypotheses=["hypothèse"],
        infos_manquantes=["contexte"], sources=["doc#1"], abstention=False),
        passages=[dict(id="doc#1", text="extrait", source_url="https://example.org/source")],
        steps=[dict(agent="writer", tentative=1, verdict="accepte", errors=[], seconds=0.1)],
        statut="accepte", n_calls=3, seconds=0.1, errors=[])


def test_valid_render():
    """Affiche toutes les sections, la provenance et le journal."""
    text = app.render_block(valid_record())
    for expected in ("Résumé", "Faits observés", "Hypothèses", "Infos manquantes", "Abstention",
                     "Passages sources", "doc#1", "extrait", "https://example", "Journal des étapes",
                     "writer", "Nombre d'appels : 3", "Temps total"):
        assert app.safe(expected) in text or expected in text


@pytest.mark.parametrize("rejected", [False, True])
def test_invalid_render(rejected):
    """Conserve le brut et les erreurs de contrat ou de contrôle sans sections C5."""
    record = valid_record()
    if rejected:
        record.update(statut="rejete", errors=["contrôle refusé"])
    else:
        record["parsed_response"]["sources"] = ["inconnu"]
    text = app.render_block(record)
    assert "### Sortie brute" in text and "```text\nbrut\n```" in text
    assert "### Erreurs" in text
    assert "### Faits observés" not in text and "### Résumé" not in text


def test_test_block_refused_before_limit(monkeypatch):
    """Refuse aussi un bloc réservé placé après les cinq premiers sans appel."""
    monkeypatch.setattr(app, "demo_split", lambda: {"blk_6": "test"})
    monkeypatch.setattr(app, "get_retriever", forbidden_load)
    text = app.analyze("\n".join(f"log blk_{i}" for i in range(7)), mock=True)
    assert "refusée" in text and "split test" in text and "Aucun appel" in text


def forbidden_load(*args):
    """Signale tout chargement prématuré dans les tests de garde."""
    pytest.fail("aucune ressource ne doit être chargée")


def test_limit(monkeypatch):
    """Traite cinq blocs seulement et annonce explicitement la limite."""
    calls = []
    monkeypatch.setattr(app, "official_splits_available", lambda: True)
    monkeypatch.setattr(app, "demo_split", lambda: {})
    monkeypatch.setattr(app, "get_retriever", lambda mock: None)
    monkeypatch.setattr(app.single_agent, "explain_block", lambda bid, *a, **kw:
                        calls.append(bid) or valid_record())
    text = app.analyze("\n".join(f"log blk_{i}" for i in range(6)), configuration="1 agent", mock=True)
    assert len(calls) == 5 and "Limite de 5 blocs" in text


def test_no_block(monkeypatch):
    """Explique une entrée vide de blocs sans charger de ressource."""
    monkeypatch.setattr(app, "get_retriever", forbidden_load)
    assert "Aucun bloc" in app.analyze("texte libre")


def require_sample():
    """Ignore les vérifications de données si l'échantillon n'est pas disponible."""
    if not (SAMPLE / "HDFS_sample.log").exists():
        pytest.skip("data/sample absent")


def test_examples_only_val():
    """Les deux exemples sont non vides et tous leurs identifiants sont en validation."""
    require_sample()
    examples = app.choose_examples()
    assert all(examples)
    for text in examples:
        assert all(app.demo_split().get(b) == "val" for b in app.single_agent.lines_by_block(text.splitlines()))


def test_mock_three_agents(monkeypatch):
    """Exécute réellement les trois rôles factices sur un exemple de validation."""
    require_sample()
    monkeypatch.setattr(app, "get_caller", forbidden_load)
    monkeypatch.setenv("TEAMAI_SLM_MOCK", "original")
    text = app.analyze(app.choose_examples()[0], mock=True)
    assert "Mode factice actif" in text and "### Résumé" in text
    assert "search" in text and "writer" in text and "checker" in text
    assert "Nombre d'appels : 3" in text
    assert app.os.environ["TEAMAI_SLM_MOCK"] == "original"


@pytest.mark.parametrize("invalid", [False, True])
def test_html_escape(invalid):
    """Neutralise du HTML ainsi que les clôtures de bloc de code injectées."""
    record = valid_record()
    record["parsed_response"]["resume_evenements"] = '<script>alert("x")</script>'
    if invalid:
        record.update(parsed_response=None, raw_text='```\n<script>alert("x")</script>')
    text = app.render_block(record)
    assert "<script>" not in text and "&lt;script&gt;" in text


def test_build_interface():
    """Construit l'interface si Gradio est installé, sans lancer de serveur."""
    pytest.importorskip("gradio")
    assert app.build_app(mock=True) is not None


def test_unknown_block_refused_without_official_splits(monkeypatch):
    """Sans data/splits/splits.csv, un bloc absent de l'échantillon est refusé avant tout chargement."""
    monkeypatch.setattr(app, "official_splits_available", lambda: False)
    monkeypatch.setattr(app, "demo_split", lambda: {"blk_1": "val"})
    monkeypatch.setattr(app, "get_retriever", forbidden_load)
    text = app.analyze("log blk_1\nlog blk_999", mock=True)
    assert "refusée" in text and app.safe("blk_999") in text and "Aucun appel" in text


def test_unknown_block_allowed_with_official_splits(monkeypatch):
    """Avec le C4 complet, un bloc inconnu (logs hors Loghub) n'est pas refusé."""
    monkeypatch.setattr(app, "official_splits_available", lambda: True)
    monkeypatch.setattr(app, "demo_split", lambda: {})
    monkeypatch.setattr(app, "get_retriever", lambda mock: None)
    monkeypatch.setattr(app.single_agent, "explain_block", lambda bid, *a, **kw: valid_record())
    text = app.analyze("log blk_999", configuration="1 agent", mock=True)
    assert "refusée" not in text
