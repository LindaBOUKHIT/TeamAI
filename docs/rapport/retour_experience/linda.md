# Retour d'expérience — Linda Boukhit

## Mon rôle

J'étais la **pilote** de l'équipe : j'ai organisé le projet dans Jira (sprints, tickets, échéances), mis en place le classeur de suivi et le journal d'usage de l'IA (SCRUM-14), préparé les preuves de mi-parcours (SCRUM-17) et relu environ 30 pull requests de l'équipe. Côté technique, j'ai travaillé sur le **volet B** : le corpus documentaire (SCRUM-30), le RAG (SCRUM-37), l'orchestration à 3 agents (SCRUM-42) et l'interface de démonstration (SCRUM-43). J'ai aussi écrit le prétraitement JavaScript du site du volet A (SCRUM-26).

## Ce que j'ai appris techniquement

- **Le prétraitement des données.** Transformer des lignes de logs en événements E1 à E29 m'a montré qu'un détail compte : le site devait donner exactement le même résultat que Python. Les tests de parité (2 000 blocs sur 2 000 identiques) m'ont appris à **prouver** que deux programmes font la même chose, au lieu de le supposer.
- **Le fonctionnement d'un RAG.** J'ai compris toute la chaîne : découper une documentation, transformer les passages en vecteurs, chercher par le sens et par les mots-clés, puis donner les passages au modèle. Surtout, j'ai appris qu'il faut **mesurer avant de décider** : j'avais prévu un seuil de pertinence, mais les mesures sur la validation ont montré qu'il retirerait autant de bons passages que de mauvais. Je l'ai donc abandonné et documenté (`eval/results/SCRUM-37/retrieval_val.json`).
- **Les limites d'un RAG.** La documentation HDFS explique le fonctionnement normal, pas les pannes (`docs/volet_b/corpus_rag.md`). Un RAG ne vaut que ce que vaut son corpus.
- **L'organisation en agents.** Découper le travail entre une recherche, une rédaction et un contrôle, avec une limite d'appels. La première mesure réelle (`eval/results/SCRUM-42/kaggle_val5/`) a montré que le contrôleur rejetait de bonnes réponses parce qu'il ne connaissait pas les règles : un agent doit recevoir le même contrat que celui qu'il contrôle.

**Ce qui me manque encore :** je dois approfondir l'**évaluation des modèles de langage**. Je sais construire une chaîne RAG et mesurer la recherche, mais juger si une explication générée est vraiment juste reste difficile : il faut une relecture humaine, et je veux apprendre des méthodes plus solides pour le faire.

## Ce que j'ai appris en équipe

- **Organiser un projet à quatre.** La règle « un ticket, une branche, une PR, une relecture » nous a évité beaucoup d'erreurs, et les contrats C1 à C7 (`docs/contrats.md`) ont permis à chacun d'avancer sans attendre les autres.
- **Oser dire que je n'ai pas compris.** Au milieu du projet, je me suis rendu compte que je ne comprenais plus bien ce que faisait l'équipe sur le volet B. J'ai pris le temps de tout me faire réexpliquer (le projet, les codes d'événements, le RAG) avant de continuer. Ça m'a permis de mieux piloter ensuite.
- **Les délais.** Plusieurs de mes tickets ont pris du retard (SCRUM-42 et SCRUM-43, prévus pour le 9 et le 13/11) parce qu'ils dépendaient du passage à Gemma. J'aurais dû **relancer plus tôt** et réajuster le planning dans Jira au lieu de laisser les échéances dépasser.
- **Déléguer et utiliser l'IA.** J'ai appris à confier des tâches, à l'équipe comme à des outils d'IA, tout en gardant la responsabilité de vérifier (`docs/projet/journal.md`). Par exemple, une relecture automatique a classé un problème comme « bloquant » alors qu'il était mineur : il faut toujours vérifier avant de conclure.

## Ce que je ferais autrement

- Tenir les **sprints Jira à jour** chaque semaine : fermer les sprints, déplacer les tickets en retard.
- **Relancer plus tôt** quand une tâche bloque les autres.
- Garder plus de **temps pour coder moi-même**, pas seulement organiser et vérifier.
