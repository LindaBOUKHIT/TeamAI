# TeamAI — Journal du projet

Point de départ local à partager avec le groupe. Ce fichier ne remplace pas à lui seul le classeur partagé demandé dans le sujet.

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
| 06/10/2026 | Entraînement LoRA sur GPU gratuit en ligne (Kaggle, Colab en secours) | Pas de GPU NVIDIA en local ; QLoRA exige CUDA | SCRUM-15 ; l'adaptation reste faite, seul le lieu d'entraînement change |

## Usages des assistants IA

| Date | Personne | Outil | Usage | Résultat et vérification | Limite / suite |
|---|---|---|---|---|---|
| 21/09/2026 | Alain | Codex | Aide à la rédaction du courriel et examen du dataset Loghub | Consultation du README Loghub et de la documentation HDFS ; distinction entre anomalie et cause de panne | Données non téléchargées et faisabilité non testée |
| 21/09/2026 | Alain | Codex | Vérification des attendus du PDF et préparation de l’organisation | Lecture des pages sur le cadrage, les jalons et les livrables ; fichiers de cadrage et tâches préparés | Relecture du groupe requise ; board et classeur partagé non créés |
| 06/10/2026 | Alain | Claude Code + connecteur MCP Atlassian | Création du board Jira (epics, sprints, tâches, dépendances), téléchargement et audit de HDFS_v1, structure du dépôt, relevé de la machine | Données vérifiées (MD5, statistiques recalculées) ; tickets relus | Répartition et contrats à valider en réunion (SCRUM-55) |

## Expériences

Aucune expérience technique renseignée à ce stade. Pour chaque essai, consigner la date, le responsable, la version du code, les données, les paramètres, la machine, les résultats, les erreurs et la décision qui en découle.

## Réunions

Aucune réunion renseignée à ce stade. Pour chaque réunion, noter les participants, les points examinés, les décisions, les responsables et les échéances.
