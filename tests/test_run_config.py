"""SCRUM-38 — Évaluation factice sur des exemples fabriqués, sans ouvrir le test réservé."""
import json

import pytest

from eval.volet_b import run_config as runner
from teamai.paths import SAMPLE
from volet_b.slm.generate import MOCK_ANSWER, generate


@pytest.fixture
def examples(tmp_path, monkeypatch):
    """Fabrique deux C5 pour un bloc de sample classé train dans le split C4 officiel (seed 42)."""
    monkeypatch.setenv("TEAMAI_SLM_MOCK", "1")
    # Appartenance train vérifiée dans splits.csv ; aucune ligne du split test n'est utilisée.
    block_id = "blk_4971154345890344"
    with (SAMPLE / "HDFS_sample.log").open(encoding="utf-8") as source:
        lines = [line.rstrip() for line in source if block_id in line]
    assert lines
    rows = [{
        "id": f"factice-{i}", "block_id": block_id, "split": "train", "trace_lines": lines,
        "events": ["ANNOTATION_EVENTS_INTERDITE"], "label": 1,
        "expected": {**MOCK_ANSWER, "resume_evenements": "ANNOTATION_EXPECTED_INTERDITE"},
        "annotator": "ANNOTATEUR_INTERDIT", "reviewed_by": "RELECTEUR_INTERDIT",
        "extra_annotation": "ANNOTATION_SUPPLEMENTAIRE_INTERDITE",
    } for i in range(2)]
    path = tmp_path / "exemples.jsonl"
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    return path


def read_records(run_dir):
    """Lit les seules prédictions fabriquées pour le test courant."""
    return [json.loads(line) for line in (run_dir / "predictions.jsonl").read_text(encoding="utf-8").splitlines()]


def test_missing_input(tmp_path, monkeypatch, capsys):
    """Une entrée absente est signalée avant toute génération ou création de dossier."""
    def forbidden(*args, **kwargs):
        """Interdit tout appel du modèle sur une entrée absente."""
        pytest.fail("Le modèle ne doit pas être appelé.")

    monkeypatch.setattr(runner, "generate", forbidden)
    with pytest.raises(SystemExit) as error:
        runner.main(["--config", "base", "--data", str(tmp_path / "absent.jsonl")])
    assert error.value.code == 2
    assert "Fichier d'exemples C5 absent" in capsys.readouterr().err
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("config", ["base", "rag1"])
def test_messages_and_fresh_c7(examples, tmp_path, monkeypatch, config):
    """Seules les lignes et les passages atteignent generate ; chaque exécution crée son C7."""
    calls = []
    queries = []

    class FakeRetriever:
        """Retriever local factice, sans index ni téléchargement."""

        def search(self, query, k):
            """Conserve la requête pour vérifier l'absence d'annotations."""
            queries.append(query)
            return [{"id": "guide#section#1", "text": "PASSAGE_FOURNI", "doc": "Guide",
                     "section": "Section", "source_url": "https://example.org", "version": "factice", "score": 0.9}]

    def retriever(*args, **kwargs):
        """Rend le retriever factice, même en l'absence d'index local."""
        assert kwargs == {"local_files_only": True}
        return FakeRetriever()

    def spy(messages, adapter=None):
        """Capture l'appel exact puis utilise le mode mock existant de generate."""
        calls.append(messages)
        assert adapter == "adaptateur-factice"
        return generate(messages, adapter=adapter)

    monkeypatch.setattr(runner.single_agent, "load_retriever", retriever)
    monkeypatch.setattr(runner, "generate", spy)
    root = tmp_path / "runs"
    first = runner.run_config(config, examples, adapter="adaptateur-factice", run_root=root)
    second = runner.run_config(config, examples, limit=1, adapter="adaptateur-factice", run_root=root)
    assert first != second
    assert {p.name for p in first.iterdir()} == {"predictions.jsonl", "config.json", "metrics.json"}
    records = read_records(first)
    assert len(records) == 2 and len(read_records(second)) == 1
    assert all(not r["errors"] and r["mock"] for r in records)
    metadata = json.loads((first / "config.json").read_text(encoding="utf-8"))
    assert metadata["input_sha256"] == runner.sha256_file(examples)
    assert metadata["model_revision"] == runner.load_config()["revision"]
    assert metadata["generation"] == runner.load_config()
    assert metadata["splits"] == ["train"]
    text = json.dumps(calls + queries)
    for forbidden in ("label", "expected", "ANNOTATION_", "ANNOTATEUR_INTERDIT", "RELECTEUR_INTERDIT"):
        assert forbidden not in text
    assert bool(queries) == (config == "rag1")
    assert ("PASSAGE_FOURNI" in text) == (config == "rag1")
    assert bool(records[0]["passages"]) == (config == "rag1")
    assert (runner.NO_RAG_NOTE in text) == (config == "base")
    values = json.loads((first / "metrics.json").read_text(encoding="utf-8"))
    assert values["n"] == 2 and values["conformity_rate"] == 1
    assert values["abstention_rate"] == 1 and values["sources_valid_rate"] == 1
    assert values["process_peak_rss_bytes"] > 0


@pytest.mark.parametrize("failure", ["invalid_json", "exception", "invalid_input"])
def test_failures_stay_in_denominator(examples, tmp_path, monkeypatch, failure):
    """Les échecs JSON, de génération et d'entrée restent chacun une prédiction comptée."""
    calls = 0

    def mixed(messages, adapter=None):
        """Rend une réussite puis l'échec demandé, sans appeler de modèle."""
        nonlocal calls
        calls += 1
        if calls == 2:
            if failure == "exception":
                raise RuntimeError("échec factice")
            return {"text": "pas de JSON", "seconds": 0.0, "new_tokens": 1}
        return generate(messages, adapter=adapter)

    if failure == "invalid_input":
        with examples.open("a", encoding="utf-8") as output:
            output.write("JSON mal formé\n")
    monkeypatch.setattr(runner, "generate", mixed)
    run_dir = runner.run_config("base", examples, run_root=tmp_path / "runs")
    records = read_records(run_dir)
    values = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
    n = 3 if failure == "invalid_input" else 2
    assert values["n"] == len(records) == n
    assert values["c5_valid"] == 1 and values["failures"] == n - 1
    assert values["conformity_rate"] == values["abstention_rate"] == 1 / n
    assert records[1]["parsed_response"] is None and records[1]["errors"]
    if failure == "exception":
        assert records[1]["new_tokens"] is None and records[1]["generation_seconds"] is None


@pytest.mark.parametrize("cited,valid", [("guide#fourni#1", True), ("guide#absent#1", False)])
def test_rag_allowed_sources(examples, tmp_path, monkeypatch, cited, valid):
    """check_answer reçoit exactement les IDs fournis par le retrieval rag1."""
    class FakeRetriever:
        """Passage unique pour contrôler les citations."""

        def search(self, query, k):
            """Retourne le seul passage autorisé."""
            return [{"id": "guide#fourni#1", "text": "Documentation"}]

    def retriever(*args, **kwargs):
        """Rend un retriever sans dépendances externes."""
        return FakeRetriever()

    def answer(messages, adapter=None):
        """Produit une réponse structurée citant la source paramétrée."""
        return {"text": json.dumps({**MOCK_ANSWER, "sources": [cited]}), "seconds": 0.1, "new_tokens": 10}

    seen = []
    original = runner.check_answer

    def validate(value, allowed_sources=None):
        """Vérifie le passage de allowed_sources au contrôle réel de l'agent."""
        seen.append(allowed_sources)
        return original(value, allowed_sources=allowed_sources)

    monkeypatch.setattr(runner.single_agent, "load_retriever", retriever)
    monkeypatch.setattr(runner, "generate", answer)
    monkeypatch.setattr(runner, "check_answer", validate)
    result = runner.run_config("rag1", examples, limit=1, run_root=tmp_path / "runs")
    record = read_records(result)[0]
    assert seen == [["guide#fourni#1"]]
    assert record["sources_valid"] == valid
    assert bool(record["errors"]) != valid
    assert record["parsed_response"]["sources"] == [cited]


def test_official_hash_refusal(examples, tmp_path, monkeypatch):
    """Le garde-fou du test officiel est vérifié avec un fichier fabriqué uniquement."""
    reference = tmp_path / "reference.sha256"
    monkeypatch.setattr(runner, "VOLET_B_TEST", examples)
    monkeypatch.setattr(runner, "VOLET_B_TEST_SHA256", reference)
    reference.write_text("0" * 64, encoding="utf-8")
    with pytest.raises(ValueError, match="SHA-256"):
        runner.run_config("base", examples, run_root=tmp_path / "runs")
    assert not (tmp_path / "runs").exists()
    reference.write_text(runner.sha256_file(examples) + "  test.jsonl\n", encoding="utf-8")
    assert runner.input_hash(examples) == runner.sha256_file(examples)


def test_update_summary(tmp_path):
    """La section est actualisée sans doublon ni perte des autres sections ; le mock est refusé."""
    output = tmp_path / "resultats.md"
    output.write_text("# Résultats\n\n## Après adaptation\n\nÀ venir.\n", encoding="utf-8")
    paths = []
    for name in ("base", "rag1"):
        path = tmp_path / f"{name}.json"
        runner.write_json(path, {
            **runner.metrics([], 1024), "config": name, "mock": False, "adapter": None,
            "official_test": True, "limit": None, "input_sha256": "empreinte-factice",
        })
        paths.append(path)
    runner.update_summary(paths, output)
    first = output.read_text(encoding="utf-8")
    runner.update_summary(paths, output)
    assert output.read_text(encoding="utf-8") == first
    assert first.count("## Avant adaptation") == 1
    assert first.count("| base |") == first.count("| rag1 |") == 1
    assert "## Après adaptation\n\nÀ venir." in first
    values = json.loads(paths[0].read_text(encoding="utf-8"))
    runner.write_json(paths[0], {**values, "mock": True})
    with pytest.raises(ValueError, match="sans mock"):
        runner.update_summary(paths, output)
    assert output.read_text(encoding="utf-8") == first
