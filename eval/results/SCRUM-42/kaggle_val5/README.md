# SCRUM-42 — mesure réelle à 3 agents sur 5 blocs de validation

Run du 16/11/2026 sur Kaggle (Tesla T4 15 Go, Python 3.13), lancé par Alain. Le code est celui du commit `8f532e7` de la PR #53, sans modification. Modèle Gemma 4 E4B QAT (`google/gemma-4-E4B-it-qat-q4_0-gguf`, révision `4b4a2c1d`), wheel llama.cpp 0.3.36 vérifiée par SHA-256. Index RAG reconstruit sur place (`BAAI/bge-small-en-v1.5@5c38ec7c`, 51 passages).

## Données

Il s'agit des 5 blocs `val` que choisit `--split val --n 5 --seed 42`. Seules leurs 104 lignes ont été envoyées à Kaggle, sous forme d'un extrait dont le SHA-256 est vérifié. Les autres lignes restent vides, pour garder la numérotation de `HDFS_sample.log`. Le dépôt a été cloné sans `HDFS_sample.log` ni `Event_traces.csv` : aucune trace de test n'a été téléchargée. Le run a été lancé avec `--file val5.log`. En mode `--mock`, un contrôle local donne des prompts et des sorties identiques à ceux de `--split val --n 5` (vérifié le 16/11). Le script Kaggle est conservé dans `kaggle_script.py.txt` (extension `.txt`, car ce n'est pas du code du dépôt) ; son lien signé vers la wheel, qui expire, a été retiré.

## Résultats (`metrics.json`, `predictions.jsonl`)

| Mesure | Valeur |
|---|---|
| Statuts | 1 `accepte`, 4 `rejete` |
| Réponses conformes à C5 (contrôles code) | 5/5 |
| Appels SLM par bloc | 4,6 en moyenne, 5 au maximum ; 4 reprises |
| Réponses citant un passage | 0/5 |
| Génération SLM | 433,2 s au total, soit 86,6 s par bloc (450,5 s pour l'orchestrateur complet) |
| Tokens de prompt | 1 226 à 2 814, sous `n_ctx` = 4 096 ; 1 passage retiré par la garde de contexte (premier bloc) |

## Lecture

- Les 4 rejets ne viennent pas des contrôles code : les 5 réponses les passent. Ils viennent du contrôleur SLM, qui demande deux fois une correction.
- **Le contrôleur ne voit pas le contrat de réponse.** `checker.py` retire `INSTRUCTION` des preuves (`removeprefix`), et `checker.txt` ne rappelle ni « 2 à 5 faits » ni la règle des sources. 6 de ses 8 verdicts `corriger` reprochent des sources vides. D'autres demandent la liste exhaustive des événements, alors que le contrat en demande une sélection.
- Certains motifs relèvent pourtant de vraies erreurs : un « au même instant » alors que [F10] dit l'ordre non déterminable, ou une confusion sur [F09]. Le contrôle sémantique a donc du signal, mais il est noyé par des exigences hors contrat.
- Le rédacteur n'a cité aucun passage. Dans ce run, l'apport du RAG n'est pas visible dans les réponses.
- La latence est environ 2,8 fois celle du v16 à un appel (30,6 s par bloc sur T4, correction comprise ; SCRUM-63). Les protocoles diffèrent : le v16 a été mesuré sur d'autres blocs.

Ces 5 blocs ne suffisent pas à mesurer une qualité. Ils montrent que la chaîne fonctionne de bout en bout sur GPU, et que le prompt du contrôleur doit recevoir les règles du contrat avant la mesure de SCRUM-45.
