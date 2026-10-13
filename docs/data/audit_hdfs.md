## Splits — SCRUM-20

### Protocole

Les 575 061 blocs HDFS_v1 sont répartis en trois ensembles, avec une stratification selon le label et une seed fixe de 42.

- Train : 70 %
- Validation : 15 %
- Test : 15 %

Le découpage est effectué par BlockId, sans chevauchement entre les ensembles.

### Résultats

| Ensemble | Blocs | Anomalies | Taux |
|---|---:|---:|---:|
| Train | 402 542 | 11 787 | 2,93 % |
| Validation | 86 259 | 2 525 | 2,93 % |
| Test | 86 260 | 2 526 | 2,93 % |

### Séquences inédites

Le dataset contient de nombreuses séquences d'événements répétées. Un découpage par bloc peut donc placer des séquences identiques dans le train et le test.

La colonne `unseen_seq` identifie les blocs du test dont la séquence complète d'EventId est absente de l'entraînement.

Résultat : 1 962 blocs du test présentent une séquence inédite, soit 2,27 % du test.

Les performances des modèles devront être rapportées à la fois sur le test complet et sur le sous-ensemble `unseen_seq=True`.

### Reproductibilité

- Seed : 42
- Méthode : découpage aléatoire stratifié par label, au niveau BlockId
- Sous-échantillonnage des normaux : aucun
- Distribution réelle des classes conservée dans les trois ensembles
- Génération : `python data/make_splits.py`
- Chargement : `teamai.data.splits.load_split(name)`
- Métadonnées : `data/splits/splits_meta.json`
- Hash SHA-256 : `f504592cb7ac13b8b7e5d532a336b4e3641ec441a863c5efafd164faa2a43f22`

Le fichier `splits.csv` est régénérable et n'est pas versionné dans Git.