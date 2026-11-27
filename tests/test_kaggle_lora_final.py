"""SCRUM-39 : configurations d'essai et règle de sélection sur val, sans GPU."""
import yaml

from volet_b.slm.kaggle_lora_final import CONFIG, merge, select, trial_configs
from volet_b.slm.lora_data import validate_lora_config


def test_essais_complets_et_surs(tmp_path):
    """Chaque essai hérite du socle, cible des projections sûres et écrit dans working."""
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    trials = trial_configs(cfg, tmp_path)
    assert list(trials) == ["r8_qv", "r16_qkvo"]
    for name, trial in trials.items():
        validate_lora_config(trial["lora"])
        assert trial["data"] == "volet_b/annotations/train.jsonl"
        assert "val" not in trial and "essais" not in trial
        assert trial["adapter_dir"].endswith(name) and trial["run_name"] == f"lora_{name}"
    assert trials["r16_qkvo"]["lora"]["r"] == 16 and trials["r16_qkvo"]["lora"]["dropout"] == 0.05
    assert trials["r16_qkvo"]["training"]["learning_rate"] == 1.0e-4
    assert trials["r8_qv"]["training"]["steps"] == 400


def test_merge_ne_modifie_pas_le_socle():
    """La fusion récursive renvoie une copie."""
    base = {"a": {"x": 1, "y": 2}}
    assert merge(base, {"a": {"y": 3}}) == {"a": {"x": 1, "y": 3}}
    assert base == {"a": {"x": 1, "y": 2}}


def test_selection_ordre_des_criteres():
    """Contrat valide, puis hypothèses, puis erreurs d'appui, puis ordre déclaré."""
    metrics = {
        "r8_qv": {"accepted": 30, "hypotheses_per_block_with_incident": 0.2, "unknown_references": 0, "unsupported_network": 0},
        "r16_qkvo": {"accepted": 31, "hypotheses_per_block_with_incident": 0.1, "unknown_references": 2, "unsupported_network": 1},
    }
    assert select(metrics)["selected"] == "r16_qkvo"
    metrics["r8_qv"]["accepted"] = 31
    assert select(metrics)["selected"] == "r8_qv"
    metrics["r8_qv"]["hypotheses_per_block_with_incident"] = 0.1
    assert select(metrics)["selected"] == "r8_qv"  # moins d'erreurs d'appui
    metrics["r16_qkvo"].update(unknown_references=0, unsupported_network=0)
    assert select(metrics)["selected"] == "r8_qv"  # égalité complète : premier essai déclaré
