# TeamAI — Cadrage du projet NLP 2

21 septembre 2026 — Alain, Nassim, Bachar et Linda

Sujet proposé : détection et aide à l’interprétation d’anomalies dans des logs HDFS.

## État du projet

Le [dépôt Git du groupe](https://github.com/LindaBOUKHIT/TeamAI) existe. Le sujet est rédigé ; sa validation par l’enseignant n’est pas connue. Le corpus HDFS_v1 est un candidat, pas un jeu de données déjà préparé. Le tableau de tâches reste à créer. L’exécution locale est prévue sur l’ordinateur d’un membre du groupe, dont les caractéristiques restent à relever.

Cette fiche et les tâches associées constituent une proposition d’organisation. Les responsabilités ci-dessous doivent être confirmées par le groupe avant d’être présentées comme définitives.

## Périmètre

**Volet A.** Une application publique, hébergée gratuitement, classe des traces HDFS complètes en « normal » ou « anomalie ». Le modèle est entraîné par le groupe puis exécuté dans le navigateur. Le site accepte le format documenté par le projet, affiche les résultats et permet leur export. Le BiLSTM sera comparé à une référence simple.

**Volet B.** Une application locale reçoit une trace, en résume les événements et propose une interprétation appuyée sur une documentation HDFS. Un SLM est adapté sur des exemples vérifiés. Trois agents partagent le même modèle pour rechercher, rédiger et contrôler, avec une seule reprise autorisée. Leur apport est comparé à une version à un agent.

**Hors périmètre.** Supervision en temps réel, formats de logs autres que HDFS, collecte sur une infrastructure de production, diagnostic causal garanti et correction automatique d’incidents. Les deux applications fonctionnent indépendamment.

## Répartition proposée

| Personne | Domaine principal | Domaine secondaire et binôme |
|---|---|---|
| Nassim | Audit HDFS_v1, préparation des traces, séparation apprentissage/validation/test | Relecture du classifieur avec Bachar |
| Bachar | Modèle de classification, comparaison à la référence, export ONNX et application web | Vérification des données avec Nassim |
| Alain | Essais du SLM, protocole d’adaptation LoRA et mesures avant/après | Relecture du RAG et des agents avec Linda |
| Linda | Documentation HDFS, recherche documentaire, orchestration et interface locale | Évaluation de l’adaptation avec Alain |

Tous participent à l’annotation des exemples, à l’évaluation humaine, au rapport et aux démonstrations. L’évaluation n’est pas confiée uniquement à la personne ayant développé le composant. Chaque membre doit pouvoir expliquer les deux volets.

## Environnement envisagé et informations à déclarer

Socle proposé : Python avec environnement isolé pour la préparation et l’apprentissage ; PyTorch pour les modèles ; ONNX Runtime Web et JavaScript pour le navigateur ; Transformers et PEFT pour le SLM et son adaptation. Les versions seront consignées après le premier essai fonctionnel. Aucun environnement commun installé n’est affirmé à ce stade.

| Personne | Système et éditeur utilisés | Environnement Python | Machine / rôle matériel |
|---|---|---|---|
| Alain | À renseigner | À renseigner | À renseigner |
| Nassim | À renseigner | À renseigner | À renseigner |
| Bachar | À renseigner | À renseigner | À renseigner |
| Linda | À renseigner | À renseigner | À renseigner |

Pour la machine SLM : noter le propriétaire, le processeur, la RAM, le GPU, la VRAM et l’espace disque disponible. Tester l’inférence et l’adaptation séparément.

Modèle candidat : SmolLM2-1.7B-Instruct. Pour 1,7 milliard de paramètres, les seuls poids représentent théoriquement environ 0,85 Go en 4 bits ou 3,4 Go en 16 bits. Ces calculs excluent les métadonnées, les activations, le cache et les bibliothèques ; ils ne constituent pas une estimation de la mémoire totale du programme. La mémoire réelle et la faisabilité de LoRA restent à mesurer. Réduire le modèle ou le contexte si nécessaire, sans remplacer silencieusement l’adaptation par du prompting.

## Hypothèses et risques

| Hypothèse ou risque | Vérification et réponse prévue |
|---|---|
| Le sous-ensemble contient assez de traces anormales | Compter les classes avant l’échantillonnage et publier leur répartition. Conserver des traces complètes. |
| La classification peut profiter d’informations artificielles | Séparer par bloc, contrôler les doublons et normaliser les identifiants. Apprendre le prétraitement sur l’entraînement uniquement. |
| L’export du BiLSTM fonctionne dans le navigateur | Tester rapidement un petit modèle et comparer les prédictions Python / navigateur avant de construire toute l’interface. |
| Le matériel permet l’adaptation | Réaliser un essai court ; diminuer la taille du modèle, du contexte ou du lot si nécessaire et prévenir l’enseignant si le blocage persiste. |
| Les explications ne sont pas disponibles dans le corpus | Construire un petit corpus annoté en s’appuyant sur les traces et une documentation versionnée. Séparer les exemples d’adaptation et d’évaluation. |
| La documentation ne correspond pas au système des traces | Identifier les versions autant que possible, consigner les écarts et éviter de transformer une procédure générale en cause avérée. |
| Les agents augmentent la latence sans améliorer la réponse | Limiter les appels et mesurer leur apport face à un seul agent. Documenter aussi un résultat négatif. |
| Un membre devient indisponible | Binômes, documentation de lancement et revue régulière des travaux. |

## Critères de réussite

- Le volet A fonctionne à une URL publique avant la soutenance et exécute réellement le modèle côté navigateur.
- La préparation des données est reproductible et les performances sur un test réservé sont rapportées : précision/rappel des anomalies, macro-F1 et matrice de confusion.
- Le volet B fonctionne sur la machine retenue, affiche ses sources et distingue observation, hypothèse et information manquante.
- L’adaptation du SLM est effectivement réalisée et évaluée avant/après à protocole comparable.
- L’apport des agents est mesuré : exactitude des faits, pertinence des sources, abstention, latence et mémoire. Un gain n’est pas présupposé.
- Les scripts, versions, décisions, limites et résultats permettent à un autre membre de reproduire la démonstration.

## Suivi et échéances

Board proposé : GitHub Projects associé à TeamAI, avec « À faire », « En cours », « À relire », « Terminé ». Ajouter les quatre membres et donner accès à l’enseignant. Chaque tâche porte un responsable, un relecteur, une échéance et un critère de fin. Le board n’a pas encore été créé ; les tâches du fichier Taches_Loghub.md sont préparatoires.

Organisation proposée : deux points courts par semaine, tickets créés avant le travail, branches par tâche et revue par le binôme avant intégration. Consigner les décisions et les usages d’IA au fil du projet.

| Échéance | Résultat attendu |
|---|---|
| J2 — 21 septembre | Board créé avec membres et colonnes ; environnement déclaré ; étude des deux volets et du matériel ; cadrage et répartition initiale. |
| 23 septembre — objectif interne | Corpus audité, machine identifiée, essai d’export ONNX et essai d’inférence. |
| 1er octobre | Volet A minimal déployé, première inférence locale réussie, tag Git et capture du board. |
| 16 octobre | Volet A fonctionnel, adaptation engagée, supports préparés même incomplets ; rédaction du rapport commencée au plus tard à cette date. |
| Avant le 7 décembre | Site fonctionnel, V1 du rapport PDF remise ; expériences et démonstrations préparées. |
| 7 décembre | Pitch et présentation transmis, démonstration locale ou vidéo, soutenance. |

Le sujet comporte des formulations de dates contradictoires. Cette proposition suit les dates explicites du tableau des jalons, notamment le 1er octobre ; confirmer toute modification avec l’enseignant. La soumission initiale est indiquée avant le 20 septembre : la préparation actuelle ne prouve pas que cet envoi a été effectué.

## Contrôle avant transmission

- Confirmer les responsabilités nominatives et l’organisation à quatre.
- Compléter les environnements et les caractéristiques de la machine SLM.
- Créer réellement le board, ajouter les membres et vérifier l’accès de l’enseignant.
- Partager le suivi et le journal d’usage de l’IA. Le journal Markdown fourni est un point de départ ; le classeur partagé demandé par le sujet reste à mettre en place.
- Joindre cette fiche au courriel Loghub et ajouter le lien réel du board. Les anciennes propositions « support client » ne correspondent plus au sujet retenu.
