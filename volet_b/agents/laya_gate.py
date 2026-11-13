"""Porte Laya optionnelle : abstention et vérification des hypothèses C5.

Installation facultative pour une utilisation réelle : ``pip install laya``.
Aucun import ni chargement du modèle avant le premier appel sans prédicteur injecté.
Les templates sont un dictionnaire EventId → EventTemplate, issu notamment de
teamai.data.loader.load_templates().set_index("EventId")["EventTemplate"].to_dict().
Le backend utilise l'API Router() par défaut ; modèle et révision du YAML décrivent
la référence attendue ; la révision est transmise à Router(revision=...).
"""
from copy import deepcopy
from itertools import groupby
import math
import re
from time import perf_counter

import yaml

from teamai import paths
from teamai.contracts import validate_answer


def load_config(path=None):
    """Lit et vérifie les paramètres de la porte depuis les chemins centralisés."""
    target = paths.AGENTS / "configs" / "laya.yaml" if path is None else paths.resolve_path(path)
    config = yaml.safe_load(target.read_text(encoding="utf-8"))
    low, high, minimum = (config[k] for k in ("abstention_low", "abstention_high", "hypothesis_min"))
    if not (0 <= low <= high <= 1 and 0 <= minimum <= 1):
        raise ValueError("Seuils Laya invalides : probabilités attendues entre 0 et 1.")
    if not isinstance(config["max_chars"], int) or config["max_chars"] < 1:
        raise ValueError("max_chars doit être un entier positif.")
    config["hypothesis_question"].format(hypothesis="exemple")
    return config


def state_from_events(events, templates, max_chars):
    """Groupe les codes consécutifs et conserve des lignes entières sous la limite.

    Les événements omis sont comptés avec leurs répétitions. Une limite trop courte
    pour la seule mention d'omission est refusée, plutôt que de masquer la troncature.
    Aucun message brut n'est accepté comme code ou utilisé comme template implicite.
    """
    events = list(events)
    if not isinstance(max_chars, int) or max_chars < 1:
        raise ValueError("max_chars doit être un entier positif.")
    lines, counts = [], []
    for code, group in groupby(events):
        if not isinstance(code, str) or not re.fullmatch(r"E[0-9]+", code):
            raise ValueError("Chaque événement doit être un code Exx, jamais un log brut.")
        if code not in templates or not isinstance(templates[code], str):
            raise ValueError(f"Template texte absent pour {code}.")
        count = sum(1 for _ in group)
        text = " ".join(templates[code].split())
        lines.append(f"{code}" + (f" ×{count}" if count > 1 else "") + f" : {text}")
        counts.append(count)
    if len("\n".join(lines)) <= max_chars:
        return "\n".join(lines)
    omitted = 0
    while lines:
        omitted += counts.pop()
        lines.pop()
        marker = f"[{omitted} événements omis]"
        state = "\n".join([*lines, marker])
        if len(state) <= max_chars:
            return state
    raise ValueError("max_chars insuffisant pour indiquer le nombre d'événements omis.")


class LayaGate:
    """Applique une porte conservatrice sans modifier la réponse fournie."""

    def __init__(self, config, predict=None):
        """Copie la configuration et conserve un prédicteur injectable sans modèle."""
        self.config = deepcopy(config)
        self._predict = predict
        self._router = None

    def _prediction(self, state, questions):
        """Charge le backend optionnel à la demande, puis fait un seul appel groupé."""
        if self._predict is None:
            try:
                from laya import Router
            except ImportError as exc:
                raise ImportError("Laya absent : installer le paquet optionnel avec pip install laya.") from exc
            self._router = Router(revision=self.config.get("revision"))
            model = self.config.get("router_model", "english")

            def predict(state, questions):
                """Interroge le checkpoint choisi dans la configuration, à la révision figée."""
                return self._router.predict(state, questions, model=model)

            self._predict = predict
        return self._predict(state, questions)

    def load(self):
        """Charge le backend et fait un appel d'échauffement ; renvoie la durée en secondes."""
        start = perf_counter()
        self._prediction("E5 : warm-up", {"warmup": {"type": "noul", "instructions": "Is this a warm-up?"}})
        return perf_counter() - start

    def apply(self, answer, events, templates):
        """Retourne une réponse C5 indépendante et les probabilités avec indices d'origine."""
        errors = validate_answer(answer)
        if errors:
            raise ValueError("Réponse d'entrée C5 invalide : " + "; ".join(errors))
        result = deepcopy(answer)
        config = self.config
        state = state_from_events(events, templates, config["max_chars"])
        questions = {"anomaly": {"type": "noul", "instructions": config["anomaly_question"]}}
        for index, hypothesis in enumerate(answer["hypotheses"]):
            questions[f"hypothesis_{index}"] = {
                "type": "noul", "instructions": config["hypothesis_question"].format(hypothesis=hypothesis)}
        start = perf_counter()
        prediction = self._prediction(state, questions)
        seconds = perf_counter() - start
        probabilities = {}
        for name in questions:
            try:
                value = prediction["answers"][name]["noul"]
                if isinstance(value, bool):
                    raise ValueError
                value = float(value)
                if not math.isfinite(value) or not 0 <= value <= 1:
                    raise ValueError
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"Probabilité Laya invalide ou absente : {name}.") from exc
            probabilities[name] = value
        p = probabilities["anomaly"]
        ambiguous = config["abstention_low"] <= p <= config["abstention_high"]
        result["abstention"] = answer["abstention"] or ambiguous
        moved, kept = [], []
        for index, hypothesis in enumerate(answer["hypotheses"]):
            if ambiguous or probabilities[f"hypothesis_{index}"] < config["hypothesis_min"]:
                prefix = "Hypothèse non confirmée : " if ambiguous else "À vérifier : "
                result["infos_manquantes"].append(prefix + hypothesis)
                moved.append(index)
            else:
                kept.append(hypothesis)
        result["hypotheses"] = kept
        if ambiguous:
            result["infos_manquantes"].append(f"Signal d'anomalie ambigu (Laya p={p:.2f})")
        errors = validate_answer(result)
        if errors:
            raise ValueError("Réponse de sortie C5 invalide : " + "; ".join(errors))
        return result, {"anomaly_probability": p,
                        "hypothesis_probabilities": [probabilities[f"hypothesis_{i}"]
                                                     for i in range(len(answer["hypotheses"]))],
                        "moved_indices": moved,
                        "abstention_added": ambiguous and not answer["abstention"],
                        "predict_seconds": seconds}
