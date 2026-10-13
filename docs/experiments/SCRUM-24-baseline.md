
# SCRUM-24 — Baseline HDFS : régression logistique

## 1. Objectif

Développer une baseline de détection d'anomalies dans les logs HDFS à partir des comptages d'événements, puis évaluer ses performances et sa capacité de généralisation sur les séquences inédites.

Cette baseline servira de référence pour comparer les futurs modèles, notamment le BiLSTM du volet A.

## 2. Dataset et préparation des données

- Dataset : HDFS v1 (Loghub)
- Source : `data/raw/HDFS_v1/preprocessed/Event_occurrence_matrix.csv`
- Unité d'analyse : bloc HDFS (`BlockId`)
- Caractéristiques : 29 comptages d'événements (`E1` à `E29`)
- Variable cible : `Label`
  - `Success` : normal (0)
  - `Fail` : anomalie (1)
- Splits officiels : SCRUM-20
- Seed : 42

### Répartition des données

| Split | Nombre de blocs | Utilisation |
|---|---:|---|
| Train | 402 542 | Entraînement |
| Validation | 86 259 | Évaluation pendant le développement |
| Test | 86 260 | Évaluation finale |
| **Total** | **575 061** | |

Les splits sont effectués au niveau des `BlockId`, sans chevauchement entre train, validation et test.

## 3. Configuration du modèle

| Paramètre | Valeur |
|---|---|
| Algorithme | LogisticRegression |
| Bibliothèque | scikit-learn |
| Caractéristiques | E1 à E29 |
| Normalisation | StandardScaler |
| class_weight | balanced |
| max_iter | 1000 |
| random_state | 42 |
| Seuil de classification | 0,5 (par défaut) |
| Environnement | CPU |

Le pipeline est constitué d'un `StandardScaler` suivi d'une `LogisticRegression`.

La normalisation est ajustée uniquement sur le jeu d'entraînement afin d'éviter les fuites de données.

Le modèle est entraîné uniquement sur le split `train`. Les jeux de validation et de test ne sont pas utilisés pour l'ajustement des coefficients.

## 4. Résultats de validation

### 4.1 Performances globales

| Métrique | Résultat |
|---|---:|
| Nombre de blocs | 86 259 |
| Accuracy | 0.9988 |
| Précision anomalie | 0.9608 |
| Rappel anomalie | 1.0000 |
| Macro-F1 | 0.9897 |
| Vrais négatifs (TN) | 83 631 |
| Faux positifs (FP) | 103 |
| Faux négatifs (FN) | 0 |
| Vrais positifs (TP) | 2 525 |

### 4.2 Matrice de confusion

| Réel / Prédit | Normal | Anomalie |
|---|---:|---:|
| Normal | 83 631 | 103 |
| Anomalie | 0 | 2 525 |

Le modèle détecte les 2 525 anomalies de validation sans faux négatif, mais génère 103 fausses alertes.

### 4.3 Séquences inédites et connues

Une séquence est considérée comme inédite lorsque sa succession exacte d'événements n'apparaît pas dans le jeu d'entraînement.

| Métrique | Global | Inédites | Connues |
|---|---:|---:|---:|
| Blocs | 86 259 | 1 929 | 84 330 |
| Accuracy | 0.9988 | 0.9684 | 0.9995 |
| Précision anomalie | 0.9608 | 0.8977 | 0.9793 |
| Rappel anomalie | 1.0000 | 1.0000 | 1.0000 |
| Macro-F1 | 0.9897 | 0.9618 | 0.9947 |
| Faux positifs | 103 | 61 | 42 |
| Faux négatifs | 0 | 0 | 0 |

Les séquences inédites sont plus difficiles à classifier, notamment en raison d'une augmentation des faux positifs.

## 5. Résultats du test officiel

L'évaluation finale a été réalisée avec les paramètres du modèle fixés avant l'utilisation du jeu de test.

### 5.1 Performances globales

| Métrique | Résultat |
|---|---:|
| Nombre de blocs | 86 260 |
| Accuracy | 0.9986 |
| Précision anomalie | 0.9561 |
| Rappel anomalie | 0.9992 |
| Macro-F1 | 0.9882 |
| Vrais négatifs (TN) | 83 618 |
| Faux positifs (FP) | 116 |
| Faux négatifs (FN) | 2 |
| Vrais positifs (TP) | 2 524 |

### 5.2 Matrice de confusion

| Réel / Prédit | Normal | Anomalie |
|---|---:|---:|
| Normal | 83 618 | 116 |
| Anomalie | 2 | 2 524 |

Sur les 2 526 anomalies présentes dans le test, le modèle en détecte 2 524 et en manque 2.

### 5.3 Séquences inédites et connues

| Métrique | Global | Inédites | Connues |
|---|---:|---:|---:|
| Blocs | 86 260 | 1 962 | 84 298 |
| Accuracy | 0.9986 | 0.9648 | 0.9994 |
| Précision anomalie | 0.9561 | 0.8898 | 0.9759 |
| Rappel anomalie | 0.9992 | 0.9963 | 1.0000 |
| Macro-F1 | 0.9882 | 0.9576 | 0.9937 |
| Faux positifs | 116 | 67 | 49 |
| Faux négatifs | 2 | 2 | 0 |

Les deux faux négatifs du test appartiennent aux séquences inédites.

## 6. Analyse des résultats

### 6.1 Points forts

- Macro-F1 de 0.9882 sur le test officiel.
- Rappel des anomalies de 0.9992.
- Seulement 2 anomalies manquées parmi 2 526.
- Performances proches entre validation et test.
- Modèle simple, rapide à entraîner et exécutable sur CPU.

### 6.2 Limites

- Le modèle génère 116 faux positifs sur le test.
- La précision diminue sur les séquences inédites (0.8898).
- Les deux faux négatifs concernent des séquences inédites.
- Le modèle exploite les comptages d'événements et non leur ordre temporel.
- Les résultats portent sur HDFS v1 et ne garantissent pas les mêmes performances sur d'autres systèmes.

### 6.3 Interprétation

La régression logistique est une baseline performante pour la détection d'anomalies HDFS.

Les résultats suggèrent que les comptages d'événements contiennent une information fortement discriminante.

Cependant, la baisse des performances sur les séquences inédites montre que la généralisation reste un point à surveiller.

## 7. Reproductibilité

### Fichiers

- `volet_a/training/baseline.py` : entraînement et évaluation
- `eval/metrics.py` : calcul des métriques
- `teamai/data/splits.py` : chargement des splits officiels
- `volet_a/results/SCRUM-24-baseline-results.json` : résultats enregistrés

### Commande d'exécution

Depuis la racine du dépôt :

```powershell
python -m volet_a.training.baseline
```

Le script charge les splits officiels, entraîne le modèle, effectue les évaluations et enregistre les résultats au format JSON.

## 8. Conclusion

La baseline de régression logistique atteint un Macro-F1 de **0.9882** sur le test officiel HDFS, avec un rappel des anomalies de **0.9992**.

Elle constitue une référence solide pour les prochaines expérimentations du volet A, notamment pour la comparaison avec le BiLSTM.

Les performances sur les séquences inédites devront être prises en compte dans cette comparaison.
