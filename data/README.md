# data/ — Corpus HDFS_v1

**Responsable** : Nassim · **Binôme** : Bachar · **Epic** : SCRUM-6

```
data/
├── download_hdfs.py   Téléchargement + vérification MD5 (reprise automatique)       ✅
├── make_sample.py     Échantillon partagé ~2 000 blocs + lignes brutes              SCRUM-18
├── parse_hdfs.py      Lignes brutes → EventId (29 regex) validé contre Loghub        SCRUM-19
├── make_splits.py     Splits train/val/test par bloc + drapeau « séquence inédite »  SCRUM-20
├── raw/               HDFS_v1 complet (1,5 Go)                         — non versionné
├── sample/            Event_traces.csv + HDFS_sample.log réduits       — versionné
└── splits/            splits.csv (non versionné) + splits_meta.json    — versionné
```

## Utilisation

```bash
python data/download_hdfs.py          # → data/raw/HDFS_v1/
python -m teamai.data.loader          # statistiques de contrôle
```

En Python, ne jamais lire les CSV directement : passer par `teamai.data.loader` (format C1 de `docs/contrats.md`).

## Fichiers Loghub (`raw/HDFS_v1/`)

| Fichier | Contenu | Utilisé par |
|---|---|---|
| `HDFS.log` | 11 M lignes brutes | parser, exemples du site, volet B |
| `preprocessed/Event_traces.csv` | Séquence d'EventId par bloc + label + type | BiLSTM, splits, volet B |
| `preprocessed/Event_occurrence_matrix.csv` | Comptages d'événements par bloc | baseline |
| `preprocessed/HDFS.log_templates.csv` | 29 templates E1…E29 | vocabulaire, parser |
| `preprocessed/anomaly_label.csv` | BlockId → Normal / Anomaly | contrôle de cohérence |

## Points d'attention

- **Fuite train/test** : 575 061 blocs mais 18 373 séquences uniques. Toujours rapporter les scores aussi sur les séquences inédites (C4).
- Déséquilibre : 2,93 % d'anomalies → macro-F1 et rappel de la classe anomalie, jamais l'accuracy seule.
