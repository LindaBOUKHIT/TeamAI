# Formats d'échange entre les tâches

**Version proposée : v1, préparée le 08/10/2026 pour SCRUM-55. Validation du groupe en attente.** Les formats servent de base de travail avec des exemples factices. Ils seront figés après relecture des quatre membres et fusion de la PR vers `dev`. Aucune réunion de validation n'est attestée à ce jour.

Périmètre proposé : classification **binaire** pour le volet A ; `anomaly_type` reste une métadonnée du corpus. Les deux applications restent indépendantes. Un label d'anomalie ne fournit pas une cause de panne.

Conventions communes : fichiers UTF-8, JSON strict (`null`, jamais `NaN`), une ligne JSON par exemple dans les `.jsonl`, chemins relatifs à la racine du dépôt. Les exemples ci-dessous illustrent les structures ; ils ne constituent pas des annotations validées ni des résultats d'évaluation.

Toute modification d'un format passe par une PR identifiant les producteurs et consommateurs concernés. Avant fusion, le groupe vérifie les effets sur les deux implémentations et leurs exemples.

## C1 — Trace HDFS (données → tout le monde)

Source : `data/raw/HDFS_v1/preprocessed/Event_traces.csv` (Loghub), chargée par `teamai.data.loader.load_traces()`.

| Champ | Type | Exemple |
|---|---|---|
| `BlockId` | str | `blk_-1608999687919862906` |
| `label` | int | `0` normal, `1` anomalie (`Fail` dans Loghub) |
| `anomaly_type` | float / NaN | type d'anomalie Loghub (renseigné seulement si `label = 1`) |
| `events` | list[str] | `["E5", "E22", "E5", "E11", …]` dans l'ordre chronologique |

`BlockId` doit être non vide et unique dans le fichier de traces. Les lignes brutes d'un bloc conservent leur ordre dans le fichier source. Le format complet C1 est conservé ; la troncature intervient uniquement lors de l'encodage C2. Dans un export JSON, une valeur `anomaly_type` manquante devient `null`.

Chiffres du relevé du 06/10, à confirmer par l'audit de Nassim : 575 061 blocs, 16 838 anomalies (2,93 %), 18 373 séquences uniques, longueur médiane 19, p99 33, max 298. Une longueur maximale de 50 est proposée ; la proportion réellement tronquée doit être mesurée sur le split utilisé.

## C2 — Vocabulaire (données → volet A Python et JavaScript)

Fichier : `volet_a/web/public/vocab.json`, produit par SCRUM-19.

```json
{
  "contract_version": "v1",
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
- Les `regex` de l'exemple sont des placeholders : le producteur fournit les expressions réelles et les cas de parité. Elles doivent être compatibles avec les deux moteurs ; leur ordre de priorité est l'ordre numérique des EventId. Une ligne sans correspondance reçoit `unk_id` et est comptée comme inconnue.
- Encodage : garder les **50 premiers événements**, puis compléter à droite avec `pad_id` ; ne jamais trier ni dédupliquer la séquence. Signaler le nombre d'événements tronqués et inconnus dans l'interface.
- Une trace vide est rejetée avec un message explicite ; elle ne doit pas être classée comme un bloc normal. Les longueurs supérieures à 50 restent acceptées, avec avertissement de troncature.

**État du code au 08/10 :** `teamai.data.loader.encode()` réalise déjà la troncature et le padding, mais lève une erreur sur un événement inconnu. La gestion de `unk_id`, l'export de `vocab.json` et les cas de parité restent à livrer dans SCRUM-19/26 ; ce document décrit leur interface attendue.

## C3 — Modèle ONNX du volet A (entraînement → site)

Fichier : `volet_a/web/public/model/detector.onnx` (+ `detector.meta.json`).

| | Nom | Type | Forme |
|---|---|---|---|
| Entrée | `event_ids` | int64 | `[batch, 50]` (indices C2, padding à droite) |
| Sortie | `p_anomaly` | float32 | `[batch]` probabilité d'anomalie (sigmoïde appliquée dans le modèle) |

Exemple de `detector.meta.json` :

```json
{
  "contract_version": "v1",
  "model": "bilstm",
  "version": "v1",
  "threshold": 0.5,
  "max_len": 50,
  "pad_id": 0,
  "unk_id": 30,
  "vocab_sha256": "SHA256_A_RENSEIGNER",
  "model_sha256": "SHA256_A_RENSEIGNER",
  "splits_sha256": "SHA256_A_RENSEIGNER",
  "val_macro_f1": null
}
```

Les valeurs de l'exemple ne sont pas des mesures. Avant publication, les hashes réels et la macro-F1 de validation sont renseignés. Le seuil est choisi sur la validation, jamais sur le test, puis utilisé à l'identique : `p_anomaly >= threshold` donne le label `1`.

L'interface vérifie les noms, types et dimensions, la cohérence du vocabulaire et une probabilité finie comprise entre 0 et 1. Une sortie invalide devient une erreur affichée, sans prédiction de remplacement. Les scores ne sont pas présentés comme des probabilités calibrées. La parité Python/ONNX/JavaScript est vérifiée avant déploiement (SCRUM-22/26).

## C4 — Splits (données → entraînement et évaluation)

`data/splits/splits.csv` (non versionné, à produire par `data/make_splits.py` dans SCRUM-20) : colonnes `BlockId,split,unseen_seq`, avec `split ∈ {train, val, test}`. `unseen_seq` est un booléen CSV `true`/`false` : pour un bloc de test, il indique que sa séquence complète n'apparaît pas dans train ; pour les autres splits, il vaut `false` par convention.

Un bloc appartient à un seul split. Les séquences complètes identiques sont regroupées pour éviter une fuite entre splits dans le protocole officiel ; si un split provisoire est utilisé, il est nommé et rapporté séparément. L'encodage tronqué ne sert pas à décider de ces groupes. Aucun seuil ni prompt n'est ajusté sur le test.

`data/splits/splits_meta.json` (versionné) contient la seed, la méthode de regroupement, les effectifs et proportions d'anomalies par split, les SHA-256 des fichiers source et de `splits.csv`, ainsi que le commit du script. Les proportions attendues et la seed sont fixées dans SCRUM-20. Les hashes portent sur les octets des fichiers produits, sans réécriture ultérieure.

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

- `id` est unique ; `block_id` renvoie à C1 ; les valeurs de `split` sont `train`, `val`, `test`. Les exemples d'adaptation excluent le test.
- `trace_lines` et `events` décrivent le même bloc. Les résumés et hypothèses sont vérifiés par l'annotateur puis par le relecteur ; leurs noms sont renseignés après leur travail réel.
- Les six clés de `expected` sont obligatoires : une chaîne, quatre listes de chaînes et un booléen. Des listes vides sont autorisées. Une hypothèse doit rester distincte d'un fait observé ; en cas d'abstention, `hypotheses` est vide et `infos_manquantes` explique pourquoi.
- **À l'évaluation, ni `label`, ni `expected`, ni les annotations ne sont transmis au SLM ou au retrieval.** L'entrée du modèle contient seulement les traces, la consigne et, selon la configuration, les passages C6.
- La génération est du texte brut : du JSON invalide, une clé manquante ou une référence absente du corpus sont enregistrés comme erreurs. Aucune réparation silencieuse par les réponses attendues.

Interface SLM prévue dans SCRUM-28, déjà disponible sur sa branche :

```python
from volet_b.slm.generate import generate

result = generate([{"role": "user", "content": "Consigne puis trace HDFS"}])
# result : {"text": str, "new_tokens": int, "seconds": float}
```

`text` doit être analysé et vérifié par l'orchestrateur avant d'être affiché comme réponse structurée. Le mode `TEAMAI_SLM_MOCK=1` permet de développer les consommateurs sans poids de modèle ; ses résultats sont identifiés comme factices et exclus des évaluations de qualité. Le backend GGUF de SCRUM-57 n'est pas encore intégré à cette interface au 08/10.

## C6 — Passage documentaire RAG (corpus → retrieval → agents)

`volet_b/rag/corpus/chunks.jsonl` :

```json
{"id": "hdfs-design#data-replication#2", "doc": "HDFS Architecture", "section": "Data Replication", "text": "…", "source_url": "https://hadoop.apache.org/docs/r…", "version": "r2.x"}
```

L'`id` est stable : il est cité dans les réponses (C5 `sources`) et vérifié par code.

Chaque passage comporte les six champs de l'exemple ; les IDs sont uniques. Un passage révisé conserve la provenance et sa version documentaire ; un changement de découpage doit être tracé et le corpus réindexé. La méthode d'attribution des IDs est fixée par Linda dans SCRUM-30, avant annotation et entraînement.

Interface de retrieval proposée : pour une requête et un `top_k`, retourner une liste ordonnée de passages C6, enrichis d'un `score` numérique. Une liste vide est un résultat valide : elle déclenche une abstention si la réponse demande un appui documentaire. Le score de retrieval n'est pas un score de certitude sur l'explication. Les seuls IDs utilisables pour les citations sont ceux des passages fournis au modèle.

## C7 — Résultat d'une exécution d'évaluation

`eval/runs/<date>_<config>/` (non versionné) : `predictions.jsonl`, `metrics.json`, `config.json` (modèle, adaptateur, paramètres de génération, commit Git). Le résumé chiffré va dans `eval/results/` (versionné).

Les IDs de `predictions.jsonl` correspondent au jeu évalué. Chaque ligne conserve la sortie brute, la réponse analysée ou `null`, les erreurs de format/citation et les mesures ; un échec ne disparaît pas du dénominateur.

```json
{
  "id": "ex-factice-0001",
  "raw_text": "Réponse non structurée",
  "parsed_response": null,
  "errors": ["invalid_json"],
  "new_tokens": 0,
  "seconds": 0.0,
  "mock": true
}
```

`config.json` conserve aussi le split et son hash, la version du corpus RAG, le backend et la quantification, la seed, le nombre d'agents, les limites d'appels, la machine et la définition du chronométrage (chargement/prompt/génération). `metrics.json` précise les effectifs, les échecs, les unités et le protocole. Une valeur non mesurée vaut `null`, jamais zéro par défaut. La mémoire est accompagnée de la méthode et du périmètre mesuré (processus, machine ou GPU).

## Relecture et clôture de SCRUM-55

| Point à valider | Producteur principal | Consommateurs / relecture |
|---|---|---|
| C1, C2, C4 : données, vocabulaire, splits | Nassim | Bachar, Linda, Alain |
| C3 : modèle exporté et métadonnées | Bachar | Nassim, Linda |
| C5 : annotations et sortie structurée ; interface SLM | Tous pour les annotations ; Alain pour le SLM | Linda, Nassim |
| C6 : corpus et retrieval | Linda | Alain, Nassim |
| C7 : traces et résultats d'évaluation | Nassim, avec chaque responsable de volet | Alain, Linda, Bachar |

Points proposés pour accord : binaire seul, séquence de 50 événements avec avertissement, séparation stricte des jeux, JSON et IDs de sources contrôlés, conservation des échecs. Chacun vérifie aussi ses entrées, ses sorties et ses échéances dans le sprint Jira.

Critère de fin : avis des quatre membres consignés, décisions reportées dans `docs/projet/journal.md`, puis PR fusionnée vers `dev`. L'état actuel est une préparation technique, pas une validation collective.
