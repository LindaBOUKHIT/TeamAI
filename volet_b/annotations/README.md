# volet_b/annotations — Exemples d'explication (contrat C5)

Uniquement des traces issues de **train/val** HDFS. Le jeu de test réservé vit dans `eval/volet_b/` et n'est jamais copié ici.

| Fichier | Contenu | Ticket |
|---|---|---|
| `calibration.jsonl` | 3 exemples rédigés ensemble pour calibrer l'équipe | SCRUM-31 |
| `seed_alain.jsonl` | ~20 exemples provisoires pour l'essai LoRA | SCRUM-29 |
| `brouillons/lot_<prénom>.jsonl` | 4 lots corrigés de 60 exemples (50 train, 10 val), source de train/val | SCRUM-36 |
| `train.jsonl` / `val.jsonl` | Jeu d'adaptation final : 200 exemples train, 40 val | SCRUM-36 |

Pour chaque exemple : `annotator` et `reviewed_by` renseignés. Si un exemple est pré-généré par un modèle, l'indiquer dans le journal IA et noter le taux de correction humaine ici.

Exception provisoire SCRUM-29 (27/10/2026) : `seed_alain.jsonl` contient vingt
brouillons v16 produits par règles, uniquement train. `reviewed_by` est vide :
Linda doit refaire la relecture, celle de l'ancien format ne s'applique plus.
Ces brouillons passent les contrôles v16 ; ils ne sont pas des annotations C5
relues. Voir [l'essai Gemma](../slm/README.md#essai-lora-scrum-29-gemma-4-e4b-qat).

## Jeu d'adaptation SCRUM-36

`train.jsonl` contient les 200 exemples `split == "train"` des quatre lots et
`val.jsonl` les 40 exemples `split == "val"`. Les deux fichiers sont triés par
`id`, en UTF-8 avec fins de ligne LF, une ligne JSON par exemple.
`python -m volet_b.slm.merge_lots` les régénère à l'identique depuis les lots ;
`--check` vérifie qu'ils sont à jour. La fusion refuse tout doublon et tout bloc
du split test de `data/splits/splits.csv` ou `data/sample/splits.csv`.
`prepare_examples` applique les contrôles v16 à chaque fichier : split train
dans l'annotation et dans C4 pour `train.jsonl`, split val pour `val.jsonl`.

| Lot | Train / val | `annotator` | `reviewed_by` | Exemples modifiés | Taux de correction | Relecture croisée |
|---|---|---|---|---|---|---|
| linda | 50 / 10 | linda | alain | 16 | 26,7 % | faite (Alain) |
| alain | 50 / 10 | alain | vide | 18 | 30,0 % | non faite |
| bachar | 50 / 10 | alain | vide | 10 | 16,7 % | non faite |
| nassim | 50 / 10 | alain | vide | 60 | 100 % | non faite |
| Total | 200 / 40 | | | 104 | 43,3 % | 60 exemples sur 240 |

Taux de correction humaine = exemples dont `expected` diffère du brouillon / 60.

- linda : 4 corrections de Linda (`brouillons/corrections_linda.jsonl`) et 13 de
  la relecture d'Alain (`brouillons/relecture_linda.md`) ; linda-008 figure dans
  les deux. Les autres écarts avec le brouillon ne changent que l'ordre de
  `faits_observes`.
- alain, bachar, nassim : vérification ciblée par Alain contre `trace_lines`,
  sur les défauts relevés dans le lot de Linda. Corrections de fond : 9 pour
  alain, 10 pour bachar, 6 pour nassim. Elles visent des destinataires
  différents présentés comme un seul client (alain 007, 008, 014, 020, 021, 026,
  053 ; bachar 008, 014, 017, 020, 022, 049 ; nassim 007, 046), une présence ou
  un retrait antérieur supposé par « encore », « disparition » ou « retrait »
  (alain 001, 009 ; bachar 003, 005, 051 ; nassim 002, 003, 051) et un événement
  supposé côté émetteur (bachar 030 ; nassim 029).
- alain : 10 formulations négatives reprises sans changer le sens (003, 026,
  039, 040, 042, 043, 044, 047, 059, 060), car les alertes v16 qu'elles
  déclenchaient bloquent `prepare_examples` ; alain-026 compte aussi une
  correction de fond.
- nassim : dans les 60 réponses, les lettres accentuées de `resume_evenements`
  et `infos_manquantes` étaient remplacées par « ? » ; elles sont restaurées mot
  à mot, sans autre changement que les 6 corrections de fond.

Les lots alain, bachar et nassim n'ont pas eu de relecture croisée :
`reviewed_by` reste vide pour ces 180 exemples. `prepare_examples` et
`tests/test_fichiers_du_depot.py` tolèrent uniquement ce champ vide.
