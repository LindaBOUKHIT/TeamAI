# eval/ — Protocoles et résultats

**Pilotage** : Nassim · **Contributeurs** : tous (on n'évalue jamais seul son propre composant) · **Epic** : SCRUM-10

```
eval/
├── metrics.py                  Métriques communes (macro-F1, rappel anomalie, matrice de confusion…)
├── volet_a/
│   └── evaluate.py             Baseline vs BiLSTM fp32/int8, test standard + séquences inédites   SCRUM-44
├── volet_b/
│   ├── test.jsonl              Jeu de test RÉSERVÉ (C5), figé et hashé avant tout réglage           SCRUM-35
│   ├── test.sha256
│   ├── run_config.py           Mesure base via v16 (SCRUM-38) → runs/                            SCRUM-38 / SCRUM-45
│   ├── grille.md               Grille d'évaluation humaine (lien vers docs/volet_b/grille_annotation.md)
│   └── double_annotation.csv   Notes des 2 annotateurs + arbitrage                                SCRUM-45
├── runs/                       Sorties brutes par exécution (C7) — non versionné
└── results/                    Tableaux et figures pour le rapport — versionné
    ├── volet_a.md
    ├── volet_b.md
    └── comparaison_a_b.md                                                                       SCRUM-47
```

## Règles

- Le test n'est ouvert qu'une fois, modèles et prompts figés.
- Toute exécution enregistre sa configuration (C7) ; le commit est à renseigner hors script, sans commande git dans SCRUM-38.
- Un résultat négatif (ex. pas de gain des agents) est un résultat : il va dans `results/`.

## Mesures avant adaptation du volet B (SCRUM-38)

SCRUM-38 mesure **base seulement**, avec Gemma 4 E4B QAT Q4_0 sous llama.cpp
et le pipeline v16 figé. À lancer sur le **portable de Nassim après fusion de #40**,
avec les poids déjà disponibles localement et le test C5 figé par SCRUM-35 :

```bash
python -m eval.volet_b.run_config --config base
```

`rag1` renvoie une erreur explicite : « rag1 reporté : pas de variante v16 + RAG
figée ; voir SCRUM-42/SCRUM-45 ». Le retrieval de Linda reste utilisable dans
`single_agent.retrieve_for_trace` ; aucune variante RAG n'est mesurée ici.

Pour chaque exemple, `facts.prepare_block` reconstruit les faits, la chronologie,
les preuves et les causes autorisées depuis `trace_lines`, puis `explain_block`
exécute le schéma fermé, les contrôles et l'éventuelle correction unique.
`expected`, `label`, `events` annotés et les autres annotations ne sont jamais
transmis au prompt. Les références de ligne sont locales à `trace_lines`, à partir
de 1 : C5 ne conserve pas les numéros du journal global. Les 29 templates sont lus
dans `data/raw/HDFS_v1/preprocessed/`, sinon dans leur copie versionnée de
`tests/fixtures/preprocessed/` ; le chemin et l'empreinte sont enregistrés.

Le script vérifie le SHA-256 du test officiel contre `test.sha256` s'il existe.
Une entrée absente ou une empreinte divergente arrête le lancement. `--data CHEMIN`
et `--limit N` servent aux essais sur des exemples fabriqués train/val. Un
`--adapter CHEMIN` est transmis à v16, mais exclut la publication avant adaptation.
Ne jamais ajuster un prompt ou un paramètre après lecture du test réservé.

Chaque lancement écrit un C7 neuf dans `eval/runs/` :

- `config.json` : empreintes de consigne et politique issues de
  `eval/results/SCRUM-63/prompt_freeze.json`, modèle, fichier et révision GGUF,
  contexte 4096, budget 800, paramètres figés, plateforme réelle et machine cible
  informative (portable de Nassim). Le commit reste `null`, à renseigner hors
  script : aucune commande git n'est exécutée.
- `predictions.jsonl` : toutes les tentatives, textes et prompts, erreurs de
  contrat et factuelles, alertes, `finish_reason`, tokens, temps et nombre réel
  d'appels, y compris une correction échouée. Les entrées invalides comptent aussi.
- `metrics.json` : conformité C5, sources valides et abstention ; contrat v16,
  faits exactement copiés, références inexistantes, causes réseau sans appui,
  enquêtes sans indice d'incident, hypothèses avec et sans incident, anti-boucle,
  corrections déclenchées, tentées et réussies ; latences et mémoire.

Tous les taux ont pour dénominateur **tous les exemples lus, échecs compris**.
Les hypothèses par bloc avec/sans incident sont rapportées au **nombre de blocs
du groupe**, échecs compris dès que `attention` est connu ; une réponse invalide
compte 0 hypothèse. Un groupe vide donne `None` (`null` en JSON). Les effectifs
et les sommes sont conservés. Ce calcul suit SCRUM-63 : 4 hypothèses / 21 blocs
avec incident = 0,19 après arrondi ; la métrique conserve la valeur non arrondie.
L'incident correspond à `attention` calculé par v16, jamais au label.
Les faits exactement copiés exigent une structure évaluable par les contrôles v16.
L'anti-boucle compte un exemple si une tentative est rejetée par `repetition_errors`
(répétition ou budget presque épuisé). Une correction réussie satisfait tous les
contrôles v16 ; les alertes lexicales ne certifient pas la fidélité sémantique.

Le temps mural inclut préparation, contrôles et chargement éventuel ; les temps
renvoyés par la génération sont conservés séparément et sommés. Les pics RSS et
VRAM du processus sont échantillonnés toutes les 0,2 s, chargement inclus. La VRAM
somme le PID courant sur les GPU NVIDIA : `pynvml` si disponible, sinon
`nvidia-smi --query-compute-apps`. Une mesure indisponible vaut `null` ; aucune
nouvelle dépendance GPU n'est obligatoire. Ce relevé peut manquer un pic bref.

`update_summary(metric_paths)` actualise seulement la ligne `base` de « Avant
adaptation » dans `eval/results/volet_b.md`. Il refuse `rag1`, les runs factices,
partiels, vides, hors test officiel ou avec adaptateur. Aucun résumé n'est publié
automatiquement. Les tests fabriqués de `tests/test_run_config.py` traversent v16
avec une génération simulée, dont une boucle et une correction, sans modèle ni
réseau. Les tests d'empreintes de `tests/test_v16.py` restent inchangés.

## SCRUM-35 — Préparation du jeu de test du volet B

### Objectif

Constituer un jeu de test HDFS réservé pour évaluer les explications du volet B au format C5, avec des références documentaires C6 vérifiables.

### Constitution du jeu

- Source : split officiel `test` de SCRUM-20.
- Sélection : 80 traces HDFS distinctes.
- Répartition : 40 traces normales et 40 anomalies.
- Échantillonnage équilibré volontairement : il ne représente pas la prévalence réelle des anomalies dans HDFS.
- Exclusion des quatre blocs de test déjà exposés, afin de limiter les risques de fuite.
- Conservation des lignes de logs et des événements associés.

### Annotations

Chaque exemple contient :
- Un identifiant et un identifiant de bloc HDFS.
- Les lignes de logs et les événements.
- Le label officiel.
- Une explication C5 : résumé, faits observés, hypothèses, informations manquantes, sources C6 et décision d'abstention.
- Les identifiants de l'annotateur et du relecteur.

Les explications actuellement préparées sont des **brouillons non validés**.

### Contrôles réalisés

- 80 fiches présentes.
- 40 normales et 40 anomalies.
- 10 abstentions provisoires.
- 51 passages documentaires C6 disponibles.
- Contrôle structurel : 0 erreur.
- 160 avertissements attendus : annotateurs et relecteurs non renseignés.

Ces contrôles ne prouvent pas l'exactitude des explications.

### Double annotation et relecture

- 30 traces sélectionnées : 15 normales et 15 anomalies.
- Deux fichiers vierges préparés pour une annotation indépendante.
- Les réponses doivent être produites séparément, puis comparées.
- Les désaccords doivent être arbitrés.
- Les 80 annotations doivent être relues par une personne différente de leur annotateur.

La double annotation et la relecture humaine restent à réaliser.

### Gel du jeu de test

Les fichiers définitifs `eval/volet_b/test.jsonl` et `eval/volet_b/test.sha256` seront produits uniquement après validation des annotations.

Le jeu de test ne doit jamais servir à l'entraînement, à l'adaptation LoRA, au réglage des prompts ou à l'optimisation du RAG.

### État de livraison

Préparation technique réalisée. Jeu de test définitif non encore validé ni figé.
