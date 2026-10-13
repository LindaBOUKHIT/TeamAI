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