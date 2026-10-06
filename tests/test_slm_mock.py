"""Mode factice du SLM : le RAG et les agents doivent pouvoir tourner sans le modèle (3,4 Go)."""
import json

import pytest

from teamai.contracts import validate_answer

generate_module = pytest.importorskip("volet_b.slm.generate", reason="volet_b/slm/generate.py absent (SCRUM-28)")


def test_mode_factice_repond_au_format_C5(monkeypatch):
    monkeypatch.setenv("TEAMAI_SLM_MOCK", "1")
    out = generate_module.generate([{"role": "user", "content": "Explique cette trace."}])
    assert out["new_tokens"] == 0
    assert validate_answer(json.loads(out["text"])) == []
