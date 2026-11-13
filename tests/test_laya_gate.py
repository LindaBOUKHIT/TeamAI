"""SCRUM-58 : porte Laya et mesure C7 sans modèle ni données réelles."""
import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

from teamai import paths
from teamai.contracts import validate_answer
from volet_b.agents.laya_gate import LayaGate, load_config, state_from_events
from volet_b.agents import laya_measure


@pytest.fixture
def answer():
    """Fournit une réponse synthétique valide C5, avec deux hypothèses distinctes."""
    return {"resume_evenements": "Un événement synthétique est observé [F01].",
            "faits_observes": ["[F01] E9 apparaît trois fois."],
            "hypotheses": ["Une cause A serait possible.", "Une cause B serait possible."],
            "infos_manquantes": ["Une information initiale."], "sources": ["doc-1"], "abstention": False}


class Predictor:
    """Prédicteur contrôlé enregistrant ses appels et les questions groupées."""

    def __init__(self, anomaly=0.9, hypotheses=(0.2, 0.8)):
        """Mémorise les probabilités imposées par le scénario."""
        self.anomaly = anomaly
        self.hypotheses = hypotheses
        self.calls = []

    def __call__(self, state, questions):
        """Renvoie le format noul documenté sans importer Laya."""
        self.calls.append((state, deepcopy(questions)))
        return {"answers": {name: {"noul": self.anomaly if name == "anomaly"
                                   else self.hypotheses[int(name.rsplit("_", 1)[1])]}
                            for name in questions}}


@pytest.mark.parametrize("p", [0.35, 0.5, 0.65])
def test_ambiguous_abstains(answer, p):
    """Les bornes inclusives entraînent une abstention conforme C5."""
    predictor = Predictor(p)
    result, info = LayaGate(load_config(), predictor).apply(answer, ["E9"] * 3, {"E9": "Synthetic event"})
    assert result["abstention"] and result["hypotheses"] == []
    assert result["infos_manquantes"][1:3] == ["Hypothèse non confirmée : " + h for h in answer["hypotheses"]]
    assert result["infos_manquantes"][-1] == f"Signal d'anomalie ambigu (Laya p={p:.2f})"
    assert info["moved_indices"] == [0, 1] and info["abstention_added"]
    assert info["anomaly_probability"] == p
    assert validate_answer(result) == []
    assert len(predictor.calls) == 1
    assert len(predictor.calls[0][1]) == 3
    assert all(q["type"] == "noul" for q in predictor.calls[0][1].values())


@pytest.mark.parametrize("p", [0.1, 0.349, 0.651, 0.9])
def test_filters_preserves_and_copies(answer, p):
    """Déplace la faible hypothèse, garde celle au seuil et protège l'entrée."""
    original = deepcopy(answer)
    result, info = LayaGate(load_config(), Predictor(p, (0.499, 0.5))).apply(answer, ["E9"], {"E9": "Synthetic"})
    assert result["hypotheses"] == [answer["hypotheses"][1]]
    assert result["infos_manquantes"][-1] == "À vérifier : " + answer["hypotheses"][0]
    assert info["moved_indices"] == [0]
    assert info["hypothesis_probabilities"] == [0.499, 0.5]
    assert not result["abstention"] and not info["abstention_added"]
    assert info["predict_seconds"] >= 0
    assert validate_answer(result) == [] and answer == original
    for key in ("resume_evenements", "faits_observes", "sources"):
        assert result[key] == answer[key]
    result["sources"].append("autre")
    result["faits_observes"].append("autre")
    assert answer == original


@pytest.mark.parametrize("p", [0.1, 0.5, 0.9])
def test_existing_abstention_remains(answer, p):
    """Ne révoque jamais une abstention initiale et conserve la validité C5."""
    answer.update(abstention=True, hypotheses=[])
    result, info = LayaGate(load_config(), Predictor(p)).apply(answer, [], {})
    assert result["abstention"] and not info["abstention_added"]
    assert validate_answer(result) == []


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -0.1, 1.1, True, None])
def test_invalid_probability_rejected(answer, value):
    """Une valeur non probabiliste ne doit pas autoriser une hypothèse."""
    with pytest.raises(ValueError, match="Probabilité"):
        LayaGate(load_config(), Predictor(value)).apply(answer, [], {})


def test_invalid_answer_rejected(answer):
    """Refuse une entrée C5 invalide avant tout appel au prédicteur."""
    answer["sources"] = 12
    predictor = Predictor()
    with pytest.raises(ValueError, match="C5"):
        LayaGate(load_config(), predictor).apply(answer, [], {})
    assert predictor.calls == []


def test_state_groups_and_truncates():
    """Regroupe seulement les répétitions consécutives et compte les événements omis."""
    templates = {"E9": "Synthetic   event\ntext", "E1": "x" * 80}
    events = ["E9"] * 3 + ["E1"] * 2 + ["E9"]
    full = state_from_events(events, templates, 1000)
    assert full == "E9 ×3 : Synthetic event text\nE1 ×2 : " + "x" * 80 + "\nE9 : Synthetic event text"
    short = state_from_events(events, templates, 52)
    assert short == "E9 ×3 : Synthetic event text\n[3 événements omis]"
    assert len(short) <= 52
    assert state_from_events(["E1"] * 12, templates, 25) == "[12 événements omis]"
    assert state_from_events([], {}, 1) == ""
    with pytest.raises(ValueError, match="insuffisant"):
        state_from_events(["E1"], templates, 1)
    with pytest.raises(ValueError, match="log brut"):
        state_from_events(["Raw synthetic log"], {}, 100)
    with pytest.raises(ValueError, match="absent"):
        state_from_events(["E2"], templates, 100)


def test_lazy_router_and_missing_dependency(answer, monkeypatch):
    """Importe et construit Router une seule fois ; absence signalée clairement."""
    created = []

    def router(revision=None):
        """Remplace Router sans importer ni télécharger de modèle ; vérifie la révision figée."""
        created.append(revision)
        predictor = Predictor()

        def predict(state, questions, model=None):
            """Vérifie le checkpoint demandé puis délègue au prédicteur factice."""
            assert model == "english"
            return predictor(state, questions)

        return SimpleNamespace(predict=predict)

    gate = LayaGate(load_config())
    monkeypatch.setitem(sys.modules, "laya", SimpleNamespace(Router=router))
    assert created == []
    gate.apply(answer, [], {})
    gate.apply(answer, [], {})
    assert created == [load_config()["revision"]]
    monkeypatch.setitem(sys.modules, "laya", None)
    with pytest.raises(ImportError, match="pip install laya"):
        LayaGate(load_config()).apply(answer, [], {})


def write_responses(tmp_path, answer, splits=("val",)):
    """Écrit uniquement des réponses synthétiques dans le dossier temporaire."""
    target = tmp_path / "responses_validation.jsonl"
    rows = [{"block_id": f"blk_{i}", "split": split, "events": ["E9"] * 3, "answer": answer}
            for i, split in enumerate(splits)]
    target.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    return target


@pytest.mark.parametrize("forbidden", ["test", "train", "VAL", None])
def test_cli_refuses_split_even_beyond_n(tmp_path, answer, forbidden):
    """Refuse une ligne interdite après la première réponse sélectionnée."""
    source = write_responses(tmp_path, answer, ("validation", forbidden))
    with pytest.raises(SystemExit) as exc:
        laya_measure.main(["--responses", str(source), "--mock", "--n", "1", "--out", str(tmp_path / "runs")])
    assert exc.value.code == 2 and not (tmp_path / "runs").exists()


@pytest.mark.parametrize("source", ["eval/volet_b/private.jsonl", "EVAL/VOLET_B/private.jsonl",
                                    "responses_TEST.jsonl", "responses_test_backup.json"])
def test_cli_refuses_paths_without_opening(source, monkeypatch):
    """Les chemins réservés sont refusés avant toute lecture de leur contenu."""
    def no_read(*args, **kwargs):
        """Échoue si la CLI tente d'ouvrir un chemin réservé."""
        pytest.fail("Une lecture interdite a été tentée.")

    monkeypatch.setattr(Path, "read_text", no_read)
    with pytest.raises(SystemExit) as exc:
        laya_measure.main(["--responses", source, "--mock"])
    assert exc.value.code == 2


def test_cli_refuses_unsupported_path(tmp_path, answer):
    """Applique la même barrière au fichier des annotations humaines."""
    source = write_responses(tmp_path, answer)
    with pytest.raises(SystemExit) as exc:
        laya_measure.main(["--responses", str(source), "--unsupported", "eval/volet_b/private.json", "--mock"])
    assert exc.value.code == 2


def test_mock_writes_c7(tmp_path, answer, monkeypatch):
    """Écrit trois fichiers C7 neufs et vérifie les effectifs et empreintes."""
    source = write_responses(tmp_path, answer, ("val", "validation"))
    unsupported = tmp_path / "unsupported.json"
    unsupported.write_text(json.dumps([{"block_id": "blk_0", "hypothesis_index": 0},
                                       {"block_id": "blk_0", "hypothesis_index": 1},
                                       {"block_id": "blk_1", "hypothesis_index": 0}]), encoding="utf-8")
    monkeypatch.setattr(paths, "RUNS", tmp_path / "runs")
    # Le modèle reste indisponible : --mock ne doit même pas tenter son import.
    monkeypatch.setitem(sys.modules, "laya", None)
    argv = ["--responses", str(source), "--unsupported", str(unsupported), "--mock", "--n", "1"]
    first = laya_measure.main(argv)
    second = laya_measure.main(argv)
    assert first != second and first.is_dir() and second.is_dir()
    assert {p.name for p in first.iterdir()} == {"predictions.jsonl", "metrics.json", "config.json"}
    prediction = json.loads((first / "predictions.jsonl").read_text(encoding="utf-8"))
    config = json.loads((first / "config.json").read_text(encoding="utf-8"))
    metrics = json.loads((first / "metrics.json").read_text(encoding="utf-8"))
    assert validate_answer(prediction["after"]) == [] and prediction["before"] == answer
    assert config["mock"] and config["revision"] == load_config()["revision"]
    assert config["input_sha256"]["responses"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert config["input_sha256"]["unsupported"] == hashlib.sha256(unsupported.read_bytes()).hexdigest()
    assert config["machine"]["python"]
    assert metrics["blocks"] == 1 and metrics["hypotheses_before"] == 2
    assert metrics["hypotheses_moved"] == len(prediction["info"]["moved_indices"])
    assert metrics["hypotheses_after"] == 2 - metrics["hypotheses_moved"]
    assert metrics["unsupported_before"] == 2
    assert metrics["unsupported_after"] == 2 - metrics["hypotheses_moved"]
    assert metrics["abstentions_before"] == 0
    assert metrics["abstentions_after"] == int(prediction["after"]["abstention"])
    assert metrics["latency_p95_seconds"] == metrics["latency_mean_seconds"] >= 0


def test_optional_psutil(tmp_path, answer, monkeypatch):
    """Une mesure sans psutil conserve une RSS explicitement non mesurée."""
    monkeypatch.setitem(sys.modules, "psutil", None)
    source = write_responses(tmp_path, answer)
    run = laya_measure.main(["--responses", str(source), "--mock", "--out", str(tmp_path)])
    metrics = json.loads((run / "metrics.json").read_text(encoding="utf-8"))
    assert metrics["peak_rss_bytes"] is None
    assert metrics["unsupported_before"] is None and metrics["unsupported_after"] is None


def test_new_code_docstrings_and_paths():
    """Vérifie les règles de structure uniquement sur les nouveaux fichiers autorisés."""
    files = [paths.AGENTS / "laya_gate.py", paths.AGENTS / "laya_measure.py",
             paths.ROOT / "tests" / "test_laya_gate.py"]
    for path in files:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        assert ast.get_docstring(tree)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                assert ast.get_docstring(node), (path, node.name)
        if path.parent == paths.AGENTS:
            assert "Path(" + "__file__)" not in source
