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

## Réunions

### 08/10/2026 — Préparation de la relecture de SCRUM-28 (Alain)

Lecture du ticket et de la PR #4, puis vérification des quatre artefacts locaux du 06/10 (`metrics.json`, `config.json`, `prompt.txt`, `output.txt`). Les mesures historiques sont conservées. Leur configuration indique le commit `9085610`, antérieur à l'ajout du code SLM ; sans état du code ni hash des sources, ce commit seul ne suffit pas à reconstituer l'exécution.

Corrections : normalisation des arguments du cache pour éviter que `load_model()` et `load_model(None)` chargent deux copies du même modèle ; révision du modèle fixée, option hors ligne et choix explicite du bloc ; versions et hashes consignés ; dossiers distincts pour préserver les exécutions ; README et installation minimale. Sept tests de régression passent sans poids de modèle. Une nouvelle exécution sur le bloc historique est prévue pour vérifier le code corrigé ; les mesures du 06/10 ne deviennent pas rétroactivement celles de ce code.

Usage d'assistant : Alain utilise Codex pour l'examen du code et des preuves, les corrections et les tests. Aucune validation de Linda ou fusion n'est attestée. La qualité du modèle et les composants RAG/LoRA restent hors de cette vérification technique.

Aucune réunion renseignée à ce stade. Pour chaque réunion, noter les participants, les points examinés, les décisions, les responsables et les échéances.
