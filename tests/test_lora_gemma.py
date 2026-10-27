"""SCRUM-29 : contrats Gemma/QLoRA, C4, v16 et conversion sans poids ni réseau."""
import json
import re
import subprocess
import sys
import zipfile
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
import yaml

from teamai.contracts import load_jsonl, validate_example
from teamai.paths import ROOT
from volet_b.slm import convert_gguf, kaggle_lora_essai
from volet_b.slm import kaggle_bundle
from volet_b.slm.lora_data import encode_example, prepare_examples, validate_lora_config, read_splits
from volet_b.slm.train_lora import CONFIG, prepare_qlora_text
from volet_b.slm.v16.runtime import build_prompt, schema, validate


def test_gemma_configuration():
    """L'entraînement choisit la base HF texte, la précision T4 et les deux cibles convertibles."""
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    assert cfg["base_model"] == {"model_id": "google/gemma-4-E4B-it-qat-q4_0-unquantized",
                                 "revision": "476025a01dbf99361c062bbeca3d6a76bb4c4566", "architecture": "Gemma4ForCausalLM", "dtype": "float16"}
    assert cfg["lora"]["r"] == 8 and cfg["lora"]["target_modules"] == ["q_proj", "v_proj"]
    assert cfg["training"]["batch_size"] == 1
    assert cfg["training"]["fp16"] and not cfg["training"]["bf16"]
    assert cfg["training"]["gradient_checkpointing"]
    validate_lora_config(cfg["lora"])


@pytest.mark.parametrize("target", ["all-linear", "per_layer_model_projection", "embed_tokens", "lm_head",
                                    "vision_tower.q_proj", "audio_tower.v_proj"])
def test_forbidden_targets(target):
    """Même une projection vision portant un nom autorisé ne peut entrer dans les cibles."""
    with pytest.raises(ValueError, match="interdites"):
        validate_lora_config({"target_modules": [target]})


@pytest.mark.parametrize("extra", [{"use_dora": True}, {"modules_to_save": ["lm_head"]}, {"bias": "all"}])
def test_forbidden_options(extra):
    """DoRA, poids complets et biais entraînables sont refusés avant chargement."""
    with pytest.raises(ValueError):
        validate_lora_config({"target_modules": ["q_proj"], **extra})


class CharacterTokenizer:
    """Double minimal : template avec thinking désactivé, BOS et fin de tour explicites."""

    end_of_turn = "<end>"
    trailing = "\n<user>tour suivant<end>"

    @property
    def all_special_tokens(self):
        """Expose le marqueur du template, sans imposer son nom au code testé."""
        return ["<bos>", "<user>", "<model>", self.end_of_turn]

    def apply_chat_template(self, messages, *, tokenize, enable_thinking, add_generation_prompt):
        """Vérifie les options et rend un préfixe identique en génération et entraînement."""
        assert tokenize is False and enable_thinking is False
        prefix = "<bos><user>" + messages[0]["content"] + "<end><model>"
        if add_generation_prompt:
            return prefix
        return prefix + messages[1]["content"] + self.end_of_turn + self.trailing

    def __call__(self, text, *, add_special_tokens):
        """Encode chaque caractère sans ajouter un second BOS."""
        assert add_special_tokens is False
        return {"input_ids": list(text.encode("utf-8"))}


@pytest.mark.parametrize("ending", ["<end>", "<turn|>", "<end_of_turn>"])
@pytest.mark.parametrize("trailing", ["", "\n", "\n<user>tour suivant<end>"])
def test_loss_on_json_and_end_of_turn(ending, trailing):
    """Le prompt est masqué ; JSON et fin de tour contribuent, sans la suite."""
    example = {"id": "fixture", "prompt": "consigne v16 et faits", "expected": {"réponse": []}}
    tokenizer = CharacterTokenizer()
    tokenizer.end_of_turn, tokenizer.trailing = ending, trailing
    encoded = encode_example(example, tokenizer, 1000)
    learned = bytes(i for i in encoded["labels"] if i != -100).decode("utf-8")
    assert learned == json.dumps(example["expected"], ensure_ascii=False) + ending
    prefix_len = len("<bos><user>consigne v16 et faits<end><model>".encode())
    learned_end = prefix_len + len(learned.encode("utf-8"))
    assert encoded["labels"][:prefix_len] == [-100] * prefix_len
    assert encoded["labels"][prefix_len:learned_end] == encoded["input_ids"][prefix_len:learned_end]
    assert encoded["labels"][learned_end:] == [-100] * len(trailing.encode("utf-8"))
    with pytest.raises(ValueError, match="max_tokens"):
        encode_example(example, tokenizer, 5)


@pytest.mark.parametrize("ending", ["", "inconnu", "\n<end>"])
def test_missing_end_of_turn_refused(ending, monkeypatch):
    """Une fin absente, non déclarée ou séparée du JSON échoue explicitement."""
    tokenizer = CharacterTokenizer()
    tokenizer.end_of_turn, tokenizer.trailing = ending, ""
    example = {"id": "fixture", "prompt": "consigne", "expected": {}}
    # Le template est modifié sans déclarer son nouveau marqueur au tokenizer.
    monkeypatch.setattr(CharacterTokenizer, "all_special_tokens", ["<bos>", "<user>", "<model>", "<end>"])
    with pytest.raises(ValueError, match="fin de tour introuvable"):
        encode_example(example, tokenizer, 1000)


def test_seed_v16_and_train_only():
    """Reconstruit les preuves, vérifie schéma, règles et exception de relecture explicite."""
    examples = load_jsonl(ROOT / "volet_b/annotations/seed_alain.jsonl")
    blocks = prepare_examples(examples)
    assert len(examples) == 20
    splits = read_splits()
    assert all(ex["split"] == splits[ex["block_id"]] == "train" for ex in examples)
    for example, block in zip(examples, blocks):
        assert example["reviewed_by"] == ""
        assert validate_example(example) == ["reviewed_by : texte non vide attendu"]
        assert example["prompt"] == build_prompt(block)
        assert validate(json.dumps(example["expected"], ensure_ascii=False), block) == ([], [], [])
        contract = schema(block)
        assert set(example["expected"]) == set(contract["required"])
        for key, value in example["expected"].items():
            spec = contract["properties"][key]
            if isinstance(value, list):
                assert spec.get("minItems", 0) <= len(value) <= spec.get("maxItems", 1000)
                for item in value:
                    assert "enum" not in spec["items"] or item in spec["items"]["enum"]
            elif isinstance(value, str):
                assert spec.get("minLength", 0) <= len(value) <= spec.get("maxLength", 10000)
    assert sum("E27" in ex["events"] for ex in examples) >= 1
    assert sum("E28" in ex["events"] for ex in examples) >= 1


@pytest.mark.parametrize("split", ["val", "test"])
def test_non_train_refused_even_if_annotation_claims_train(tmp_path, split):
    """C4 prévaut sur la déclaration de l'annotation et bloque avant la lecture des logs."""
    examples = load_jsonl(ROOT / "volet_b/annotations/seed_alain.jsonl")[:1]
    manifest = tmp_path / "splits.csv"
    manifest.write_text("BlockId,split\n" + examples[0]["block_id"] + "," + split + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="train obligatoire"):
        prepare_examples(examples, manifest)


def test_kaggle_dry_run_no_side_effects(monkeypatch, tmp_path):
    """Le plan reste inspectable sans torch, installation, réseau ou création de sorties."""
    monkeypatch.setattr(kaggle_lora_essai.subprocess, "run", MagicMock(side_effect=AssertionError("process")))
    monkeypatch.setattr(kaggle_lora_essai.urllib.request, "urlretrieve", MagicMock(side_effect=AssertionError("network")))
    result = kaggle_lora_essai.main(["--dry-run", "--working", str(tmp_path / "absent")])
    assert result["llama_cpp_commit"] == convert_gguf.LLAMA_CPP_COMMIT == "0c1e57098"
    assert result["steps"] == 30
    assert result["revision"] == "476025a01dbf99361c062bbeca3d6a76bb4c4566"
    assert not (tmp_path / "absent").exists()


def test_kaggle_bundle_train_only(tmp_path):
    """Inspecte le ZIP réel : chemins fermés, aucun log brut ni identifiant val/test."""
    output = tmp_path / "train.zip"
    kaggle_lora_essai.main(["--bundle", str(output)])
    expected = {
        "teamai/__init__.py", "teamai/paths.py", "teamai/contracts.py",
        "teamai/data/__init__.py", "teamai/data/loader.py", "volet_b/__init__.py",
        "volet_b/slm/__init__.py", "volet_b/slm/kaggle_bundle.py",
        "volet_b/slm/kaggle_lora_essai.py", "volet_b/slm/lora_data.py",
        "volet_b/slm/train_lora.py", "volet_b/slm/first_inference.py",
        "volet_b/slm/generate.py", "volet_b/slm/convert_gguf.py",
        "volet_b/slm/configs/lora_essai.yaml", "pyproject.toml",
        "volet_b/annotations/seed_alain.jsonl", "volet_b/slm/train_allowlist.json",
    }
    with zipfile.ZipFile(output) as archive:
        assert set(archive.namelist()) == expected
        assert len(archive.namelist()) == len(expected)
        payloads = {name: archive.read(name) for name in archive.namelist()}
        extracted = tmp_path / "extracted"
        archive.extractall(extracted)
    assert not any(name.startswith("data/") or name.endswith((".log", ".csv")) for name in payloads)
    splits = read_splits()
    forbidden = {bid for bid, split in splits.items() if split != "train"}
    all_ids = set(re.findall(r"blk_-?\d+", b"\n".join(payloads.values()).decode("utf-8")))
    examples = load_jsonl(ROOT / kaggle_bundle.SEED)
    assert all_ids == {ex["block_id"] for ex in examples}
    assert not all_ids & forbidden
    manifest = json.loads(payloads[kaggle_bundle.MANIFEST])
    assert manifest["source"] == "data/splits/splits.csv"
    assert manifest["source_sha256"] == "f504592cb7ac13b8b7e5d532a336b4e3641ec441a863c5efafd164faa2a43f22"
    assert set(manifest["blocks"].values()) == {"train"}
    assert kaggle_bundle.validate_bundle(extracted) == examples
    # Un processus indépendant prouve l'absence de dépendance envers le checkout et le sample.
    subprocess.run([sys.executable, "-c",
                    "from teamai.paths import ROOT; "
                    "from teamai.contracts import load_jsonl; "
                    "from volet_b.slm.train_lora import CONFIG; "
                    "from volet_b.slm.lora_data import prepare_examples; "
                    "prepare_examples(load_jsonl(ROOT / 'volet_b/annotations/seed_alain.jsonl'))"],
                   cwd=extracted, check=True)


@pytest.mark.parametrize("split", ["val", "test"])
def test_kaggle_rejects_non_train_allowlist(tmp_path, monkeypatch, split):
    """Une autorisation non-train bloque même --install avant tout appel externe."""
    output = tmp_path / "train.zip"
    kaggle_bundle.build_bundle(output)
    root = tmp_path / "bundle"
    with zipfile.ZipFile(output) as archive:
        archive.extractall(root)
    manifest_path = root / kaggle_bundle.MANIFEST
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["blocks"][next(iter(manifest["blocks"]))] = split
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(kaggle_lora_essai, "ROOT", root)
    monkeypatch.setattr(kaggle_lora_essai.subprocess, "run", MagicMock(side_effect=AssertionError("process")))
    with pytest.raises(ValueError, match="train"):
        kaggle_lora_essai.main(["--install"])


@pytest.mark.parametrize("extra", ["data/sample", "unexpected.log"])
def test_kaggle_rejects_extra_content(tmp_path, monkeypatch, extra):
    """Un sample, même vide, ou un log supplémentaire bloque le lancement."""
    output = tmp_path / "train.zip"
    kaggle_bundle.build_bundle(output)
    root = tmp_path / "bundle"
    with zipfile.ZipFile(output) as archive:
        archive.extractall(root)
    path = root / extra
    if extra == "data/sample":
        path.mkdir(parents=True)
    else:
        path.write_text("raw log", encoding="utf-8")
    monkeypatch.setattr(kaggle_lora_essai, "ROOT", root)
    with pytest.raises(ValueError):
        kaggle_lora_essai.main(["--dry-run"])


def test_kaggle_bundle_refuses_changed_seed(tmp_path):
    """Une modification des annotations invalide leur empreinte avant entraînement."""
    output = tmp_path / "train.zip"
    kaggle_bundle.build_bundle(output)
    with zipfile.ZipFile(output) as archive:
        payloads = {name: archive.read(name) for name in archive.namelist()}
    payloads[kaggle_bundle.SEED] += b"\n"
    with pytest.raises(ValueError, match="Empreinte"):
        kaggle_bundle.check_payloads(payloads)


def test_quantized_embeddings_never_promoted():
    """La préparation gèle les embeddings FP16 sans créer une copie FP32 de 13 Gio."""
    embedding, norm = MagicMock(), MagicMock()
    norm_data = norm.data
    model = SimpleNamespace(named_parameters=lambda: [("model.embed_tokens.weight", embedding), ("model.norm.weight", norm)])
    prepare_qlora_text(model, SimpleNamespace(float32="fp32"))
    embedding.requires_grad_.assert_called_once_with(False)
    embedding.data.to.assert_not_called()
    norm_data.to.assert_called_once_with(dtype="fp32")


def test_conversion_fails_when_target_disappears(monkeypatch, tmp_path):
    """Une paire absente du GGUF déclenche une erreur même si le convertisseur a réussi."""
    reader = MagicMock()
    reader.__enter__.return_value.keys.return_value = [
        "base_model.model.model.layers.0.self_attn.q_proj.lora_A.weight",
        "base_model.model.model.layers.0.self_attn.q_proj.lora_B.weight"]
    monkeypatch.setitem(sys.modules, "safetensors", SimpleNamespace(safe_open=lambda *a, **k: reader))
    names = [SimpleNamespace(name="blk.0.attn_q.weight.lora_a")]
    monkeypatch.setitem(sys.modules, "gguf", SimpleNamespace(GGUFReader=lambda path: SimpleNamespace(tensors=names)))
    with pytest.raises(ValueError, match="ignorées"):
        convert_gguf.verify_tensor_coverage(tmp_path, tmp_path / "out.gguf")
    names.append(SimpleNamespace(name="blk.0.attn_q.weight.lora_b"))
    assert len(convert_gguf.verify_tensor_coverage(tmp_path, tmp_path / "out.gguf")) == 2


def test_converter_commit_refused(tmp_path):
    """Un checkout d'une autre révision échoue sans appeler Git."""
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git/HEAD").write_text("deadbeef", encoding="ascii")
    with pytest.raises(ValueError, match="épinglé"):
        convert_gguf.verify_converter_revision(tmp_path)
