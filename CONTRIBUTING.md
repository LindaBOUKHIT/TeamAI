# Règles de contribution

Le dépôt et le board sont consultés par l'enseignant : ils sont la trace de notre démarche.

## 1. Un ticket avant de coder

Aucun travail sans ticket Jira (`SCRUM-<n>`) créé **avant**. Passer le ticket « En cours » au démarrage, « En cours de revue » à l'ouverture de la PR, « Terminé » après fusion.

## 2. Branches

| Branche | Rôle | Qui y pousse |
|---|---|---|
| `main` | **Production** : ce qui est déployé (le site du volet A se publie depuis `main`) | Personne directement — PR depuis `dev` uniquement |
| `dev` | **Travail en cours** intégré | Personne directement — PR depuis les branches de travail |
| `feat/SCRUM-<n>-<slug>` | Une tâche | Le responsable du ticket |
| `fix/SCRUM-<n>-<slug>` | Une correction | Le responsable du ticket |

```bash
git switch dev && git pull
git switch -c feat/SCRUM-25-bilstm-v1
# … travail …
git push -u origin feat/SCRUM-25-bilstm-v1     # puis PR vers dev
```

Mise en production : PR `dev` → `main` quand une version est stable et testée, puis tag (`v0.1-mi-parcours`, `v1.0-volet-a`…).

## 3. Commits

```
SCRUM-25: entraîne le BiLSTM sur le split provisoire
```

- Clé du ticket en tête, verbe au présent, une idée par commit.
- **Aucune mention d'assistant IA** dans les commits ; l'usage de l'IA est consigné dans le journal (`docs/projet/journal.md` / classeur partagé).

## 4. Pull requests

- Relue par le **binôme** indiqué dans le ticket avant fusion (1 approbation).
- Le relecteur doit pouvoir lancer le code à partir du README du dossier.
- Remplir le modèle de PR (`.github/pull_request_template.md`).

## 5. Ce qui ne va jamais dans Git

Données brutes (`data/raw/`), splits complets, poids de modèles hors `volet_a/web/public/model/`, adaptateurs LoRA, index vectoriels, sorties d'expériences volumineuses, `.venv`, secrets. Voir `.gitignore`.

## 6. Données de test

Les jeux de test (`eval/volet_a`, `eval/volet_b`) ne servent **qu'à l'évaluation finale**. Interdit de les utiliser pour entraîner, régler un seuil ou ajuster un prompt.

## 7. Où écrire quoi

| Quoi | Où |
|---|---|
| Formats échangés entre tâches | `docs/contrats.md` (modifié par PR, prévenir l'équipe) |
| Décisions, abandons de features, usages IA, réunions | `docs/projet/journal.md` + classeur partagé |
| Résultats d'expériences | `eval/results/` + onglet Expériences du classeur |
| Documentation d'une partie | `docs/<data|volet_a|volet_b>/` |
