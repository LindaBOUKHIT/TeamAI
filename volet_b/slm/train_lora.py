"""SCRUM-29 — Essai LoRA Gemma texte seul sur T4 Kaggle : mémoire, durée par pas, descente de la loss, rechargement.

    python -m volet_b.slm.train_lora --offline              # 30 pas, configs/lora_essai.yaml
    python -m volet_b.slm.train_lora --offline --steps 3    # vérification rapide
    python -m volet_b.slm.train_lora --device cuda --qlora  # T4 16 Go (bitsandbytes), pas une carte 6 Go

Test de faisabilité matérielle, pas de qualité : les exemples sont provisoires (make_seed.py) et la loss
est mesurée sur ces mêmes exemples. La consigne est placée avant les logs (règle du volet B, SCRUM-57) ;
seule la réponse JSON v16 contribue à la loss. Les sorties vont dans un dossier C7 unique de eval/runs/.
"""
import argparse
import json
import platform
import random
import time
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import psutil
import yaml

from teamai.contracts import load_jsonl
from teamai.paths import ROOT
from volet_b.slm.first_inference import PeakMemory, gb, new_run_directory
from volet_b.slm.lora_data import encode_example, prepare_examples, validate_lora_config

CONFIG = ROOT / "volet_b" / "slm" / "configs" / "lora_essai.yaml"


def prepare_qlora_text(model, torch):
    """Gèle la base NF4 sans promouvoir les énormes embeddings en FP32, même temporairement."""
    for name, parameter in model.named_parameters():
        parameter.requires_grad_(False)
        if "norm" in name and parameter.__class__.__name__ != "Params4bit":
            parameter.data = parameter.data.to(dtype=torch.float32)
    return model


def package_versions() -> dict:
    """Versions des paquets qui influencent l'entraînement (None si absent)."""
    out = {}
    for name in ("torch", "transformers", "peft", "accelerate", "bitsandbytes"):
        try:
            out[name] = version(name)
        except PackageNotFoundError:
            out[name] = None
    return out


def main(argv=None):
    """Entraîne quelques pas de LoRA, enregistre l'adaptateur et les mesures, puis vérifie son rechargement."""
    parser = argparse.ArgumentParser(description="Essai LoRA court (SCRUM-29).")
    parser.add_argument("--config", type=Path, default=CONFIG)
    parser.add_argument("--steps", type=int, help="Remplace training.steps de la configuration.")
    parser.add_argument("--offline", action="store_true", help="Poids déjà en cache uniquement.")
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    parser.add_argument("--qlora", action="store_true", help="Modèle de base chargé en 4 bits (GPU NVIDIA, bitsandbytes).")
    args = parser.parse_args(argv)

    import torch
    from peft import LoraConfig, get_peft_model
    from transformers import AutoConfig, AutoTokenizer, Gemma4ForCausalLM, Gemma4TextConfig

    cfg = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    train = cfg["training"]
    steps = args.steps if args.steps is not None else train["steps"]
    base = cfg["base_model"]
    validate_lora_config(cfg["lora"])
    if steps <= 0 or train["batch_size"] != 1:
        parser.error("steps > 0 et batch_size=1 requis")
    if base["architecture"] != "Gemma4ForCausalLM" or not train["fp16"] or train["bf16"]:
        parser.error("Essai Gemma texte seul en fp16, bf16=False requis")
    random.seed(cfg["seed"])
    torch.manual_seed(cfg["seed"])
    torch.set_num_threads(train["torch_threads"])

    examples = load_jsonl(ROOT / cfg["data"])
    prepare_examples(examples)

    device = ("cuda" if torch.cuda.is_available() else "cpu") if args.device == "auto" else args.device
    if device == "cuda" and not torch.cuda.is_available():
        parser.error("--device cuda demandé mais aucun GPU CUDA n'est visible par PyTorch.")
    if args.qlora and device != "cuda":
        parser.error("--qlora nécessite un GPU NVIDIA (--device cuda).")
    dtype = torch.float16 if device == "cuda" else torch.float32

    proc = psutil.Process()
    start = time.perf_counter()
    source = {"revision": base["revision"], "local_files_only": args.offline}
    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()
    with PeakMemory() as load_peak:
        tokenizer = AutoTokenizer.from_pretrained(base["model_id"], **source)
        extra = {}
        if args.qlora:
            from transformers import BitsAndBytesConfig

            extra = {"quantization_config": BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                                               bnb_4bit_compute_dtype=torch.float16),
                     "device_map": {"": 0}}
        multimodal_config = AutoConfig.from_pretrained(base["model_id"], **source)
        text_config = multimodal_config.get_text_config()
        if not isinstance(text_config, Gemma4TextConfig):
            raise ValueError("Gemma4TextConfig attendu")
        model, loading = Gemma4ForCausalLM.from_pretrained(
            base["model_id"], config=text_config, dtype=dtype,
            key_mapping={r"^model\.language_model\.": "model."},
            output_loading_info=True, **extra, **source)
        # Les tours ignorées sont attendues ; aucun poids texte manquant n'est accepté.
        missing = [k for k in loading.get("missing_keys", [])
                   if not (k.endswith("lm_head.weight") and text_config.tie_word_embeddings)]
        unexpected = [k for k in loading.get("unexpected_keys", [])
                      if not any(tower in k for tower in ("vision", "audio", "embed_vision", "embed_audio"))]
        if missing or unexpected or loading.get("mismatched_keys") or loading.get("error_msgs"):
            raise ValueError(f"Chargement texte incohérent : {loading}")
        if args.qlora:
            model = prepare_qlora_text(model, torch)
        elif device == "cuda":
            model = model.to(device)
        lora = cfg["lora"]
        model = get_peft_model(model, LoraConfig(r=lora["r"], lora_alpha=lora["alpha"], lora_dropout=lora["dropout"],
                                                 target_modules=lora["target_modules"], bias="none", use_dora=False,
                                                 base_model_name_or_path=base["model_id"], revision=base["revision"],
                                                 task_type="CAUSAL_LM"))
    load_seconds = time.perf_counter() - start
    if train["gradient_checkpointing"]:
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
        model.enable_input_require_grads()
    model.config.use_cache = False
    # L'identifiant HF est conservé même si une bibliothèque normalise _name_or_path.
    model.peft_config["default"].base_model_name_or_path = base["model_id"]
    model.peft_config["default"].revision = base["revision"]
    trainable, total = model.get_nb_trainable_parameters()
    encoded = [encode_example(ex, tokenizer, train["max_tokens"]) for ex in examples]
    print(f"Modèle chargé en {load_seconds:.1f} s ; {trainable:,} paramètres entraînables sur {total:,}", flush=True)

    load_vram_peak = torch.cuda.max_memory_allocated() if device == "cuda" else None
    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()
    optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=train["learning_rate"])
    order = list(range(len(encoded)))
    log = []
    scaler = torch.amp.GradScaler("cuda", enabled=device == "cuda")
    model.train()
    with PeakMemory() as train_peak:
        for step in range(steps):
            if step % len(order) == 0:
                random.shuffle(order)
            item = encoded[order[step % len(order)]]
            t0 = time.perf_counter()
            batch = {k: torch.tensor([v], device=device) for k, v in item.items()}
            with torch.autocast(device_type=device, dtype=torch.float16, enabled=device == "cuda"):
                loss = model(**batch).loss
            if not torch.isfinite(loss):
                raise RuntimeError("Perte non finie ; arrêter et conserver le diagnostic")
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            if any(p.grad is not None and not torch.isfinite(p.grad).all() for p in model.parameters()):
                raise RuntimeError("Gradient non fini")
            scaler.step(optimizer)
            scaler.update()
            optimizer.zero_grad()
            if device == "cuda":
                torch.cuda.synchronize()
            seconds = time.perf_counter() - t0
            log.append({"step": step + 1, "example": examples[order[step % len(order)]]["id"],
                        "tokens": len(item["input_ids"]), "loss": round(loss.item(), 4), "seconds": round(seconds, 1),
                        "rss_gb": gb(proc.memory_info().rss)})
            print(json.dumps(log[-1]), flush=True)

    run_dir = new_run_directory(root=Path(cfg.get("runs_dir", ROOT / "eval/runs")), name="lora_essai")
    adapter_dir = ROOT / cfg["adapter_dir"]
    model.save_pretrained(adapter_dir, save_embedding_layers=False)
    # Vérification locale des tenseurs PEFT sauvegardés, sans génération ni base supplémentaire.
    from peft.utils.save_and_load import load_peft_weights, set_peft_model_state_dict
    reloaded = load_peft_weights(str(adapter_dir), device="cpu")
    if not reloaded or not all(torch.isfinite(t).all() for t in reloaded.values()):
        raise RuntimeError("Adaptateur PEFT vide ou non fini")
    reload_result = set_peft_model_state_dict(model, reloaded)
    if reload_result.unexpected_keys:
        raise RuntimeError(str(reload_result.unexpected_keys))
    del model, optimizer
    if device == "cuda":
        torch.cuda.empty_cache()

    window = max(1, min(5, steps // 3))
    first, last = log[:window], log[-window:]
    metrics = {
        "device": device,
        "gpu": torch.cuda.get_device_name(0) if device == "cuda" else None,
        "dtype": str(dtype).removeprefix("torch."),
        "qlora_4bit": args.qlora,
        "vram_peak_gb": gb(max(load_vram_peak, torch.cuda.max_memory_allocated())) if device == "cuda" else None,
        "vram_peak_load_gb": gb(load_vram_peak) if device == "cuda" else None,
        "checkpoint_loading_info": loading,
        "steps": steps,
        "examples": len(examples),
        "trainable_parameters": trainable,
        "total_parameters": total,
        "load_seconds": round(load_seconds, 1),
        "rss_peak_load_gb": gb(load_peak.peak),
        "rss_peak_training_gb": gb(train_peak.peak),
        "seconds_per_step_mean": round(sum(r["seconds"] for r in log) / steps, 1),
        "seconds_per_1k_tokens_mean": round(sum(r["seconds"] for r in log) / sum(r["tokens"] for r in log) * 1000, 1),
        "loss_first_mean": round(sum(r["loss"] for r in first) / len(first), 4),
        "loss_last_mean": round(sum(r["loss"] for r in last) / len(last), 4),
        "loss_window": window,
    }

    metrics["adapter_reload_ok"] = True
    metrics["adapter_reload_scope"] = "PEFT saved tensors reloaded into current model; no inference"

    config = {**cfg, "steps": steps, "base_model": base, "packages": package_versions(),
              "python": platform.python_version(),
              "machine": f"{platform.processor()} · {gb(psutil.virtual_memory().total)} GiB RAM",
              "purpose": "hardware_feasibility_not_quality", "loss_scope": "loss mesurée sur les exemples d'entraînement",
              "annotations_review_status": "Linda must review regenerated v16 examples"}
    (run_dir / "train_log.jsonl").write_text("".join(json.dumps(r) + "\n" for r in log), encoding="utf-8")
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    (run_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    print(f"Adaptateur : {adapter_dir}\nRésultats : {run_dir}")


if __name__ == "__main__":
    main()
