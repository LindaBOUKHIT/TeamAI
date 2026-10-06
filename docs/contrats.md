# Formats d'échange entre les tâches

**Statut : brouillon à valider en réunion de lancement (SCRUM-55).** Tant qu'un format est figé ici, chacun peut travailler avec des données factices sans attendre les autres. Toute modification passe par une PR et une annonce à l'équipe.

## C1 — Trace HDFS (données → tout le monde)

Source : `data/raw/HDFS_v1/preprocessed/Event_traces.csv` (Loghub), chargée par `teamai.data.loader.load_traces()`.

| Champ | Type | Exemple |
|---|---|---|
| `BlockId` | str | `blk_-1608999687919862906` |
| `label` | int | `0` normal, `1` anomalie (`Fail` dans Loghub) |
| `anomaly_type` | float / NaN | type d'anomalie Loghub (renseigné seulement si `label = 1`) |
| `events` | list[str] | `["E5", "E22", "E5", "E11", …]` dans l'ordre chronologique |

Chiffres de référence : 575 061 blocs, 16 838 anomalies (2,93 %), 18 373 séquences uniques, longueur médiane 19, p99 33, max 298.

## C2 — Vocabulaire (données → volet A Python et JavaScript)

Fichier : `volet_a/web/public/vocab.json`, produit par SCRUM-19.

```json
{
  "pad_id": 0,
  "unk_id": 30,
  "max_len": 50,
  "events": {
    "E1": {"id": 1, "template": "[*]Adding an already existing block[*]", "regex": "…"},
    "E29": {"id": 29, "template": "[*]PendingReplicationMonitor timed out block[*]", "regex": "…"}
  }
}
```

- `id` = numéro de l'EventId (`E7` → 7) ; `0` = padding ; `30` = ligne ne correspondant à aucun template.
- `regex` : seule source de vérité du parsing, appliquée à l'identique en Python (SCRUM-19) et en JavaScript (SCRUM-26).

## C3 — Modèle ONNX du volet A (entraînement → site)

Fichier : `volet_a/web/public/model/detector.onnx` (+ `detector.meta.json`).

| | Nom | Type | Forme |
|---|---|---|---|
| Entrée | `event_ids` | int64 | `[batch, 50]` (indices C2, padding à droite) |
| Sortie | `p_anomaly` | float32 | `[batch]` probabilité d'anomalie (sigmoïde appliquée dans le modèle) |

`detector.meta.json` : `{"threshold": 0.5, "model": "bilstm", "version": "v1", "trained_on": "splits@<hash>", "val_macro_f1": …}`. Le seuil est choisi sur la validation, jamais sur le test.

## C4 — Splits (données → entraînement et évaluation)

`data/splits/splits.csv` (non versionné, régénéré par `data/make_splits.py`) : `BlockId, split` avec `split ∈ {train, val, test}` ; colonne `unseen_seq` (bool) pour les blocs du test dont la séquence n'apparaît pas dans train. `data/splits/splits_meta.json` (versionné) : seed, tailles, répartition, hash.

## C5 — Exemple d'explication (volet B : annotation, LoRA, évaluation)

Une ligne JSON par exemple dans `volet_b/annotations/*.jsonl` (et `eval/volet_b/test.jsonl`, réservé) :

```json
{
  "id": "ex-0001",
  "block_id": "blk_…",
  "split": "train",
  "trace_lines": ["081109 203518 143 INFO dfs.DataNode$DataXceiver: Receiving block blk_…", "…"],
  "events": ["E5", "E22", "E5"],
  "label": 1,
  "expected": {
    "resume_evenements": "Le bloc est alloué puis reçu par 3 DataNodes ; une exception survient lors de l'écriture vers le miroir…",
    "faits_observes": ["E12 : exception d'écriture vers le miroir", "…"],
    "hypotheses": ["Défaillance réseau ou DataNode miroir indisponible"],
    "infos_manquantes": ["État du DataNode miroir au moment de l'erreur"],
    "sources": ["hdfs-design#data-replication#2"],
    "abstention": false
  },
  "annotator": "linda",
  "reviewed_by": "alain"
}
```

La sortie du modèle (volet B) suit exactement le schéma de `expected`.

## C6 — Passage documentaire RAG (corpus → retrieval → agents)

`volet_b/rag/corpus/chunks.jsonl` :

```json
{"id": "hdfs-design#data-replication#2", "doc": "HDFS Architecture", "section": "Data Replication", "text": "…", "source_url": "https://hadoop.apache.org/docs/r…", "version": "r2.x"}
```

L'`id` est stable : il est cité dans les réponses (C5 `sources`) et vérifié par code.

## C7 — Résultat d'une exécution d'évaluation

`eval/runs/<date>_<config>/` (non versionné) : `predictions.jsonl`, `metrics.json`, `config.json` (modèle, adaptateur, paramètres de génération, commit Git). Le résumé chiffré va dans `eval/results/` (versionné).
