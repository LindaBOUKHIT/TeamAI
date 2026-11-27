# SCRUM-39 : LoRA complet, sélection sur val

Run Kaggle `wsear07/teamai-scrum39-lora-final` (version 2) le 25/11/2026 sur un Tesla T4, avec le code au commit `faabb47`.

## Entraînement

Base d'entraînement : `google/gemma-4-E4B-it-qat-q4_0-unquantized`, révision `476025a`, en QLoRA 4 bits. Données : train SCRUM-36 uniquement, 199 exemples sur 200. `bachar-049` (5 778 tokens) dépasse `max_tokens` : il est écarté entier et listé dans `metrics.json`, jamais tronqué. Chaque réglage a fait 400 pas, sans pas sauté.

| Réglage | Cibles | lr | Paramètres entraînés | Perte début → fin | Pic VRAM | s/pas |
|---|---|---|---:|---|---:|---:|
| `r8_qv` | q, v | 2e-4 | 2 269 184 | 0,880 → 0,151 | 11,1 Go | 6,5 |
| `r16_qkvo` | q, k, v, o | 1e-4 | 9 076 736 | 0,827 → 0,140 | 11,2 Go | 6,6 |

Seul l'adaptateur est converti en GGUF, avec llama.cpp au commit `0c1e57098`, en `adapter_f16`. Il s'applique au GGUF QAT q4_0 avec `lora_path`.

| Réglage | `adapter.gguf` | SHA-256 |
|---|---:|---|
| `r8_qv` (retenu) | 4 547 904 octets | `52ff1ba7ca6833846b2148dba4c86dc0d5a646a6d582eaa8b2d0d6444559db7b` |
| `r16_qkvo` | 18 172 224 octets | `8ab427b91f4927e0db222689631172ac797d3a3b6f11c9bb59f2bfb964545638` |

L'adaptateur retenu est versionné ici : `adapter_r8_qv.gguf`, 4,5 Mo. C'est le seul GGUF exclu de la règle `*.gguf` de `.gitignore`. Les autres poids, `r16_qkvo` et les `adapter_model.safetensors`, restent dans les sorties du notebook Kaggle. Vérifier le SHA-256 avant usage.

## Sélection sur val (40 exemples, pipeline v16 à 1 agent)

| Mesure | Base | `r8_qv` | `r16_qkvo` |
|---|---:|---:|---:|
| Réponses acceptées | 39/40 | 39/40 | 39/40 |
| Hypothèses / bloc avec incident (28 blocs) | 0,39 (11) | 0,43 (12) | 0,43 (12) |
| Hypothèses sur un bloc sans incident | 0 | 0 | 0 |
| Références inconnues, réseau sans appui, boucles | 0 | 0 | 0 |
| Faits recopiés exactement | 38 | 39 | 39 |
| Corrections déclenchées | 1 | 0 | 0 |
| Latence moyenne | 30,1 s | 27,6 s | 27,1 s |
| Pic VRAM | 4,53 Go | 4,54 Go | 4,55 Go |

- **Échec commun.** Il est le même dans les trois colonnes : `nassim-052`, dont le prompt dépasse le plafond de 2 900 tokens.
- **Seul écart sur les hypothèses.** La seule hypothèse en plus vient de `alain-052`, un bloc avec incident : 0 hypothèse pour la base, 1 pour chaque adaptateur.
- **Égalité.** Les deux réglages sont à égalité sur les trois critères de la règle fixée avant l'entraînement. Leurs sorties diffèrent pourtant : 39 textes sur 40 ne sont pas identiques. La règle ne prévoit pas de départage : `select()` garde alors l'ordre de `lora_final.yaml`, ce qui retient `r8_qv`, le plus petit adaptateur. Ce départage est constaté ici, pas décidé à l'avance.
- **Effet du LoRA.** Sur les mesures automatiques de val, il change peu de chose : une hypothèse de plus, un fait recopié de plus, plus de correction, et une latence un peu plus basse. Son effet sur la qualité des explications sera mesuré sur le test (SCRUM-45, configurations 3 et 4) et par la double annotation.

## Fichiers

- `lora/` : configurations des essais, provenance de la base, `meta.json` et `conversion.log` de chaque export GGUF, runs d'entraînement (`metrics.json`, `train_log.jsonl`).
- `val/<base|r8_qv|r16_qkvo>/` : runs C7 sur val.
- `adapter_r8_qv.gguf` : adaptateur retenu, à passer à `--adapter`.
- `selection.json` : sortie de la règle de sélection.
- `journal.txt`, `sorties.txt` : journal du notebook.
