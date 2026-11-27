# Environnements de développement (SCRUM-15)

Socle commun : Python 3.10+ dans un `.venv` à la racine du dépôt TeamAI, `pip install -e ".[data]"` puis l'extra de sa partie (`volet_a` ou `volet_b`). Node 20+ pour le site du volet A.

| Personne | OS | Éditeur | Python | Node | Rôle matériel |
|---|---|---|---|---|---|
| Alain | Windows 11 Pro | VS Code 1.121 + Claude Code | 3.12.10 (PyTorch 2.12 CPU) | 24.12.0 | Ancienne machine d’inférence SmolLM2 (CPU) |
| Bachar | À renseigner | À renseigner | À renseigner | À renseigner | À confirmer |
| Linda | Windows 11 Famille Unilingue | VS Code | 3.13.7 | 24.19.0 | Poste de développement |
| Nassim | Windows 11 | VS Code 1.146.0 (x64) | 3.14.7 (global) / 3.12.16 (`.venv312`, SCRUM-61) | 22.22.0 | Machine cible du SLM Gemma ; RTX 3050 Laptop 6 Go ; inférence GGUF + LoRA mesurée sur GPU (SCRUM-61) |

Point du 13/10 : les environnements d'Alain et de Linda sont renseignés ; le matériel de Nassim est relevé (versions logicielles à compléter). La ligne de Bachar reste à compléter par l'intéressé dans la PR [#3](https://github.com/LindaBOUKHIT/TeamAI/pull/3). Une version non installée doit être indiquée comme telle, plutôt que laissée vide. La présence d'une ligne ne vaut pas validation collective du choix des machines.

Point du 13/11 : versions de Nassim relevées (transmises le 12/11). Point de vigilance historique : Python 3.14.7 était plus récent que la version utilisée pour les tests (3.12) ; la disponibilité d'une roue CUDA de `llama-cpp-python` 0.3.36 pour cette version restait à vérifier (sinon, environnement Python 3.12 dédié). La ligne de Bachar restait à compléter.

**Mise à jour du 26/11 (SCRUM-61)** : la mesure a été réalisée avec **Python 3.12.16 dans `.venv312`**, sans remplacer l'installation globale Python 3.14.7. `llama-cpp-python` 0.3.36 avec accélération CUDA est fonctionnel. Le test sur RTX 3050 6 Go a réussi ; les chiffres et les preuves figurent ci-dessous.

## Machine de Nassim (relevé initial du 13/10 ; actualisation du 26/11)

| Élément | Valeur |
|---|---|
| Propriétaire | Nassim Mezzai (portable) |
| Système | Windows 11 ; relevé du test : `Windows-11-10.0.26200-SP0` |
| CPU | AMD Ryzen 5 8645HS — 6 cœurs / 12 threads |
| RAM | 32 Go |
| GPU / VRAM | NVIDIA GeForce RTX 3050 6GB Laptop GPU — 6 Go (6144 Mio annoncés ; 6143 Mio relevés par le backend CUDA) |
| Pilote NVIDIA | **610.91** (26/11) ; ancien relevé : 592.82 |
| CUDA (`nvidia-smi`) | **13.3** (26/11) ; ancien relevé : 13.1. Il s'agit de la version maximale prise en charge par le pilote, pas nécessairement d'un CUDA Toolkit installé |
| Environnement Python | **3.12.16 dans `.venv312`** pour SCRUM-61 ; Python global **3.14.7** conservé |
| Node / éditeur | 22.22.0 / VS Code 1.146.0 (x64), valeurs communiquées le 12/11 |
| Inférence GPU | `llama-cpp-python` **0.3.36**, backend CUDA reconnu, `n_gpu_layers = -1` |
| Autres paquets relevés par le script | `huggingface_hub` 2.5.0 ; `torch`, `transformers` et `peft` non installés dans cet environnement de mesure |

Au relevé initial d'octobre, c'était la seule machine de l'équipe avec un GPU NVIDIA. Le fonctionnement du modèle Gemma quantifié et de l'adaptateur LoRA a ensuite été **mesuré le 26/11 dans SCRUM-61**. Ce test local d'inférence ne constitue pas un entraînement QLoRA sur la RTX 3050 : la faisabilité d'un entraînement local reste une question distincte de SCRUM-29.

## Machine cible du SLM (volet B) — SCRUM-63, 27/10/2026

Le portable de **Nassim** a été retenu comme cible pour Gemma 4 E4B QAT : Ryzen 5 8645HS, 32 Go de RAM, RTX 3050 Laptop 6 Go. Au relevé initial, le pilote était en version 592.82, `nvidia-smi` annonçait CUDA 13.1 et Python était en version 3.14.7 (relevé transmis par Nassim le 12/11).

**État historique au 27/10** : aucune inférence Gemma ni mesure de performances n'avait encore été faite sur ce portable pour SCRUM-63. La configuration prévue était `llama.cpp`, contexte 4096, réponse 800 tokens ; le chargeur CPU existant était conservé, et l'offload GPU restait à valider. Voir la [trace SCRUM-63](../../eval/results/SCRUM-63/README.md).

**État au 26/11** : l'exécution GPU du GGUF QAT et de l'adaptateur LoRA a été validée sur cette machine par **SCRUM-61**, avec toutes les couches déportées (`n_gpu_layers = -1`). La mesure SCRUM-61 porte sur le prompt `seed-0001` et trois conditions expérimentales ; elle ne remplace ni une validation de la chaîne RAG complète ni une évaluation de qualité sur tout le jeu de test.

## Mesure locale de l'adaptateur LoRA — SCRUM-61, 26/11/2026

**Objectif :** vérifier l'inférence locale du modèle GGUF quantifié et l'application de l'adaptateur LoRA `r8_qv` sur la RTX 3050 6 Go de Nassim.

**Commande :**

```powershell
python -m volet_b.slm.verif_machine --adapter eval\results\SCRUM-39\kaggle_final\adapter_r8_qv.gguf --sha256 52ff1ba7ca6833846b2148dba4c86dc0d5a646a6d582eaa8b2d0d6444559db7b
```

**Protocole :** trois générations sur le même prompt `seed-0001` : modèle de base ; adaptateur appliqué à l'échelle 0 ; adaptateur appliqué à l'échelle 1.

| Configuration | Chargement (s) | Génération (s) | Tokens générés | Débit (tokens/s) | VRAM du modèle après chargement (Mio) |
|---|---:|---:|---:|---:|---:|
| Base | 4.1 | 10.3 | 281 | 27.21 | 3697 |
| Adaptateur échelle 0 | 2.9 | 10.1 | 281 | 27.74 | 3703 |
| Adaptateur échelle 1 | 2.6 | 10.7 | 289 | 26.90 | 3705 |

**Résultats de validation :**

- L'empreinte SHA-256 de l'adaptateur correspond à la valeur de référence : `52ff1ba7ca6833846b2148dba4c86dc0d5a646a6d582eaa8b2d0d6444559db7b`.
- **Base identique à l'échelle 0 : oui** ; **échelle 1 différente de l'échelle 0 : oui**.
- **Accélération GPU active :** RTX 3050 détectée par `llama-cpp-python` ; `n_gpu_layers = -1`.
- **Mémoire du modèle :** 3705 Mio au maximum dans les trois essais, en dessous des 6144 Mio annoncés. Il ne s'agit pas d'une mesure du pic total de VRAM du système.
- Aucun échec par manque de VRAM pendant ce test ; le recours à `--n-gpu-layers 30` n'a pas été nécessaire.

**Limites :** ces trois générations vérifient l'exécution, le débit sur un prompt et l'effet observable de l'adaptateur ; elles ne suffisent pas à quantifier la qualité du modèle sur les traces HDFS ni les performances du système RAG de bout en bout.

**Preuves conservées :** [`eval/results/SCRUM-61/machine/2026-11-26_194828/`](../../eval/results/SCRUM-61/machine/2026-11-26_194828/) — `resultats.json`, `resultats.md`, `base.json`, `base.log`, `echelle_0.json`, `echelle_0.log`, `echelle_1.json`, `echelle_1.log`.

## Ancienne machine cible — Alain, historique SmolLM2

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

## Mesures historiques sur la machine d’Alain (SmolLM2)

| Usage | Faisable ? | Pourquoi |
|---|---|---|
| Inférence float32 (Transformers, CPU) | Mesurée dans SCRUM-28 | Sur une trace le 08/10 : 0,16 token/s, pic RSS de 9,84 GiB au chargement et 8,00 GiB en génération ; chargement 238 s, 156 tokens en 952,03 s |
| Inférence 4 bits Q4_K_M (llama.cpp) | Mesurée dans SCRUM-57 | Sur cinq traces de validation le 26/10 : 2,4 token/s, pic RSS de 2,8 GiB, chargement 1,7 s (float32 : 1,5 token/s, 9,9 GiB) ; backend `llamacpp` de `generate.py` |
| Embeddings + index du RAG | À mesurer | L'inférence du SLM ne valide pas la mémoire ou la latence de la chaîne RAG complète |
| Entraînement LoRA du 1.7B | Non testé sur cette machine | CPU seul : durée inconnue ; un essai court sur GPU est prévu dans SCRUM-29 |

La PR [#4](https://github.com/LindaBOUKHIT/TeamAI/pull/4) a été approuvée puis fusionnée le 11/10 ; sa [preuve du 08/10](../../eval/results/SCRUM-28/README.md) est intégrée à `dev`. La PR [#6](https://github.com/LindaBOUKHIT/TeamAI/pull/6) reste ouverte au contrôle du 12/10. Les mesures portent sur une seule trace et ne constituent pas une évaluation de qualité ni une estimation du temps d'entraînement. Les valeurs historiques du 06/10 sont conservées séparément ; leur comparaison avec celles du 08/10 n'est pas contrôlée.

## Décisions (à reporter dans le journal)

- **06/10 — Inférence et démo du volet B sur la machine d'Alain** (CPU, 32 Go).
- **06/10 — Entraînement LoRA envisagé sur GPU en ligne** (Kaggle, Colab en secours). La disponibilité du GPU, sa VRAM et un entraînement court restent à vérifier dans SCRUM-29 avant d'engager l'entraînement complet. L'adaptateur doit ensuite pouvoir être utilisé en local.
- **Cache des modèles sur `D:\`** : `HF_HOME=D:\IA_Caches\HuggingFace\` relevé le 12/10 sur la machine d'Alain. Vérifier aussi la configuration du cache Hub et la présence des poids avant une exécution hors ligne ; ne pas déclencher un second téléchargement pour cette vérification.
- **26/11 — Vérification GPU sur la machine de Nassim (SCRUM-61)** : Python 3.12 isolé dans `.venv312`, exécution de Gemma GGUF quantifié et de l'adaptateur LoRA `r8_qv` sur RTX 3050 6 Go ; base = LoRA échelle 0, LoRA échelle 1 différente, débit 26,90 à 27,74 tokens/s sur le prompt de vérification, mémoire GPU du modèle 3697 à 3705 Mio.

## Conditions de clôture de SCRUM-15

- [x] Environnement et machine d'Alain documentés.
- [x] Machine d'inférence proposée et premiers essais référencés.
- [x] Solution d'entraînement proposée, avec essai de faisabilité identifié.
- [x] Ligne de Linda renseignée dans la PR #3.
- [ ] Ligne de Bachar renseignée.
- [x] Versions Python/Node/CUDA de Nassim complétées (13/11 ; actualisation SCRUM-61 le 26/11).
- [ ] Choix des machines confirmé avec le groupe et PR #3 relue par Linda puis fusionnée.
