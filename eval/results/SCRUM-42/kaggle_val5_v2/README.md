# SCRUM-42 — deuxième mesure à 3 agents, après le correctif du contrôleur

Run du 16/11/2026 sur Kaggle (Tesla T4 15 Go, Python 3.13), lancé par Alain. Le code est celui du commit `9712718` de la PR #53, sans modification. Il contient le correctif du contrôleur (règles du contrat dans `checker.txt`, garde de contexte). Le protocole est identique à `../kaggle_val5/` :
- mêmes 5 blocs `val`, envoyés en extrait vérifié ;
- même modèle, même wheel, même index RAG ;
- dépôt cloné sans trace de test.

Le script est dans `kaggle_script.py.txt` ; son lien signé vers la wheel a été retiré.

## Résultats (`metrics.json`, `predictions.jsonl`)

| Mesure | Run 1 (`8f532e7`) | Run 2 (`9712718`) |
|---|---|---|
| Statuts | 1 `accepte`, 4 `rejete` | 1 `accepte`, 4 `rejete` |
| Réponses conformes à C5 (contrôles code) | 5/5 | 5/5 |
| Appels SLM par bloc | 4,6 en moyenne ; 4 reprises | 5,0 en moyenne ; 5 reprises |
| Réponses acceptées citant un passage | 0 | 0 |
| Génération SLM | 433,2 s, soit 86,6 s par bloc | 432,2 s, soit 86,4 s par bloc |
| Tokens de prompt | 1 226 à 2 814 | 1 226 à 2 814 ; 1 passage retiré par la garde de contexte |

Le bloc accepté est le même dans les deux runs (`blk_5458156658233261729`), après une reprise.

## Lecture des 17 motifs `corriger`

Le contrôleur demande une correction 9 fois sur 10 verdicts.

- **Le correctif a supprimé la principale cause hors contrat.** Aucun motif ne reproche des sources vides, contre 6 verdicts sur 8 au run 1.
- **Des motifs fondés.** Dans au moins 3 blocs, le rédacteur affirme un ordre (« a débuté par l'allocation… ») entre des événements de la même seconde, que [F12] ou la chronologie [Txx] donnent comme non ordonnés. Le contrôleur a raison. Le défaut vient du rédacteur, qui reprend la consigne v16 « dans leur ordre ».
- **De nouvelles exigences hors contrat.** Elles concernent 3 blocs :
  - le résumé devrait mentionner chaque fait sélectionné ;
  - le résumé ne devrait citer que des faits sélectionnés ;
  - « ne précise pas si… ».

  Le contrat ne contient aucune de ces règles. `checker.txt` dit que la sélection de faits n'a pas à être exhaustive, mais rien sur le lien entre le résumé et cette sélection.
- **7 motifs sur 17 sont coupés à 240 caractères.** La grammaire JSON (`maxLength: 240`) arrête la phrase avant ce qui est faux, par exemple « [F12] indique un ordre non déterminable au ». Dans un bloc, le modèle a réparti une même phrase sur 3 motifs. Le rédacteur reçoit donc des consignes de reprise incomplètes.

## Conclusion

La chaîne est stable, et le contrôleur ne bloque plus sur les sources. Les rejets restants mêlent de vraies erreurs d'ordre et des exigences hors contrat.

Pistes, à valider sur d'autres blocs `val` que ces 5, pour ne pas régler le contrôleur sur la cohorte qui le mesure :
1. motifs plus courts (par exemple 1 phrase, au plus 160 caractères) ou limite relevée ;
2. dans `checker.txt` : le résumé peut citer tout [Fxx] du bloc et n'a pas à reprendre chaque fait sélectionné ;
3. côté rédacteur : n'affirmer un ordre que s'il est établi par la chronologie.

Ces 5 blocs ne mesurent pas la qualité ; la mesure revient à SCRUM-45.
