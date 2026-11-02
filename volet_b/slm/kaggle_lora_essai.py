"""SCRUM-29 : archive train seule, préparation T4, trente pas QLoRA et export GGUF.

L'import et --dry-run ne téléchargent rien, n'installent rien et ne chargent aucun
modèle. Localement, construire l'archive minimale train :
python -m volet_b.slm.kaggle_lora_essai --bundle sortie.zip
Envoyer uniquement cette archive sur Kaggle et l'extraire dans un dossier dédié.
Depuis la racine extraite (jamais le dépôt complet) :
python -m volet_b.slm.kaggle_lora_essai --dry-run
python -m volet_b.slm.kaggle_lora_essai --install
Redémarrer le kernel si des bibliothèques avaient déjà été importées, puis :
python -m volet_b.slm.kaggle_lora_essai --steps 30
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
import zipfile

from teamai.paths import ROOT

COMMIT = "0c1e57098"
PACKAGES = ["torch==2.9.1", "transformers==5.6.2", "peft==0.18.1", "accelerate==1.12.0",
            "bitsandbytes==0.49.2", "safetensors==0.7.0", "gguf==0.19.0", "sentencepiece==0.2.1",
            "pyyaml==6.0.3", "psutil==7.2.2", "pandas==3.0.3"]


def plan(working, steps):
    """Décrit les entrées, versions et sorties sans importer les bibliothèques GPU."""
    return {"install": [sys.executable, "-m", "pip", "install", *PACKAGES],
            "model_id": "google/gemma-4-E4B-it-qat-q4_0-unquantized", "revision": "476025a01dbf99361c062bbeca3d6a76bb4c4566",
            "llama_cpp_commit": COMMIT, "steps": steps, "device": "cuda", "qlora": "nf4/float16",
            "batch_size": 1, "thinking": False, "split": "train only, checked against C4",
            "outputs": [str(working / p) for p in ("adapter", "gguf/adapter.gguf", "gguf/meta.json",
                        "gguf/conversion.log", "runs", "base-config", "lora_essai.yaml")]}


def fetch_converter(working):
    """Télécharge l'archive au commit figé et enregistre l'intégrité des sources, sans Git."""
    archive = working / "llama.cpp.zip"
    destination = working / "llama.cpp"
    if destination.exists():
        raise ValueError("Dossier llama.cpp déjà présent ; utiliser un nouveau dossier de travail")
    urllib.request.urlretrieve(f"https://codeload.github.com/ggml-org/llama.cpp/zip/{COMMIT}", archive)
    with zipfile.ZipFile(archive) as zipped:
        for member in zipped.infolist():
            parts = Path(member.filename).parts
            relative = Path(*parts[1:])
            target = (destination / relative).resolve()
            if not target.is_relative_to(destination.resolve()):
                raise ValueError("Chemin d'archive invalide")
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with zipped.open(member) as source, target.open("wb") as output:
                    shutil.copyfileobj(source, output)
    files = {p.relative_to(destination).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in destination.rglob("*.py")}
    (destination / "teamai-converter.json").write_text(json.dumps({"commit": COMMIT, "files": files}), encoding="utf-8")
    archive.unlink()
    return destination


def main(argv=None):
    """Valide les données avant tout téléchargement, puis entraîne et convertit en processus séparés."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, help="Construit localement une archive train seule et quitte")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--install", action="store_true", help="Installe les versions, puis quitte sans modèle")
    parser.add_argument("--steps", type=int, default=30)
    parser.add_argument("--working", type=Path, default=Path("/kaggle/working"))
    args = parser.parse_args(argv)
    if args.steps <= 0:
        parser.error("--steps doit être positif")
    from volet_b.slm.kaggle_bundle import MANIFEST, build_bundle, validate_bundle

    if args.bundle:
        if str(ROOT).startswith("/kaggle/"):
            raise ValueError("La préparation du bundle est locale uniquement")
        return build_bundle(args.bundle)
    # Tous les modes Kaggle, y compris --install, contrôlent les entrées en premier.
    if not args.dry_run or (ROOT / MANIFEST).exists() or str(ROOT).startswith("/kaggle/"):
        validate_bundle(ROOT)
    execution = plan(args.working, args.steps)
    if args.dry_run:
        print(json.dumps(execution, indent=2))
        return execution
    if args.install:
        subprocess.run(execution["install"], check=True)
        return
    import yaml
    from huggingface_hub import snapshot_download
    from teamai.contracts import load_jsonl
    from volet_b.slm.lora_data import prepare_examples, validate_lora_config
    from volet_b.slm.train_lora import CONFIG

    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    prepare_examples(load_jsonl(ROOT / cfg["data"]))
    validate_lora_config(cfg["lora"])
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError("Activer une T4 Kaggle avant de télécharger la base")
    working = args.working.resolve()
    working.mkdir(parents=True, exist_ok=True)
    if (working / "adapter").exists() or (working / "gguf").exists():
        raise ValueError("Sortie existante : ne pas écraser un essai précédent")
    base = cfg["base_model"]
    snapshot = Path(snapshot_download(base["model_id"], revision=base["revision"],
                    allow_patterns=["*.json", "*.jinja", "*.model", "tokenizer*", "*.safetensors"]))
    revision = snapshot.name
    if revision != base["revision"]:
        raise ValueError("Snapshot HF différent de la révision demandée")
    base_config = working / "base-config"
    base_config.mkdir(exist_ok=True)
    shutil.copy2(snapshot / "config.json", base_config / "config.json")
    provenance = {"model_id": base["model_id"], "revision": revision,
                  "config_sha256": hashlib.sha256((base_config / "config.json").read_bytes()).hexdigest()}
    (base_config / "teamai-base.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    tools = fetch_converter(working)
    cfg["data"] = str(ROOT / cfg["data"])
    cfg["adapter_dir"] = str(working / "adapter")
    cfg["runs_dir"] = str(working / "runs")
    # La révision complète vérifiée est enregistrée dans C7.
    cfg["resolved_base_revision"] = revision
    config_path = working / "lora_essai.yaml"
    config_path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    subprocess.run([sys.executable, "-m", "volet_b.slm.train_lora", "--config", str(config_path),
                    "--steps", str(args.steps), "--device", "cuda", "--qlora", "--offline"], cwd=ROOT, check=True)
    env = {**os.environ, "PYTHONPATH": os.pathsep.join([str(tools / "gguf-py"), str(ROOT), os.environ.get("PYTHONPATH", "")])}
    subprocess.run([sys.executable, "-m", "volet_b.slm.convert_gguf", "adapter", str(working / "adapter"),
                    "--base-config", str(base_config), "--llama-cpp", str(tools),
                    "--output-dir", str(working / "gguf")], cwd=ROOT, env=env, check=True)
    print(json.dumps(execution, indent=2))


if __name__ == "__main__":
    main()
