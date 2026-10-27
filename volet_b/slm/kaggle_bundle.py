"""Archive Kaggle minimale : preuves validées localement et autorisation C4 train seule."""
import hashlib
import json
import re
import zipfile
from pathlib import Path

from teamai.contracts import load_jsonl, validate_example
from teamai.paths import ROOT

SEED = "volet_b/annotations/seed_alain.jsonl"
MANIFEST = "volet_b/slm/train_allowlist.json"
SOURCE_SHA256 = "f504592cb7ac13b8b7e5d532a336b4e3641ec441a863c5efafd164faa2a43f22"
# Liste fermée : aucun parcours récursif de répertoire de données ou de sorties.
CODE_PATHS = (
    "teamai/__init__.py", "teamai/paths.py", "teamai/contracts.py",
    "teamai/data/__init__.py", "teamai/data/loader.py", "volet_b/__init__.py",
    "volet_b/slm/__init__.py", "volet_b/slm/kaggle_bundle.py",
    "volet_b/slm/kaggle_lora_essai.py", "volet_b/slm/lora_data.py",
    "volet_b/slm/train_lora.py", "volet_b/slm/first_inference.py",
    "volet_b/slm/generate.py", "volet_b/slm/convert_gguf.py",
    "volet_b/slm/configs/lora_essai.yaml", "pyproject.toml",
)
BUNDLE_PATHS = frozenset((*CODE_PATHS, SEED, MANIFEST))


def sha256(payload):
    """Renvoie l'empreinte SHA-256 des octets fournis."""
    return hashlib.sha256(payload).hexdigest()


def check_payloads(payloads):
    """Refuse chemins supplémentaires, corruption et identifiants étrangers à l'autorisation train."""
    if set(payloads) != BUNDLE_PATHS:
        raise ValueError("Archive Kaggle : liste blanche de chemins obligatoire, sans data/sample/")
    manifest = json.loads(payloads[MANIFEST])
    if (set(manifest) != {"source", "source_sha256", "blocks", "files_sha256"}
            or manifest["source"] != "data/splits/splits.csv"
            or manifest["source_sha256"] != SOURCE_SHA256):
        raise ValueError("Provenance C4 invalide")
    blocks = manifest["blocks"]
    if not isinstance(blocks, dict) or not blocks or any(
        not re.fullmatch(r"blk_-?\d+", bid) or split != "train" for bid, split in blocks.items()
    ):
        raise ValueError("Autorisation train obligatoire, aucun bloc non-train")
    hashes = manifest["files_sha256"]
    if set(hashes) != BUNDLE_PATHS - {MANIFEST} or any(
        sha256(payloads[name]) != digest for name, digest in hashes.items()
    ):
        raise ValueError("Empreinte de fichier incorrecte")
    examples = [json.loads(line) for line in payloads[SEED].decode("utf-8").splitlines() if line.strip()]
    ids = [ex["block_id"] for ex in examples]
    if len(set(ids)) != len(ids) or set(ids) != set(blocks):
        raise ValueError("Autorisation différente des blocs utilisés")
    for ex in examples:
        errors = validate_example(ex)
        if ex.get("reviewed_by") == "":
            errors = [e for e in errors if e != "reviewed_by : texte non vide attendu"]
        if errors or ex.get("split") != "train":
            raise ValueError("Exemple train C5 invalide")
    for payload in payloads.values():
        if set(re.findall(r"blk_-?\d+", payload.decode("utf-8"))) - set(blocks):
            raise ValueError("Identifiant hors autorisation train")
    return examples


def validate_bundle(root=ROOT):
    """Vérifie uniquement le contenu extrait de l'archive, sans lire de corpus local."""
    root = Path(root)
    if (root / "data/sample").exists():
        raise ValueError("data/sample/ interdit sur Kaggle")
    files = {}
    for path in root.rglob("*"):
        if "__pycache__" in path.parts:
            continue
        if path.is_symlink():
            raise ValueError("Lien symbolique interdit dans l'archive")
        if path.is_file():
            name = path.relative_to(root).as_posix()
            if name not in BUNDLE_PATHS:
                raise ValueError("Chemin hors liste blanche : " + name)
            files[name] = path.read_bytes()
    return check_payloads(files)


def build_bundle(output, root=ROOT):
    """Vérifie C4 et v16 localement puis écrit uniquement le code et les exemples train autorisés."""
    from volet_b.slm.lora_data import prepare_examples, read_splits

    root = Path(root)
    official = root / "data/splits/splits.csv"
    if official.is_file():
        source_hash = sha256(official.read_bytes())
        splits_path = official
    else:
        provenance = json.loads((root / "data/sample/splits_provenance.json").read_text(encoding="utf-8"))
        metadata = json.loads((root / "data/splits/splits_meta.json").read_text(encoding="utf-8"))
        source_hash = provenance["source_sha256"]
        if provenance["source"] != "data/splits/splits.csv" or source_hash != metadata["splits_csv_sha256"]:
            raise ValueError("Provenance du sous-ensemble C4 incohérente")
        splits_path = root / "data/sample/splits.csv"
    if source_hash != SOURCE_SHA256:
        raise ValueError("Empreinte C4 source inattendue")
    examples = load_jsonl(root / SEED)
    prepare_examples(examples, splits_path)
    splits = read_splits(splits_path)
    blocks = {ex["block_id"]: splits[ex["block_id"]] for ex in examples}
    payloads = {name: (root / name).read_bytes() for name in (*CODE_PATHS, SEED)}
    manifest = {"source": "data/splits/splits.csv", "source_sha256": source_hash,
                "blocks": blocks, "files_sha256": {name: sha256(data) for name, data in payloads.items()}}
    payloads[MANIFEST] = json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8")
    check_payloads(payloads)
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, payload in sorted(payloads.items()):
            archive.writestr(name, payload)
    return Path(output)
