# volet_b/annotations — Exemples d'explication (contrat C5)

Uniquement des traces issues de **train/val** HDFS. Le jeu de test réservé vit dans `eval/volet_b/` et n'est jamais copié ici.

| Fichier | Contenu | Ticket |
|---|---|---|
| `calibration.jsonl` | 3 exemples rédigés ensemble pour calibrer l'équipe | SCRUM-31 |
| `seed_alain.jsonl` | ~20 exemples provisoires pour l'essai LoRA | SCRUM-29 |
| `lot_<prénom>.jsonl` | Lots annotés par chacun, avant relecture | SCRUM-36 |
| `train.jsonl` / `val.jsonl` | Jeu d'adaptation final, relu | SCRUM-36 |

Pour chaque exemple : `annotator` et `reviewed_by` renseignés. Si un exemple est pré-généré par un modèle, l'indiquer dans le journal IA et noter le taux de correction humaine ici.
