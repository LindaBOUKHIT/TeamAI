# Environnements de développement (SCRUM-15)

Socle commun : Python 3.10+ dans un `.venv` à la racine de `projet/`, `pip install -e ".[data]"` puis l'extra de sa partie (`volet_a` ou `volet_b`). Node 20+ pour le site du volet A.

| Personne | OS | Éditeur | Python | Node | Rôle matériel |
|---|---|---|---|---|---|
| Alain | Windows 11 Pro | VS Code 1.121 + Claude Code | 3.12.10 (PyTorch 2.12 CPU) | 24.12.0 | Machine d'inférence du SLM (volet B) |
| Bachar | À renseigner | À renseigner | À renseigner | À renseigner | À confirmer |
| Linda | À renseigner | À renseigner | À renseigner | À renseigner | À confirmer |
| Nassim | À renseigner | À renseigner | À renseigner | À renseigner | À confirmer |

Point du 08/10 : la partie d'Alain est renseignée ; les trois autres environnements n'ont pas été communiqués. Chaque membre complète sa propre ligne dans la PR [#3](https://github.com/LindaBOUKHIT/TeamAI/pull/3). Une version non installée doit être indiquée comme telle, plutôt que laissée vide.

## Machine cible du SLM (volet B)

| Élément | Valeur |
|---|---|
| Propriétaire | Alain (portable) |
| CPU | Intel Core i5-1240P — 12 cœurs / 16 threads |
| RAM | 32 Go |
| GPU / VRAM | Intel Iris Xe (graphique intégré, mémoire partagée) — **pas de GPU NVIDIA** |
| CUDA / MPS | Non — PyTorch 2.12 en version CPU |
| Disque libre | C: 55 Go · D: 780 Go (relevé du 08/10 ; valeurs variables) |
| Machine d'entraînement LoRA | GPU en ligne envisagé : Kaggle en priorité, Colab en secours ; accès et essai à vérifier dans SCRUM-29 |

Relevé initial du 06/10/2026 (SCRUM-15), CPU et GPU revérifiés le 08/10 ; 31,7 Go de mémoire visibles par Windows pour 32 Go installés. Commandes PowerShell pour le relevé :

```powershell
Get-CimInstance Win32_OperatingSystem | Select-Object Caption
Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory
Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors
Get-CimInstance Win32_VideoController | Select-Object Name
Get-PSDrive -Name C,D | Select-Object Name, Free
python --version
node --version
```

## Ce que cette machine permet

| Usage | Faisable ? | Pourquoi |
|---|---|---|
| Inférence float32 (Transformers, CPU) | Mesurée dans SCRUM-28 | Sur une trace le 06/10 : 0,6 token/s, pic de mémoire du processus de 16,3 Go |
| Inférence 4 bits Q4_K_M (llama.cpp) | Mesurée dans SCRUM-57 | Sur une trace le 06/10 : 1,9 token/s, pic de 2,8 Go, fichier GGUF de 0,98 Go ; backend encore à intégrer à `generate.py` |
| Embeddings + index du RAG | À mesurer | L'inférence du SLM ne valide pas la mémoire ou la latence de la chaîne RAG complète |
| Entraînement LoRA du 1.7B | Non testé sur cette machine | CPU seul : durée inconnue ; un essai court sur GPU est prévu dans SCRUM-29 |

Ces mesures sont rapportées dans les PR [#4](https://github.com/LindaBOUKHIT/TeamAI/pull/4) et [#6](https://github.com/LindaBOUKHIT/TeamAI/pull/6), encore en revue au 08/10. Elles portent sur une seule trace et ne constituent pas une évaluation de qualité ni une estimation du temps d'entraînement.

## Décisions (à reporter dans le journal)

- **06/10 — Inférence et démo du volet B sur la machine d'Alain** (CPU, 32 Go).
- **06/10 — Entraînement LoRA envisagé sur GPU en ligne** (Kaggle, Colab en secours). La disponibilité du GPU, sa VRAM et un entraînement court restent à vérifier dans SCRUM-29 avant d'engager l'entraînement complet. L'adaptateur doit ensuite pouvoir être utilisé en local.
- **Cache des modèles sur D:** : définir `HF_HOME=D:\hf_cache` avant le téléchargement.

## Conditions de clôture de SCRUM-15

- [x] Environnement et machine d'Alain documentés.
- [x] Machine d'inférence proposée et premiers essais référencés.
- [x] Solution d'entraînement proposée, avec essai de faisabilité identifié.
- [ ] Lignes de Bachar, Linda et Nassim renseignées par les intéressés.
- [ ] Choix des machines confirmé avec le groupe et PR #3 relue par Linda puis fusionnée.
