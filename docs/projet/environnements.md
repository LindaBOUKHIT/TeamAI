# Environnements de développement (SCRUM-15)

Socle commun : Python 3.10+ dans un `.venv` à la racine du dépôt TeamAI, `pip install -e ".[data]"` puis l'extra de sa partie (`volet_a` ou `volet_b`). Node 20+ pour le site du volet A.

| Personne | OS | Éditeur | Python | Node | Rôle matériel |
|---|---|---|---|---|---|
| Alain | Windows 11 Pro | VS Code 1.121 + Claude Code | 3.12.10 (PyTorch 2.12 CPU) | 24.12.0 | Machine d'inférence du SLM (volet B) |
| Bachar | À renseigner | À renseigner | À renseigner | À renseigner | À confirmer |
| Linda | Windows 11 Famille Unilingue | VS Code | 3.13.7 | 24.19.0 | Poste de développement |
| Nassim | À renseigner | À renseigner | À renseigner | À renseigner | À confirmer |

Point du 12/10 : les environnements d'Alain et de Linda sont renseignés. Les lignes de Bachar et Nassim restent à compléter par les intéressés dans la PR [#3](https://github.com/LindaBOUKHIT/TeamAI/pull/3). Une version non installée doit être indiquée comme telle, plutôt que laissée vide. La présence d'une ligne ne vaut pas validation collective du choix des machines.

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
| Inférence float32 (Transformers, CPU) | Mesurée dans SCRUM-28 | Sur une trace le 08/10 : 0,16 token/s, pic RSS de 9,84 GiB au chargement et 8,00 GiB en génération ; chargement 238 s, 156 tokens en 952,03 s |
| Inférence 4 bits Q4_K_M (llama.cpp) | Mesurée dans SCRUM-57 | Sur une trace le 06/10 : 1,9 token/s, pic de 2,8 Go, fichier GGUF de 0,98 Go ; backend encore à intégrer à `generate.py` |
| Embeddings + index du RAG | À mesurer | L'inférence du SLM ne valide pas la mémoire ou la latence de la chaîne RAG complète |
| Entraînement LoRA du 1.7B | Non testé sur cette machine | CPU seul : durée inconnue ; un essai court sur GPU est prévu dans SCRUM-29 |

La PR [#4](https://github.com/LindaBOUKHIT/TeamAI/pull/4) a été approuvée puis fusionnée le 11/10 ; sa [preuve du 08/10](../../eval/results/SCRUM-28/README.md) est intégrée à `dev`. La PR [#6](https://github.com/LindaBOUKHIT/TeamAI/pull/6) reste ouverte au contrôle du 12/10. Les mesures portent sur une seule trace et ne constituent pas une évaluation de qualité ni une estimation du temps d'entraînement. Les valeurs historiques du 06/10 sont conservées séparément ; leur comparaison avec celles du 08/10 n'est pas contrôlée.

## Décisions (à reporter dans le journal)

- **06/10 — Inférence et démo du volet B sur la machine d'Alain** (CPU, 32 Go).
- **06/10 — Entraînement LoRA envisagé sur GPU en ligne** (Kaggle, Colab en secours). La disponibilité du GPU, sa VRAM et un entraînement court restent à vérifier dans SCRUM-29 avant d'engager l'entraînement complet. L'adaptateur doit ensuite pouvoir être utilisé en local.
- **Cache des modèles sur D:** : `HF_HOME=D:\IA_Caches\HuggingFace` relevé le 12/10 sur la machine d'Alain. Vérifier aussi la configuration du cache Hub et la présence des poids avant une exécution hors ligne ; ne pas déclencher un second téléchargement pour cette vérification.

## Conditions de clôture de SCRUM-15

- [x] Environnement et machine d'Alain documentés.
- [x] Machine d'inférence proposée et premiers essais référencés.
- [x] Solution d'entraînement proposée, avec essai de faisabilité identifié.
- [x] Ligne de Linda renseignée dans la PR #3.
- [ ] Lignes de Bachar et Nassim renseignées par les intéressés.
- [ ] Choix des machines confirmé avec le groupe et PR #3 relue par Linda puis fusionnée.
