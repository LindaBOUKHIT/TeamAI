
# SCRUM-21 : Format d'entrée du site HDFS

## 1. Objectif

Définir les formats d'entrée acceptés par le site du volet A
et fournir des fichiers d'exemple pour tester l'importation
des logs HDFS.

## 2. Formats acceptés

Deux méthodes d'entrée sont prévues :

1. Copier-coller de lignes brutes issues de `HDFS.log`.
2. Importation d'un fichier `.log` ou `.txt`.

Le contenu doit correspondre au format des logs HDFS v1
utilisé dans le projet.

Les fichiers CSV, JSON et les séquences d'EventId ne sont
pas des formats d'entrée utilisateur prévus par ce contrat.

## 3. Format des lignes

Exemple de ligne HDFS brute :

```text
081109 203518 143 INFO dfs.DataNode$DataXceiver: Receiving block blk_-1608999687919862906 src: /10.250.19.102:54106dest: /10.250.19.102:50010
```

Une ligne comporte notamment :

- Une date et une heure.
- Un identifiant de processus ou de thread.
- Un niveau de journalisation.
- Un composant HDFS.
- Un message contenant éventuellement un identifiant `blk_`.

Le site doit analyser les lignes, identifier les événements
connus et regrouper les lignes par identifiant de bloc.

## 4. Regroupement par bloc

Un identifiant de bloc respecte le motif :

`blk_-?[0-9]+`

Une même entrée peut contenir plusieurs blocs.

Chaque bloc doit être analysé indépendamment.

Une ligne contenant plusieurs identifiants de blocs peut
être associée à plusieurs blocs si le parseur le prévoit.

L'ordre des événements d'un bloc doit respecter l'ordre
d'apparition des lignes dans le fichier d'entrée.

## 5. Reconnaissance des événements

Le projet utilise 29 templates d'événements HDFS
référencés de E1 à E29.

Les lignes non reconnues ne doivent pas être transformées
silencieusement en événements connus.

Le site doit distinguer les lignes valides, non reconnues
et sans identifiant de bloc.

## 6. Cas limites et messages attendus

| Cas | Comportement attendu | Message proposé |
|---|---|---|
| Entrée vide | Refuser l'analyse | Aucun log fourni. |
| Fichier `.csv` ou autre extension non acceptée | Refuser l'import | Format non pris en charge. Utilisez `.log` ou `.txt`. |
| Fichier trop volumineux | Refuser l'import | Fichier trop volumineux pour l'analyse. |
| Ligne sans identifiant `blk_` | Signaler et ignorer pour le regroupement | Ligne sans identifiant de bloc HDFS. |
| Ligne hors des 29 templates | Signaler la ligne non reconnue | Événement HDFS non reconnu. |
| Bloc incomplet | Signaler un résultat potentiellement non fiable | Bloc potentiellement incomplet : résultat à interpréter avec prudence. |
| Aucun bloc exploitable | Ne pas lancer la prédiction | Aucun bloc HDFS exploitable détecté. |
| Plusieurs blocs | Analyser séparément | Plusieurs blocs détectés : analyse par bloc. |

La taille maximale autorisée doit être définie avec
l'équipe web selon les contraintes de déploiement.

Un bloc incomplet ne peut pas toujours être identifié
de manière certaine à partir d'un simple extrait.
Le message correspondant est donc un avertissement
lorsqu'une troncature est connue ou suspectée.

## 7. Fichiers d'exemple

Les fichiers se trouvent dans :

`volet_a/web/public/examples/`

| Fichier | Description |
|---|---|
| `01_normal.log` | Bloc normal issu de la validation SCRUM-20 |
| `02_anomalie.log` | Bloc anormal issu de la validation SCRUM-20 |
| `03_plusieurs_blocs.log` | Plusieurs blocs issus de la validation |
| `04_bloc_incomplet.log` | Bloc normal volontairement tronqué |
| `05_lignes_invalides.log` | Lignes artificielles invalides |

Les exemples normaux et anormaux sont sélectionnés
à partir des labels du jeu de **validation** : le test officiel
reste réservé à l'évaluation finale (CONTRIBUTING §6, contrat C4).

Correction du 13/10 : une première version tirait ces exemples du test.
Les trois blocs alors exposés sont `blk_-1000014584150379967`,
`blk_-100004553717737248` et `blk_-1001299764911418845`. Aucun modèle n'a été
réglé dessus ; ils restent dans le test mais sont signalés ici, et l'évaluation
finale du volet A peut rapporter un résultat qui les exclut.

Les fichiers incomplets et invalides servent uniquement
aux tests de robustesse de l'importation.

## 8. Périmètre du ticket

SCRUM-21 définit le contrat d'entrée et les exemples.

Il ne comprend pas l'implémentation complète de
l'interface web, du parseur ou du modèle de prédiction.

## 9. Vérification

Les exemples doivent :

- Être lisibles comme fichiers texte UTF-8.
- Conserver le format brut des lignes HDFS.
- Contenir les identifiants de blocs attendus.
- Permettre de tester les cas normaux, anormaux
  et les erreurs d'importation.

La génération peut être reproduite avec :

```bash
python -m data.generate_web_examples
```
