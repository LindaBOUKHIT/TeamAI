# TeamAI — Détection et interprétation d'anomalies dans les logs HDFS

Projet NLP 2 (M2 IA, FGES) — Alain, Bachar, Linda, Nassim.

- **Volet A — en ligne** : un BiLSTM entraîné par l'équipe classe chaque trace HDFS en normal / anomalie, **dans le navigateur** (ONNX Runtime Web, site statique gratuit).
- **Volet B — local** : un SLM (SmolLM2-1.7B-Instruct) adapté par LoRA explique une trace en s'appuyant sur la documentation HDFS (RAG), avec une variante à 3 agents.

Pilotage : [board Jira SCRUM](https://lindaboukhit04.atlassian.net/jira/software/projects/SCRUM/boards/1) · [feuille de route](docs/projet/feuille_de_route.md) · [formats d'échange](docs/contrats.md) · [règles de contribution](CONTRIBUTING.md)

## Arborescence

```
projet/
├── teamai/            Code Python partagé (chargement HDFS, vocabulaire, métriques) — importé par tous
├── data/              Téléchargement, échantillon partagé, splits (données brutes non versionnées)
├── volet_a/
│   ├── training/      Baseline, BiLSTM, export ONNX, contrôle de parité        (Bachar, Nassim)
│   └── web/           Site statique : prétraitement JS, inférence, interface  (Bachar, Linda)
├── volet_b/
│   ├── slm/           Inférence locale, entraînement LoRA, configs             (Alain)
│   ├── rag/           Corpus documentaire HDFS, découpage, index, retrieval    (Linda)
│   ├── agents/        Orchestrateur 1 agent / 3 agents, prompts                (Linda)
│   ├── app/           Interface locale (Gradio)                                (Linda)
│   └── annotations/   Exemples d'explication (adaptation) — jamais le test     (tous)
├── eval/              Protocoles, jeux de test réservés, résultats              (Nassim + tous)
├── notebooks/         Explorations personnelles (préfixées par le prénom)
└── docs/              Sujet, cadrage, contrats, documentation par volet, rapport, soutenance
```

Chaque dossier contient un `README.md` : responsable, tickets Jira, entrées, sorties et commande de lancement.

## Démarrage rapide

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/Mac : source .venv/bin/activate)
pip install -e ".[data]"        # socle commun ; ajouter [volet_a] ou [volet_b] selon sa partie
python data/download_hdfs.py    # ~180 Mo → data/raw/HDFS_v1/ (non versionné)
python -m teamai.data.loader    # vérification : affiche les statistiques du corpus
```

Pas envie de télécharger 1,5 Go de logs ? `data/sample/` contient un échantillon versionné (dès SCRUM-18).

## Jalons

| Date | Jalon |
|---|---|
| 16/10/2026 | J3 — volet A fonctionnel, adaptation engagée, supports, rapport commencé |
| 07/12/2026 | J4 — soutenance (site en ligne **avant** ce jour) |

## Données

HDFS_v1 de [Loghub](https://github.com/logpai/loghub) (Zenodo, CC-BY-4.0). Citer : Xu et al., *Detecting Large-Scale System Problems by Mining Console Logs*, SOSP 2009 ; Zhu et al., *Loghub*, ISSRE 2023.
