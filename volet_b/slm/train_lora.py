"""SCRUM-29 — Essai LoRA court sur CPU : mémoire, durée par pas, descente de la loss, rechargement.

    python -m volet_b.slm.train_lora --offline              # 30 pas, configs/lora_essai.yaml
    python -m volet_b.slm.train_lora --offline --steps 3    # vérification rapide
    python -m volet_b.slm.train_lora --device cuda --qlora  # GPU NVIDIA à faible VRAM (bitsandbytes)

Test de faisabilité matérielle, pas de qualité : les exemples sont provisoires (make_seed.py) et la loss
est mesurée sur ces mêmes exemples. La consigne est placée avant les logs (règle du volet B, SCRUM-57) ;
seule la réponse attendue C5 contribue à la loss. Les sorties vont dans un dossier C7 unique de eval/runs/.
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

from teamai.contracts import load_jsonl, validate_answer
from teamai.paths import ROOT
from volet_b.slm.first_inference import PeakMemory, gb, new_run_directory
from volet_b.slm.generate import load_config

CONFIG = Path(__file__).parent / "configs" / "lora_essai.yaml"

INSTRUCTION = """Tu analyses les logs HDFS d'un seul bloc de données. Réponds uniquement par un objet JSON avec les clés :
resume_evenements (texte), faits_observes, hypotheses, infos_manquantes, sources (listes de textes), abstention (booléen).
N'invente aucune information absente des logs ; si la trace ne permet pas de conclure, mets abstention à true.

Logs :
{lines}"""


def build_messages(trace_lines: list[str]) -> list[dict]:
    """Prompt du volet B : consigne d'abord, logs ensuite ; ni label ni réponse attendue (C5)."""
    return [{"role": "user", "content": INSTRUCTION.format(lines="\n".join(trace_lines))}]


def encode_example(example: dict, tokenizer, max_tokens: int) -> dict:
    """Ids du prompt + réponse ; labels à -100 sur le prompt pour n'apprendre que la réponse."""
    prompt_ids = tokenizer.apply_chat_template(build_messages(example["trace_lines"]), add_generation_prompt=True)
    answer = json.dumps(example["expected"], ensure_ascii=False)
    answer_ids = tokenizer(answer, add_special_tokens=False)["input_ids"] + [tokenizer.eos_token_id]
    ids = list(prompt_ids) + answer_ids
    if len(ids) > max_tokens:
        raise ValueError(f"{example['id']} : {len(ids)} tokens > max_tokens {max_tokens}")
    return {"input_ids": ids, "labels": [-100] * len(prompt_ids) + answer_ids}


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
    from transformers import AutoModelForCausalLM, AutoTokenizer

    cfg = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    train = cfg["training"]
    steps = args.steps or train["steps"]
    base = load_config()
    random.seed(cfg["seed"])
    torch.manual_seed(cfg["seed"])
    torch.set_num_threads(train["torch_threads"])

    examples = load_jsonl(ROOT / cfg["data"])
    for ex in examples:
        if ex["split"] != "train" or validate_answer(ex["expected"]):
            raise ValueError(f"{ex['id']} : exemple hors train ou réponse C5 invalide")

    device = ("cuda" if torch.cuda.is_available() else "cpu") if args.device == "auto" else args.device
    if device == "cuda" and not torch.cuda.is_available():
        parser.error("--device cuda demandé mais aucun GPU CUDA n'est visible par PyTorch.")
    if args.qlora and device != "cuda":
        parser.error("--qlora nécessite un GPU NVIDIA (--device cuda).")
    # CPU : float32 comme l'inférence (bfloat16 lent sur processeur) ; GPU : bfloat16 si supporté.
    dtype = getattr(torch, base["dtype"])
    if device == "cuda":
        dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16

    proc = psutil.Process()
    start = time.perf_counter()
    source = {"revision": base["revision"], "local_files_only": args.offline}
    with PeakMemory() as load_peak:
        tokenizer = AutoTokenizer.from_pretrained(base["model_id"], **source)
        extra = {}
        if args.qlora:
            from transformers import BitsAndBytesConfig

            extra = {"quantization_config": BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                                               bnb_4bit_compute_dtype=dtype),
                     "device_map": {"": 0}}
        model = AutoModelForCausalLM.from_pretrained(base["model_id"], dtype=dtype, **extra, **source)
        if args.qlora:
            from peft import prepare_model_for_kbit_training

            model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=train["gradient_checkpointing"])
        elif device == "cuda":
            model = model.to(device)
        lora = cfg["lora"]
        model = get_peft_model(model, LoraConfig(r=lora["r"], lora_alpha=lora["alpha"], lora_dropout=lora["dropout"],
                                                 target_modules=lora["target_modules"], task_type="CAUSAL_LM"))
    load_seconds = time.perf_counter() - start
    if train["gradient_checkpointing"]:
        model.gradient_checkpointing_enable()
        model.enable_input_require_grads()
    trainable, total = model.get_nb_trainable_parameters()
    encoded = [encode_example(ex, tokenizer, train["max_tokens"]) for ex in examples]
    print(f"Modèle chargé en {load_seconds:.1f} s ; {trainable:,} paramètres entraînables sur {total:,}", flush=True)

    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()
    optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=train["learning_rate"])
    order = list(range(len(encoded)))
    log = []
    model.train()
    with PeakMemory() as train_peak:
        for step in range(steps):
            if step % len(order) == 0:
                random.shuffle(order)
            item = encoded[order[step % len(order)]]
            t0 = time.perf_counter()
            batch = {k: torch.tensor([v], device=device) for k, v in item.items()}
            loss = model(**batch).loss
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            if device == "cuda":
                torch.cuda.synchronize()
            seconds = time.perf_counter() - t0
            log.append({"step": step + 1, "example": examples[order[step % len(order)]]["id"],
                        "tokens": len(item["input_ids"]), "loss": round(loss.item(), 4), "seconds": round(seconds, 1),
                        "rss_gb": gb(proc.memory_info().rss)})
            print(json.dumps(log[-1]), flush=True)

    run_dir = new_run_directory(name="lora_essai")
    adapter_dir = ROOT / cfg["adapter_dir"]
    model.save_pretrained(adapter_dir)
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
        "vram_peak_gb": gb(torch.cuda.max_memory_allocated()) if device == "cuda" else None,
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

    # Rechargement par la porte d'entrée commune du volet B (critère du ticket) : sur CPU, en float32,
    # comme toutes les inférences de generate() ; un adaptateur entraîné sur GPU se recharge donc aussi ici.
    from volet_b.slm.generate import generate

    t0 = time.perf_counter()
    reload = generate(build_messages(examples[0]["trace_lines"]), adapter=str(adapter_dir),
                      max_new_tokens=60, local_files_only=args.offline)
    metrics["adapter_reload_ok"] = bool(reload["text"].strip())
    metrics["adapter_reload_seconds"] = round(time.perf_counter() - t0, 1)

    config = {**cfg, "steps": steps, "base_model": base, "packages": package_versions(),
              "python": platform.python_version(),
              "machine": f"{platform.processor()} · {gb(psutil.virtual_memory().total)} GiB RAM",
              "purpose": "hardware_feasibility_not_quality", "loss_scope": "loss mesurée sur les exemples d'entraînement"}
    (run_dir / "train_log.jsonl").write_text("".join(json.dumps(r) + "\n" for r in log), encoding="utf-8")
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    (run_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    (run_dir / "reload_output.txt").write_text(reload["text"], encoding="utf-8")
    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    print(f"Adaptateur : {adapter_dir}\nRésultats : {run_dir}")


if __name__ == "__main__":
    main()
