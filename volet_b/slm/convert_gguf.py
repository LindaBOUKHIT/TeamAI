"""SCRUM-57 : conversion hors ligne d'un adaptateur PEFT, seul ou fusionné, vers GGUF."""
import argparse
import ctypes
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

from teamai.paths import ROOT, SLM_ADAPTERS, resolve_path
from volet_b.slm.lora_data import validate_lora_config

LLAMA_CPP_COMMIT = "0c1e57098"


def verify_converter_revision(directory):
    """Vérifie HEAD par lecture seule, ou le manifeste d'archive Kaggle, sans commande Git."""
    directory = resolve_path(directory)
    marker = directory / "teamai-converter.json"
    if marker.is_file():
        manifest = json.loads(marker.read_text(encoding="utf-8"))
        if manifest.get("commit") != LLAMA_CPP_COMMIT:
            raise ValueError("Commit llama.cpp incorrect")
        files = manifest.get("files", {})
        if "convert_lora_to_gguf.py" not in files or "conversion/gemma.py" not in files:
            raise ValueError("Manifeste du convertisseur incomplet")
        for name, digest in files.items():
            if hashlib.sha256((directory / name).read_bytes()).hexdigest() != digest:
                raise ValueError("Convertisseur modifié : " + name)
        return LLAMA_CPP_COMMIT
    git_dir = directory / ".git"
    head = (git_dir / "HEAD").read_text(encoding="ascii").strip()
    if head.startswith("ref: "):
        ref = head[5:]
        if (git_dir / ref).is_file():
            head = (git_dir / ref).read_text(encoding="ascii").strip()
        else:
            head = next(line.split()[0] for line in (git_dir / "packed-refs").read_text().splitlines()
                        if line.endswith(" " + ref))
    if not head.startswith(LLAMA_CPP_COMMIT):
        raise ValueError("llama.cpp doit être épinglé à " + LLAMA_CPP_COMMIT)
    return head


def verify_tensor_coverage(source, output):
    """Exige une paire GGUF A/B pour chaque projection PEFT, sans cible ignorée."""
    from safetensors import safe_open
    from gguf import GGUFReader

    names = {"q_proj": "attn_q", "k_proj": "attn_k", "v_proj": "attn_v", "o_proj": "attn_output",
             "gate_proj": "ffn_gate", "up_proj": "ffn_up", "down_proj": "ffn_down"}
    expected = set()
    with safe_open(str(source / "adapter_model.safetensors"), framework="pt", device="cpu") as tensors:
        for name in tensors.keys():
            match = re.fullmatch(r"(?:base_model\.model\.)?model\.layers\.(\d+)\.(self_attn|mlp)\.([a-z_]+)\.lora_([AB])\.weight", name)
            if not match or match[3] not in names:
                raise ValueError("Tenseur PEFT interdit ou inconnu : " + name)
            expected.add(f"blk.{match[1]}.{names[match[3]]}.weight.lora_{match[4].lower()}")
    actual = {tensor.name for tensor in GGUFReader(str(output)).tensors}
    if not expected or actual != expected:
        raise ValueError(f"Cibles ignorées ou inattendues : absentes={expected-actual}, supplémentaires={actual-expected}")
    for name in expected:
        other = name[:-1] + ("b" if name.endswith("a") else "a")
        if other not in expected:
            raise ValueError("Paire LoRA incomplète : " + name)
    return sorted(actual)


def conversion_command(route, llama_cpp, source, base, output):
    """Construit une commande llama.cpp sans l'exécuter ; les chemins sont des arguments distincts."""
    if route not in {"adapter", "merged"}:
        raise ValueError(f"Route inconnue : {route}")
    script = "convert_lora_to_gguf.py" if route == "adapter" else "convert_hf_to_gguf.py"
    command = [sys.executable, str(resolve_path(llama_cpp) / script), str(source),
               "--outfile", str(output), "--outtype", "f16"]
    if route == "adapter":
        command += ["--base", str(base)]
    return command


def source_hash(source):
    """Empreinte déterministe des noms relatifs et contenus de tous les fichiers de l'adaptateur."""
    digest = hashlib.sha256()
    for path in sorted(source.rglob("*")):
        if path.is_file():
            digest.update(path.relative_to(source).as_posix().encode("utf-8") + b"\0")
            digest.update(str(path.stat().st_size).encode("ascii") + b"\0")
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
    return digest.hexdigest()


def run_converter(command):
    """Exécute le convertisseur installé, réseau désactivé, et explicite ses erreurs."""
    env = {**os.environ, "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"}
    try:
        result = subprocess.run(command, cwd=ROOT, env=env, check=True, capture_output=True, text=True)
        log = result.stdout + result.stderr
        if re.search(r"\b(?:skip(?:ped|ping)?|ignor(?:e[ds]?|ing))\b", log, re.I):
            raise RuntimeError("Le convertisseur signale une cible ignorée : " + log)
        return log
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "Échec du convertisseur llama.cpp. Vérifier ses dépendances "
            "et la compatibilité PEFT ; conserver le diagnostic avant tout nouvel essai.\n"
            + (exc.stdout or "") + (exc.stderr or "")
        ) from exc


def merge_adapter(source, base, destination):
    """Fusionne PEFT en float32 CPU dans un modèle HF temporaire, uniquement depuis le cache."""
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    config_file = base / "config.json"
    if config_file.is_file() and json.loads(config_file.read_text(encoding="utf-8")).get("model_type") == "gemma4":
        from transformers import AutoConfig, Gemma4ForCausalLM
        text_config = AutoConfig.from_pretrained(str(base), local_files_only=True).get_text_config()
        model = Gemma4ForCausalLM.from_pretrained(str(base), config=text_config, dtype=torch.float32,
                    key_mapping={r"^model\.language_model\.": "model."}, local_files_only=True)
    else:
        model = AutoModelForCausalLM.from_pretrained(str(base), dtype=torch.float32, local_files_only=True)
    adapted = PeftModel.from_pretrained(model, str(source), local_files_only=True)
    merged = adapted.merge_and_unload()
    merged.save_pretrained(str(destination), safe_serialization=True)
    AutoTokenizer.from_pretrained(str(base), local_files_only=True).save_pretrained(str(destination))


def quantize(source, output):
    """Quantifie le GGUF f16 en Q4_K_M via l'API C exposée par llama-cpp-python."""
    try:
        import llama_cpp
        params = llama_cpp.llama_model_quantize_default_params()
        params.ftype = llama_cpp.LLAMA_FTYPE_MOSTLY_Q4_K_M
        code = llama_cpp.llama_model_quantize(os.fsencode(source), os.fsencode(output), ctypes.byref(params))
    except (ImportError, AttributeError) as exc:
        raise RuntimeError("llama-cpp-python avec llama_model_quantize est requis pour merged.") from exc
    if code != 0:
        raise RuntimeError(f"Quantification Q4_K_M échouée (code {code}).")


def main(argv=None):
    """Convertit explicitement à la demande ; --dry-run affiche les commandes sans poids ni conversion."""
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="route", required=True)
    for route in ("adapter", "merged"):
        command = sub.add_parser(route)
        command.add_argument("source", help="Dossier de l'adaptateur PEFT.")
        command.add_argument("--llama-cpp", default=os.environ.get("TEAMAI_LLAMA_CPP"))
        command.add_argument("--name", help="Nom d'un nouveau sous-dossier dans adapters/.")
        command.add_argument("--dry-run", action="store_true")
        command.add_argument("--base-config", help="Configuration HF locale de la base exacte, sans poids pour adapter.")
        command.add_argument("--output-dir", help="Nouveau dossier de sortie explicite (Kaggle).")
    args = parser.parse_args(argv)
    import yaml
    from volet_b.slm.train_lora import CONFIG
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))["base_model"]
    source = resolve_path(args.source)
    if not args.llama_cpp:
        parser.error("Fournir --llama-cpp ou TEAMAI_LLAMA_CPP (clone local de llama.cpp).")
    tools = resolve_path(args.llama_cpp)
    script = tools / ("convert_lora_to_gguf.py" if args.route == "adapter" else "convert_hf_to_gguf.py")
    if not script.is_file():
        parser.error(f"Convertisseur introuvable : {script}")
    if not (source / "adapter_config.json").is_file():
        parser.error(f"adapter_config.json introuvable dans {source}")
    try:
        adapter_cfg = json.loads((source / "adapter_config.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        parser.error(f"Configuration PEFT illisible : {exc}")
    if not isinstance(adapter_cfg, dict):
        parser.error("adapter_config.json doit contenir un objet JSON.")
    if adapter_cfg.get("peft_type") != "LORA" or adapter_cfg.get("base_model_name_or_path") != cfg["model_id"]:
        parser.error("Adaptateur LORA attendu pour le model_id configuré.")
    if adapter_cfg.get("revision") is not None and not adapter_cfg["revision"].startswith(cfg["revision"]):
        parser.error("La révision déclarée par l'adaptateur diffère du modèle de base configuré.")
    try:
        validate_lora_config(adapter_cfg)
    except ValueError as exc:
        parser.error(str(exc))
    name = args.name or f"{source.name}-{args.route}"
    output_dir = resolve_path(args.output_dir) if args.output_dir else resolve_path(SLM_ADAPTERS / name)
    if (not args.output_dir and output_dir.parent != SLM_ADAPTERS.resolve()) or output_dir.exists():
        parser.error("--name doit désigner un nouveau sous-dossier direct de adapters/.")
    output = output_dir / ("adapter.gguf" if args.route == "adapter" else "model-q4_k_m.gguf")
    if args.dry_run:
        base = str(resolve_path(args.base_config)) if args.base_config else "<snapshot HF local à la révision " + cfg["revision"] + ">"
        intermediate = output_dir / "temporaire" / "merged-hf"
        print(json.dumps({"command": conversion_command(
            args.route, tools, source if args.route == "adapter" else intermediate, base,
            output if args.route == "adapter" else output_dir / "temporaire" / "model-f16.gguf"),
            "merge_and_unload": args.route == "merged",
            "llama_cpp_commit": LLAMA_CPP_COMMIT,
            "quantization": "Q4_K_M" if args.route == "merged" else None}, indent=2))
        return
    try:
        commit = verify_converter_revision(tools)
        if args.base_config:
            base = resolve_path(args.base_config)
        else:
            from huggingface_hub import snapshot_download
            base = resolve_path(snapshot_download(cfg["model_id"], revision=cfg["revision"], local_files_only=True))
        base_config = json.loads((base / "config.json").read_text(encoding="utf-8"))
        provenance = json.loads((base / "teamai-base.json").read_text(encoding="utf-8"))
        if provenance.get("model_id") != cfg["model_id"] or not provenance.get("revision", "").startswith(cfg["revision"]):
            raise ValueError("--base : provenance différente de la base exacte")
        if hashlib.sha256((base / "config.json").read_bytes()).hexdigest() != provenance.get("config_sha256"):
            raise ValueError("Configuration de base modifiée")
        if base_config.get("model_type") not in ("gemma4", "gemma4_text"):
            raise ValueError("Configuration Gemma 4 attendue")
        digest = source_hash(source)
        output_dir.mkdir(parents=True, exist_ok=False)
        if args.route == "adapter":
            log = run_converter(conversion_command("adapter", tools, source, base, output))
            (output_dir / "conversion.log").write_text(log, encoding="utf-8")
            coverage = verify_tensor_coverage(source, output)
        else:
            with tempfile.TemporaryDirectory(dir=output_dir) as temporary:
                temporary = resolve_path(temporary)
                merged = temporary / "merged-hf"
                f16 = temporary / "model-f16.gguf"
                merge_adapter(source, base, merged)
                run_converter(conversion_command("merged", tools, merged, base, f16))
                quantize(f16, output)
        if not output.is_file() or not output.stat().st_size:
            raise RuntimeError("Le convertisseur n'a pas produit de GGUF non vide.")
        metadata = {"route": args.route, "source": str(source), "source_sha256": digest,
                    "source_hash_method": "sorted relative names, sizes and contents; SHA-256",
                    "base_model": cfg["model_id"], "base_revision": cfg["revision"],
                    "adapter_declared_revision": adapter_cfg.get("revision"),
                    "llama_cpp_commit": commit, "size_bytes": output.stat().st_size,
                    "quantization": "Q4_K_M" if args.route == "merged" else "adapter_f16",
                    "output": output.name, "inference_validated": False}
        metadata["tensor_coverage"] = coverage if args.route == "adapter" else None
        (output_dir / "meta.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
        print(output)
    except (ImportError, OSError, RuntimeError, TypeError, ValueError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"Conversion impossible : {exc}\nRepli : évaluation PEFT sur GPU ; aucune validation d'inférence revendiquée.\n")


if __name__ == "__main__":
    main()
