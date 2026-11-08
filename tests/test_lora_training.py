"""SCRUM-29 : loss et AMP sur petits modules CPU, sans poids téléchargés ni GPU."""
import copy
from types import SimpleNamespace

import pytest

torch = pytest.importorskip("torch")

from volet_b.slm.train_lora import (
    OptimizerProgress, amp_optimizer_step, ensure_trainable_float32, supervised_causal_loss,
)


class TinyCausalLM(torch.nn.Module):
    """Double de Gemma : découpe avant lm_head, puis softcapping, sans argument labels."""

    def __init__(self):
        """Construit un vocabulaire et des états minuscules déterministes sur CPU."""
        super().__init__()
        self.embedding = torch.nn.Embedding(13, 5)
        self.lm_head = torch.nn.Linear(5, 13)
        self.kept = []

    def forward(self, input_ids, attention_mask, logits_to_keep):
        """Reproduit la sémantique de logits_to_keep=0 et des suffixes positifs."""
        self.kept.append(logits_to_keep)
        hidden = self.embedding(input_ids) * attention_mask.unsqueeze(-1)
        logits = self.lm_head(hidden[:, -logits_to_keep:])
        return SimpleNamespace(logits=3.0 * torch.tanh(logits / 3.0))


@pytest.mark.parametrize("labels", [
    [-100, -100, -100, 4, 5, 6, 7],
    [-100, -100, 3, -100, 5, -100, -100],
    [-100, 2, -100, -100, -100, -100, -100],
    [-100, -100, -100, -100, -100, -100, 7],
])
def test_reduced_loss_and_gradients_equal_full_shift(labels):
    """Compare loss à 1e-6 et gradients avec CE complète, trous et fins masquées inclus."""
    torch.manual_seed(42)
    reduced_model = TinyCausalLM()
    full_model = copy.deepcopy(reduced_model)
    batch = {"input_ids": torch.tensor([[1, 2, 3, 4, 5, 6, 7]]),
             "attention_mask": torch.ones(1, 7, dtype=torch.long),
             "labels": torch.tensor([labels])}
    reduced = supervised_causal_loss(reduced_model, batch)
    first = next(i for i, value in enumerate(labels) if value != -100)
    assert reduced_model.kept == [7 - first + 1]
    logits = full_model(batch["input_ids"], batch["attention_mask"], 0).logits
    full = torch.nn.functional.cross_entropy(logits[:, :-1].float().reshape(-1, 13),
                                             batch["labels"][:, 1:].reshape(-1), ignore_index=-100)
    torch.testing.assert_close(reduced, full, atol=1e-6, rtol=0)
    reduced.backward()
    full.backward()
    for reduced_parameter, full_parameter in zip(reduced_model.parameters(), full_model.parameters()):
        torch.testing.assert_close(reduced_parameter.grad, full_parameter.grad, atol=1e-6, rtol=0)


@pytest.mark.parametrize("labels,first,message", [
    ([-100, -100, -100], None, "aucun label supervisé"),
    ([-100, 2, 3], 2, "précède first"),
    ([-100, -100, 3], 1, "premier label supervisé"),
    ([1, 2, 3], None, "position précédente"),
])
def test_reduced_loss_invalid_boundary(labels, first, message):
    """Refuse les labels vides ou une frontière incohérente avant le forward."""
    model = TinyCausalLM()
    batch = {"input_ids": torch.tensor([[1, 2, 3]]),
             "attention_mask": torch.ones(1, 3, dtype=torch.long), "labels": torch.tensor([labels])}
    with pytest.raises(ValueError, match=message):
        supervised_causal_loss(model, batch, first=first)
    assert model.kept == []


class FakeScaler:
    """Simule sur CPU un GradScaler actif qui détecte les inf et réduit son échelle."""

    def __init__(self, inject_inf=False):
        """Initialise les compteurs et l'injection facultative après backward."""
        self.current_scale = 1024.0
        self.inject_inf = inject_inf
        self.found_inf = False
        self.step_calls = 0
        self.update_calls = 0
        self.unscale_calls = 0

    def is_enabled(self):
        """Active le chemin AMP malgré l'absence de CUDA."""
        return True

    def get_scale(self):
        """Expose l'échelle avant et après update."""
        return self.current_scale

    def scale(self, loss):
        """Multiplie réellement la loss afin de vérifier l'ordre unscale puis clipping."""
        return loss * self.current_scale

    def unscale_(self, optimizer):
        """Divise les gradients FP32 et peut injecter un débordement isolé."""
        self.unscale_calls += 1
        self.found_inf = False
        for group in optimizer.param_groups:
            for parameter in group["params"]:
                if parameter.grad is not None:
                    assert parameter.grad.dtype == torch.float32
                    parameter.grad.div_(self.current_scale)
                    if self.inject_inf:
                        parameter.grad.fill_(float("inf"))
                    self.found_inf |= not bool(torch.isfinite(parameter.grad).all())

    def step(self, optimizer):
        """Compte l'appel au scaler mais n'applique l'optimiseur qu'avec des gradients finis."""
        self.step_calls += 1
        if not self.found_inf:
            optimizer.step()

    def update(self):
        """Réduit l'échelle en cas de débordement détecté."""
        self.update_calls += 1
        if self.found_inf:
            self.current_scale /= 2


def test_inf_gradient_skipped_then_finite_step_applied():
    """Un inf isolé ne lève pas ; le pas suivant applique un gradient écrêté après unscale."""
    parameter = torch.nn.Parameter(torch.tensor([2.0]))
    optimizer = torch.optim.SGD([parameter], lr=0.1)
    scaler = FakeScaler(inject_inf=True)
    progress = OptimizerProgress(8)
    skipped = amp_optimizer_step(parameter.square().sum(), [parameter], optimizer, scaler, 1.0)
    progress.record(skipped["skipped"])
    assert skipped == {"scale": 512.0, "skipped": True, "grad_norm": None}
    assert parameter.item() == 2.0
    assert parameter.grad is None
    scaler.inject_inf = False
    applied = amp_optimizer_step(parameter.square().sum(), [parameter], optimizer, scaler, 1.0)
    progress.record(applied["skipped"])
    progress.finish()
    assert applied == {"scale": 512.0, "skipped": False, "grad_norm": 4.0}
    assert parameter.item() == pytest.approx(1.9, abs=1e-6)
    assert progress.optimizer_steps == progress.skipped_steps == 1
    assert progress.consecutive_skips == 0
    assert scaler.step_calls == scaler.update_calls == scaler.unscale_calls == 2


def test_scale_decrease_alone_marks_skip(monkeypatch):
    """Une baisse d'échelle suffit à détecter un saut même sans gradient inf observé."""
    parameter = torch.nn.Parameter(torch.tensor([2.0]))
    optimizer = torch.optim.SGD([parameter], lr=0.1)
    scaler = FakeScaler()

    def skipped_step(optimizer):
        """Simule un scaler qui découvre tardivement un débordement et évite l'optimiseur."""
        scaler.found_inf = True

    monkeypatch.setattr(scaler, "step", skipped_step)
    result = amp_optimizer_step(parameter.square().sum(), [parameter], optimizer, scaler, 1.0)
    assert result["skipped"] is True and result["scale"] == 512.0
    assert parameter.item() == 2.0


def test_consecutive_skips_stop_at_limit():
    """La boucle laisse passer les premiers inf et échoue exactement au seuil configuré."""
    parameter = torch.nn.Parameter(torch.tensor([2.0]))
    optimizer = torch.optim.SGD([parameter], lr=0.1)
    scaler = FakeScaler(inject_inf=True)
    progress = OptimizerProgress(3)
    for _ in range(2):
        result = amp_optimizer_step(parameter.square().sum(), [parameter], optimizer, scaler, 1.0)
        progress.record(result["skipped"])
    with pytest.raises(RuntimeError, match="gradients non finis persistants en fp16.*activations hors plage"):
        result = amp_optimizer_step(parameter.square().sum(), [parameter], optimizer, scaler, 1.0)
        progress.record(result["skipped"])
    assert progress.skipped_steps == scaler.update_calls == 3
    assert progress.optimizer_steps == 0
    assert parameter.item() == 2.0


def test_no_optimizer_step_is_failure_even_below_limit():
    """Un essai d'un pas sauté échoue sans annoncer un adaptateur entraîné."""
    progress = OptimizerProgress(8)
    progress.record(True)
    with pytest.raises(RuntimeError, match="Aucun pas d'optimiseur appliqué"):
        progress.finish()


@pytest.mark.parametrize("value", [float("inf"), float("nan")])
def test_nonfinite_loss_is_always_fatal(value):
    """Une loss inf ou NaN arrête avant backward, unscale, step et update."""
    parameter = torch.nn.Parameter(torch.tensor([2.0]))
    optimizer = torch.optim.SGD([parameter], lr=0.1)
    scaler = FakeScaler()
    with pytest.raises(RuntimeError, match="Perte non finie"):
        amp_optimizer_step(parameter.sum() * value, [parameter], optimizer, scaler, 1.0)
    assert scaler.step_calls == scaler.update_calls == scaler.unscale_calls == 0
    assert parameter.grad is None


def test_trainable_parameters_promoted_before_optimizer():
    """Seul l'adaptateur FP16 est promu ; ses gradients deviennent compatibles avec unscale."""
    model = torch.nn.Linear(2, 1, dtype=torch.float16)
    model.bias.requires_grad_(False)
    frozen = model.bias.data
    parameters = ensure_trainable_float32(model)
    assert len(parameters) == 1 and parameters[0] is model.weight
    assert model.weight.dtype == torch.float32
    assert model.bias.dtype == torch.float16 and model.bias.data_ptr() == frozen.data_ptr()
    optimizer = torch.optim.SGD(parameters, lr=0.1)
    result = amp_optimizer_step(model.weight.square().sum(), parameters, optimizer, FakeScaler(), 1.0)
    assert result["skipped"] is False


def test_loading_info_is_json_serializable():
    """Transformers 5 renvoie des ensembles dans loading_info : metrics.json doit rester écrivable."""
    import json

    from volet_b.slm.train_lora import jsonable

    info = {"missing_keys": {"b", "a"}, "unexpected_keys": set(), "error_msgs": [], "mismatched_keys": [("w", object())]}
    out = json.loads(json.dumps(jsonable(info)))
    assert out["missing_keys"] == ["a", "b"] and out["unexpected_keys"] == []
    assert isinstance(out["mismatched_keys"][0][1], str)
