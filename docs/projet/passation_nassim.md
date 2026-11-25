# Suite du volet B pour Nassim

Ce qui reste à faire sur tes tickets et que toi seul peux faire : ta machine, tes annotations, ta présentation. Tout le reste (entraînement, runs de test, tableaux) est fait ou tourne sur Kaggle.

| # | Quoi | Ticket | Prérequis | Durée estimée |
|---|---|---|---|---|
| 1 | Mesure de l'adaptateur sur la RTX 3050 | SCRUM-61, étapes 1 et 5 | aucun (adaptateur dans le dépôt) | 30 min, téléchargement compris |
| 2 | Double annotation à l'aveugle | SCRUM-45 | fiches générées après les runs LoRA | quelques heures |
| 3 | Préparer l'oral sur tes tickets | SCRUM-35, 38, 39, 45, 61 | aucun | 1 h de lecture |

## 1. Mesure sur la RTX 3050 (SCRUM-61)

C'est le seul point du critère de fin de SCRUM-61 encore ouvert : la vérification a été faite sur T4, mais le ticket demande la machine cible du volet B.

**Installation**, une seule fois. Utilise Python 3.12 plutôt que ton 3.14.7 : la roue CUDA de llama-cpp-python n'est pas garantie pour 3.14.

```powershell
py -3.12 -m venv .venv312
.venv312\Scripts\Activate.ps1
python -m pip install -e ".[volet_b_gguf]"
python -m pip install --upgrade --force-reinstall --no-cache-dir --only-binary=llama-cpp-python llama-cpp-python==0.3.36 --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124
```

**Adaptateur.** Le réglage retenu par SCRUM-39 est `r8_qv`. Il est versionné dans le dépôt : `eval/results/SCRUM-39/kaggle_final/adapter_r8_qv.gguf` (4 547 904 octets, SHA-256 `52ff1ba7ca6833846b2148dba4c86dc0d5a646a6d582eaa8b2d0d6444559db7b`).

**Mesure**, en une commande depuis la racine du dépôt :

```powershell
python -m volet_b.slm.verif_machine --adapter C:\chemin\adapter.gguf --sha256 52ff1ba7ca6833846b2148dba4c86dc0d5a646a6d582eaa8b2d0d6444559db7b
```

Le script :
1. relève ton système, ta version de Python, le GPU, le pilote et les versions des paquets (étape 1) ;
2. télécharge le GGUF QAT q4_0 à la révision figée (plusieurs Go, une seule fois, dans le cache Hugging Face) ;
3. génère trois fois sur le même prompt d'entraînement (`seed-0001`) : sans adaptateur, avec l'adaptateur à l'échelle 0, puis à l'échelle 1 ;
4. écrit `eval/results/SCRUM-61/machine/<date>/` avec `resultats.json`, `resultats.md` et un journal par lancement.

Attendu : la base identique à l'échelle 0, l'échelle 1 différente, et la mémoire GPU sous 6 Go.

Si la mémoire GPU ne suffit pas, relance avec `--n-gpu-layers 30` (ou moins) et note le débit obtenu. Un échec documenté avec l'erreur exacte vaut aussi critère de fin.

**À rendre** : le dossier `eval/results/SCRUM-61/machine/<date>/` sur la branche `feat/SCRUM-39-lora-final` (PR #78), et la ligne « Nassim » de `docs/projet/environnements.md` mise à jour avec les versions relevées.

## 2. Double annotation à l'aveugle (SCRUM-45)

Les fiches sont générées une fois les quatre runs de test complets : le modèle de base est fait, les deux runs LoRA suivent la sélection SCRUM-39. Tu recevras un des deux fichiers `eval/volet_b/double_annotation/aveugle_annotateur_1.csv` ou `aveugle_annotateur_2.csv` :

- **Contenu** : 30 cas × 4 réponses, étiquetées A à D. L'étiquette ne dit pas de quelle configuration vient la réponse, et l'ordre change d'un cas à l'autre.
- **Notation** : note les colonnes `F`, `S`, `A`, `U` selon `docs/volet_b/grille_annotation.md`, et ajoute un `commentaire` si besoin.
- **La clé** : n'ouvre pas `cle_aveugle.json` avant la fin des deux grilles.
- **Fin** : coche ta colonne `annotation_N_terminee` dans `eval/volet_b/double_annotation.csv`.

Le dépouillement (moyennes, kappa, désaccords à arbitrer) se fait ensuite avec `python -m eval.volet_b.blind_scores`.

## 3. Préparer l'oral

Ce qu'il faut savoir présenter, dans l'ordre :

- **Jeu de test (SCRUM-35)** : 80 cas figés, empreinte vérifiée avant chaque run.
- **Banc et protocole (SCRUM-45, PR #77)** : `eval/README.md` et `eval/volet_b/run_eval.py`. Les échecs restent au dénominateur, et rien n'est retouché après avoir vu le test.
- **Modèle de base sur le test (SCRUM-38)** : `eval/results/SCRUM-45/kaggle_base/README.md`.
  - 1 agent : 79/80 réponses acceptées, 22 hypothèses, toutes sur des blocs avec incident.
  - 3 agents : 9/80 réponses acceptées, car le contrôleur rejette la plupart des brouillons. Environ un rejet sur trois est justifié : un ordre inventé entre des événements de la même seconde.
  - Un résumé « accepté » n'est pas forcément juste : la double annotation tranche.
- **LoRA (SCRUM-39 et 61, PR #78)** :
  - deux réglages, sélection sur val selon une règle fixée avant l'entraînement ;
  - exemple trop long écarté et listé ;
  - adaptateur seul converti en GGUF et appliqué au modèle quantifié : 132 tenseurs, échelle 0 identique à la base, échelle 1 différente.
