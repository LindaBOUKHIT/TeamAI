# llama.cpp / GGUF (via llama-cpp-python) — runtime d'inférence local

- **Utilisé par / pour** : Alain, inférence du SLM du volet B : SmolLM2 1,7 B en Q4_K_M (SCRUM-57), puis Gemma 4 E4B QAT en Q4_0 avec le prompt v16 et une sortie contrainte par schéma JSON (SCRUM-63) ; conversion de l'adaptateur LoRA en GGUF (SCRUM-29). Mesures et décisions dans le [journal](../../projet/journal.md).
- **Temps d'appropriation constaté** : premier GGUF mesuré le 06/10, le jour même de la première inférence en Transformers (SCRUM-28). Le temps passé en heures n'a pas été relevé.
- **Ce qui a marché** :
  - Sur la machine d'Alain (i5-1240P, sans GPU NVIDIA), avec le même bloc et les mêmes paramètres, comparé à Transformers float32 : 0,98 Go sur disque au lieu de 3,4 Go, chargement en 2,9 s au lieu de 24 s, pic mémoire de 2,8 Go au lieu de 16,1 Go, 1,9 token/s au lieu de 0,64 (SCRUM-57, une seule trace).
  - Le schéma JSON transmis à llama.cpp garantit une réponse au format attendu par les contrôles v16 (SCRUM-63).
  - Le convertisseur `convert_lora_to_gguf.py` de llama.cpp (commit `0c1e57098`) produit un adaptateur GGUF de 4,5 Mo à partir de l'adaptateur PEFT (08/11).
- **Ce qui a échoué ou déçu** :
  - Avec l'ancien prompt (logs puis consigne), le modèle Q4_K_M recopiait les logs au lieu de les résumer. Il a fallu placer la consigne avant les logs, et l'expérience ne sépare pas l'effet de la quantification de celui du backend.
  - Les débits sont instables : relancé le 13/10 sur la même machine, chargée par d'autres processus, le même calcul donne 0,71 token/s au lieu de 1,9. Une seule mesure ne suffit pas.
  - La sortie contrainte garantit la forme, pas le fond : sur 40 blocs val, chronologies et causalités restent parfois fausses, et un résumé boucle (SCRUM-63, SCRUM-46).
- **Ce que la documentation omet** :
  - La roue pip de llama-cpp-python est compilée pour le CPU. Le GPU demande une installation CUDA à part, et `n_gpu_layers` vaut 0 par défaut : sans le régler, tout tourne sur le CPU sans avertissement. Nous l'avons corrigé en relecture le 27/10 (`n_gpu_layers: -1` pour la RTX 3050).
  - Le coût dominant vient du traitement du prompt (~2 200 tokens) et d'une pénalité de répétition appliquée à tout le contexte, pas de la génération (SCRUM-57).
- **Comparaison avec l'outil utilisé avant** : Transformers en float32 sur CPU (SCRUM-28) : 0,64 token/s, si lent qu'évaluer 4 configurations sur 60 à 100 traces aurait pris plusieurs dizaines d'heures. llama.cpp rend les évaluations faisables. La comparaison n'est pas contrôlée : une trace, une exécution par backend.
- **Verdict** : on garde llama.cpp comme runtime du volet B (démo et évaluations). Reste à vérifier l'inférence sur la RTX 3050 de Nassim, avec et sans adaptateur (SCRUM-61).
