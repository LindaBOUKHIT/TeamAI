#### Alain Evina : retour individuel (SCRUM-49)

##### Mon rôle

J'ai mis en place le socle commun du dépôt : arborescence, contrats d'échange C1 à C7, règles de contribution, tests automatisés et intégration continue, structure en paquets et chemins centralisés (SCRUM-13, 55, 56, 59 et 60). J'ai construit le board Jira et préparé les supports de la revue J3 (SCRUM-32). Ce travail se voit peu dans les résultats, mais il a permis à chacun de brancher son code sur les mêmes formats et de faire relire chaque PR sur une CI commune.

Sur le volet B, j'étais chargé du SLM. La première inférence de SmolLM2-1.7B sur ma machine (SCRUM-28) a montré qu'il ignorait les lignes WARN et inventait des informations ; sa lenteur tenait surtout à la pleine précision sur CPU. Nous avons choisi Gemma 4 E4B QAT, exécuté avec llama.cpp (SCRUM-57 et 63). J'ai mené les itérations du prompt jusqu'à la v16 figée, sur des blocs de validation uniquement, avec des faits calculés par le code et un contrat de réponse vérifié. J'ai écrit la chaîne d'adaptation LoRA (SCRUM-29), le banc d'évaluation du volet B (SCRUM-38 et 45), la comparaison des deux volets et la V1 du rapport (SCRUM-47 et 48).

##### Ce que j'ai appris techniquement

- **Le format ne garantit pas le fond.** Une réponse conforme au schéma peut inverser une chronologie ou affirmer une causalité que la trace ne montre pas (SCRUM-46). Il faut des contrôles sur le contenu, et une relecture humaine.
- **Séparer réglage et évaluation.** Pour Laya (SCRUM-58), choisir la question sur une cohorte de validation puis la mesurer une seule fois sur une autre m'a évité de conclure sur un résultat favorable de mise au point : l'AUC finale vaut 0,47 et la porte n'a pas été intégrée.
- **La mémoire décide de l'architecture.** L'entraînement LoRA de Gemma ne tient pas sur 6 Go : les tables d'embeddings pèsent à elles seules environ 6,5 Gio. D'où la voie retenue, entraînement sur T4 puis adaptateur seul converti en GGUF et appliqué sur le modèle quantifié.

##### Ce que j'ai appris en équipe

- **Un outil d'aide doit être testé comme du code.** Le pré-contrôle que j'avais écrit pour la relecture du test réservé (SCRUM-35) produisait des faux positifs, que Bachar a dû contourner. Je l'ai corrigé après coup ; il aurait fallu le tester sur des cas connus avant de le diffuser.
- **Un ticket fermé n'est pas un travail fini.** SCRUM-38 a été fermé automatiquement à la fusion de son script alors que les mesures restaient à faire. Depuis, je vérifie le critère de fin avant chaque clôture.

##### Ce que je ferais autrement

Le jalon de mi-parcours a été manqué et l'adaptation complète du volet B est arrivée tard. Je figerais plus tôt le modèle et le jeu de test réservé, pour que l'entraînement et les mesures avant/après ne dépendent pas des dernières semaines. Je réduirais aussi le nombre d'itérations du prompt au profit d'un jeu d'exemples relus plus tôt.

##### Bilan personnel

Ce projet m'a appris à piloter un travail d'équipe autant qu'à développer : découper en tickets, faire relire, tracer les décisions. Sur le plan technique, je retiens la séparation stricte entre réglage et évaluation, et le fait qu'un résultat négatif bien documenté a autant de valeur qu'un gain.
