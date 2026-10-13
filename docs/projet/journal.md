# TeamAI — Journal du projet

Point de départ local à partager avec le groupe. Ce fichier ne remplace pas à lui seul le classeur partagé demandé dans le sujet.

Classeur partagé : [TeamAI : Classeur de suivi](https://docs.google.com/spreadsheets/d/1W8IjMS2L9-SxDK-FGQvjVIdG9NSwmwVBR8dpT5AitLg/edit?gid=1148275204#gid=1148275204).

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

- **Qualité (modèle de base, sans RAG ni adaptation)** : la trace contient deux `WARN … Got exception while serving` et un `WARN … Unexpected error trying to delete block … BlockInfo not found in volumeMap`. Le modèle n'en mentionne **aucun**, ne répond pas à la question normal/anormal et invente des éléments absents des logs (« nom de domaine », « ports spéciaux », envoi « vers l'utilisateur »). Exemple de développement pour le rapport, sans évaluation générale de qualité.
- **Conséquences** :
  1. L'inférence locale fonctionne (jalon de mi-parcours, preuve pour SCRUM-17).
  2. À 0,6 token/s, évaluer 4 configurations sur 60–100 traces prendrait plusieurs dizaines d'heures en float32 sur CPU. Il faut une version quantifiée (GGUF 4 bits via llama.cpp/Ollama) pour la démo et les évaluations, ou faire tourner les évaluations sur le GPU Kaggle. À décider.
  3. Le modèle ignore les lignes `WARN` : piste pour le prompt, le RAG et les exemples d'adaptation (mettre en avant les événements rares).

### 08/10/2026 — Préparation de la relecture de SCRUM-28 (Alain)

Lecture du ticket et de la PR #4, puis vérification des quatre artefacts locaux du 06/10 (`metrics.json`, `config.json`, `prompt.txt`, `output.txt`). Les mesures historiques sont conservées. Leur configuration indique le commit `9085610`, antérieur à l'ajout du code SLM ; sans état du code ni hash des sources, ce commit seul ne suffit pas à reconstituer l'exécution.

Corrections : normalisation des arguments du cache pour éviter que `load_model()` et `load_model(None)` chargent deux copies du même modèle ; révision du modèle fixée, option hors ligne et choix explicite du bloc ; versions et hashes consignés ; dossiers distincts pour préserver les exécutions ; README et installation minimale. Sept tests de régression passent sans poids de modèle. Le paquet a été construit et importé hors du dépôt ; les modules SLM et le YAML sont inclus.

Nouvelle inférence réelle hors ligne : `python -m volet_b.slm.first_inference --offline --block-id blk_8362325295506522506 --torch-threads 12`. Le commit de mesure est `4ee4034f30196caf3242632e1a0423a228b533b4`, avec code suivi propre. Les versions exactes, hashes des sources, du prompt et du log sont enregistrés. Le prompt est identique à celui du 06/10 ; les cinq artefacts sont cohérents et conservés dans `eval/runs/2026-10-08_033634_958183Z_816ba8d3_first_inference/`.

| Mesure du 08/10 | Valeur |
|---|---|
| Chargement | 238,0 s |
| RSS après chargement / pic au chargement | 6,77 GiB / 9,84 GiB |
| Pic RSS en génération | 8,00 GiB |
| Génération | 156 tokens en 952,03 s, soit 0,16 token/s |
| GPU / VRAM | Aucun GPU utilisé ; VRAM non mesurée |

La réponse est exactement celle du 06/10 et conserve les omissions et inventions constatées. Le cas de double chargement est corrigé et testé, mais les mesures ne constituent pas une comparaison contrôlée de son effet : le contexte de cache et de charge diffère. Au contrôle de fin d'exécution, 2,2 GiB de RAM étaient disponibles sur la machine ; ce relevé ponctuel n'est pas une mesure de pic ni une explication causale de la latence. Les anciennes mesures restent distinctes. La [preuve compacte](../../eval/results/SCRUM-28/README.md) publie paramètres, mesures, réponse brute et manifeste, sans corpus ni poids.

Décision : conserver SmolLM2-1.7B-Instruct pour cette première preuve, l'inférence aboutissant sur la machine. La vitesse pour la démo et la faisabilité LoRA nécessitent leurs propres essais. Le bloc déjà inspecté sert au développement et doit être exclu du futur test réservé du volet B.

Usage d'assistant : Alain utilise Codex pour l'examen du code et des preuves, les corrections et les tests. Aucune validation de Linda ou fusion n'est attestée. La qualité du modèle et les composants RAG/LoRA restent hors de cette vérification technique.

## Réunions

Aucune réunion renseignée à ce stade. Pour chaque réunion, noter les participants, les points examinés, les décisions, les responsables et les échéances.

### 08/10/2026 — Préparation de la relecture des formats (SCRUM-55, Alain)

Réunion non attestée ; aucune approbation collective enregistrée. Alain prépare la proposition v1 de `docs/contrats.md` pour permettre le travail de chaque composant : classification binaire, troncature/padding explicites, gestion des inconnus à implémenter, formes ONNX, splits sans fuite, sortie SLM et citations vérifiées, traçabilité des évaluations.

Relecture attendue : Nassim pour C1/C2/C4 et le protocole C7 ; Bachar pour C3 ; Linda pour C5/C6 et les consommateurs JavaScript ; Alain pour l'interface SLM et la traçabilité de ses mesures. Les quatre membres valident les choix et consignent leur avis dans la PR. Les différences entre format attendu et code livré sont indiquées dans les contrats.

Suite : corriger selon les retours, consigner les décisions réelles et fusionner la PR vers `dev`. SCRUM-55 reste ouvert jusque-là ; les dépendances SCRUM-25/26/29 restent suivies dans Jira.

### Usage d'assistant — 08/10/2026

Alain utilise Codex pour relire SCRUM-55, examiner le chargeur de données et l'interface SLM existante sur la branche SCRUM-28, puis préciser les sept formats. Vérification : cohérence documentaire avec le code observé et contrôle syntaxique des exemples JSON. Limite : pas de validation collective, pas de modèle ONNX ou de retrieval livré par ce travail.

## 2026-10-11 — SCRUM-22 — Bachar Ben Slama

Création d’un BiLSTM jouet à poids aléatoires et export ONNX
conforme au contrat C3.

Comparaison Python / navigateur avec ONNX Runtime Web (WASM) :
- Dix entrées identiques.
- Batchs testés : 1, 3 et 10.
- Écart maximal : 2,9802e-8, inférieur au seuil de 1e-4.
- Taille du modèle : environ 7,9 Ko.
- Chargement et préparation : 1436,5 ms.
- Inférences pour les batchs 1, 3 et 10 : 33,8 / 2,1 / 2,1 ms.

Usage IA : assistance de Codex pour préparer l’environnement,
proposer le script Python et la page de comparaison, et interpréter
les résultats. Exécution et vérification réalisées par Bachar.

Relecture par Nassim à effectuer avant fusion.
