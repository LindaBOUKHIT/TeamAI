# Comparaison de validation

diagnostic backend + quantification ; aucun score de justesse sémantique

Conformité C5 et abstention ne mesurent pas la justesse des explications. Relecture humaine nécessaire.
L'effet du backend et celui de la quantification ne sont pas séparés. Aucun résultat de test.

| Backend | N | Conformité | Abstention | Tokens/s moyen | Pic RSS (octets) | Chargement (s) |
|---|---:|---:|---:|---:|---:|---:|
| transformers | 5 | 0.0% | 0.0% | 1.5186421142452462 | 9974497280 | 11.709246399987023 |
| llamacpp | 5 | 0.0% | 20.0% | 2.3747079852684307 | 2279698432 | 1.7446273999812547 |

Sorties brutes et erreurs par bloc : `predictions.jsonl`. Prompts exacts : `config.json`.
