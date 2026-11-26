# SCRUM-45 : modèle adapté sur le test (configurations 3 et 4)

Run Kaggle `wsear07/teamai-scrum45-lora-test` le 25/11/2026 sur un Tesla T4. Code au commit `faabb47`, le même que pour les runs du modèle de base. Adaptateur `r8_qv` de SCRUM-39, `adapter.gguf`, SHA-256 `52ff1ba7ca6833846b2148dba4c86dc0d5a646a6d582eaa8b2d0d6444559db7b`, vérifié avant usage et inscrit dans chaque `metrics.json`. Entrées : les 80 cas figés, empreinte identique à `eval/volet_b/test_inputs.sha256`. Les runs sont complets.

| Mesure | lora_1agent | lora_3agents |
|---|---|---|
| Conformité C5 | 79/80 | 79/80 |
| Acceptées | 79/80 | 25/80 (12 sur des blocs avec incident) |
| Hypothèses / bloc avec incident (35 blocs) | 0,63 (22) | 0,26 (9) |
| Hypothèses sur un bloc sans incident | 0 | 0 |
| Réponses acceptées citant un passage | sans objet (aucun passage en 1 agent) | 5 |
| Appels SLM moyens | 1,00 | 4,61 |
| Latence moyenne / médiane | 24,6 s / 22,3 s | 73,8 s / 77,5 s |
| Durée totale | 1 976 s | 5 922 s |

**Comparaison avec la base** (`../kaggle_base/README.md`) :
- **1 agent.** Les textes changent dans 79 cas sur 80, mais les mesures automatiques restent les mêmes. Une seule réponse affirme encore un ordre entre événements, contre 35 pour la base.
- **3 agents.** Le contrôleur demande une correction dans 119 de ses 144 passages, contre 137 sur 146 pour la base.

**Échec commun.** `test-0011` échoue dans les deux configurations : son prompt dépasse le plafond de 2 900 tokens.

Fichiers : `runs/<config>/<run>/` (format C7) et `journal.txt`.
