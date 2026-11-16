# Guide d’annotation des explications HDFS

Ce guide définit comment rédiger et évaluer les explications de référence du volet B. Les exemples suivent le contrat C5 v1.1 de `docs/contrats.md` ; leur format est vérifié automatiquement par `teamai.contracts.validate_example()` (CI).

## 1. Règles avant d’annoter

- Utiliser uniquement une trace dont le split est `train` ou `val`. Ne jamais annoter ni copier une trace de `test` dans les fichiers d’entraînement ou de calibration.
- Lire les lignes brutes disponibles pour le bloc et vérifier les `events` correspondants. Ne pas déduire un événement absent de la trace.
- Le label HDFS (`0` = normal, `1` = anomalie, selon C1) sert à identifier l’exemple, mais ne constitue pas une preuve à citer dans l’explication.
- Distinguer ce que montrent les logs, ce que la documentation permet d’expliquer et ce qui reste inconnu.
- Chaque exemple est relu par une autre personne : `reviewed_by` est différent de `annotator`. Ces deux noms sont renseignés **après** le travail réel (rédaction, puis relecture), jamais à l'avance.
- `label`, `expected` et les annotations ne sont jamais transmis au modèle ni au retrieval : ils servent uniquement à l'adaptation et à l'évaluation.

## 2. Rédiger les champs `expected`

### `resume_evenements`

Résumer brièvement les événements du bloc dans leur ordre. Décrire les opérations et erreurs effectivement présentes dans la trace. Ne pas ajouter de cause qui n’est pas visible.

### `faits_observes`

Énoncer uniquement des faits directement vérifiables dans `trace_lines` ou `events` : opération, composant, identifiant ou erreur observée. Chaque fait doit pouvoir être relié à une ligne ou à un événement précis.

### `hypotheses`

Proposer seulement des explications plausibles, en indiquant clairement qu’il s’agit d’hypothèses (« pourrait indiquer », « compatible avec »). Une hypothèse ne devient pas un fait parce qu’elle semble probable ou parce que le label vaut `1` (anomalie).

### `infos_manquantes`

Nommer les éléments précis qu’il faudrait connaître pour confirmer ou écarter les hypothèses : par exemple, l’état d’un nœud, une mesure réseau ou un événement qui n’apparaît pas dans la trace. Si rien de pertinent ne manque, utiliser une liste vide.

### `sources`

- Les faits concernant le bloc sont justifiés par `trace_lines` et `events` ; ils ne nécessitent pas de citation documentaire.
- Citer un passage C6 lorsqu’une explication s’appuie sur le fonctionnement général de HDFS ou sur une règle documentaire.
- Citer les identifiants exacts des passages documentaires C6 qui étayent les explications.
- Vérifier que chaque identifiant existe dans le corpus et que le passage soutient réellement l’affirmation associée.
- Ne pas inventer d’identifiant, de titre de page ou de citation. Ne pas utiliser une source documentaire pour prétendre qu’un événement est présent dans les logs : les faits viennent de la trace.
- Si aucune explication documentaire n’est nécessaire, utiliser une liste vide. Si une explication en nécessite une mais qu’aucun passage pertinent n’est disponible, ne pas fabriquer de source ; décrire cette limite et s’abstenir si elle empêche une explication fiable.

### `abstention`

Mettre `true` lorsque la trace est trop incomplète, contradictoire ou ambiguë pour produire une explication fiable, ou lorsque l’explication demandée nécessiterait une information que ni les logs ni les sources ne fournissent. Dans ce cas, `hypotheses` est une **liste vide** et `infos_manquantes` contient **au moins un élément** qui explique la limite (règle C5 v1.1, vérifiée par la CI). `resume_evenements` et `faits_observes` restent remplis : s'abstenir porte sur l'interprétation, pas sur la description de la trace.

Mettre `false` lorsqu’une explication limitée mais utile peut être donnée à partir de faits vérifiés et de sources pertinentes. Une anomalie n’impose pas automatiquement une abstention, et un label normal n’autorise pas à ignorer les événements observés.

## 3. Grille de relecture humaine

Attribuer à chaque dimension un score de 0, 1 ou 2. Le total est sur 8 ; ce score sert à comparer et discuter les annotations, sans seuil automatique de validation.

| Dimension | 0 — Insuffisant | 1 — Partiel | 2 — Satisfaisant |
|---|---|---|---|
| Exactitude des faits | Fait central inventé ou contredit par la trace | Faits principaux justes, avec une imprécision ou une omission importante | Tous les faits sont traçables et formulés sans extrapolation |
| Appui sur les sources | Une source citée est invalide, contredit l’affirmation, ou une explication documentaire importante n’est pas étayée | Une source pertinente soutient une partie de l’explication, mais l’appui reste incomplet ou imprécis | Chaque affirmation documentaire est soutenue par un passage pertinent ; une liste vide est correcte si la réponse ne fait aucune affirmation documentaire |
| Abstention justifiée | Décision clairement inadaptée : affirmation hasardeuse malgré un manque majeur, ou abstention malgré des éléments suffisants | Cas limite ; la décision est défendable mais insuffisamment expliquée | La décision correspond aux preuves disponibles et ses limites sont explicites |
| Utilité | Réponse confuse, non pertinente ou inutilisable | Réponse compréhensible mais trop vague ou incomplète | Résumé clair, limites précises et explication utile pour comprendre la trace |

La relecture vérifie aussi que `block_id`, `split`, `trace_lines`, `events`, `label`, `expected`, `annotator` et `reviewed_by` respectent C5. Une erreur de format doit être corrigée, même si le contenu est bon.

## 4. Désaccords et calibration

Pour les trois exemples de `volet_b/annotations/calibration.jsonl`, les annotateurs rédigent ou relisent ensemble la réponse, puis notent les quatre dimensions. En cas de désaccord, revenir à la ligne brute ou au passage documentaire concerné, corriger l’exemple et noter la règle retenue dans le compte rendu d’équipe. Ne pas masquer un désaccord en transformant une hypothèse en fait.

Avant d’ajouter un exemple à `calibration.jsonl`, vérifier son split dans `data/splits/splits.csv` et vérifier chacun de ses identifiants de source dans `volet_b/rag/corpus/chunks.jsonl`. Ces deux contrôles, ainsi que le format C5, sont automatiques :

```bash
pytest tests/test_fichiers_du_depot.py -q
```

Les trois exemples de calibration portent sur des blocs du split `train` présents dans `data/sample/` : un bloc normal complet (`calib-0001`), une anomalie avec exception d'écriture (`calib-0002`) et une trace trop incomplète pour être interprétée (`calib-0003`, abstention). Ils sont proposés comme base de discussion ; `reviewed_by` est renseigné par le relecteur une fois sa relecture faite.
