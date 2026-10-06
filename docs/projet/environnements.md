# Environnements de développement (SCRUM-15)

Socle commun : Python 3.10+ dans un `.venv` à la racine de `projet/`, `pip install -e ".[data]"` puis l'extra de sa partie (`volet_a` ou `volet_b`). Node 20+ pour le site du volet A.

| Personne | OS | Éditeur | Python | Node | Rôle matériel |
|---|---|---|---|---|---|
| Alain | Windows 11 Pro | VS Code 1.121 + Claude Code | 3.12.10 (PyTorch 2.12 CPU) | 24.12.0 | Machine d'inférence du SLM (volet B) |
| Bachar | | | | | |
| Linda | | | | | |
| Nassim | | | | | |

## Machine cible du SLM (volet B)

| Élément | Valeur |
|---|---|
| Propriétaire | Alain (portable) |
| CPU | Intel Core i5-1240P — 12 cœurs / 16 threads |
| RAM | 32 Go |
| GPU / VRAM | Intel Iris Xe (graphique intégré, mémoire partagée) — **pas de GPU NVIDIA** |
| CUDA / MPS | Non — PyTorch 2.12 en version CPU |
| Disque libre | C: 59 Go · D: 787 Go |
| Machine d'entraînement LoRA | **GPU gratuit en ligne (Kaggle ou Colab)** — voir décision ci-dessous |

Relevé du 06/10/2026 (SCRUM-15). Commandes utiles : `nvidia-smi` (NVIDIA) ; RAM sous Windows : `systeminfo | findstr Mémoire`.

## Ce que cette machine permet (estimation, à confirmer par SCRUM-28)

| Usage | Faisable ? | Pourquoi |
|---|---|---|
| Inférence SmolLM2-1.7B en bf16/fp32 (Transformers, CPU) | Oui, lent | Poids ≈ 3,4 Go (bf16) à 6,8 Go (fp32), largement sous les 32 Go ; quelques tokens/s attendus |
| Inférence quantifiée 4 bits (GGUF via llama.cpp / Ollama) | Oui, plus rapide | Poids ≈ 1 Go ; recommandé pour la démo et les évaluations répétées |
| Embeddings + index FAISS du RAG | Oui | Petits modèles (bge-small, e5-small) très légers sur CPU |
| Entraînement LoRA du 1.7B | Non réaliste en local | Sans GPU NVIDIA, un entraînement prendrait des heures par époque ; QLoRA (bitsandbytes) exige CUDA |

## Décisions (à reporter dans le journal)

- **06/10 — Inférence et démo du volet B sur la machine d'Alain** (CPU, 32 Go).
- **06/10 — Entraînement LoRA sur GPU gratuit en ligne** (Kaggle : ~30 h de GPU/semaine ; Colab en secours). L'adaptateur entraîné est ensuite chargé en local pour l'inférence. Ce n'est pas un remplacement de l'adaptation par du prompting : l'adaptation reste faite, seul le lieu d'entraînement change.
- **Cache des modèles sur D:** (C: n'a que 59 Go libres) : définir `HF_HOME=D:\hf_cache` avant le premier téléchargement.
