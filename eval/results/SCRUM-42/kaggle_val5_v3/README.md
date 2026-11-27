# SCRUM-42 — troisième mesure à 3 agents, après les correctifs de la PR #67

Run du 24/11/2026 sur Kaggle (Tesla T4 15 Go, Python 3.13), lancé par Claude à la demande d'Alain. Le code est celui du commit `2be514d` de la PR #67, sans modification. Il contient les quatre correctifs : reprise déclenchée par le code sur le drapeau d'ordre v16, motifs du contrôleur jusqu'à 400 caractères, règles hors contrat retirées de `checker.txt`, consigne de citation des passages dans `writer.txt`. Même modèle, même wheel, même index RAG que `../kaggle_val5/` et `../kaggle_val5_v2/` ; dépôt cloné sans trace de test.

Deux cohortes `val`, traitées l'une après l'autre dans la même session :
- **`seed7/`** : 5 blocs `val` jamais utilisés pour le réglage, tirés comme `--split val --n 5 --seed 7` avec le `splits.csv` officiel (`blk_-4732326805048063705`, `blk_3036603747764053369`, `blk_8342213972413455107`, `blk_-2762091965675374009`, `blk_6080543005931752460`). Seules leurs lignes sont envoyées, en extrait vérifié par SHA-256.
- **`reglage/`** : les 5 blocs des runs 1 et 2, pour comparer.

Le script est dans `kaggle_script.py.txt` (lien signé de la wheel retiré) et le journal de la session dans `journal.txt`. `config.json` n'est archivé que pour `seed7/` ; celui de `reglage/` ne diffère que par le fichier d'entrée.

## Résultats (`*/metrics.json`, `*/predictions.jsonl`)

| Mesure | Run 2 (`9712718`), 5 blocs de réglage | Run 3, mêmes 5 blocs | Run 3, 5 nouveaux blocs (seed 7) |
|---|---|---|---|
| Statuts | 1 `accepte`, 4 `rejete` | 5 `rejete` | 5 `rejete` |
| Réponses conformes à C5 (contrôles code) | 5/5 | 5/5 | 5/5 |
| Appels SLM par bloc | 5,0 en moyenne | 4,8 en moyenne | 5,0 en moyenne |
| Réponses finales citant un passage | non relevé ; 0 réponse acceptée | 1/5 | 2/5 |
| Motifs du contrôleur | 17, dont 7 coupés à 240 caractères | 14, aucun coupé (max. 265) | 17, aucun coupé (max. 287) |
| Reprises déclenchées par le drapeau d'ordre | sans objet | 1 | 0 |
| Génération SLM | 432,2 s | 427,1 s | 469,3 s |

## Lecture

- **Les correctifs agissent comme prévu.** Les motifs sont complets (4 dépassent l'ancienne limite de 240 caractères). Des passages sont cités dans 3 réponses finales sur 10. Le drapeau d'ordre a déclenché une reprise sans appel au contrôleur (`blk_-4683813028403463392`).
- **Mais aucune réponse n'est acceptée.** Le bloc accepté aux runs 1 et 2 (`blk_5458156658233261729`) est rejeté. Le dernier motif porte sur invalidSet, que la réponse finale ne mentionne pas.
- **Des rejets non fondés.** Sur `blk_3036603747764053369`, la réponse finale n'affirme aucun ordre (« incluant l'allocation … et le début d'écriture ») ; le contrôleur exige qu'elle mentionne l'incertitude d'ordre, ce que le contrat ne demande pas. D'autres motifs portent sur un singulier ou un pluriel, ou sur des faits absents de la réponse.
- **Des ordres affirmés non détectés.** Sur `blk_7069523072054316608`, la réponse finale dit « a débuté par l'allocation du bloc … suivi par des événements d'écriture » ; le drapeau v16 ne se déclenche pas, et le contrôleur reproche à la place un nombre d'occurrences.

## Conclusion

La chaîne reste stable et conforme au contrat (10/10), mais le contrôleur SLM devient le goulot : il rejette aussi des réponses sans erreur visible, et il manque des ordres affirmés. Aucun réglage supplémentaire n'est fait avant la soutenance du 30/11. Pistes :
1. élargir le contrôle d'ordre par le code aux tournures « débute par », « suivi par », « puis » ;
2. limiter le contrôleur à une liste fermée de défauts vérifiables, chacun avec sa référence ;
3. en démonstration, montrer la réponse du rédacteur avec les motifs du contrôleur comme avertissements plutôt que comme refus.

Ces 10 blocs ne mesurent pas la qualité des explications ; la mesure revient à SCRUM-45.
