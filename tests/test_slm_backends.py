"""SCRUM-57 : backends, conversion et artefacts C7, sans poids ni conversion réelle."""
import contextlib
import json
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from teamai.contracts import validate_answer
from volet_b.slm import bench_gguf as bench
from volet_b.slm import compare_backends as compare
from volet_b.slm import convert_gguf as convert
from volet_b.slm import generate as slm


@pytest.fixture(autouse=True)
def isolated_models(monkeypatch):
    """Empêche toute réutilisation de cache et neutralise le mode factice extérieur au test."""
    monkeypatch.delenv("TEAMAI_SLM_MOCK", raising=False)
    slm.clear_model_cache()
    yield
    slm.clear_model_cache()


@pytest.mark.parametrize("backend", ["transformers", "llamacpp"])
def test_mock_both_backends(monkeypatch, backend):
    """Les deux backends rendent la même interface factice sans charger de modèle."""
    monkeypatch.setenv("TEAMAI_SLM_MOCK", "1")
    loader = MagicMock(side_effect=AssertionError("Chargement interdit"))
    monkeypatch.setattr(slm, "load_backend", loader)
    result = slm.generate("logs", backend=backend)
    assert set(result) == {"text", "new_tokens", "seconds"}
    assert validate_answer(json.loads(result["text"])) == []
    loader.assert_not_called()


def test_llamacpp_config_cache_adapter_and_greedy(monkeypatch, tmp_path):
    """La config choisit llama.cpp, épingle le snapshot et passe l'adaptateur en lora_path."""
    cfg = {**slm.load_config(), "backend": "llamacpp", "local_files_only": True}
    monkeypatch.setattr(slm, "load_config", lambda: cfg)
    adapter = tmp_path / "adapter.gguf"
    adapter.write_bytes(b"fake")
    download = MagicMock(return_value="cached.gguf")
    llama = MagicMock()
    llama.return_value.create_chat_completion.return_value = {
        "choices": [{"message": {"content": "réponse"}}], "usage": {"completion_tokens": 3}}
    monkeypatch.setitem(sys.modules, "huggingface_hub", SimpleNamespace(hf_hub_download=download))
    monkeypatch.setitem(sys.modules, "llama_cpp", SimpleNamespace(Llama=llama))
    for _ in range(2):
        result = slm.generate("logs", adapter=str(adapter))
        assert set(result) == {"text", "new_tokens", "seconds"}
        assert result["text"] == "réponse" and result["new_tokens"] == 3
        assert isinstance(result["seconds"], float)
    assert llama.call_count == 1
    assert llama.call_args.kwargs["lora_path"] == str(adapter.resolve())
    assert llama.call_args.kwargs["last_n_tokens_size"] == cfg["n_ctx"]
    download.assert_called_once_with(cfg["gguf_repo"], cfg["gguf_file"],
                                     revision=cfg["gguf_revision"], local_files_only=True)
    assert llama.return_value.create_chat_completion.call_args.kwargs["temperature"] == 0.0


@pytest.mark.parametrize("loader", [slm.load_backend, bench.load_llamacpp])
@pytest.mark.parametrize("n_gpu_layers", [None, 0, -1, 8])
def test_llamacpp_gpu_layers_config(monkeypatch, loader, n_gpu_layers):
    """Les deux chargeurs transmettent les couches GPU et gardent le défaut CPU sans poids."""
    cfg = {**slm.load_config(), "backend": "llamacpp"}
    cfg.pop("n_gpu_layers", None)
    if n_gpu_layers is not None:
        cfg["n_gpu_layers"] = n_gpu_layers
    download = MagicMock(return_value="cached.gguf")
    llama = MagicMock()
    monkeypatch.setitem(sys.modules, "huggingface_hub", SimpleNamespace(hf_hub_download=download))
    monkeypatch.setitem(sys.modules, "llama_cpp", SimpleNamespace(Llama=llama))

    assert loader(cfg) is llama.return_value

    llama.assert_called_once()
    assert llama.call_args.kwargs["n_gpu_layers"] == (0 if n_gpu_layers is None else n_gpu_layers)
    download.assert_called_once()


def test_llamacpp_gpu_layers_cache(monkeypatch):
    """Une modification des couches GPU recharge l'instance ; une config identique la réutilise."""
    cfg = {**slm.load_config(), "backend": "llamacpp", "n_gpu_layers": 0}
    download = MagicMock(return_value="cached.gguf")
    llama = MagicMock(side_effect=[object(), object()])
    monkeypatch.setitem(sys.modules, "huggingface_hub", SimpleNamespace(hf_hub_download=download))
    monkeypatch.setitem(sys.modules, "llama_cpp", SimpleNamespace(Llama=llama))

    cpu = slm.load_backend(cfg)
    assert slm.load_backend(cfg) is cpu
    gpu_cfg = {**cfg, "n_gpu_layers": -1}
    gpu = slm.load_backend(gpu_cfg)
    assert gpu is not cpu
    assert slm.load_backend(gpu_cfg) is gpu
    assert [call.kwargs["n_gpu_layers"] for call in llama.call_args_list] == [0, -1]
    assert download.call_count == 2


def test_transformers_loading_and_interface(monkeypatch):
    """Transformers reste le défaut ; ses chargeurs sont remplacés et son retour reste identique."""
    cfg = {**slm.load_config(), "backend": "transformers"}
    monkeypatch.setattr(slm, "load_config", lambda: cfg)
    torch = SimpleNamespace(float32="float32", manual_seed=MagicMock(),
                            inference_mode=contextlib.nullcontext)
    tokenizer = MagicMock()
    tokenizer.apply_chat_template.return_value = {"input_ids": SimpleNamespace(shape=(1, 4))}
    tokenizer.decode.return_value = "réponse"
    model = MagicMock()
    model.generate.return_value.__getitem__.return_value.shape = (3,)
    auto_model = SimpleNamespace(from_pretrained=MagicMock(return_value=model))
    auto_tokenizer = SimpleNamespace(from_pretrained=MagicMock(return_value=tokenizer))
    monkeypatch.setitem(sys.modules, "torch", torch)
    monkeypatch.setitem(sys.modules, "transformers", SimpleNamespace(
        AutoModelForCausalLM=auto_model, AutoTokenizer=auto_tokenizer))
    result = slm.generate("logs", local_files_only=True)
    assert set(result) == {"text", "new_tokens", "seconds"}
    assert result["text"] == "réponse" and result["new_tokens"] == 3
    auto_model.from_pretrained.assert_called_once_with(cfg["model_id"], dtype="float32",
                                                       revision=cfg["revision"], local_files_only=True)
    assert model.generate.call_args.kwargs["do_sample"] is False


def test_backend_override_and_invalid_backend(monkeypatch):
    """L'override sélectionne explicitement le backend et une valeur inconnue est rejetée."""
    loader = MagicMock(return_value="instance")
    monkeypatch.setattr(slm, "_load_llamacpp", loader)
    assert slm.load_backend({**slm.load_config(), "backend": "llamacpp"}) == "instance"
    with pytest.raises(ValueError, match="Backend inconnu"):
        slm.generate("logs", backend="absent")


@pytest.mark.parametrize("route,script", [("adapter", "convert_lora_to_gguf.py"),
                                         ("merged", "convert_hf_to_gguf.py")])
def test_conversion_commands_only(tmp_path, route, script):
    """Les commandes gardent les chemins avec espaces et imposent f16 sans lancer d'outil."""
    source, base, output = [tmp_path / name for name in ("source peft", "base hf", "sortie.gguf")]
    command = convert.conversion_command(route, tmp_path, source, base, output)
    assert command[:3] == [sys.executable, str(tmp_path / script), str(source)]
    assert command[3:7] == ["--outfile", str(output), "--outtype", "f16"]
    assert command[7:] == (["--base", str(base)] if route == "adapter" else [])


def test_dry_run_never_converts(monkeypatch, tmp_path, capsys):
    """--dry-run ne charge ni poids ni snapshot et ne crée pas de sortie."""
    (tmp_path / "convert_lora_to_gguf.py").write_text("", encoding="utf-8")
    source = tmp_path / "source"
    source.mkdir()
    (source / "adapter_config.json").write_text(json.dumps({
        "peft_type": "LORA", "base_model_name_or_path": slm.load_config()["model_id"]}), encoding="utf-8")
    output_root = tmp_path / "adapters"
    monkeypatch.setattr(convert, "SLM_ADAPTERS", output_root)
    monkeypatch.setattr(convert, "run_converter", MagicMock(side_effect=AssertionError("Conversion")))
    convert.main(["adapter", str(source), "--llama-cpp", str(tmp_path), "--dry-run"])
    assert "convert_lora_to_gguf.py" in capsys.readouterr().out
    assert not output_root.exists()


def test_quantization_api_without_conversion(monkeypatch, tmp_path):
    """Le paramètre Q4_K_M et les chemins encodés sont transmis à l'API C simulée."""
    import ctypes

    class Params(ctypes.Structure):
        """Structure minimale remplaçant les paramètres C sans charger llama.cpp."""
        _fields_ = [("ftype", ctypes.c_int)]

    params = Params()
    quantize = MagicMock(return_value=0)
    monkeypatch.setitem(sys.modules, "llama_cpp", SimpleNamespace(
        llama_model_quantize_default_params=lambda: params, LLAMA_FTYPE_MOSTLY_Q4_K_M=15,
        llama_model_quantize=quantize))
    convert.quantize(tmp_path / "f16.gguf", tmp_path / "q4.gguf")
    assert params.ftype == 15
    assert quantize.call_count == 1


def test_merge_sequence_without_weights(monkeypatch, tmp_path):
    """La fusion appelle merge_and_unload et sauvegarde le modèle/tokenizer HF sans vrai poids."""
    base_model, adapted, merged, tokenizer = [MagicMock() for _ in range(4)]
    adapted.merge_and_unload.return_value = merged
    auto_model = SimpleNamespace(from_pretrained=MagicMock(return_value=base_model))
    auto_tokenizer = SimpleNamespace(from_pretrained=MagicMock(return_value=tokenizer))
    peft = SimpleNamespace(from_pretrained=MagicMock(return_value=adapted))
    monkeypatch.setitem(sys.modules, "torch", SimpleNamespace(float32="float32"))
    monkeypatch.setitem(sys.modules, "transformers", SimpleNamespace(
        AutoModelForCausalLM=auto_model, AutoTokenizer=auto_tokenizer))
    monkeypatch.setitem(sys.modules, "peft", SimpleNamespace(PeftModel=peft))
    source, base, destination = [tmp_path / name for name in ("adapter", "base", "merged")]
    convert.merge_adapter(source, base, destination)
    peft.from_pretrained.assert_called_once_with(base_model, str(source), local_files_only=True)
    adapted.merge_and_unload.assert_called_once_with()
    merged.save_pretrained.assert_called_once_with(str(destination), safe_serialization=True)
    tokenizer.save_pretrained.assert_called_once_with(str(destination))


def test_test_split_rejected_before_loading(monkeypatch):
    """Le split test est refusé aux trois entrées, avant tout accès au modèle."""
    monkeypatch.setattr(compare, "load_backend", MagicMock(side_effect=AssertionError("Modèle")))
    with pytest.raises(ValueError, match="test"):
        compare.select_blocks(5, split="test")
    with pytest.raises(SystemExit):
        compare.main(["--split", "test"])
    with pytest.raises(ValueError, match="test"):
        compare.measure_backend({"blocks": [{"split": "test"}]}, "llamacpp")


def test_selection_uses_only_validation_and_no_labels(tmp_path):
    """Le tirage exclut test/train et construit une consigne avant les lignes sans label."""
    (tmp_path / "splits.csv").write_text("BlockId,split,unseen_seq\nblk_1,val,False\nblk_2,test,True\n", encoding="utf-8")
    (tmp_path / "Event_traces.csv").write_text("BlockId,Label\nblk_1,SECRET_LABEL\nblk_2,Fail\n", encoding="utf-8")
    (tmp_path / "HDFS_sample.log").write_text("ligne blk_1\nligne blk_2\n", encoding="utf-8")
    selected = compare.select_blocks(1, sample=tmp_path, splits=tmp_path)
    assert selected[0]["block_id"] == "blk_1"
    assert "SECRET_LABEL" not in json.dumps(selected)
    assert selected[0]["messages"][0]["content"].startswith("Analyse les logs")
    with pytest.raises(ValueError, match="Seulement"):
        compare.select_blocks(2, sample=tmp_path, splits=tmp_path)


def test_comparison_creates_fresh_c7(monkeypatch, tmp_path):
    """Deux lancements créent chacun les quatre fichiers C7 sans écraser le premier."""
    blocks = [{"block_id": "blk_1", "split": "val", "messages": [{"role": "user", "content": "logs"}]}]
    monkeypatch.setattr(compare, "select_blocks", lambda *args: blocks)
    monkeypatch.setattr(compare, "sha256_file", lambda path: "hash")
    real_new = compare.new_run_directory
    monkeypatch.setattr(compare, "new_run_directory", lambda name: real_new(tmp_path, name))

    def fake_process(command, **kwargs):
        """Simule git et le worker ; aucun sous-processus ni modèle n'est lancé."""
        if command[0] == "git":
            return SimpleNamespace(stdout="commit")
        run = compare.resolve_path(command[command.index("--worker") + 1])
        backend = command[-1]
        prediction = {"id": "blk_1", "backend": backend, "raw_text": "réponse"}
        metrics = {"n": 1, "conformity": 0, "abstention": 0, "mean_tokens_per_second": 2,
                   "peak_rss_bytes": 123, "load_seconds": 1}
        compare.write_json(run / f"{backend}.json", {"predictions": [prediction], "metrics": metrics})
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(compare.subprocess, "run", fake_process)
    for _ in range(2):
        compare.main(["--n", "1", "--backends", "llamacpp"])
    runs = list(tmp_path.iterdir())
    assert len(runs) == 2
    for run in runs:
        assert all((run / name).is_file() for name in
                   ("config.json", "predictions.jsonl", "metrics.json", "comparison.md"))


def test_measurement_preserves_invalid_outputs(monkeypatch):
    """Une sortie invalide et une erreur restent dans les métriques avec des mesures nulles."""
    monkeypatch.setattr(compare, "load_backend", MagicMock())
    monkeypatch.setattr(compare, "generate", MagicMock(side_effect=[
        {"text": "pas JSON", "new_tokens": 4, "seconds": 2.0}, RuntimeError("échec")]))
    config = {"generation": slm.load_config(), "adapters": {"llamacpp": None}, "blocks": [
        {"block_id": f"blk_{i}", "split": "val", "messages": []} for i in (1, 2)]}
    predictions, metrics = compare.measure_backend(config, "llamacpp")
    assert metrics["n"] == metrics["failures"] == 2
    assert metrics["conformity"] == 0
    assert predictions[0]["parsed_response"] is None
    assert predictions[1]["seconds"] is None
    assert metrics["mean_tokens_per_second"] == 2


def test_measurement_refuses_non_strict_json(monkeypatch):
    """NaN n'entre jamais dans les artefacts JSON stricts même si le modèle l'émet."""
    monkeypatch.setattr(compare, "load_backend", MagicMock())
    monkeypatch.setattr(compare, "generate", MagicMock(return_value={
        "text": '{"resume_evenements": NaN}', "new_tokens": 4, "seconds": 1.0}))
    config = {"generation": slm.load_config(), "adapters": {"llamacpp": None}, "blocks": [
        {"block_id": "blk_1", "split": "val", "messages": []}]}
    predictions, metrics = compare.measure_backend(config, "llamacpp")
    assert predictions[0]["parsed_response"] is None
    assert predictions[0]["errors"] == ["invalid_json"]
    assert metrics["failures"] == 1
