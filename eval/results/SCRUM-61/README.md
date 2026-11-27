# SCRUM-61 · Adaptateur LoRA GGUF appliqué au GGUF QAT q4_0

Vérification du 25/11/2026 sur Kaggle (notebook privé `teamai-scrum61-verif-adaptateur`, version 1, 2 × Tesla T4, Python 3.13). Elle termine l'étape 5 du ticket : charger l'adaptateur exporté en GGUF sur le modèle quantifié et mesurer son effet. La RTX 3050 de l'équipe n'était pas disponible ; la mesure est faite sur T4 avec le même backend que la démo.

## Entrées

| Élément | Valeur |
|---|---|
| Modèle | `google/gemma-4-E4B-it-qat-q4_0-gguf`, `gemma-4-E4B_q4_0-it.gguf`, révision `4b4a2c1d584be7264f87aac328a1bc739ce81b6c` |
| Adaptateur | `adapter.gguf` de l'essai SCRUM-29/61 (30 pas, r = 8, `q_proj` et `v_proj`), SHA-256 `a6ca706c55e2e587c918afc03c071f34ac09d066588db633480198245d75b003`, 4 547 904 octets |
| Backend | `llama-cpp-python` 0.3.36, roue CUDA (SHA-256 `b89030f4…`), `n_ctx = 4096`, `n_gpu_layers = -1`, glouton, 400 tokens au plus, graine 42 |
| Prompt | prompt v16 de `seed-0001` (`volet_b/annotations/seed_alain.jsonl`, bloc train), 1 632 tokens |

## Résultats

| Lancement | Chargement (s) | Génération (s) | Tokens générés | Débit (tokens/s) | Mémoire GPU utilisée (Mio, GPU 0 / GPU 1) |
|---|---:|---:|---:|---:|---|
| Base, sans adaptateur | 2,6 | 7,3 | 315 | 43,4 | 1 923 / 2 385 |
| Adaptateur, échelle 0 | 4,1 | 7,1 | 315 | 44,2 | 1 933 / 2 391 |
| Adaptateur, échelle 1 | 4,2 | 4,2 | 151 | 35,6 | 1 935 / 2 393 |

- llama.cpp charge **132 tenseurs** de l'adaptateur (paires A/B de `attn_q` et `attn_v`, autant que dans `meta.json` de l'export), pour 4,3 Mio de mémoire GPU en plus.
- **Échelle 0 : sortie identique** à la base, caractère pour caractère. **Échelle 1 : sortie différente.** L'adaptateur agit donc bien au moment de l'inférence.
- Effet visible même après 30 pas : à l'échelle 1, la réponse est un JSON nu au schéma v16 avec les références `[F03]`, `[F08]` dans les faits. La base entoure le JSON d'un bloc Markdown et omet les références dans `faits_observes`.

## Limites

- Un seul prompt, un seul passage : ce contrôle établit le chargement et l'effet de l'adaptateur, pas sa qualité. La qualité est mesurée par SCRUM-39 (sélection sur val) et SCRUM-45 (test).
- Mesure sur T4, pas sur la RTX 3050 6 Go : le modèle avec adaptateur occupe environ 4,3 Gio répartis sur deux GPU, ce qui reste sous les 6 Go de la carte visée.
