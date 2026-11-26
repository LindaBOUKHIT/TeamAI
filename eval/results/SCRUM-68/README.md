# SCRUM-68 : chat documentaire avec le vrai modèle

Contrôle sur Kaggle (`wsear07/teamai-scrum68-chat-reel`, version 2) le 25/11/2026, sur un Tesla T4. Code au commit `261a238`, modèle Gemma 4 E4B QAT q4_0 sans adaptateur, llama-cpp-python 0.3.36 CUDA. Retriever hybride BGE-small + BM25 (SCRUM-37), corpus de 51 passages HDFS 1.2.1 (SCRUM-30), avec en plus les templates Loghub pour les codes Exx.

## Bug trouvé par la version 1

Avec `maxLength: 1200` sur le champ `reponse`, llama.cpp plante en construisant la grammaire du schéma (segfault, code -11) dès la première réponse. La limite est donc fixée à 750 caractères, la plus grande valeur déjà validée par v16 sur les 80 cas de test. Un test l'empêche de dépasser cette valeur. Sans ce correctif, l'onglet « Demander à la doc » plantait avec le vrai modèle. Le mode factice ne le montrait pas.

## Réponses (version 2)

| Question | Statut | Temps | Sources citées |
|---|---|---:|---|
| Que signifie l'événement E23 ? | sourcée | 7,8 s | `loghub-templates#E23` |
| Comment HDFS détecte-t-il qu'un DataNode est en panne ? | sourcée | 6,9 s | `data-disk-failure-heartbeats-and-re-replication#1` |
| Que se passe-t-il quand une réplique d'un bloc est perdue ? | abstention | 5,8 s | aucune |
| Pourquoi l'erreur BlockInfo not found in volumeMap apparaît-elle (E20) ? | sourcée | 8,7 s | `loghub-templates#E20` |
| Quelle est la capitale de l'Australie ? | abstention | 3,3 s | aucune |

- **Réponses justes et sourcées : E23 et DataNode.**
  - E23 : le NameNode ajoute le bloc à l'ensemble d'invalidation.
  - DataNode : le NameNode le déclare en panne en l'absence de Heartbeat.
- **Question hors sujet : abstention correcte.**
- **Réplique perdue : abstention prudente, mais due à un défaut de recherche.** La requête `block replica loss` ne retrouve pas le passage sur la re-réplication (`data-disk-failure-heartbeats-and-re-replication#1`). Le modèle n'invente pas de réponse. C'est le rappel du retriever qui est en cause.
- **E20 : la réponse reformule le template sans donner de cause.** La documentation indexée ne la donne pas, et le modèle n'en invente pas.
- **Affichage corrigé après ce contrôle :**
  - les étiquettes `[P1]` sont retirées du texte, puisque les sources sont listées en dessous ;
  - une abstention sans phrase (le modèle a renvoyé « abstention ») affiche le message standard.

Cinq questions ne font pas une évaluation : ce contrôle établit que la chaîne tourne avec le vrai modèle et que le contrat est respecté. La note « hors schéma, sans source » reste au contrôle de `check_reply`.

## Fichiers

- `chat_reel.json` : chaque question avec sa requête, les passages consultés, la réponse, les erreurs et la durée.
- `journal.txt` : journal du notebook.
