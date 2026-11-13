# SCRUM-58 — porte Laya (abstention et vérification des hypothèses)

Expérience optionnelle, menée le 13/11/2026 sur la **validation uniquement**. Aucune donnée de test n'a été lue.

## Protocole

- Modèle : `convaiinnovations/laya`, licence Apache 2.0, révision `85cc74ddae6109077ebe2853a9b3077fb6606a78`, paquet `laya` 0.4.31, sous `laya.Router`. La révision est transmise au routeur ; la révision effectivement chargée n'est pas vérifiée (`loaded_revision_verified: false`).
- Entrées : réponses finales v16 de Gemma 4 E4B QAT (SCRUM-63) déjà produites sur la validation. Il y a deux cohortes de 40 blocs `val` : la mise au point v16 et la validation unique. Chacune compte 10 blocs `Fail` et 30 blocs `Success`. Laya reçoit la séquence de templates HDFS (codes et texte du template, répétitions regroupées), jamais les logs bruts ni le label.
- Machine : portable d'Alain, i5-1240P, CPU seul, Windows 11, Python 3.12.10, torch 2.12.0+cpu, transformers 5.22.2 (venv isolé).
- Porte (`volet_b/agents/laya_gate.py`) : un appel par bloc. Si la probabilité d'anomalie est dans [0,35 ; 0,65], la porte force l'abstention et déplace les hypothèses dans `infos_manquantes`. Sinon, une hypothèse dont la probabilité d'être appuyée est inférieure à 0,5 est déplacée. La sortie reste conforme à C5.
- Réglage : la question est choisie sur la cohorte de mise au point seulement (runs 1 à 3). Elle est ensuite appliquée **une seule fois** à la validation unique (run 4), sans aucun ajustement après lecture.

## Résultats

| Run | Cohorte | Variante | AUC Fail/Success | Abstentions ajoutées | Hypothèses avant → après | Latence moy. / p95 | Pic RSS | Chargement |
|---|---|---|---|---|---|---|---|---|
| 1 | mise au point | question initiale, anglais | 0,3667 | 7/40 | 3 → 1 | 2,24 s / 3,68 s | 2,69 GiB | 57,0 s |
| 2 | mise au point | question A, anglais | 0,5500 | 5/40 | 3 → 2 | 2,26 s / 3,29 s | 2,70 GiB | 33,4 s |
| 3 | mise au point | question initiale, multilingue | 0,5333 | 2/40 | 3 → 3 | 0,71 s / 1,22 s | 2,22 GiB | 47,7 s |
| 4 | **validation unique** | **question A, anglais** | **0,4700** | **8/40** | 4 → 3 | 2,25 s / 3,98 s | 2,65 GiB | 32,1 s |

Sources : `*/metrics.json` (`anomaly_auc_fail_vs_success`, `abstentions_after`, `hypotheses_before`, `hypotheses_after`, `latency_mean_seconds`, `latency_p95_seconds`, `peak_rss_bytes`, `load_seconds`). L'AUC est calculée à partir de `per_block`. La latence porte sur un appel groupé par bloc, après chargement et échauffement. Le pic RSS est échantillonné toutes les 0,02 s et inclut le chargement.

Vérification des hypothèses (run 4) : la validation unique ne contient que 4 hypothèses. La relecture humaine de SCRUM-63 (`eval/results/SCRUM-63/revue_qualitative_validation.json`) signale 2 des cas qui en portent : le cas 1 (lien à nuancer) et le cas 13 (chronologie et causalité erronées). Laya garde ces deux hypothèses (p = 0,89 et 0,87). Il déplace la seule hypothèse d'un cas que la relecture ne met pas en cause (cas 16, p = 0,29). L'effectif est trop faible pour un taux, mais aucun bénéfice n'est observé.

## Décision

**Porte non intégrée** : elle n'est pas proposée comme 5ᵉ configuration de SCRUM-45. En zéro-shot, la probabilité d'anomalie de Laya ne sépare pas les blocs `Fail` des blocs `Success` : l'AUC vaut 0,47 sur la validation unique, soit le niveau du hasard. Les abstentions ajoutées ne suivent donc pas le label. Le coût ajouté serait d'environ 2,3 s par bloc et 2,7 GiB de RSS sur CPU.

L'adaptation de Laya sur Kaggle (option du ticket) n'est pas lancée. Supervisée par les labels d'anomalie, elle ferait de Laya un second détecteur binaire, rôle déjà tenu par le volet A, ce qui sort du périmètre de la porte. Supervisée par les annotations du volet B, elle demanderait un jeu relu qui n'existe pas encore (SCRUM-36). Le code reste disponible et testé (`tests/test_laya_gate.py`) pour une reprise éventuelle.
