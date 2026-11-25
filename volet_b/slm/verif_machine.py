"""SCRUM-61 étapes 1 et 5 : relevé de la machine et adaptateur GGUF appliqué au GGUF QAT q4_0, en une commande.

    python -m volet_b.slm.verif_machine --adapter chemin/adapter.gguf [--sha256 …] [--n-gpu-layers -1] [--offline]

Même protocole que la vérification sur T4 (eval/results/SCRUM-61/README.md) : prompt v16 de seed-0001
(bloc train), glouton, 400 tokens au plus, graine 42, trois lancements séparés (base, échelle 0, échelle 1).
Chaque lancement tourne dans son propre processus pour que la mémoire GPU mesurée soit la sienne.
Écrit eval/results/SCRUM-61/machine/<horodatage>/ : resultats.json, resultats.md et les trois textes générés.
"""
import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from importlib.metadata import PackageNotFoundError, version

from teamai.paths import ANNOTATIONS, RESULTS, resolve_path
from volet_b.slm.generate import load_config

SEED = ANNOTATIONS / "seed_alain.jsonl"
OUT = RESULTS / "SCRUM-61" / "machine"
PACKAGES = ("llama_cpp_python", "torch", "transformers", "peft", "huggingface_hub")
RUNS = (("base", None, 0.0), ("echelle_0", "adapter", 0.0), ("echelle_1", "adapter", 1.0))
MAX_TOKENS = 400


def gpu_query(fields: str) -> list[str]:
    """Une ligne par GPU NVIDIA, ou une liste vide si nvidia-smi est absent."""
    try:
        r = subprocess.run(["nvidia-smi", f"--query-gpu={fields}", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return []
    return [line.strip() for line in r.stdout.splitlines() if line.strip()] if r.returncode == 0 else []


def vram_used_mib() -> int | None:
    """Mémoire utilisée sur le premier GPU, en Mio."""
    lines = gpu_query("memory.used")
    return int(lines[0]) if lines else None


def environment() -> dict:
    """Étape 1 du ticket : système, Python, GPU et versions des paquets."""
    versions = {}
    for name in PACKAGES:
        try:
            versions[name] = version(name)
        except PackageNotFoundError:
            versions[name] = None
    return {"systeme": platform.platform(), "processeur": platform.processor(), "python": platform.python_version(),
            "gpu": gpu_query("name,memory.total,driver_version"), "paquets": versions}


def sha256(path) -> str:
    """Empreinte d'un fichier lu par morceaux."""
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def seed_prompt() -> tuple[str, str]:
    """Prompt v16 du premier exemple vérifié (bloc train), identique à la mesure sur T4."""
    example = json.loads(SEED.read_text(encoding="utf-8").splitlines()[0])
    if example.get("split") != "train":
        raise ValueError(f"{example['id']} n'est pas un bloc train.")
    return example["id"], example["prompt"]


def child(args) -> None:
    """Un lancement : charge le modèle (avec ou sans adaptateur), génère une fois, écrit ses mesures."""
    from huggingface_hub import hf_hub_download
    from llama_cpp import Llama

    cfg = load_config()
    model = hf_hub_download(cfg["gguf_repo"], cfg["gguf_file"], revision=cfg["gguf_revision"],
                            local_files_only=args.offline)
    _, prompt = seed_prompt()
    extra = {"lora_path": args.adapter, "lora_scale": args.scale} if args.adapter else {}
    before = vram_used_mib()
    t0 = time.perf_counter()
    llm = Llama(model_path=model, n_ctx=cfg["n_ctx"], n_gpu_layers=args.n_gpu_layers, seed=cfg["seed"],
                verbose=False, **extra)
    load = time.perf_counter() - t0
    t1 = time.perf_counter()
    r = llm.create_chat_completion(messages=[{"role": "user", "content": prompt}], max_tokens=MAX_TOKENS,
                                   temperature=0.0, seed=cfg["seed"])
    gen = time.perf_counter() - t1
    after = vram_used_mib()
    tokens = r["usage"]["completion_tokens"]
    result = {"chargement_s": round(load, 1), "generation_s": round(gen, 1), "tokens": tokens,
              "tokens_par_s": round(tokens / gen, 2) if gen else None, "vram_avant_mib": before,
              "vram_apres_mib": after, "vram_modele_mib": after - before if None not in (before, after) else None,
              "texte": r["choices"][0]["message"]["content"]}
    resolve_path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


def summarize(results: dict) -> dict:
    """Critère de fin : base = échelle 0 au caractère près, échelle 0 ≠ échelle 1."""
    texts = {name: value.get("texte") for name, value in results.items() if "texte" in value}
    if not {"base", "echelle_0", "echelle_1"} <= set(texts):
        return {"complet": False}
    return {"complet": True, "base_egale_echelle_0": texts["base"] == texts["echelle_0"],
            "echelle_0_differe_echelle_1": texts["echelle_0"] != texts["echelle_1"]}


def markdown(report: dict) -> str:
    """Tableau à coller dans le ticket ou dans le README de SCRUM-61."""
    env = report["environnement"]
    lines = [f"Relevé du {report['date']} : {env['systeme']}, Python {env['python']}, "
             f"GPU {', '.join(env['gpu']) or 'non détecté'}, n_gpu_layers = {report['n_gpu_layers']}.", "",
             "| Lancement | Chargement (s) | Génération (s) | Tokens | Débit (tokens/s) | Mémoire GPU du modèle (Mio) |",
             "|---|---:|---:|---:|---:|---:|"]
    for name, value in report["lancements"].items():
        if "erreur" in value:
            lines.append(f"| {name} | erreur : {value['erreur']} | | | | |")
        else:
            lines.append(f"| {name} | {value['chargement_s']} | {value['generation_s']} | {value['tokens']} | "
                         f"{value['tokens_par_s']} | {value['vram_modele_mib']} |")
    s = report["resume"]
    lines += ["", f"Paquets : {', '.join(f'{k} {v}' for k, v in env['paquets'].items())}.",
              f"Adaptateur : SHA-256 `{report['adaptateur_sha256']}`."]
    if s["complet"]:
        lines.append(f"Base identique à l'échelle 0 : {'oui' if s['base_egale_echelle_0'] else 'non'} ; "
                     f"échelle 1 différente de l'échelle 0 : {'oui' if s['echelle_0_differe_echelle_1'] else 'non'}.")
    return "\n".join(lines) + "\n"


def main(argv=None):
    """Relève l'environnement, lance les trois générations et enregistre le tout."""
    parser = argparse.ArgumentParser(description="Relevé machine et adaptateur GGUF (SCRUM-61).")
    parser.add_argument("--adapter", required=True, help="adapter.gguf exporté par SCRUM-39.")
    parser.add_argument("--sha256", help="Empreinte attendue de l'adaptateur ; arrêt si elle diffère.")
    parser.add_argument("--n-gpu-layers", type=int, default=-1, help="-1 = tout sur GPU ; réduire si mémoire insuffisante.")
    parser.add_argument("--offline", action="store_true", help="GGUF déjà en cache uniquement.")
    parser.add_argument("--child", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--scale", type=float, default=1.0, help=argparse.SUPPRESS)
    parser.add_argument("--out", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.child:
        args.adapter = args.adapter if args.adapter != "-" else None
        return child(args)

    adapter = resolve_path(args.adapter)
    if not adapter.is_file():
        raise SystemExit(f"Adaptateur introuvable : {adapter}")
    digest = sha256(adapter)
    if args.sha256 and digest != args.sha256.lower():
        raise SystemExit(f"SHA-256 de l'adaptateur différent : {digest}")
    example_id, _ = seed_prompt()
    stamp = time.strftime("%Y-%m-%d_%H%M%S")
    folder = OUT / stamp
    folder.mkdir(parents=True, exist_ok=False)
    report = {"date": stamp, "exemple": example_id, "n_gpu_layers": args.n_gpu_layers,
              "adaptateur": adapter.name, "adaptateur_sha256": digest, "environnement": environment(),
              "lancements": {}}
    for name, use_adapter, scale in RUNS:
        out = folder / f"{name}.json"
        cmd = [sys.executable, "-m", "volet_b.slm.verif_machine", "--child", "--out", str(out),
               "--adapter", str(adapter) if use_adapter else "-", "--scale", str(scale),
               "--n-gpu-layers", str(args.n_gpu_layers)] + (["--offline"] if args.offline else [])
        print(f"{name} …", flush=True)
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        (folder / f"{name}.log").write_text(r.stdout + r.stderr, encoding="utf-8")
        if r.returncode or not out.is_file():
            report["lancements"][name] = {"erreur": (r.stderr.strip().splitlines() or ["code " + str(r.returncode)])[-1]}
        else:
            report["lancements"][name] = json.loads(out.read_text(encoding="utf-8"))
        print(f"{name} : {({k: v for k, v in report['lancements'][name].items() if k != 'texte'})}", flush=True)
    report["resume"] = summarize(report["lancements"])
    (folder / "resultats.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (folder / "resultats.md").write_text(markdown(report), encoding="utf-8")
    print("\n" + markdown(report))
    print(f"Dossier : {folder}")


if __name__ == "__main__":
    main()
