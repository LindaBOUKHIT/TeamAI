# Connecteur MCP Atlassian (Jira) via Claude Code — MCP

- **Utilisé par / pour** :
  - Alain : création et suivi du board Jira (epics, sprints, tâches, liens de dépendance), commentaires et transitions de tickets.
  - Linda : préparation de relectures avec les connecteurs Atlassian et GitHub, et automatisation « PR fusionnée dans dev → Terminé » (13/10).
  - Usages consignés dans le [journal](../../projet/journal.md) (tableau des usages d'IA).
- **Temps d'appropriation constaté** : le board complet a été créé en une séance le 06/10. Le temps passé en heures n'a pas été relevé.
- **Ce qui a marché** :
  - Le 06/10 : 7 epics, 5 sprints alignés sur les jalons, tickets SCRUM-5 à SCRUM-55 avec responsable, relecteur, critère de fin et dépendances.
  - Ensuite : un commentaire par changement réel et des transitions faites sans quitter le terminal.
- **Ce qui a échoué ou déçu** :
  - Le même compte donne accès à plusieurs sites Atlassian. Une règle locale fixe donc le site et son identifiant pour ce projet, et interdit d'utiliser l'autre connecteur, même pour vérifier un accès.
  - Les actions de l'agent apparaissent dans Jira sous le nom de la personne connectée. L'historique ne distingue pas un commentaire écrit par l'agent d'un commentaire écrit à la main : la traçabilité de l'usage d'IA repose sur le journal.
  - Un statut Jira ne prouve pas qu'un critère de fin est rempli : SCRUM-15 a dû être rouvert le 18/10 après audit, parce que le tableau des environnements restait incomplet.
- **Ce que la documentation omet** : rien n'empêche l'agent d'agir sur le mauvais site quand plusieurs sont accessibles. Il faut le préciser dans les consignes du projet (`AGENTS.md`).
- **Comparaison avec l'outil utilisé avant** : le 21/09, le board n'existait pas encore (« board et classeur partagé non créés »). Le gain du connecteur tient à la création en lot des tickets et de leurs liens.
- **Verdict** : on garde le connecteur pour le suivi, avec trois garde-fous :
  - un site fixé pour le projet ;
  - un seul commentaire par changement réel ;
  - avant de fermer un ticket, une vérification du statut contre son critère de fin.
