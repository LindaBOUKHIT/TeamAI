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
Version compilée : `npm.cmd run build` puis `npx vite preview`.
Cliquer sur « Lancer la comparaison ».

## Correctifs du 14/10 (relecture d'Alain)

- **Padding ignoré** : le premier BiLSTM lisait aussi les zéros de padding (même bloc : 0,463 paddé contre 0,450 sans padding). Les deux directions sont désormais deux LSTM qui s'arrêtent au dernier vrai événement ; le script vérifie l'invariance (écart 0) avant l'export. Même technique à reprendre pour le modèle réel (SCRUM-25).
- **Moteur plus léger** : import de `onnxruntime-web/wasm` au lieu de `onnxruntime-web` : 14 Mo de WASM (3,7 Mo compressé) au lieu de 28 Mo (6,8 Mo).
- **Session réutilisée** : le modèle est chargé au premier clic seulement.
- **Build** : `npm run build` produit `dist/` (liens relatifs pour GitHub Pages), comme l'attend le workflow de déploiement.

Mesures après correctifs (build `vite preview`, Chrome du panneau Claude, une exécution) : modèle 16,8 Ko ; chargement 373 ms ; batchs 1/3/10 : 58,5 / 1,3 / 1,9 ms ; écart maximal 2,98e-8. Second clic : 0 ms de chargement.

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