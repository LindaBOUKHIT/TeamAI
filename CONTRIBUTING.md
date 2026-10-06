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
- **Fusion seulement si les tests automatiques sont au vert** (coche verte sur la PR, voir §8).

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

## 8. Tests automatisés

GitHub Actions (`.github/workflows/tests.yml`) lance les tests à chaque PR vers `dev` ou `main` : une coche verte ou une croix rouge s'affiche sur la PR.

En local, avant d'ouvrir une PR :

```bash
pip install -e ".[dev]"
pytest -q -rs          # -rs affiche pourquoi certains tests sont sautés
```

| Dossier | Contenu |
|---|---|
| `tests/` | Tests Python (pytest) : chargeur de données, formats d'échange, fichiers d'annotation, mode factice du SLM |
| `tests/fixtures/` | Petites données extraites de HDFS_v1 (5 Ko) : les tests tournent partout sans les 1,5 Go |
| `volet_a/web/tests/` | Tests du site (`npm test`), dont la parité JavaScript ↔ Python |

Règles :
- Pas de données lourdes ni de modèle dans les tests : utiliser `tests/fixtures/` et `TEAMAI_SLM_MOCK=1`.
- Un test qui a besoin du corpus complet porte la marque `@pytest.mark.full_data` : il est sauté s'il manque (donc sur GitHub), mais tourne chez ceux qui l'ont téléchargé.
- Chaque ticket qui ajoute du code ajoute ses tests (ex. parser : concordance avec Loghub ; splits : aucune fuite train/test).
- `teamai.contracts` vérifie le format C5 : l'utiliser aussi dans le code (taux de réponses conformes du volet B).
