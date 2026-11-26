# Retour d’expérience — Bachar Ben Slama

## Mon rôle

J’ai principalement travaillé sur le volet A, la détection d’anomalies dans les logs HDFS. J’ai réalisé le premier essai d’export ONNX et d’inférence dans le navigateur (SCRUM-22), le site initial (SCRUM-23), puis l’entraînement et l’export du BiLSTM (SCRUM-25). J’ai ensuite développé la saisie des logs, le traitement par lot, le filtre des anomalies et l’export CSV (SCRUM-27).

J’ai également analysé le seuil de décision (SCRUM-62), comparé les versions FP32 et INT8 et intégré un Web Worker (SCRUM-40). Pour SCRUM-41, j’ai ajouté le détail des événements par bloc et corrigé leur affichage sur mobile. Enfin, j’ai contribué aux vérifications et relectures des corrigés du volet B dans SCRUM-35.

## Ce que j’ai appris techniquement

- **Entraîner et intégrer un modèle.** J’ai entraîné un BiLSTM à partir de poids aléatoires sur HDFS_v1, puis exporté le modèle en ONNX pour l’exécuter avec ONNX Runtime Web. J’ai appris à vérifier la cohérence des scores entre Python et le navigateur.
- **Choisir un seuil de décision.** Un bon macro-F1 peut masquer des anomalies manquées. En ajustant le seuil sur la validation, nous sommes passés de 21 anomalies manquées à une seule, avec une augmentation des fausses alertes de 23 à 59. J’ai mieux compris le compromis entre précision et rappel.
- **Mesurer une optimisation.** Le candidat INT8 était environ 62 % plus léger. Les mesures de latence variaient selon le moteur et la taille des lots. Cela m’a appris à comparer plusieurs critères avant de choisir une version.
- **Développer une interface utilisable.** J’ai appris à relier le modèle au parcours utilisateur, à gérer les erreurs et à afficher les résultats. L’essai à 390 px a révélé une colonne trop étroite qui coupait les codes d’événements. Les captures avant/après montrent la correction.

**Ce que je dois encore approfondir.** Je souhaite mieux comprendre les différences numériques entre moteurs d’inférence et les méthodes permettant de vérifier qu’une optimisation conserve un comportement acceptable. Je dois aussi progresser dans l’organisation des tests utilisateurs.

## Ce que j’ai appris en équipe

- **Travailler avec Git et les pull requests.** J’ai appris à créer une branche par ticket, à sauvegarder mon travail et à proposer une PR vers `dev`. J’ai aussi compris la différence entre une modification fusionnée dans `dev` et une version publiée depuis `main`.
- **Utiliser les retours des collègues.** Le retour sur les anomalies manquées a conduit à SCRUM-62. Il m’a aidé à regarder les résultats au-delà d’un score global.
- **Clarifier les dépendances.** Les contrats de données et les échanges avec mes collègues ont permis de relier l’entraînement, le prétraitement et le site. J’ai appris à vérifier ce qui était déjà intégré avant de commencer une nouvelle tâche.
- **Utiliser l’IA avec recul.** Je me suis appuyé sur un assistant pour comprendre des erreurs, préparer du code et interpréter des résultats. Certains échanges ont demandé des corrections, notamment sur le pré-contrôle des annotations. Cela m’a montré l’importance de confronter les suggestions aux traces et aux résultats observés.

## Ce que je ferais autrement

- Prévoir plus tôt les essais avec des utilisateurs extérieurs à l’équipe.
- Vérifier régulièrement le site public après les fusions pour éviter un décalage avec la version locale.
- Conserver dès chaque expérience un compte rendu avec la commande, les paramètres, l’empreinte du modèle et les résultats.
- Prendre davantage de temps pour comprendre chaque modification avant de l’intégrer.