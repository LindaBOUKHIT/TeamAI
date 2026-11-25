# Résultats du volet B

## Évaluation automatique des 4 configurations

Entrées figées `eval/volet_b/test_inputs.jsonl` (SHA-256 `32b75a84e100bb1101c7fd4c8cab2ef5e322b6c205716aac378d56bf1a7ec4b8`), mêmes traces, même corpus et mêmes paramètres de génération pour les 4 configurations. Mesures sur la réponse finale ; tous les cas au dénominateur, échecs compris. Acceptées : statut `accepte` pour 3 agents, contrat v16 valide pour 1 agent. Incident : indice `attention` calculé par le code, jamais le label.

| Configuration | n | Conformité C5 | Acceptées | Abstentions | Hypothèses/bloc avec incident | Références inconnues | Réseau sans appui | Boucles | Appels SLM moyens | Latence moyenne (s) | Latence médiane (s) | Pic VRAM (Mio) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| base_1agent | 80 | 98,8 % | 98,8 % | 0,0 % | 0,63 | 0,0 % | 0,0 % | 0,0 % | 1,01 | 27,82 | 27,35 | 4314 |
| base_3agents | 80 | 98,8 % | 11,2 % | 0,0 % | 0,00 | 0,0 % | 0,0 % | 0,0 % | 4,70 | 84,30 | 85,75 | 4322 |
| lora_1agent | 80 | 98,8 % | 98,8 % | 0,0 % | 0,63 | 0,0 % | 0,0 % | 0,0 % | 1,00 | 24,56 | 22,33 | 4322 |
| lora_3agents | 80 | 98,8 % | 31,2 % | 0,0 % | 0,26 | 0,0 % | 0,0 % | 0,0 % | 4,61 | 73,81 | 77,52 | 4330 |


## Lecture des mesures automatiques

Runs Kaggle sur T4 du 25/11/2026, avec le code du commit `faabb47`. Adaptateur `r8_qv`, SHA-256 `52ff1ba7…59db7b`, retenu sur val par SCRUM-39. Détails : `eval/results/SCRUM-45/kaggle_base/README.md` et `eval/results/SCRUM-45/kaggle_lora/README.md`.

- **Échec commun.** `test-0011` échoue dans les 4 configurations avant toute génération : son prompt dépasse le plafond de 2 900 tokens. Il reste au dénominateur.
- **1 agent.** Le LoRA ne change ni le taux d'acceptation (79/80) ni le nombre d'hypothèses (22, toutes sur des blocs avec incident). Il change en revanche la forme des réponses :
  - les résumés qui affirment un ordre entre événements (« débuté par », « suivi de »…) passent de 35/80 à 1/80 ;
  - les faits recopiés exactement passent de 78 à 79 ;
  - aucune correction n'est déclenchée, contre une pour la base ;
  - la latence moyenne baisse de 27,8 s à 24,6 s.
- **3 agents.** Le contrôleur accepte 25 réponses sur 80 avec le LoRA, contre 9 pour la base.
  - 12 réponses acceptées portent sur des blocs avec incident, contre 0 pour la base, ce qui donne 9 hypothèses retenues.
  - 5 réponses acceptées citent un passage de la documentation, contre 0.
  - La recherche ne renvoie toujours que 4 passages distincts sur les 80 cas.
- **Aucune hypothèse sur un bloc sans incident**, dans aucune configuration, et aucune référence inconnue.
- **Mémoire GPU.** Le pic reste entre 4,3 et 4,4 Gio dans les 4 configurations : l'adaptateur ajoute moins de 10 Mio.

Ces mesures automatiques portent sur la forme et sur l'appui des réponses, pas sur leur justesse. La justesse sera mesurée par la double annotation à l'aveugle (30 cas × 4 configurations, `eval/volet_b/double_annotation/`).
