# SCRUM-57 — Transformers float32 contre llama.cpp Q4_K_M (26/10/2026)

Copies des deux dossiers C7 produits par `python -m volet_b.slm.compare_backends --n 5` sur la machine d'Alain (CPU seul). Mêmes cinq blocs `val` du sample (seed 42), même prompt, décodage glouton, 300 tokens max. Exécution dans un worktree séparé de la branche : les chemins absolus de `config.json` le reflètent.

- `base/` : modèle de base des deux côtés.
- `essai-adapter/` : adaptateur `essai` (deux pas d'entraînement) chargé par PEFT côté Transformers et converti en GGUF f16 (route b) côté llama.cpp.

| Run | Backend | Conformité C5 | Abstention | Tokens/s moyen | Pic RSS | Chargement |
|---|---|---:|---:|---:|---:|---:|
| base | Transformers float32 | 0/5 | 0/5 | 1,49 | 9,94 GiB | 11,4 s |
| base | llama.cpp Q4_K_M | 0/5 | 2/5 | 2,44 | 2,83 GiB | 1,7 s |
| essai-adapter | Transformers float32 + PEFT | 0/5 | 0/5 | 1,52 | 9,29 GiB | 11,7 s |
| essai-adapter | llama.cpp Q4_K_M + LoRA GGUF | 0/5 | 1/5 | 2,37 | 2,12 GiB | 1,7 s |

Abstention : champ `abstention` lu dans la sortie brute, réponse non conforme comprise ; ce n'est pas une abstention C5 valide.

Lecture :

- Débit environ ×1,6, pic mémoire divisé par 3,5 à 4,4 et chargement environ ÷7 avec llama.cpp Q4_K_M, sur cette machine et ces cinq traces.
- Qualité non comparable : 19 des 20 sorties sont du JSON aux bonnes clés mais aux champs vides (`resume_evenements` vide, listes rendues comme textes vides), donc rejetées par C5 des deux côtés. Une sortie Transformers + adaptateur est un JSON invalide (300 tokens). llama.cpp met parfois un objet dans `sources` ; ce cas faisait planter `validate_answer`, corrigé dans cette PR.
- L'adaptateur `essai` ne sert qu'à vérifier le chemin de chargement ; il ne change pas la qualité ici.
- Le changement de backend et de quantification reste confondu : ces chiffres ne permettent pas d'attribuer un écart à la seule quantification.
