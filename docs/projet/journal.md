# TeamAI — Journal du projet

Point de départ local à partager avec le groupe. Ce fichier ne remplace pas à lui seul le classeur partagé demandé dans le sujet.

Classeur partagé : [TeamAI : Classeur de suivi](https://docs.google.com/spreadsheets/d/1W8IjMS2L9-SxDK-FGQvjVIdG9NSwmwVBR8dpT5AitLg/edit?gid=1148275204#gid=1148275204).

## Décisions

| Date | Décision ou proposition | Motif | État |
|---|---|---|---|
| 21/09/2026 | Proposition d’un sujet sur les logs HDFS en remplacement du support client | Nouveau sujet présenté dans le texte du groupe et examiné avec un assistant IA | Validation enseignant non connue |
| 21/09/2026 | Périmètre initial proposé : HDFS_v1, classification binaire par trace et interprétation sourcée | Alignement sur les annotations décrites par Loghub | Audit des fichiers à réaliser |
| 21/09/2026 | Répartition nominative et liste de tâches préparées | Formaliser les attendus d’organisation du jalon J2 | À confirmer par les quatre membres |
| 06/10/2026 | Board Jira structuré : 7 epics, 5 sprints alignés sur les jalons, tâches avec responsable, relecteur et critère de fin | Jalon de mi-parcours manqué ; tickets à créer avant le travail | Fait (SCRUM-5 à SCRUM-55) |
| 06/10/2026 | Dépôt : `main` = production, `dev` = travail en cours, une branche et une PR par ticket | Traçabilité exigée par le sujet | Fait (SCRUM-13) |
| 06/10/2026 | Structure du dépôt d'Alain conservée sur `main` ; arborescence parallèle de Linda abandonnée (compatible) | Éviter deux structures concurrentes | Décidé avec Linda |
| 06/10/2026 | Inférence et démo du volet B sur la machine d'Alain (i5-1240P, 32 Go, sans GPU NVIDIA) | Seule machine relevée à ce jour ; RAM suffisante pour un modèle de 1,7 B | SCRUM-15, à confirmer par SCRUM-28 |
| 06/10/2026 | Entraînement LoRA envisagé sur GPU en ligne (Kaggle, Colab en secours) | Machine d'Alain sans GPU NVIDIA ; essai court requis | Proposition SCRUM-15 ; disponibilité et faisabilité à vérifier dans SCRUM-29 |
| 08/10/2026 | Rattrapage de SCRUM-15 : relevé d'Alain vérifié, premiers essais SLM référencés, informations manquantes explicites | Avancer avec les éléments vérifiables | PR #3 à compléter par Bachar, Linda et Nassim puis relire par Linda ; ticket ouvert |

## Usages des assistants IA

| Date | Personne | Outil | Usage | Résultat et vérification | Limite / suite |
|---|---|---|---|---|---|
| 21/09/2026 | Alain | Codex | Aide à la rédaction du courriel et examen du dataset Loghub | Consultation du README Loghub et de la documentation HDFS ; distinction entre anomalie et cause de panne | Données non téléchargées et faisabilité non testée |
| 21/09/2026 | Alain | Codex | Vérification des attendus du PDF et préparation de l’organisation | Lecture des pages sur le cadrage, les jalons et les livrables ; fichiers de cadrage et tâches préparés | Relecture du groupe requise ; board et classeur partagé non créés |
| 06/10/2026 | Alain | Claude Code + connecteur MCP Atlassian | Création du board Jira (epics, sprints, tâches, dépendances), téléchargement et audit de HDFS_v1, structure du dépôt, relevé de la machine | Données vérifiées (MD5, statistiques recalculées) ; tickets relus | Répartition et contrats à valider en réunion (SCRUM-55) |
| 08/10/2026 | Alain | Codex | Complément de SCRUM-15 | Lecture du ticket et de la PR #3, relevé CPU/RAM/GPU/disque et comparaison aux essais documentés dans les PR #4 et #6 | Environnements des camarades et accès GPU non connus ; validation du groupe requise |
| 13/10/2026 | Linda | Codex | Aide à la construction du corpus documentaire HDFS et aux corrections demandées dans la revue de SCRUM-30 | Couverture des templates E1–E29 documentée ; sections de liens exclues ; empreintes SHA-256 ajoutées ; reconstruction locale sans téléchargement : 51 passages par section et 28 par fenêtre glissante | Suite à la relecture du reviewer ; tests automatisés non exécutés |
| 13/10/2026 | Linda | Claude Code + connecteurs Atlassian et GitHub (`gh`) | Préparation des relectures des PR #3, #5, #6 et #18 ; résolution des conflits de fusion sur #5, #6 et #19 ; automatisation Jira « PR fusionnée dans dev → Terminé » | Relectures vérifiées sur le code et relues par Linda avant envoi ; conflits résolus en gardant les deux versions ; CI verte après chaque résolution | Approbations et fusions faites par Linda |
| 13/10/2026 | Linda | Claude Code | SCRUM-26 : génération de `vocab.json`, prétraitement Python et JavaScript, tests de parité | Parité vérifiée par les tests : 2 000/2 000 blocs de l'échantillon (Python et JS), cas limites partagés, et 575 061/575 061 blocs du corpus complet en Python | Intégration dans l'interface du site (SCRUM-27, Bachar) à faire |
| 13/10/2026 | Linda | Claude Code | SCRUM-31 : alignement de la grille d'annotation sur C5 v1.1, rédaction des 3 exemples de calibration, contrôles automatiques des sources et des splits | Faits vérifiés ligne par ligne sur les logs bruts de `data/sample/` ; sources présentes dans `chunks.jsonl` ; exemples lus et validés par Linda | Hypothèses et cas d'abstention à discuter en équipe ; `reviewed_by` renseigné après la relecture |

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

- **Constat sur l'ordre du prompt** : avec le prompt de SCRUM-28 (logs puis consigne), la version 4 bits **recopie les logs** au lieu de les résumer — reproduit même avec 5 lignes de logs ; une question courte sans logs est bien traitée. Consigne placée **avant** les logs → résumé correct. Cette sensibilité est observée avec Q4_K_M **sous llama.cpp** : l'expérience ne sépare pas l'effet de la quantification de celui du backend (gabarit de conversation, échantillonneur). Règle retenue pour tous les prompts du volet B : consigne d'abord, données ensuite.
- **Qualité** : aucune des deux versions ne cite les `WARN`. La 4 bits répond « anormal » mais justifie par un problème de suppression mal interprété ; la float32 conclut « normal » et affirme que le bloc « n'est pas supprimé ». Une seule trace : aucune conclusion générale sur la qualité.
- **Débit** : 1,9 token/s ici contre 3,8 token/s mesurés avec un prompt plus court ; le coût vient surtout du traitement du prompt (~2 200 tokens) et de la pénalité appliquée sur tout le contexte.
- **Limites (relevées le 13/10)** : mesure faite avec l'ancienne version de `generate.py` (avant la normalisation du cache de SCRUM-28) ; une seule trace, une seule exécution par backend ; les dossiers de sortie d'un même jour s'écrasaient. Ces chiffres sont des **observations**, pas une comparaison contrôlée. Exemple : relancé le 13/10 avec le script corrigé (même bloc, même GGUF, révision figée), llama.cpp donne la même réponse de 192 tokens mais à 0,71 token/s au lieu de 1,9, la machine étant chargée par d'autres processus ; la mémoire est identique (2,28 / 2,77 GiB).
- **Décision provisoire** : Q4_K_M est le candidat pour la démo et les évaluations, au vu de l'ordre de grandeur (environ ×3 en débit et une mémoire de pic bien plus faible sur cette trace). À confirmer par une comparaison contrôlée sur le code corrigé et plusieurs traces de **validation** (SCRUM-38). Reste pour le Sprint 2 : convertir le modèle adapté par LoRA en GGUF et brancher le backend llama.cpp derrière `generate()`.

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

### 13/10/2026 — Alignement des contrats sur le code fusionné (SCRUM-55, Alain)

Un audit croisé des branches (Codex, lecture seule, vérifié par Alain) montre que la v1 de la PR #7 imposait un regroupement des séquences identiques entre splits, alors que SCRUM-20 a livré, conformément au contrat alors en vigueur sur `dev`, un tirage stratifié bloc par bloc sur lequel reposent déjà les résultats de la baseline SCRUM-24. Proposition retenue dans la v1.1 : `C4-bloc` reste le protocole de référence, avec des métriques du test toujours rapportées aussi sur les séquences inédites (`unseen_seq`) ; un regroupement éventuel devient une variante nommée `C4-groupe`. Mises à jour associées : état réel de C2 (inconnus → SCRUM-26), migration des métadonnées C3 du spike, sources vides autorisées et règles d'abstention C5, dossier d'exécution unique en C7. À valider par Nassim (C4) et le groupe avant fusion.

### Usage d'assistant — 08/10/2026

Alain utilise Codex pour relire SCRUM-55, examiner le chargeur de données et l'interface SLM existante sur la branche SCRUM-28, puis préciser les sept formats. Vérification : cohérence documentaire avec le code observé et contrôle syntaxique des exemples JSON. Limite : pas de validation collective, pas de modèle ONNX ou de retrieval livré par ce travail.

## Suivi du 12/10/2026 — SCRUM-15 (Alain)

Vérification GitHub : la PR #4 de SCRUM-28 a été approuvée par Linda et fusionnée le 11/10. La PR #3 de SCRUM-15 reste ouverte, sans avis de relecture au contrôle du 12/10. La ligne de Linda est renseignée sur sa branche ; les environnements de Bachar et Nassim restent manquants. Aucune validation collective du choix des machines n'est attestée.

La branche de SCRUM-15 intègre les changements approuvés de `dev`, puis le relevé est actualisé avec les mesures du 08/10 et le chemin de cache observé. Alain utilise Codex pour ces vérifications et corrections documentaires. Le ticket ne remplit pas encore son critère de clôture ; la mise à jour Jira est également indisponible dans cette session faute d'outils MCP TeamAI.

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



## 2026-10-16 — SCRUM-23 — Bachar Ben Slama

Création du site statique v0 avec Vite et ONNX Runtime Web :
- Page d’accueil et bouton de test sur une séquence artificielle.
- Chargement du vocabulaire C2 et du modèle ONNX C3.
- Vérification des empreintes SHA-256 du modèle et du vocabulaire.
- Mise en cache du modèle avec la Cache API.
- Avertissement explicite pour le modèle factice de SCRUM-22.
- Ajout des commandes build et preview.
- Configuration du chemin /TeamAI/ pour GitHub Pages.
- Adaptation du workflow : Node.js 24, tests et build.
- Exclusion du dossier généré dist de Git.

Vérifications locales :
- Les 11 tests de prétraitement passent.
- Inférence fonctionnelle sur la page locale et en preview.
- Réutilisation du cache confirmée après actualisation.
- Score observé : 0,46178886 sur la séquence artificielle
  E5, E22, E5, E11. Ce score n’a aucune valeur prédictive.

Usage IA : assistance de Codex pour proposer le code du site,
le chargement du modèle, la mise en cache et la configuration
de déploiement. Manipulations et vérifications locales par Bachar.

Publication publique restant à vérifier après passage vers main
via SCRUM-17. Relecture par Nassim à effectuer.

## 2026-10-16 — SCRUM-25 — Bachar Ben Slama

Entraînement du BiLSTM sur HDFS_v1 avec les splits officiels
SCRUM-20. Le hash de splits.csv correspond exactement à celui
de l’équipe : f504592cb7ac13b8b7e5d532a336b4e3641ec441a863c5efafd164faa2a43f22.

Run : 20261016T184412Z_4f3011f2_bilstm.
Architecture : embedding 16, BiLSTM 32 par direction,
agrégation moyenne hors padding, 13 361 paramètres.
Entraînement CPU : 5 époques, batch 512, seed 42,
Adam avec learning rate 0,001 et perte pondérée.
Durée entraînement et validation : environ 352 secondes.

Sélection sur validation uniquement :
- Époque retenue : 5.
- Seuil : 0,99, borne supérieure de la grille explorée.
- Macro-F1 globale : 0,995514, contre 0,989698 pour la baseline.
- Macro-F1 sur les 1 929 séquences inédites : 0,976748,
  contre 0,961848 pour la baseline.
- Validation globale : 23 fausses alertes et 21 anomalies manquées.
- Baseline : 103 fausses alertes et aucune anomalie manquée.

Le BiLSTM réduit les fausses alertes et améliore la macro-F1,
avec une baisse du rappel. La comparaison utilise les résultats
publiés par Nassim ; la baseline n’a pas été réentraînée ici.
Le test officiel n’a pas été évalué.

Export ONNX : environ 55,5 Ko, conforme au contrat C3.
Parité Python sur 86 259 blocs de validation :
écart maximal 1,1921e-7 et aucune différence de classification.
Parité navigateur WASM sur dix séquences de validation :
écart maximal 4,3277e-8. Batchs 1, 3 et 10 vérifiés.

Le modèle entraîné et ses métadonnées remplacent le spike
sur la branche SCRUM-25. Résumés dans
eval/results/SCRUM-25-bilstm-v1/ ; checkpoint et prédictions
détaillées conservés localement dans eval/runs/.

Usage IA : assistance de Codex pour proposer les scripts de
préparation, d’entraînement, d’export et de contrôle de parité,
corriger un problème d’import et interpréter les résultats.
Exécution et vérifications locales réalisées par Bachar.

Relecture par Nassim et vérification de la CI à effectuer.
Intégration et vérification sur le site complet restant à confirmer
après combinaison avec SCRUM-23.


## 2026-10-23 — SCRUM-27 — Bachar Ben Slama

Ajout du parcours fonctionnel du volet A :
- Saisie de logs par copier-coller.
- Import de fichier texte limité à 10 Mo.
- Chargement des cinq exemples disponibles.
- Tableau par bloc : classe, score, longueur, événements tronqués,
  inconnus encodés et avertissements.
- Filtre « anomalies seulement » et export CSV des lignes affichées.
- Seuil lu dans detector.meta.json, sans réglage depuis l’interface.
- Rejet des entrées sans bloc reconnu et effacement des anciens
  résultats lors d’un changement de source.
- Signalement des lignes ignorées et des événements inconnus.

La complétude des blocs n’est pas déduite automatiquement :
elle est indiquée comme non vérifiée. L’exemple volontairement
incomplet est signalé lorsqu’il est chargé par le sélecteur.

Vérifications locales :
- 16 tests JavaScript réussis.
- Build de production réussi.
- Exemple multi-blocs : trois blocs, dont une anomalie.
- Import du même fichier : résultats identiques.
- Filtre et CSV vérifiés : une anomalie exportée.
- Entrée invalide rejetée.
- Lignes ignorées, événement inconnu et exemple incomplet signalés.

Le traitement utilise des lots de 64 blocs ; le Web Worker est
prévu dans SCRUM-40. Aucun test officiel utilisé pour ces essais.

Usage IA : assistance de Codex pour proposer l’interface,
le raccordement au modèle, l’export CSV et les tests.
Manipulations et vérifications locales réalisées par Bachar.

Relecture par Nassim à effectuer. Publication publique et tag
v0.2-J3 à vérifier après intégration et PR dev vers main.

## 2026-10-23 — SCRUM-62 — Bachar Ben Slama

Analyse du seuil du BiLSTM v1 en réponse aux retours sur SCRUM-25.
Les poids restent inchangés ; seule la décision de classification
est ajustée, sur la validation uniquement.

Les scores des 21 anomalies initialement manquées ont été examinés.
Le script explore les seuils distincts et une grille de 0 à 1,
avec courbes précision, rappel et F1 de la classe anomalie.

Choix proposé : seuil 0,40814146399497986, maximisant le F1 anomalie
avec au maximum deux anomalies manquées.
Le même seuil est optimal sous la contrainte d’une seule manquée.

Validation globale :
- Ancien seuil 0,99 : 23 fausses alertes, 21 anomalies manquées.
- Nouveau seuil : 59 fausses alertes, 1 anomalie manquée.
- Rappel anomalie : 0,999604.
- F1 anomalie : 0,988254.
- Macro-F1 : 0,993948, contre 0,995514 auparavant.

Validation sur les 1 929 séquences inédites :
- 41 fausses alertes et 1 anomalie manquée.
- Auparavant : 19 fausses alertes et 17 anomalies manquées.
- Rappel anomalie : 0,998131.
- Macro-F1 : 0,973439.

Le compromis privilégie le rappel : 20 anomalies récupérées pour
36 fausses alertes supplémentaires sur la validation globale.
Le candidat sans anomalie manquée entraîne 295 fausses alertes.

Métadonnées du site actualisées : threshold et val_macro_f1,
avec référence à l’analyse et à l’objectif de sélection.

Parité au nouveau seuil :
- Python / ONNX : 86 259 blocs, aucune différence de classe,
  écart maximal 1,1921e-7.
- Navigateur WASM : dix cas proches du seuil, dont un exactement
  au seuil ; batchs 1, 3 et 10 ; aucune différence de classe,
  écart maximal 5,9605e-8.

Résultats :
eval/results/SCRUM-62_20261023T153242Z_690fcb/

Aucun test officiel évalué. SCRUM-44 est réservé à Nassim,
après fixation du seuil et de la version finale du modèle.
La quantification SCRUM-40 nécessitera une nouvelle vérification
des scores et des décisions au seuil retenu.

Usage IA : assistance de Codex pour les scripts d’analyse,
la vérification de parité, le test navigateur et la documentation.
Exécutions et vérifications locales réalisées par Bachar.

Relecture par Alain à effectuer. Les modifications de SCRUM-27,
encore en attente, ne sont pas intégrées dans cette branche.

## 2026-10-24 — SCRUM-37 — Linda Boukhit

RAG de référence à un agent : trace → requête → passages C6 → `generate()` → réponse C5 vérifiée par code.

- **Retrieval** : 51 passages encodés avec `BAAI/bge-small-en-v1.5` (révision `5c38ec7c`), index FAISS exact (cosinus) dans `volet_b/rag/index/` (non versionné, reconstruit par `build_index`). BM25 (`rank-bm25`) et fusion des deux par Reciprocal Rank Fusion.
- **Requête** : les templates bruts (« allocateBlock ») donnaient de mauvais résultats ; chaque événement est paraphrasé en anglais (`volet_b/rag/event_descriptions.json`, écrit à partir des templates seuls).
- **Mesure sur la validation** (`eval/results/SCRUM-37/retrieval_val.json`, 306 blocs `val` de `data/sample/`, référence : table de couverture de `corpus_rag.md`) :

| Méthode | Requête | Templates trouvés (top 3) | Rappel@3 traces |
|---|---|---:|---:|
| dense | template brut | 3/10 | 0,323 |
| dense | paraphrase | 6/10 | 0,348 |
| BM25 | paraphrase | 6/10 | 0,695 |
| hybride (retenu) | paraphrase | 6/10 | 0,664 |

- **Décision** : méthode hybride par défaut. BM25 seul est légèrement meilleur ici, mais l'hybride garde les embeddings, plus robustes aux reformulations libres des agents (SCRUM-42). Les deux passages « Safemode » remontent souvent dans le top 3 avec les embeddings seuls (passages très généraux).
- **Limites** : la référence (table de couverture) et les paraphrases ont été écrites par l'équipe : ce n'est pas un jugement indépendant de la pertinence. Les traces de validation de l'échantillon répètent peu de séquences distinctes. Le test n'a pas été utilisé.
- **Seuil `min_score` (liste vide → abstention)** : étudié puis non activé. Sur les passages du top 3 des traces de validation, la médiane du cosinus est de 0,779 pour les pertinents et de 0,813 pour les non pertinents (les passages généraux comme « Safemode » sont très proches de tout) ; les scores BM25 se chevauchent (médianes 79,7 et 60,5) et dépendent de la longueur de la requête. Un seuil retirerait autant de passages pertinents que de non pertinents. Le cas « aucun passage utile » reste traité par la consigne (`sources: []` autorisé) et par le contrôle C5. Mesure reproductible : champ `score_separation` de `retrieval_val.json`.
- **Garde-fou** : l'agent refuse tout bloc du split `test`, qu'il vienne de `--block` ou d'un fichier `--file`.
- **Agent** : `python -m volet_b.agents.single_agent` vérifié de bout en bout en mode factice (`--mock`) ; l'exécution avec le vrai SLM est à faire sur la machine d'Alain (SCRUM-38).

Usage IA : Linda avec Claude Code pour le code du retrieval, de l'agent et des tests, et pour la comparaison des méthodes ; chiffres recalculés par le script `evaluate_retrieval`.

## 2026-10-26 — SCRUM-57 : backend llama.cpp et conversion LoRA → GGUF

Code écrit avec Codex (gpt-6.1-sol), supervisé par Claude ; relecture d'Alain à faire avant fusion. Transformers float32 reste le défaut de `generate()` ; `backend: llamacpp` charge le GGUF officiel Q4_K_M à la révision figée du banc du 06/10, l'adaptateur GGUF étant passé par `lora_path`.

Conversions réelles de l'adaptateur `essai` (llama.cpp cloné au commit `d854d98`) :
- route b, adaptateur seul : `adapter.gguf` f16 de 3,1 Mo, chargé sur la base Q4_K_M ;
- route a, fusion PEFT → HF → GGUF f16 → Q4_K_M : 3 264 → 1 005 Mio. Elle exigeait `sentencepiece`, ajouté à l'extra `volet_b_gguf`. Le modèle fusionné se charge et répond à une consigne courte (`{"ok": true}`, 5 tokens en 0,81 s) ; `meta.json` garde `inference_validated: false`, cette vérification n'étant pas une évaluation.

Comparaison sur cinq blocs `val` du sample (preuve : [`eval/results/SCRUM-57/`](../../eval/results/SCRUM-57/README.md)) : llama.cpp Q4_K_M donne environ ×1,6 en débit (2,4 contre 1,5 token/s), un pic RSS de 2,1–2,8 GiB contre 9,3–9,9 GiB et un chargement de 1,7 s contre 11,5 s. Qualité : 0/5 sorties conformes C5 pour les deux backends, avec ou sans adaptateur ; le modèle rend les bonnes clés avec des champs vides. Cette comparaison ne départage donc pas la qualité, et le backend reste confondu avec la quantification. Proposition à valider en équipe : Q4_K_M sous llama.cpp pour la démo ; pour comparer base, LoRA, RAG et agents, un seul couple backend/quantification, à consigner ici.

Correction associée : `validate_answer` plantait lorsqu'un objet apparaissait dans `sources` (sortie llama.cpp) ; il signale désormais l'erreur sans exception (test ajouté).


## 2026-10-26 — SCRUM-38

SCRUM-38 : script des mesures avant adaptation, écrit avec Codex (gpt-6.1-sol), relu par Alain.

Essai réel du 26/10 (pas une mesure) : une trace de calibration du split `train`, vrai SmolLM2 float32 sur CPU, `--limit 1`. En `base`, réponse JSON conforme à C5 (182 tokens, 77 s de génération). En `rag1`, trois passages récupérés, mais le modèle écrit des clés sans guillemets : `invalid_json`, compté comme échec. Mémoire RSS maximale du processus : environ 10,7 Go. Le pipeline complet fonctionne ; le test n'a pas été ouvert.


## 2026-10-27 — SCRUM-63 : passage à Gemma 4 E4B QAT

Correctif de relecture : GPU activé (`n_gpu_layers: -1`) et pré-téléchargement du GGUF documenté.

Le modèle courant du volet B devient Gemma 4 E4B QAT (GGUF Q4_0), révision
`4b4a2c1d584be7264f87aac328a1bc739ce81b6c`, sous llama.cpp. Prompt v16 figé,
contexte 4096, 800 tokens maximum, température 0, seed 42, repeat_penalty 1.0,
réflexion désactivée. SmolLM2 et ses mesures SCRUM-28/SCRUM-57 restent historiques.
La machine cible devient le portable de Nassim (Ryzen 5 8645HS, 32 Go, RTX 3050
Laptop 6 Go) ; versions CUDA/Python et inférence locale à relever par Nassim.

Port de l’extraction des faits via `data.parse_hdfs`, du glossaire restreint aux
codes présents, de la consigne, du schéma, des listes de causes et contrôles v16,
avec correction unique et conservation des deux réponses. L’interface existante
de `generate()` est conservée et transmet désormais le schéma JSON à llama.cpp.
Seul ajout aux contrôles : répétition en boucle ou budget presque épuisé (95 %),
qui déclenche la correction unique sans changer le prompt initial.

Tests sans réseau ni GGUF : 40 prompts reconstruits depuis les lignes val,
40 schémas, consigne et politique vérifiés contre les empreintes originales ;
cas réel F09 ×130 (783 tokens), cas normal et correction unique couverts.
Suite complète `python -m pytest -q` exécutée le 27/10 avec le Python du projet : 89 tests réussis, 5 ignorés, sans réseau ni GGUF. Aucun modèle téléchargé ou exécuté, aucun service externe appelé.

[Trace SCRUM-63](../../eval/results/SCRUM-63/README.md) : choix v6–v11,
réglage v12–v16 et validation unique de 40 nouveaux blocs val. Les contrôles
formels se maintiennent, mais chronologies et causalités restent parfois fausses,
et un résumé boucle ; 0,19 hypothèse par bloc avec indice d’incident. Ces résultats
ne valident ni une détection par le SLM ni la fidélité globale des explications.

Usage IA : code écrit avec Codex gpt-6.1-sol, supervisé par Claude ; relecture d'Alain à faire.

## 2026-10-27 — SCRUM-38 : mesures base alignées sur le pipeline v16 ; rag1 reporté

Correctif de relecture : hypothèses par bloc rapportées au nombre de blocs du groupe.

`base` reconstruit les faits depuis les lignes brutes C5 et appelle le pipeline
v16 figé : schéma fermé, contrôles, correction unique et anti-boucle. Aucune
annotation n'atteint le prompt. Le code `volet_b/slm/v16/` reste inchangé.
`rag1` est refusé explicitement en attendant une variante v16 + RAG figée
(SCRUM-42/SCRUM-45) ; le retrieval de Linda reste disponible.

Le C7 conserve les empreintes de consigne et politique v16, la révision GGUF,
le contexte, le budget, les tentatives et leurs erreurs, arrêts, tokens, temps
et nombre réel d'appels. Les mesures ajoutent contrat v16, faits exacts,
références inexistantes, causes réseau sans appui, enquêtes sans incident,
hypothèses avec/sans incident, anti-boucle et corrections déclenchées/réussies.
Tous les exemples restent au dénominateur. Le RSS est conservé et la VRAM du PID
NVIDIA est relevée si disponible, sans dépendance obligatoire.

À exécuter sur le portable de Nassim après fusion de #40, poids déjà présents,
sans réglage après ouverture du test. Aucun modèle téléchargé ou exécuté,
aucun service externe ni aucune opération git pendant cette mission.

Suite complète lancée par Alain avec le Python du projet le 27/10 : 108 tests réussis, 5 ignorés, en mode factice.

Usage IA : Codex gpt-6.1-sol supervisé par Claude ; relecture d'Alain à faire.
