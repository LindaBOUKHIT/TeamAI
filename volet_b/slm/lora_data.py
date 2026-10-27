"""Données LoRA v16 : provenance C4, preuves reconstruites et perte sur le JSON seul."""
import csv
import json
import re
from pathlib import Path

from teamai.contracts import validate_example
from teamai.paths import ROOT, SAMPLE, SPLITS

SAMPLE_SPLITS = SAMPLE / "splits.csv"
SAFE_TARGETS = {"q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"}


def validate_lora_config(config):
    """Refuse toute cible ou option sans conversion LoRA sûre dans llama.cpp."""
    targets = config.get("target_modules")
    if not isinstance(targets, (list, set)) or not targets or set(targets) - SAFE_TARGETS:
        raise ValueError("Cibles LoRA interdites ; projections texte explicites uniquement")
    if config.get("use_dora") or config.get("modules_to_save") or config.get("bias", "none") != "none":
        raise ValueError("DoRA, modules_to_save et bias entraînable interdits")


def read_splits(path=None):
    """Lit C4 sans inventer de split ; le manifeste sample est un sous-ensemble du CSV officiel."""
    path = Path(path) if path else (SPLITS / "splits.csv" if (SPLITS / "splits.csv").is_file() else SAMPLE_SPLITS)
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    result = {row["BlockId"]: row["split"] for row in rows}
    if len(result) != len(rows) or set(result.values()) - {"train", "val", "test"}:
        raise ValueError("Manifeste C4 invalide")
    return result


def schema_errors(answer, block):
    """Applique les types, bornes et énumérations du schéma v16 fermé, sans dépendance GPU."""
    from volet_b.slm.v16.runtime import schema

    contract = schema(block)
    errors = []
    if not isinstance(answer, dict) or set(answer) != set(contract["required"]):
        return ["six clés v16 exactes requises"]
    for key, spec in contract["properties"].items():
        value = answer[key]
        if spec["type"] == "boolean":
            if not isinstance(value, bool):
                errors.append(key + " : booléen requis")
        elif spec["type"] == "string":
            if not isinstance(value, str) or not spec.get("minLength", 0) <= len(value) <= spec.get("maxLength", float("inf")):
                errors.append(key + " : longueur/type invalide")
        else:
            if not isinstance(value, list) or not spec.get("minItems", 0) <= len(value) <= spec.get("maxItems", float("inf")):
                errors.append(key + " : cardinalité/type invalide")
                continue
            item = spec["items"]
            for text in value:
                if not isinstance(text, str) or not item.get("minLength", 0) <= len(text) <= item.get("maxLength", float("inf")):
                    errors.append(key + " : élément invalide")
                elif "enum" in item and text not in item["enum"]:
                    errors.append(key + " : valeur hors énumération")
    return errors


def prepare_examples(examples, splits_path=None):
    """Vérifie l'archive Kaggle ou reconstruit localement chaque prompt depuis le sample.

    En mode archive, ne lit que les exemples et leur autorisation C4 train.
    Seule l'absence volontaire de relecture est tolérée pour ces brouillons ;
    le contrat C5 des annotations relues conserve sa règle habituelle.
    """
    from volet_b.slm.kaggle_bundle import MANIFEST, validate_bundle

    if (ROOT / MANIFEST).exists() or str(ROOT).startswith("/kaggle/"):
        bundled = validate_bundle(ROOT)
        if examples != bundled:
            raise ValueError("Exemples différents de l'archive autorisée")
        return []  # Les preuves v16 ont été reconstruites localement avant empaquetage.
    from data.parse_hdfs import compile_templates
    from volet_b.slm.v16.facts import prepare_block
    from volet_b.slm.v16.runtime import build_prompt, validate

    if not examples:
        raise ValueError("Aucun exemple train")
    splits = read_splits(splits_path)
    wanted = {ex["block_id"] for ex in examples}
    if len(wanted) != len(examples):
        raise ValueError("Blocs dupliqués")
    for ex in examples:
        if ex.get("split") != "train" or splits.get(ex["block_id"]) != "train":
            raise ValueError(f"{ex['block_id']} : split train obligatoire (C4)")
        errors = validate_example(ex)
        if ex.get("reviewed_by") == "":
            errors = [e for e in errors if e != "reviewed_by : texte non vide attendu"]
        if errors:
            raise ValueError(str(errors))
    lines = {bid: [] for bid in wanted}
    with (SAMPLE / "HDFS_sample.log").open(encoding="utf-8") as stream:
        for number, raw in enumerate(stream, 1):
            for bid in set(re.findall(r"blk_-?\d+", raw)) & wanted:
                lines[bid].append((number, raw.rstrip("\r\n")))
    templates = compile_templates(SAMPLE / "HDFS.log_templates.csv")
    blocks = []
    for ex in examples:
        block = prepare_block(ex["block_id"], lines[ex["block_id"]], templates, split="train")
        if ex["trace_lines"] != [raw for _, raw in lines[ex["block_id"]]] or ex["events"] != [e["event"] for e in block["raw_events"]]:
            raise ValueError("Trace ou codes différents du sample")
        if ex.get("prompt") != build_prompt(block):
            raise ValueError("Prompt différent de v16")
        checks = (schema_errors(ex["expected"], block), *validate(json.dumps(ex["expected"], ensure_ascii=False), block))
        if any(checks):
            raise ValueError(f"{ex['id']} : contrôles v16 {checks}")
        blocks.append(block)
    return blocks


def encode_example(example, tokenizer, max_tokens):
    """Rend le dialogue Gemma sans thinking et masque tout sauf les tokens du JSON.

    Les fins de tour restent dans l'entrée, avec une perte masquée. Les frontières
    tokenisées doivent être identiques ; aucune troncature silencieuse n'est admise.
    """
    messages = [{"role": "user", "content": example["prompt"]}]
    answer = json.dumps(example["expected"], ensure_ascii=False)
    options = {"tokenize": False, "enable_thinking": False}
    prompt = tokenizer.apply_chat_template(messages, add_generation_prompt=True, **options)
    full = tokenizer.apply_chat_template(messages + [{"role": "assistant", "content": answer}],
                                         add_generation_prompt=False, **options)
    if not full.startswith(prompt + answer):
        raise ValueError("Template Gemma : préfixe assistant incompatible")
    prompt_ids = tokenizer(prompt, add_special_tokens=False)["input_ids"]
    through_answer = tokenizer(prompt + answer, add_special_tokens=False)["input_ids"]
    ids = tokenizer(full, add_special_tokens=False)["input_ids"]
    if through_answer[:len(prompt_ids)] != prompt_ids or ids[:len(through_answer)] != through_answer:
        raise ValueError("Frontière JSON incompatible avec la tokenisation")
    if len(ids) > max_tokens:
        raise ValueError(f"{example['id']} : {len(ids)} tokens > max_tokens {max_tokens}")
    labels = [-100] * len(ids)
    labels[len(prompt_ids):len(through_answer)] = ids[len(prompt_ids):len(through_answer)]
    return {"input_ids": ids, "attention_mask": [1] * len(ids), "labels": labels}
