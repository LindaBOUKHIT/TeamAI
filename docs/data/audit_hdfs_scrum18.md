# SCRUM-18 — Audit du dataset HDFS_v1

## 1. Objectif

Évaluer la qualité, la cohérence et les risques de fuite de données du corpus HDFS_v1 avant l'entraînement des modèles TeamAI.

## 2. Description du dataset

| Indicateur | Valeur |
|---|---:|
| Nombre total de blocs | 575 061 |
| Blocs normaux | 558 223 |
| Blocs anormaux | 16 838 (2,93 %) |
| Événements distincts | 29 |
| Séquences uniques | 18 373 |
| Longueur médiane | 19 |
| Longueur p99 | 33 |
| Longueur maximale | 298 |

Source : Loghub HDFS_v1, Zenodo, licence CC-BY-4.0.

## 3. Audit des doublons

| Indicateur | Résultat |
|---|---:|
| Séquences répétées | 7 409 |
| Blocs appartenant à des séquences répétées | 564 097 |
| Pourcentage de blocs concernés | 98,09 % |
| Occurrences supplémentaires | 556 688 |

### Doublons par classe

| Indicateur | Normal | Anomalie |
|---|---:|---:|
| Blocs | 558 223 | 16 838 |
| Séquences uniques | 14 259 | 4 124 |
| Séquences répétées | 6 491 | 915 |
| Blocs dans des séquences répétées | 550 455 | 13 629 |
| Occurrences supplémentaires | 543 964 | 12 714 |

Les doublons sont identifiés à partir des séquences complètes et ordonnées d'EventId.

## 4. Séquences avec labels contradictoires

- 10 séquences identiques présentent des labels différents.
- 46 blocs sont concernés.
- 24 blocs sont anormaux et 22 normaux.

Ces résultats indiquent une ambiguïté pour un modèle utilisant uniquement les EventId. Ils ne prouvent pas une erreur d'annotation.

## 5. Cohérence des fichiers CSV

Comparaison entre `anomaly_label.csv` et `Event_traces.csv` par `BlockId`.

| Contrôle | Résultat |
|---|---:|
| Blocs présents dans les deux fichiers | 575 061 |
| Identifiants dupliqués | 0 |
| Blocs manquants | 0 |
| Labels non reconnus | 0 |
| Désaccords de labels | 0 |

**Conclusion :** les identifiants et labels binaires sont cohérents entre les deux fichiers.

## 6. Distribution des types d'anomalies

Le dataset contient 26 types d'anomalies.

| Type | Nombre | Pourcentage |
|---|---:|---:|
| 5 | 4 167 | 24,75 % |
| 31 | 3 225 | 19,15 % |
| 3 | 2 950 | 17,52 % |
| 0 | 2 809 | 16,68 % |
| 4 | 1 240 | 7,36 % |
| 1 | 953 | 5,66 % |
| 21 | 724 | 4,30 % |
| 7 | 476 | 2,83 % |
| Autres types | 294 | 1,75 % |

Les quatre types dominants concentrent environ 78,10 % des anomalies.

Treize types possèdent moins de 10 exemples. Aucun bloc anormal ne possède un type manquant ; les 558 223 blocs normaux ont un type non renseigné.

## 7. Risques identifiés

**Fuite train/test :** 98,09 % des blocs appartiennent à des séquences répétées. Une séparation aléatoire par bloc peut produire des résultats trop optimistes.

**Ambiguïté des labels :** certaines séquences identiques sont associées à des labels différents.

**Déséquilibre :** les anomalies ne représentent que 2,93 % du corpus, et les types d'anomalies sont très inégalement répartis.

## 8. Recommandations

1. Pour SCRUM-20, prévoir une évaluation sur des séquences inédites et contrôler l'absence de chevauchement des séquences exactes entre entraînement et test.
2. Ne pas supprimer automatiquement les séquences contradictoires ; analyser leur contexte.
3. Utiliser macro-F1, précision, rappel et F1 de la classe anomalie, plutôt que l'accuracy seule.
4. Documenter les classes rares et les éventuelles classes absentes des splits multi-classes.
5. Conserver une évaluation sur la distribution naturelle des anomalies (2,93 %), indépendamment de l'échantillon enrichi de la PR 1.

## 9. Reproductibilité

Notebook : `notebooks/nassim_SCRUM-18_audit_hdfs.ipynb`

Chargement des données avec `teamai.data.loader.load_traces()`.

Les analyses sont réalisées sur les 575 061 blocs, sans suppression préalable des doublons.

## 10. Références

- Xu et al., SOSP 2009.
- Zhu et al., ISSRE 2023.
- Loghub HDFS_v1, Zenodo, CC-BY-4.0 — compléter avec le lien exact de l'archive utilisée.