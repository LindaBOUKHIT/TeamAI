"""Seule porte d'entrée vers le SLM du volet B (RAG, agents, évaluation passent tous par ici).

    from volet_b.slm.generate import generate
    out = generate([{"role": "user", "content": "…"}])            # modèle de base
    out = generate(messages, adapter="volet_b/slm/adapters/essai")  # avec un adaptateur LoRA
    out["text"], out["new_tokens"], out["seconds"]

Mode factice (sans modèle, pour développer le RAG et les agents sur n'importe quelle machine) :
    TEAMAI_SLM_MOCK=1  → renvoie une réponse au format C5 de docs/contrats.md.
"""
import hashlib
import json
import os
import time
from functools import lru_cache

import yaml

from teamai.paths import SLM_CONFIGS, resolve_path

CONFIG = SLM_CONFIGS / "generation.yaml"

MOCK_ANSWER = {
    "resume_evenements": "Réponse factice (TEAMAI_SLM_MOCK=1) : aucun modèle n'a été appelé.",
    "faits_observes": [],
    "hypotheses": [],
    "infos_manquantes": ["Modèle non chargé"],
    "sources": [],
    "abstention": True,
}


def load_config() -> dict:
    """Paramètres de génération lus dans configs/generation.yaml."""
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


def load_model(adapter: str | None = None, local_files_only: bool = False):
    """Normalise les arguments pour que () et (None) partagent la même instance."""
    return _load_model(adapter, local_files_only)


@lru_cache(maxsize=1)
def _load_model(adapter: str | None, local_files_only: bool):
    """Charge le modèle (et l'adaptateur LoRA éventuel) une seule fois par processus."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    cfg = load_config()
    source = {"revision": cfg["revision"], "local_files_only": local_files_only}
    tokenizer = AutoTokenizer.from_pretrained(cfg["model_id"], **source)
    model = AutoModelForCausalLM.from_pretrained(
        cfg["model_id"], dtype=getattr(torch, cfg["dtype"]), **source
    )
    if adapter:
        from peft import PeftModel

        model = PeftModel.from_pretrained(model, adapter, local_files_only=local_files_only)
    model.eval()
    return model, tokenizer


@lru_cache(maxsize=1)
def _load_llamacpp(repo, filename, revision, n_ctx, seed, adapter, offline, model_path):
    """Charge une instance llama.cpp ; la clé inclut tous ses paramètres de chargement."""
    from huggingface_hub import hf_hub_download
    from llama_cpp import Llama

    if adapter and not resolve_path(adapter).is_file():
        raise FileNotFoundError(f"Adaptateur GGUF introuvable : {adapter}")
    path = str(resolve_path(model_path)) if model_path else hf_hub_download(
        repo, filename, revision=revision, local_files_only=offline
    )
    return Llama(model_path=path, n_ctx=n_ctx, last_n_tokens_size=n_ctx,
                 seed=seed, verbose=False, n_gpu_layers=0,
                 lora_path=str(resolve_path(adapter)) if adapter else None)


def load_backend(cfg: dict, adapter: str | None = None):
    """Charge le backend demandé, en conservant le chargeur Transformers historique."""
    backend = cfg.get("backend", "transformers")
    if backend == "transformers":
        return load_model(adapter, local_files_only=cfg.get("local_files_only", False))
    if backend != "llamacpp":
        raise ValueError(f"Backend inconnu : {backend}")
    return _load_llamacpp(cfg["gguf_repo"], cfg["gguf_file"], cfg["gguf_revision"],
                          cfg["n_ctx"], cfg["seed"], adapter,
                          cfg.get("local_files_only", False), cfg.get("gguf_path"))


def clear_model_cache():
    """Libère les références des deux caches entre les mesures des backends."""
    _load_model.cache_clear()
    _load_llamacpp.cache_clear()


def v16_context_error(llm, messages, cfg):
    """Vérifie le contexte et le template sans réflexion, comme le worker v16.

    Renvoie une erreur précise ou None ; aucune génération n'est effectuée.
    Le template Gemma doit produire exactement le même texte par défaut
    qu'avec enable_thinking=False (aucun argument chat non supporté ajouté).
    """
    from llama_cpp.llama_chat_format import Jinja2ChatFormatter

    template = llm.metadata["tokenizer.chat_template"]
    if hashlib.sha256(template.encode()).hexdigest() != "0a2c8073c878ab1da004bee933a998606537bbb62016310352c7285c3f01c5b5":
        return "template différent de v13"
    formatter = Jinja2ChatFormatter(
        template=template,
        bos_token=llm.detokenize([llm.token_bos()], special=True).decode(),
        eos_token=llm.detokenize([llm.token_eos()], special=True).decode())
    rendered = formatter(messages=messages).prompt
    if (rendered != formatter(messages=messages, enable_thinking=False).prompt
            or "<|think|>" in rendered or "<|channel>thought" in rendered):
        return "réflexion active dans le template v16"
    if len(llm.tokenize(messages[0]["content"].encode())) > 2900:
        return "prompt supérieur au plafond v13 de 2900 tokens"
    length = len(llm.tokenize(rendered.encode(), add_bos=False, special=True))
    if length + cfg["max_new_tokens"] + 32 > cfg["n_ctx"]:
        return "contexte insuffisant pour la réponse complète"
    return None


def generate(messages: str | list[dict], adapter: str | None = None, **overrides) -> dict:
    """Accepte un prompt texte ou des messages chat ({"role", "content"})."""
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]
    if not messages:
        raise ValueError("Au moins un message est nécessaire.")
    cfg = {**load_config(), **overrides}
    if cfg.get("backend", "transformers") not in {"transformers", "llamacpp"}:
        raise ValueError(f"Backend inconnu : {cfg['backend']}")
    if os.environ.get("TEAMAI_SLM_MOCK") == "1":
        result = {"text": json.dumps(MOCK_ANSWER, ensure_ascii=False), "new_tokens": 0, "seconds": 0.0}
        if cfg.get("return_metadata"):
            result.update(finish_reason="stop", prompt_tokens=0)
        return result

    if cfg.get("backend") == "llamacpp":
        if cfg["do_sample"]:
            raise ValueError("Le backend llama.cpp exige do_sample=false (glouton).")
        llm = load_backend(cfg, adapter)
        start = time.perf_counter()
        options = {}
        if cfg.get("response_format") is not None:
            options["response_format"] = cfg["response_format"]
        if cfg.get("enforce_v16_context"):
            problem = v16_context_error(llm, messages, cfg)
            if problem:
                raise ValueError(problem)
        out = llm.create_chat_completion(
            messages=messages, max_tokens=cfg["max_new_tokens"], temperature=0.0,
            repeat_penalty=cfg["repetition_penalty"], **options,
        )
        result = {"text": out["choices"][0]["message"]["content"] or "",
                "new_tokens": int(out["usage"]["completion_tokens"]),
                "seconds": time.perf_counter() - start}
        if cfg.get("return_metadata"):
            result.update(finish_reason=out["choices"][0].get("finish_reason"),
                          prompt_tokens=out["usage"].get("prompt_tokens", 0))
        return result

    import torch

    model, tokenizer = load_backend(cfg, adapter)
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
        "seconds": seconds,
    }
