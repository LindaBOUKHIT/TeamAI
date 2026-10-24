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
│   ├── run_config.py           Exécute une des 4 configurations → runs/                            SCRUM-38 / SCRUM-45
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
- Toute exécution enregistre sa configuration et le commit Git (C7) ; un résultat sans configuration n'existe pas.
- Un résultat négatif (ex. pas de gain des agents) est un résultat : il va dans `results/`.

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
