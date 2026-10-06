# TeamAI — Tâches à saisir dans le board

Préparation du 21 septembre 2026. Ce document ne constitue pas un board GitHub créé. Tous les responsables sont proposés et doivent être confirmés par le groupe. Les statuts sont « À faire » ; aucun travail technique n’est présenté comme accompli.

| ID | Tâche | Responsable proposé | Relecteur | Échéance cible | Dépendance | Critère de fin |
|---|---|---|---|---|---|---|
| ORG-01 | Créer le board, ajouter les membres et partager les accès | Linda | Alain | 21/09 | — | Quatre membres, colonnes et accès enseignant vérifiés ; lien consigné. |
| ORG-02 | Confirmer les rôles, déclarer les environnements et le matériel | Alain | Linda | 21/09 | — | Fiche complétée pour chaque membre ; machine SLM identifiée avec RAM et GPU/VRAM. |
| ORG-03 | Partager le suivi et le journal d’usage de l’IA | Linda | Nassim | 21/09 | ORG-01 | Support partagé accessible ; premières entrées factuelles, sans activités inventées. |
| DATA-01 | Auditer et préparer un échantillon HDFS_v1 | Nassim | Bachar | 23/09 | — | Provenance, conditions d’usage, format, traces complètes, comptes des classes et anomalies de qualité documentés. |
| WEB-01 | Tester l’export d’un petit modèle ONNX | Bachar | Nassim | 23/09 | — | Prédictions Python et navigateur comparées sur les mêmes entrées ; limites relevées. |
| LOCAL-01 | Tester une inférence du SLM sur la machine cible | Alain | Linda | 23/09 | ORG-02 | Exécution reproduisible, versions et mémoire/temps observés consignés. |
| DATA-02 | Construire et figer les jeux de données | Nassim | Bachar | 25/09 | DATA-01 | Séparation par bloc, contrôles des doublons, prétraitement appris sur train, répartition des classes publiée. |
| DOC-01 | Sélectionner la documentation et la grille d’annotation | Linda | Alain | 25/09 | DATA-01 | Sources identifiées avec versions ; exemples relus ; distinction faits/hypothèses et grille commune écrites. |
| LOCAL-02 | Réaliser un essai court d’adaptation LoRA | Alain | Linda | 28/09 | LOCAL-01, DOC-01 | Faisabilité matérielle vérifiée sur exemples d’apprentissage ; procédure et coût mémoire consignés. |
| WEB-02 | Entraîner la référence et le premier classifieur | Bachar | Nassim | 28/09 | DATA-02, WEB-01 | Résultats de validation comparés ; modèle et prétraitement exportables. |
| DOC-02 | Constituer les exemples d’adaptation et le test d’explication | Linda | Nassim | 30/09 | DOC-01 | Exemples vérifiés par le groupe ; test réservé, sources attendues et cas insuffisamment documentés inclus. |
| WEB-03 | Déployer la version web minimale | Bachar | Nassim | 01/10 | WEB-02 | URL publique gratuite, import d’exemples et prédictions réellement exécutées dans le navigateur. |
| ORG-04 | Préparer les preuves du jalon de mi-parcours | Linda | Alain | 01/10 | WEB-03, LOCAL-01 | Tag Git, URL, preuve d’inférence et capture du board disponibles. |
| LOCAL-03 | Construire la référence RAG à un agent | Linda | Alain | 05/10 | DOC-02, LOCAL-01 | Recherche et réponse locale avec références contrôlées ; trace des résultats. |
| LOCAL-04 | Adapter le modèle et enregistrer les expériences | Alain | Linda | 12/10 | LOCAL-02, DOC-02 | Adaptateur sauvegardé, configuration et données d’apprentissage tracées, aucune utilisation du test pour le réglage. |
| LOCAL-05 | Ajouter les trois agents avec une reprise maximale | Linda | Alain | 14/10 | LOCAL-03 | Rôles, sorties et transitions testés ; limite d’appels effective ; version simple conservée pour comparaison. |
| WEB-04 | Finaliser le parcours web et ses tests | Bachar | Nassim | 16/10 | WEB-03 | Import, erreurs de format, scores et export vérifiés ; latence mesurée. |
| ORG-05 | Préparer la revue J3 et commencer le rapport | Alain | Linda | 16/10 | WEB-04, LOCAL-04 | Supports, état des blocages et premières sections du rapport disponibles. |
| EVAL-01 | Comparer les configurations sur le test réservé | Nassim | Bachar | 06/11 | LOCAL-04, LOCAL-05 | Résultats des quatre configurations, mesures et relecture humaine commune ; tous les membres contribuent. |
| DOC-03 | Terminer le rapport et documenter les outils réellement employés | Alain | Nassim | 27/11 | EVAL-01 | Résultats, limites, retour d’expérience et usages des outils relus par les quatre membres. |
| DEMO-01 | Répéter et enregistrer les démonstrations | Bachar | Linda | 30/11 | WEB-04, LOCAL-05 | Vidéos lisibles des deux volets et procédure de lancement vérifiée par un autre membre. |
| ORG-06 | Vérifier les accès et remettre les livrables | Linda | Alain | 04/12 | DOC-03, DEMO-01 | Site accessible, rapport PDF et supports remis selon consignes, dépôts et suivi accessibles. |

Les échéances intermédiaires sont des objectifs internes proposés, pas des dates supplémentaires imposées par le professeur. Les réunions et la maintenance du board se poursuivent pendant tout le projet.
