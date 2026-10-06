# TeamAI — Journal du projet

Point de départ local à partager avec le groupe. Ce fichier ne remplace pas à lui seul le classeur partagé demandé dans le sujet.

## Décisions

| Date | Décision ou proposition | Motif | État |
|---|---|---|---|
| 21/09/2026 | Proposition d’un sujet sur les logs HDFS en remplacement du support client | Nouveau sujet présenté dans le texte du groupe et examiné avec un assistant IA | Validation enseignant non connue |
| 21/09/2026 | Périmètre initial proposé : HDFS_v1, classification binaire par trace et interprétation sourcée | Alignement sur les annotations décrites par Loghub | Audit des fichiers à réaliser |
| 21/09/2026 | Répartition nominative et liste de tâches préparées | Formaliser les attendus d’organisation du jalon J2 | À confirmer par les quatre membres |

## Usages des assistants IA

| Date | Personne | Outil | Usage | Résultat et vérification | Limite / suite |
|---|---|---|---|---|---|
| 21/09/2026 | Alain | Codex | Aide à la rédaction du courriel et examen du dataset Loghub | Consultation du README Loghub et de la documentation HDFS ; distinction entre anomalie et cause de panne | Données non téléchargées et faisabilité non testée |
| 21/09/2026 | Alain | Codex | Vérification des attendus du PDF et préparation de l’organisation | Lecture des pages sur le cadrage, les jalons et les livrables ; fichiers de cadrage et tâches préparés | Relecture du groupe requise ; board et classeur partagé non créés |

## Expériences

Pour chaque essai, consigner la date, le responsable, la version du code, les données, les paramètres, la machine, les résultats, les erreurs et la décision qui en découle.

### 06/10/2026 — Première inférence locale du SLM (SCRUM-28, Alain)

- **Commande** : `python -m volet_b.slm.first_inference` · sorties complètes dans `eval/runs/2026-10-06_first_inference/` (non versionné).
- **Modèle** : SmolLM2-1.7B-Instruct, float32, décodage glouton, `repetition_penalty` 1,1, 300 tokens max (`volet_b/slm/configs/generation.yaml`). Transformers 4.57, PyTorch 2.12 CPU.
- **Machine** : i5-1240P, 32 Go, sans GPU NVIDIA.
- **Donnée** : bloc anormal `blk_8362325295506522506` (25 lignes brutes), prompt en français demandant un résumé et un avis normal/anormal.

| Mesure | Valeur |
|---|---|
| Téléchargement du modèle | 14 min 30 (3,4 Go) — bloqué sans le paquet `hf_xet` |
| Chargement | 37 s |
| Mémoire après chargement / pic en génération | 6,8 Go / 16,3 Go |
| Génération | 156 tokens en 258 s → **0,6 token/s** |

- **Qualité (modèle de base, sans RAG ni adaptation)** : la trace contient deux `WARN … Got exception while serving` et un `WARN … Unexpected error trying to delete block … BlockInfo not found in volumeMap`. Le modèle n'en mentionne **aucun**, ne répond pas à la question normal/anormal et invente des éléments absents des logs (« nom de domaine », « ports spéciaux », envoi « vers l'utilisateur »). Point de référence « avant adaptation » pour le rapport.
- **Conséquences** :
  1. L'inférence locale fonctionne (jalon de mi-parcours, preuve pour SCRUM-17).
  2. À 0,6 token/s, évaluer 4 configurations sur 60–100 traces prendrait plusieurs dizaines d'heures en float32 sur CPU. Il faut une version quantifiée (GGUF 4 bits via llama.cpp/Ollama) pour la démo et les évaluations, ou faire tourner les évaluations sur le GPU Kaggle. À décider.
  3. Le modèle ignore les lignes `WARN` : piste pour le prompt, le RAG et les exemples d'adaptation (mettre en avant les événements rares).

### 06/10/2026 — Version 4 bits du SLM : GGUF Q4_K_M contre float32 (SCRUM-57, Alain)

- **Commande** : `python -m volet_b.slm.bench_gguf --backend llamacpp|transformers` · sorties dans `eval/runs/2026-10-06_bench_<backend>/` (non versionné).
- **Modèles** : GGUF officiel `HuggingFaceTB/SmolLM2-1.7B-Instruct-GGUF` (`q4_k_m`, 0,98 Go) via llama-cpp-python 0.3.36 (roue CPU) ; float32 via Transformers comme SCRUM-28. Mêmes paramètres (glouton, pénalité 1,1 sur tout le contexte, 300 tokens max), même bloc, même machine.
- **Prompt** : consigne **avant** les logs (voir constat ci-dessous), identique pour les deux versions.

| Mesure | float32 (Transformers) | Q4_K_M (llama.cpp) |
|---|---|---|
| Taille sur disque | 3,4 Go | 0,98 Go |
| Chargement | 24 s | **2,9 s** |
| Mémoire après chargement / pic | 6,8 Go / 16,1 Go | **2,3 Go / 2,8 Go** |
| Génération | 158 tokens en 246 s → 0,64 token/s | 192 tokens en 101 s → **1,9 token/s** |
| Avis normal/anormal | « normal » (faux) | « anormal » (juste) |

- **Constat sur l'ordre du prompt** : avec le prompt de SCRUM-28 (logs puis consigne), la version 4 bits **recopie les logs** au lieu de les résumer — reproduit même avec 5 lignes de logs ; une question courte sans logs est bien traitée. Consigne placée **avant** les logs → résumé correct. La quantification rend le modèle plus sensible à la place de la consigne. Règle retenue pour tous les prompts du volet B : consigne d'abord, données ensuite.
- **Qualité** : aucune des deux versions ne cite les `WARN`. La 4 bits répond « anormal » mais justifie par un problème de suppression mal interprété ; la float32 conclut « normal » et affirme que le bloc « n'est pas supprimé ». Les deux restent au niveau « avant adaptation ».
- **Débit** : 1,9 token/s ici contre 3,8 token/s mesurés avec un prompt plus court ; le coût vient surtout du traitement du prompt (~2 200 tokens) et de la pénalité appliquée sur tout le contexte.
- **Décision** : la version Q4_K_M sert de modèle local pour la démo et les évaluations (×3 en vitesse, ÷6 en mémoire, réponse au moins aussi bonne). Reste pour le Sprint 2 : convertir le modèle adapté par LoRA en GGUF et brancher le backend llama.cpp dans `generate.py`.

## Réunions

Aucune réunion renseignée à ce stade. Pour chaque réunion, noter les participants, les points examinés, les décisions, les responsables et les échéances.
