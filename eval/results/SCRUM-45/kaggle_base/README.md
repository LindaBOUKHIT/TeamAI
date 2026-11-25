# SCRUM-45 : modèle de base sur le test (configurations 1 et 2)

Run Kaggle `wsear07/teamai-scrum45-base-test` le 25/11/2026, sur un Tesla T4 15 Gio avec le pilote 580.178.04.

- Code : commit `faabb47`. Pour `eval/`, `volet_b/agents/` et `teamai/`, ce commit est identique à `ac8c030` (PR #77).
- Backend : llama-cpp-python 0.3.36 CUDA.
- Modèle : Gemma 4 E4B QAT q4_0 GGUF, sans adaptateur.
- Entrées : les 80 cas figés, empreinte `32b75a84…ec4b8` identique à `eval/volet_b/test_inputs.sha256`. Les deux runs sont complets (`complete: true`, sans `--limit` ni `--ids`).

| Mesure | base_1agent | base_3agents |
|---|---|---|
| Conformité C5 | 79/80 (98,8 %) | 79/80 (98,8 %) |
| Acceptées | 79/80 (98,8 %) | 9/80 (11,3 %) |
| Abstentions | 0 | 0 |
| Hypothèses / bloc avec incident (35 blocs) | 0,63 (22) | 0,00 |
| Hypothèses sur un bloc sans incident (45 blocs) | 0 | 0 |
| Références inconnues, réseau sans appui, boucles | 0 | 0 |
| Appels SLM moyens (max) | 1,01 (2) | 4,70 (5) |
| Latence moyenne / médiane | 27,8 s / 27,3 s | 84,3 s / 85,7 s |
| Pic RSS / VRAM | 5,80 Go / 4,52 Go | 6,70 Go / 4,53 Go |

## Lecture

- **Échec commun.** Le cas `test-0011` échoue dans les deux configurations avant génération : le prompt dépasse le plafond de 2 900 tokens. Il reste au dénominateur.
- **1 agent.** Les 22 hypothèses portent toutes sur des blocs marqués incident. Elles se répartissent sur 22 des 35 blocs avec incident, et aucun bloc sans incident n'en reçoit. Une seule correction a été déclenchée, et elle a réussi.
- **3 agents.** Le contrôleur demande une correction dans 137 de ses 146 passages, et 71 réponses finissent rejetées. Ses motifs portent surtout :
  - sur l'ordre attribué à des événements de la même seconde ;
  - sur des comptes d'occurrences que le résumé ne reprend pas ;
  - plus rarement, sur des formulations jugées trop larges.

  Le rédacteur a proposé une hypothèse dans 22 brouillons sur 150, mais aucune ne figure dans une réponse acceptée. Aucune réponse acceptée ne cite de passage : `answers_with_sources` vaut 0.
- **Protocole.** Ces chiffres sont mesurés sur le test : aucun prompt ni seuil n'est modifié après les avoir vus. Les configurations 3 et 4 (adaptateur LoRA) suivront la sélection SCRUM-39, au même protocole.

## Fichiers

- `runs/<config>/<run>/` : `config.json`, `metrics.json` et `predictions.jsonl` (format C7).
- `journal.txt` et `sorties.txt` : journal horodaté et sorties des commandes du notebook.
