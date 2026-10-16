# SCRUM-22 — Spike BiLSTM / ONNX

Responsable : Bachar Ben Slama.
Relecteur : Nassim.

## Objectif

Vérifier l’export d’un BiLSTM jouet vers ONNX et son exécution
dans le navigateur avec ONNX Runtime Web, backend WASM.

Les poids sont aléatoires. Les scores n’ont aucune valeur prédictive.

## Exécution Python

Ouvrir PowerShell à la racine du dépôt et exécuter :

    .\.venv\Scripts\python.exe -m pip install -e ".[volet_a]"
    .\.venv\Scripts\python.exe volet_a/training/spike_onnx.py

Ces commandes supposent que l’environnement .venv existe déjà.
Pour le créer : python -m venv .venv

## Test navigateur

Depuis la racine du dépôt, exécuter dans PowerShell :

    cd volet_a/web
    npm.cmd ci
    npm.cmd run dev

Ouvrir l’adresse affichée par Vite suivie de /spike.html.
Cliquer sur « Lancer la comparaison ».

## Contrat C3

- Entrée : event_ids, int64, [batch, 50].
- Sortie : p_anomaly, float32, [batch].
- Taille du batch dynamique.

## Résultats observés

- Taille du modèle : environ 7,9 Ko.
- Dix entrées identiques comparées entre Python et navigateur.
- Batchs vérifiés : 1, 3 et 10.
- Écart maximal navigateur : 2,9802e-8.
- Critère : écart inférieur à 1e-4 — satisfait.
- Chargement et préparation : 1436,5 ms.
- Inférence batch 1 : 33,8 ms.
- Inférence batch 3 : 2,1 ms.
- Inférence batch 10 : 2,1 ms.

Mesures d’une seule exécution locale, dans cet ordre.
La première inférence peut inclure un coût d’initialisation.
Ces résultats ne constituent pas un benchmark général.


## SCRUM-25 — BiLSTM entraîné sur HDFS_v1

### Données et protocole

Source : Loghub HDFS_v1, fichier preprocessed/Event_traces.csv.
Les fichiers Event_traces.csv et HDFS.log_templates.csv doivent être
placés dans data/raw/HDFS_v1/preprocessed/.

Splits officiels SCRUM-20 : stratification par label, seed 42.
- Train : 402 542 blocs, dont 11 787 anomalies.
- Validation : 86 259 blocs, dont 2 525 anomalies.
- Validation inédite : 1 929 séquences absentes du train.

SHA-256 de splits.csv :
f504592cb7ac13b8b7e5d532a336b4e3641ec441a863c5efafd164faa2a43f22

Le test officiel n’est ni évalué ni utilisé pour sélectionner
le modèle, les hyperparamètres ou le seuil.

### Architecture et entraînement

Embedding : 31 entrées, dimension 16, padding 0.
BiLSTM : 32 unités par direction.
Agrégation : moyenne des sorties aux positions non padding.
Couche linéaire et sigmoïde : une sortie p_anomaly par bloc.
Nombre de paramètres : 13 361.

L’agrégation exclut les positions padding ; le BiLSTM lui-même
parcourt les 50 positions de la séquence encodée.

Entraînement CPU : 5 époques, batch 512, 4 threads, seed 42.
Optimiseur Adam, learning rate 0,001.
BCEWithLogitsLoss pondérée selon les effectifs du train.
Gradient clipping : norme maximale 1.

Le meilleur couple époque/seuil est choisi sur la macro-F1
de validation, avec une grille de seuils de 0,01 à 0,99.
Modèle retenu : époque 5, seuil 0,99.
Ce seuil se trouve à la borne supérieure de la grille explorée.
Les scores ne sont pas des probabilités calibrées.

### Commandes

Depuis la racine du dépôt, dans PowerShell :

    python -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -e ".[data,volet_a]"

Si les splits officiels sont absents :

    .\.venv\Scripts\python.exe data/make_splits.py

Vérifier que le hash généré correspond à la référence ci-dessus.
Le script de génération réécrit splits_meta.json :
conserver les métadonnées officielles pour la comparaison.

Préparation et entraînement :

    .\.venv\Scripts\python.exe volet_a/training/dataset.py
    .\.venv\Scripts\python.exe volet_a/training/train.py --split officiel --epochs 5 --batch-size 512 --threads 4

Chaque entraînement crée un dossier neuf dans eval/runs/.
Remplacer CHEMIN_DU_RUN ci-dessous par le dossier affiché :

    .\.venv\Scripts\python.exe volet_a/training/export_onnx.py --run CHEMIN_DU_RUN
    .\.venv\Scripts\python.exe volet_a/training/check_parity.py --run CHEMIN_DU_RUN

L’export est créé dans le sous-dossier export du run.
Il ne remplace pas automatiquement le modèle du site.
L’export et le rapport de parité refusent d’écraser leurs
résultats existants.

### Résultats de validation

Run : 20261016T184412Z_4f3011f2_bilstm.
Durée entraînement et validation : environ 352 secondes.
Cette durée exclut le chargement initial des données.

Validation globale :
- Macro-F1 : 0,995514.
- Précision anomalie : 0,990898.
- Rappel anomalie : 0,991683.
- Fausses alertes : 23.
- Anomalies manquées : 21.

Validation sur les 1 929 séquences inédites :
- Macro-F1 : 0,976748.
- Précision anomalie : 0,964618.
- Rappel anomalie : 0,968224.
- Fausses alertes : 19.
- Anomalies manquées : 17.

Comparaison aux résultats publiés de la baseline SCRUM-24 :
- Macro-F1 globale : baseline 0,989698 ; BiLSTM 0,995514.
- Macro-F1 inédite : baseline 0,961848 ; BiLSTM 0,976748.
- Validation globale : baseline 103 fausses alertes et aucune
  anomalie manquée ; BiLSTM 23 fausses alertes et 21 manquées.

Le BiLSTM améliore la macro-F1 et réduit les fausses alertes,
avec une baisse du rappel. La baseline utilise les comptages
complets ; le BiLSTM conserve au maximum 50 événements.
Ces résultats de validation servent aussi à la sélection :
ils ne remplacent pas une évaluation finale indépendante.

### Export et parité

Modèle ONNX : environ 55,5 Ko.
Contrat C3 : event_ids int64 [batch, 50] vers p_anomaly float32 [batch].
Les métadonnées contiennent le seuil et les hashes du modèle,
du vocabulaire et des splits.

PyTorch / ONNX Runtime Python :
- 86 259 blocs de validation comparés.
- Écart maximal : 1,1921e-7, inférieur à 1e-4.
- Aucune différence de classification au seuil 0,99.
- Batchs 1, 3, 10 et 512 vérifiés.

PyTorch / ONNX Runtime Web, backend WASM :
- Dix séquences de validation comparées.
- Batchs 1, 3 et 10 vérifiés.
- Hash du modèle vérifié avant inférence.
- Écart maximal observé : 4,3277e-8, inférieur à 1e-4.

Pour reproduire le test navigateur :

    cd volet_a/web
    npm.cmd ci
    npm.cmd run dev

Ouvrir l’adresse affichée suivie de /spike.html.
Si la configuration Vite de SCRUM-23 est présente, utiliser
le préfixe /TeamAI/, donc /TeamAI/spike.html.

### Artefacts

Résumés versionnés : eval/results/SCRUM-25-bilstm-v1/.
Checkpoint et prédictions détaillées : eval/runs/, ignoré par Git.
Modèle servi : volet_a/web/public/model/detector.onnx.
Cas de parité navigateur : public/model/parity_cases.json.

La page spike.html utilise désormais le modèle entraîné et
parity_cases.json. Les anciens spike_cases.json documentent
le modèle jouet et ne doivent pas être comparés au nouveau modèle.