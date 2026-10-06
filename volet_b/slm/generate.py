"""Seule porte d'entrée vers le SLM du volet B (RAG, agents, évaluation passent tous par ici).

    from volet_b.slm.generate import generate
    out = generate([{"role": "user", "content": "…"}])            # modèle de base
    out = generate(messages, adapter="volet_b/slm/adapters/essai")  # avec un adaptateur LoRA
    out["text"], out["new_tokens"], out["seconds"]

Mode factice (sans modèle, pour développer le RAG et les agents sur n'importe quelle machine) :
    TEAMAI_SLM_MOCK=1  → renvoie une réponse au format C5 de docs/contrats.md.
"""
import json
import os
import time
from functools import lru_cache
from pathlib import Path

import yaml

CONFIG = Path(__file__).parent / "configs" / "generation.yaml"

MOCK_ANSWER = {
    "resume_evenements": "Réponse factice (TEAMAI_SLM_MOCK=1) : aucun modèle n'a été appelé.",
    "faits_observes": [],
    "hypotheses": [],
    "infos_manquantes": ["Modèle non chargé"],
    "sources": [],
    "abstention": True,
}


def load_config() -> dict:
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


@lru_cache(maxsize=2)
def load_model(adapter: str | None = None):
    """Charge le modèle (et l'adaptateur LoRA éventuel) une seule fois par processus."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    cfg = load_config()
    tokenizer = AutoTokenizer.from_pretrained(cfg["model_id"])
    model = AutoModelForCausalLM.from_pretrained(cfg["model_id"], dtype=getattr(torch, cfg["dtype"]))
    if adapter:
        from peft import PeftModel

        model = PeftModel.from_pretrained(model, adapter)
    model.eval()
    return model, tokenizer


def generate(messages: list[dict], adapter: str | None = None, **overrides) -> dict:
    """Génère une réponse à partir de messages au format chat ({"role", "content"})."""
    if os.environ.get("TEAMAI_SLM_MOCK") == "1":
        return {"text": json.dumps(MOCK_ANSWER, ensure_ascii=False), "new_tokens": 0, "seconds": 0.0}

    import torch

    cfg = {**load_config(), **overrides}
    model, tokenizer = load_model(adapter)
    torch.manual_seed(cfg["seed"])

    inputs = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, return_tensors="pt", return_dict=True
    )
    start = time.perf_counter()
    with torch.inference_mode():
        output = model.generate(
            **inputs,
            max_new_tokens=cfg["max_new_tokens"],
            do_sample=cfg["do_sample"],
            repetition_penalty=cfg["repetition_penalty"],
            pad_token_id=tokenizer.eos_token_id,
        )
    seconds = time.perf_counter() - start
    new_tokens = output[0, inputs["input_ids"].shape[1]:]
    return {
        "text": tokenizer.decode(new_tokens, skip_special_tokens=True),
        "new_tokens": int(new_tokens.shape[0]),
        "seconds": round(seconds, 2),
    }
