# SCRUM-44 — Evaluation finale du volet A

**Protocole :** C4-bloc, test officiel (campagne unique), contrats C3/C7.
**Seuil BiLSTM figé SCRUM-62 :** `0.40814146399497986`.
**Historique :** le fichier SCRUM-24-baseline-results.json contenait deja des resultats du test (commit b77b1a2, 12/10/2026). Ce precedent est declare et n'a pas servi au reglage de l'evaluation actuelle.

## Metriques

| Modele | Population | N | Precision anomalie | Rappel anomalie | Macro-F1 | TN | FP | FN | TP |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | test_complet | 86260 | 0.956061 | 0.999208 | 0.988227 | 83618 | 116 | 2 | 2524 |
| baseline | unseen_seq | 1962 | 0.889803 | 0.996317 | 0.957585 | 1352 | 67 | 2 | 541 |
| baseline | sans_3_blocs_exposes | 86257 | 0.956044 | 0.999208 | 0.988222 | 83616 | 116 | 2 | 2523 |
| bilstm_fp32 | test_complet | 86260 | 0.977528 | 0.998812 | 0.993846 | 83676 | 58 | 3 | 2523 |
| bilstm_fp32 | unseen_seq | 1962 | 0.926244 | 0.994475 | 0.971354 | 1376 | 43 | 3 | 540 |
| bilstm_fp32 | sans_3_blocs_exposes | 86257 | 0.977519 | 0.998812 | 0.993843 | 83674 | 58 | 3 | 2522 |
| bilstm_int8 | test_complet | 86260 | 0.977528 | 0.998812 | 0.993846 | 83676 | 58 | 3 | 2523 |
| bilstm_int8 | unseen_seq | 1962 | 0.926244 | 0.994475 | 0.971354 | 1376 | 43 | 3 | 540 |
| bilstm_int8 | sans_3_blocs_exposes | 86257 | 0.977519 | 0.998812 | 0.993843 | 83674 | 58 | 3 | 2522 |

## Artefacts C7

- `baseline` : `eval/runs/2026-11-12_230115_349899Z_e888b8e6_SCRUM-44_baseline` (`predictions.jsonl`, `metrics.json`, `config.json`).
- `bilstm_fp32` : `eval/runs/2026-11-12_230117_551947Z_a4c02b8c_SCRUM-44_bilstm_fp32` (`predictions.jsonl`, `metrics.json`, `config.json`).
- `bilstm_int8` : `eval/runs/2026-11-12_230118_952075Z_8af03c4e_SCRUM-44_bilstm_int8` (`predictions.jsonl`, `metrics.json`, `config.json`).

## Performance CPU (ONNX Runtime Python)

- FP32 : {'seconds_inference': 1.910527699998056, 'blocks_per_second': 45149.82954713913, 'batch_size': 512}
- INT8 : {'seconds_inference': 1.7848188999996637, 'blocks_per_second': 48329.833351728994, 'batch_size': 512}

## Parite navigateur et performance web - TERMINEE

Parite test officiel : 86 260 blocs compares avec les scores Python sauvegardes, sans rouvrir le test.

| Mesure | BiLSTM FP32 | BiLSTM INT8 |
|---|---:|---:|
| Blocs compares | 86260 | 86260 |
| Decisions divergentes Python / Chrome | 0 | 0 |
| Ecart maximal des scores | 2.38419e-7 | 0.00414035 |
| Ecart moyen des scores | 2.68815e-8 | 1.93924e-6 |
| Ecarts superieurs a 1e-4 | 0 | 216 |
| Scores non finis | 0 | 0 |
| Debit Chrome WASM, blocs/s | 6198.58 | 3004.27 |
| Taille du modele, octets | 56806 | 22570 |

La parite decisionnelle Python / Chrome est de 100 % sur cette campagne.
La parite numerique stricte a 1e-4 n'est pas atteinte pour INT8.

Les debits Chrome comprennent la boucle JavaScript de traitement.
Sur un benchmark distinct sous Node.js WASM, les debits observes
etaient de 7770.86 blocs/s (FP32) et 12727.07 blocs/s (INT8).
Ces deux protocoles ne doivent pas etre confondus.

Mesures ponctuelles Chrome sur localhost :
- FP32 : chargement reseau 7.30 ms ; lecture Cache Storage 2.60 ms.
- INT8 : chargement reseau 9.30 ms ; lecture Cache Storage 1.00 ms.

Ces temps n'incluent pas la creation de session ONNX Runtime.
Ils ne constituent pas des benchmarks reproductibles de bout en bout.

## Analyse commentee de 10 erreurs

Selection : 3 faux negatifs et 7 faux positifs du BiLSTM FP32.
Seuil fige : 0.40814146399497986.
Les commentaires sont bases sur les 50 premiers EventId encodes et
les scores sauvegardes. Les logs bruts n'ont pas encore ete examines.

1. **FN - blk_-1791865405548036877** - Score 0.071263.
   Sequence inedite de 15 evenements. Repetitions de E5, E11,
   E9 et E26 (trois occurrences chacun). Anomalie reelle classee
   normale avec un score nettement sous le seuil. La sequence
   partage des motifs avec d'autres cas ; ces seuls motifs ne
   permettent pas d'expliquer la cause de l'erreur.

2. **FN - blk_-6087083534651006725** - Score 0.243681.
   Sequence inedite de 28 evenements. E26 apparait six fois,
   E5 cinq fois et les couples E16/E6 se repetent. Le modele
   manque cette anomalie malgre ces repetitions. Une comparaison
   avec des sequences normales proches serait necessaire pour
   caracteriser la confusion.

3. **FN - blk_-8738042664044254309** - Score 0.135839.
   Sequence inedite de 29 evenements. E26 apparait sept fois,
   E5 cinq fois, avec repetitions de E3 absentes mais de E6/E16
   presentes. Son organisation ressemble en partie au FN n° 2.
   Le motif commun est une observation, pas une cause demontree.

4. **FP - blk_-124688922795231579** - Score 0.998606.
   Sequence inedite normale de 31 evenements. Elle contient
   notamment E2, E3, E4 et trois E23 successifs, suivis
   d'evenements E21. Le modele attribue un score d'anomalie
   tres eleve a ce bloc pourtant normal.

5. **FP - blk_-2447005583092276996** - Score 0.996390.
   Sequence connue de 34 evenements, seul cas non inedit de
   cette selection. Quatre occurrences chacune de E2, E23,
   E21 et E26. Ce faux positif montre que les erreurs ne se
   limitent pas aux sequences absentes de l'entrainement.

6. **FP - blk_-2908465845659009905** - Score 0.995094.
   Sequence inedite de 34 evenements. Repetitions de E2,
   E23 et E21, proches du cas n° 5 avec un ordre different.
   La forte confiance incorrecte merite une comparaison
   avec les sequences normales et anormales similaires.

7. **FP - blk_-3379001534066811520** - Score 0.999451.
   Sequence inedite de 28 evenements. E23 est repete trois
   fois, E21 quatre fois, et la sequence contient E3/E4.
   Le score tres eleve signale une fausse alerte de forte
   confiance, sans qu'une panne puisse etre deduite.

8. **FP - blk_-3548550939092147723** - Score 0.997348.
   Sequence inedite de 33 evenements. Trois E2, quatre E23,
   quatre E21 et deux E4. Plusieurs motifs sont communs
   aux faux positifs n° 5 et n° 6, mais leur relation
   causale avec la prediction reste a verifier.

9. **FP - blk_-3907603481176056256** - Score 0.903189.
   Sequence inedite dont les 50 positions conservees
   comprennent 28 occurrences de E3. Cette repetition
   domine l'entree du modele. Comme le BiLSTM conserve
   au maximum 50 evenements, une troncature eventuelle
   doit etre verifiee sur la trace originale.

10. **FP - blk_-4767450795485027771** - Score 0.999522.
    Sequence inedite de 28 evenements. E5, E26 et E21
    apparaissent quatre fois chacun, E23 trois fois.
    Forte confiance incorrecte avec une fin comportant
    E23/E21 repetes. Ce motif ressemble a plusieurs
    autres faux positifs selectionnes.

**Synthese :** les trois FN et six des sept FP selectionnes
concernent des sequences inedites. Plusieurs FP partagent
des motifs repetitifs E2/E23/E21, tandis que les FN montrent
des repetitions E5/E11/E9/E26. Ces ressemblances sont
des pistes d'analyse, pas des causes etablies.

Aucune modification du modele ni du seuil n'a ete effectuee
apres l'ouverture du test officiel.

## Provenance et limitations

- Empreinte FP32 : `ab98e8c45ef398c5c2ad13e05503fd94c5f13453daedda32d61c3ae43611a5ad`.
- Empreinte des splits : `f504592cb7ac13b8b7e5d532a336b4e3641ec441a863c5efafd164faa2a43f22`.
- Les trois blocs exposes historiquement ont ete exclus uniquement de la population `sans_3_blocs_exposes`.
- L'etape navigateur et la revue Bachar restent indispensables avant de considerer SCRUM-44 termine.

