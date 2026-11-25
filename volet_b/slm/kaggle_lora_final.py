"""SCRUM-39 : essais LoRA complets sur T4, export GGUF de chaque adaptateur et sélection sur val.

Depuis la racine d'un clone du dépôt hors de /kaggle (le mode archive de SCRUM-29 ne s'applique pas) :
python -m volet_b.slm.kaggle_lora_final --dry-run
python -m volet_b.slm.kaggle_lora_final --install
python -m volet_b.slm.kaggle_lora_final --train --working /kaggle/working
python -m volet_b.slm.kaggle_lora_final --select runs/val_r8_qv/metrics.json runs/val_r16_qkvo/metrics.json
"""
import argparse
import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from teamai.paths import ROOT

CONFIG = ROOT / "volet_b" / "slm" / "configs" / "lora_final.yaml"
SUPPORT_KEYS = ("unknown_references", "unsupported_network")


def merge(base, override):
    """Fusion récursive : les clés de l'essai remplacent celles du socle."""
    result = copy.deepcopy(base)
    for key, value in override.items():
        result[key] = merge(result[key], value) if isinstance(value, dict) and isinstance(result.get(key), dict) else value
    return result


def trial_configs(cfg, working):
    """Construit une configuration train_lora complète par essai, avec sorties dans working."""
    common = {k: v for k, v in cfg.items() if k not in ("essais", "selection", "val")}
    trials = {}
    for name, override in cfg["essais"].items():
        trial = merge(common, override)
        trial.update(adapter_dir=str(Path(working) / "adapters" / name), runs_dir=str(Path(working) / "runs"),
                     run_name=f"lora_{name}", essai=name)
        trials[name] = trial
    return trials


def selection_key(metrics):
    """Clé de tri de la règle écrite : contrat valide, hypothèses appuyées, puis moins d'erreurs d'appui."""
    hypotheses = metrics.get("hypotheses_per_block_with_incident")
    errors = sum(metrics.get(key, 0) or 0 for key in SUPPORT_KEYS)
    return (metrics["v16_contract_valid"], -1.0 if hypotheses is None else hypotheses, -errors)


def select(named_metrics):
    """Choisit l'essai selon selection_key ; une égalité complète garde le premier essai déclaré."""
    if not named_metrics:
        raise ValueError("Aucun essai à comparer")
    ranked = sorted(named_metrics.items(), key=lambda item: selection_key(item[1]), reverse=True)
    best = ranked[0][0]
    return {"selected": best, "ranking": [{"essai": name, "key": list(selection_key(m))} for name, m in ranked],
            "rule": "v16_contract_valid max, puis hypotheses_per_block_with_incident max, "
                    "puis unknown_references + unsupported_network min ; val uniquement"}


def snapshot_base_config(cfg, working):
    """Télécharge la base exacte et copie sa configuration pour le convertisseur."""
    from huggingface_hub import snapshot_download

    base = cfg["base_model"]
    snapshot = Path(snapshot_download(base["model_id"], revision=base["revision"],
                                      allow_patterns=["*.json", "*.jinja", "*.model", "tokenizer*", "*.safetensors"]))
    if snapshot.name != base["revision"]:
        raise ValueError("Snapshot HF différent de la révision demandée")
    target = Path(working) / "base-config"
    target.mkdir(parents=True, exist_ok=True)
    shutil.copy2(snapshot / "config.json", target / "config.json")
    provenance = {"model_id": base["model_id"], "revision": snapshot.name,
                  "config_sha256": hashlib.sha256((target / "config.json").read_bytes()).hexdigest()}
    (target / "teamai-base.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    return target


def train_all(cfg, working):
    """Entraîne chaque essai dans un sous-processus, puis convertit l'adaptateur seul en GGUF."""
    from volet_b.slm.kaggle_lora_essai import fetch_converter, training_environment

    working = Path(working).resolve()
    working.mkdir(parents=True, exist_ok=True)
    if (working / "adapters").exists():
        raise ValueError("Sortie existante : ne pas écraser un essai précédent")
    base_config = snapshot_base_config(cfg, working)
    tools = fetch_converter(working)
    outputs = {}
    for name, trial in trial_configs(cfg, working).items():
        path = working / f"lora_{name}.yaml"
        path.write_text(yaml.safe_dump(trial, allow_unicode=True), encoding="utf-8")
        subprocess.run([sys.executable, "-m", "volet_b.slm.train_lora", "--config", str(path),
                        "--device", "cuda", "--qlora"], cwd=ROOT, env=training_environment(os.environ), check=True)
        env = {**os.environ, "PYTHONPATH": os.pathsep.join([str(tools / "gguf-py"), str(ROOT), os.environ.get("PYTHONPATH", "")])}
        gguf = working / "gguf" / name
        subprocess.run([sys.executable, "-m", "volet_b.slm.convert_gguf", "adapter", trial["adapter_dir"],
                        "--base-config", str(base_config), "--llama-cpp", str(tools), "--output-dir", str(gguf)],
                       cwd=ROOT, env=env, check=True)
        outputs[name] = str(gguf / "adapter.gguf")
    (working / "adapters.json").write_text(json.dumps(outputs, indent=2), encoding="utf-8")
    return outputs


def main(argv=None):
    """Affiche le plan, installe, entraîne ou sélectionne selon l'option."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=CONFIG)
    parser.add_argument("--working", type=Path, default=Path("/kaggle/working"))
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--install", action="store_true")
    mode.add_argument("--train", action="store_true")
    mode.add_argument("--select", nargs="+", type=Path, metavar="METRICS",
                      help="metrics.json des runs val, un par essai, dans l'ordre des essais")
    args = parser.parse_args(argv)
    cfg = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    if args.dry_run:
        print(json.dumps(trial_configs(cfg, args.working), indent=2, ensure_ascii=False))
    elif args.install:
        from volet_b.slm.kaggle_lora_essai import PACKAGES
        subprocess.run([sys.executable, "-m", "pip", "install", *PACKAGES], check=True)
    elif args.train:
        print(json.dumps(train_all(cfg, args.working), indent=2))
    else:
        names = list(cfg["essais"])
        if len(args.select) != len(names):
            parser.error(f"Un metrics.json par essai attendu : {names}")
        metrics = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in zip(names, args.select)}
        print(json.dumps(select(metrics), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
