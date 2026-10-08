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

Aucune expérience technique renseignée à ce stade. Pour chaque essai, consigner la date, le responsable, la version du code, les données, les paramètres, la machine, les résultats, les erreurs et la décision qui en découle.

## Réunions

Aucune réunion renseignée à ce stade. Pour chaque réunion, noter les participants, les points examinés, les décisions, les responsables et les échéances.

### 08/10/2026 — Préparation de la relecture des formats (SCRUM-55, Alain)

Réunion non attestée ; aucune approbation collective enregistrée. Alain prépare la proposition v1 de `docs/contrats.md` pour permettre le travail de chaque composant : classification binaire, troncature/padding explicites, gestion des inconnus à implémenter, formes ONNX, splits sans fuite, sortie SLM et citations vérifiées, traçabilité des évaluations.

Relecture attendue : Nassim pour C1/C2/C4 et le protocole C7 ; Bachar pour C3 ; Linda pour C5/C6 et les consommateurs JavaScript ; Alain pour l'interface SLM et la traçabilité de ses mesures. Les quatre membres valident les choix et consignent leur avis dans la PR. Les différences entre format attendu et code livré sont indiquées dans les contrats.

Suite : corriger selon les retours, consigner les décisions réelles et fusionner la PR vers `dev`. SCRUM-55 reste ouvert jusque-là ; les dépendances SCRUM-25/26/29 restent suivies dans Jira.

### Usage d'assistant — 08/10/2026

Alain utilise Codex pour relire SCRUM-55, examiner le chargeur de données et l'interface SLM existante sur la branche SCRUM-28, puis préciser les sept formats. Vérification : cohérence documentaire avec le code observé et contrôle syntaxique des exemples JSON. Limite : pas de validation collective, pas de modèle ONNX ou de retrieval livré par ce travail.
