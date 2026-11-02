# Comparaison de validation

diagnostic backend + quantification ; aucun score de justesse sémantique

Conformité C5 et abstention ne mesurent pas la justesse des explications. Relecture humaine nécessaire.
L'effet du backend et celui de la quantification ne sont pas séparés. Aucun résultat de test.

| Backend | N | Conformité | Abstention | Tokens/s moyen | Pic RSS (octets) | Chargement (s) |
|---|---:|---:|---:|---:|---:|---:|
| transformers | 5 | 0.0% | 0.0% | 1.485394619803171 | 10676346880 | 11.441411800013157 |
| llamacpp | 5 | 0.0% | 40.0% | 2.435281837547858 | 3040342016 | 1.6637293999956455 |

Sorties brutes et erreurs par bloc : `predictions.jsonl`. Prompts exacts : `config.json`.
