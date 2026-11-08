"""SCRUM-29 — Essai LoRA Gemma texte seul sur T4 Kaggle : mémoire, durée par pas, descente de la loss, rechargement.

    python -m volet_b.slm.train_lora --offline              # 30 pas, configs/lora_essai.yaml
    python -m volet_b.slm.train_lora --offline --steps 3    # premier essai
    python -m volet_b.slm.train_lora --device cuda --qlora  # T4 16 Go (bitsandbytes), pas une carte 6 Go

Test de faisabilité matérielle, pas de qualité : les exemples sont provisoires (make_seed.py) et la loss
est mesurée sur ces mêmes exemples. La consigne est placée avant les logs (règle du volet B, SCRUM-57) ;
seuls le JSON v16 et sa fin de tour contribuent à la loss. Les sorties vont dans un dossier C7 unique de eval/runs/.
"""
import argparse
import json
import math
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
FP16_FAILURE = ("gradients non finis persistants en fp16 : l'échelle ne suffit pas, "
                "activations hors plage fp16 probables")


def supervised_causal_loss(model, batch, *, first=None):
    """Calcule la CE décalée FP32 sur le suffixe utile d'un seul exemple.

    Sans labels au forward, Gemma découpe les états avant lm_head et softcapping.
    first peut être fourni pour vérifier une frontière précalculée ; tous les
    labels supervisés doivent être à partir de cet indice (strictement positif).
    Les trous et la fin masquée restent autorisés. Seuls les logits réduits sont
    promus en FP32 ; autograd garde les tenseurs nécessaires au backward.
    """
    import torch

    labels = batch["labels"]
    if labels.ndim != 2 or labels.shape[0] != 1 or labels.shape != batch["input_ids"].shape:
        raise ValueError("Loss réduite : batch_size=1 et labels alignés requis")
    positions = (labels[0] != -100).nonzero(as_tuple=True)[0]
    if positions.numel() == 0:
        raise ValueError("Loss réduite : aucun label supervisé")
    actual_first = int(positions[0].item())
    first = actual_first if first is None else first
    if not isinstance(first, int) or not 0 < first < labels.shape[1]:
        raise ValueError("Loss réduite : first doit avoir une position précédente")
    if bool((positions < first).any()):
        raise ValueError("Loss réduite : un label supervisé précède first")
    if first != actual_first:
        raise ValueError("Loss réduite : first doit être le premier label supervisé")
    outputs = model(input_ids=batch["input_ids"], attention_mask=batch["attention_mask"],
                    logits_to_keep=labels.shape[1] - first + 1)
    logits = outputs.logits
    loss = torch.nn.functional.cross_entropy(
        logits[:, :-1].float().reshape(-1, logits.shape[-1]),
        labels[:, first:].reshape(-1), ignore_index=-100, reduction="mean")
    del outputs, logits
    return loss


def ensure_trainable_float32(model):
    """Vérifie et promeut les seuls paramètres entraînables avant création de l'optimiseur."""
    import torch

    parameters = [p for p in model.parameters() if p.requires_grad]
    if not parameters:
        raise ValueError("Aucun paramètre LoRA entraînable")
    for parameter in parameters:
        if parameter.dtype != torch.float32:
            parameter.data = parameter.data.to(dtype=torch.float32)
    if any(p.dtype != torch.float32 for p in parameters):
        raise RuntimeError("Paramètres LoRA entraînables float32 requis pour GradScaler.unscale_")
    return parameters


def amp_optimizer_step(loss, parameters, optimizer, scaler, max_grad_norm):
    """Backprop, unscale, écrête les gradients finis et laisse AMP sauter les débordements.

    scale est l'échelle après update. Un pas est sauté si un gradient après
    unscale est non fini ou si cette échelle a diminué. Sans AMP, un gradient
    non fini évite aussi toute application de l'optimiseur.
    """
    import torch

    if not bool(torch.isfinite(loss)):
        raise RuntimeError("Perte non finie ; arrêter et conserver le diagnostic")
    scale_before = scaler.get_scale()
    scaler.scale(loss).backward()
    scaler.unscale_(optimizer)
    finite = all(bool(torch.isfinite(p.grad).all()) for p in parameters if p.grad is not None)
    grad_norm = None
    if finite:
        norm = torch.nn.utils.clip_grad_norm_(parameters, max_grad_norm)
        grad_norm = float(norm.item()) if bool(torch.isfinite(norm)) else None
    if finite or scaler.is_enabled():
        scaler.step(optimizer)
    scaler.update()
    scale = scaler.get_scale()
    optimizer.zero_grad(set_to_none=True)
    return {"scale": scale, "skipped": not finite or scale < scale_before, "grad_norm": grad_norm}


class OptimizerProgress:
    """Compte les pas appliqués et sautés, avec arrêt sur débordements persistants."""

    def __init__(self, max_consecutive_skips):
        """Initialise une limite strictement positive de pas consécutifs sautés."""
        if not isinstance(max_consecutive_skips, int) or max_consecutive_skips <= 0:
            raise ValueError("training.max_consecutive_skips doit être un entier positif")
        self.max_consecutive_skips = max_consecutive_skips
        self.optimizer_steps = 0
        self.skipped_steps = 0
        self.consecutive_skips = 0

    def record(self, skipped):
        """Enregistre chaque pas après journalisation et refuse la limite de sauts atteinte."""
        if skipped:
            self.skipped_steps += 1
            self.consecutive_skips += 1
        else:
            self.optimizer_steps += 1
            self.consecutive_skips = 0
        if self.consecutive_skips >= self.max_consecutive_skips:
            raise RuntimeError(FP16_FAILURE)

    def finish(self):
        """Refuse une exécution terminée sans aucune mise à jour de l'optimiseur."""
        if self.optimizer_steps == 0:
            raise RuntimeError("Aucun pas d'optimiseur appliqué ; " + FP16_FAILURE)


def prepare_qlora_text(model, torch):
    """Gèle la base NF4 sans promouvoir les énormes embeddings en FP32, même temporairement."""
    for name, parameter in model.named_parameters():
        parameter.requires_grad_(False)
        if "norm" in name and parameter.__class__.__name__ != "Params4bit":
            parameter.data = parameter.data.to(dtype=torch.float32)
    return model


def jsonable(value):
    """Rend les infos de chargement Transformers sérialisables (ensembles triés, objets en texte)."""
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (set, frozenset)):
        return sorted(jsonable(v) for v in value)
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    return value if value is None or isinstance(value, (str, int, float, bool)) else str(value)


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
    """Entraîne LoRA avec loss réduite et AMP suivi, puis sauvegarde et vérifie le rechargement local."""
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
    init_scale = train.get("init_scale", 1024)
    max_grad_norm = train.get("max_grad_norm", 1.0)
    progress = OptimizerProgress(train.get("max_consecutive_skips", 8))
    if not math.isfinite(init_scale) or init_scale <= 0 or not math.isfinite(max_grad_norm) or max_grad_norm <= 0:
        parser.error("training.init_scale et training.max_grad_norm doivent être finis et positifs")
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
                                                 task_type="CAUSAL_LM"), autocast_adapter_dtype=True)
        parameters = ensure_trainable_float32(model)
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
    optimizer = torch.optim.AdamW(parameters, lr=train["learning_rate"])
    order = list(range(len(encoded)))
    log = []
    scaler = torch.amp.GradScaler("cuda", enabled=device == "cuda", init_scale=init_scale)
    model.train()
    with PeakMemory() as train_peak:
        for step in range(steps):
            if step % len(order) == 0:
                random.shuffle(order)
            item = encoded[order[step % len(order)]]
            t0 = time.perf_counter()
            batch = {k: torch.tensor([v], device=device) for k, v in item.items()}
            with torch.autocast(device_type=device, dtype=torch.float16, enabled=device == "cuda"):
                loss = supervised_causal_loss(model, batch)
            amp = amp_optimizer_step(loss, parameters, optimizer, scaler, max_grad_norm)
            if device == "cuda":
                torch.cuda.synchronize()
            seconds = time.perf_counter() - t0
            log.append({"step": step + 1, "example": examples[order[step % len(order)]]["id"],
                        "tokens": len(item["input_ids"]), "loss": loss.item(), "seconds": round(seconds, 1),
                        "rss_gb": gb(proc.memory_info().rss), **amp,
                        "vram_allocated_gb": gb(torch.cuda.memory_allocated()) if device == "cuda" else None,
                        "vram_peak_gb": gb(torch.cuda.max_memory_allocated()) if device == "cuda" else None})
            print(json.dumps(log[-1]), flush=True)
            del loss, batch
            progress.record(amp["skipped"])
    progress.finish()

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
    del model, optimizer, parameters
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
        "checkpoint_loading_info": jsonable(loading),
        "steps": steps,
        "optimizer_steps": progress.optimizer_steps,
        "skipped_steps": progress.skipped_steps,
        "final_scale": scaler.get_scale(),
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
        "loss_mean": round(sum(r["loss"] for r in log) / len(log), 4),
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
