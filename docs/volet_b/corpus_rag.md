# Corpus documentaire HDFS pour le RAG

Ce corpus apporte du contexte documentaire pour expliquer les traces du volet B. Les faits concernant un bloc doivent toujours venir de ses lignes HDFS et de ses événements ; les documents servent à expliquer le fonctionnement général de HDFS. Ils ne permettent pas, à eux seuls, d’établir la cause d’un incident dans une trace particulière.

## Sources et version

Le corpus indexe deux guides officiels Apache HDFS : le guide d’architecture et le guide utilisateur, consultés dans la documentation Hadoop 1.2.1. Ils portent un copyright 2008, cohérent avec la période des logs, mais cette documentation ne permet pas d’affirmer que le système qui a produit HDFS_v1 exécutait Hadoop 1.2.1. La version du binaire n’est pas précisée dans les références Loghub consultées.

Les guides couvrent les rôles NameNode/DataNode, les blocs, la réplication, les heartbeats, les block reports, l’intégrité des données, les pannes DataNode/NameNode et le diagnostic `fsck`. Les publications utilisées pour vérifier la provenance et les différences de taille du jeu sont répertoriées, mais ne sont pas copiées dans le corpus. Les URL, versions et informations de licence sont détaillées dans [`sources.md`](../../volet_b/rag/corpus/sources.md).

Les fichiers HTML téléchargés vont dans `volet_b/rag/corpus/raw/`, ignoré par Git. Le fichier versionné [`chunks.jsonl`](../../volet_b/rag/corpus/chunks.jsonl) respecte C6 ; ses identifiants ont la forme `document#section#numéro`. Le champ `version` décrit la documentation consultée et ne prétend pas identifier la version du cluster ayant produit les logs.

## Couverture des templates de logs

Ce tableau indique si le corpus contient un passage qui apporte du contexte utile pour chaque template Loghub. Un identifiant C6 explique le mécanisme général, pas la présence de l'événement ni la cause d'une anomalie. `Aucun` signifie qu'aucun passage du corpus ne justifie actuellement une explication documentaire pour ce template ; une réponse RAG doit alors pouvoir garder `sources: []`.

| Template | Passage C6 pertinent, ou aucun |
|---|---|
| E1 — ajout d'un bloc déjà présent | Aucun |
| E2 — vérification réussie d'un bloc | `hdfs-architecture-1.2.1#data-integrity#1` — vérification par checksum |
| E3 — bloc servi à un client | `hdfs-architecture-1.2.1#namenode-and-datanodes#1` — rôle de service des DataNodes |
| E4 — exception pendant le service d'un bloc | Aucun — le guide ne précise pas la cause de cette exception |
| E5 — réception d'un bloc avec source et destination | `hdfs-architecture-1.2.1#replication-pipelining#1` — transfert entre DataNodes |
| E6 — réception d'un bloc avec sa taille | `hdfs-architecture-1.2.1#replication-pipelining#1` — écriture et transfert des portions du bloc |
| E7 — exception reçue par `writeBlock` | Aucun — le pipeline est décrit, mais pas cette exception |
| E8 — interruption de `PacketResponder` | Aucun |
| E9 — bloc reçu depuis un DataNode | `hdfs-architecture-1.2.1#replication-pipelining#1` — réception dans le pipeline |
| E10 — exception de `PacketResponder` | Aucun |
| E11 — fin de `PacketResponder` | Aucun — ce détail d'implémentation n'est pas décrit |
| E12 — exception d'écriture vers un miroir | `hdfs-architecture-1.2.1#replication-pipelining#1` — contexte du transfert vers le DataNode suivant, sans expliquer l'exception |
| E13 — paquet vide reçu | Aucun |
| E14 — exception dans `receiveBlock` | Aucun — le guide ne documente pas cette exception |
| E15 — décalage du fichier de bloc modifié | Aucun |
| E16 — bloc transmis à un autre DataNode | `hdfs-architecture-1.2.1#replication-pipelining#1` — transfert des blocs entre DataNodes |
| E17 — échec de transfert d'un bloc | Aucun — le guide ne documente pas ce message ni sa cause |
| E18 — démarrage d'un thread de transfert | Aucun — le détail du thread n'est pas décrit |
| E19 — réouverture d'un bloc | Aucun |
| E20 — erreur `volumeMap` lors de la suppression | Aucun — ce détail d'implémentation n'est pas documenté |
| E21 — suppression du fichier d'un bloc | `hdfs-architecture-1.2.1#decrease-replication-factor#1` — suppression d'une réplique excédentaire |
| E22 — allocation d'un bloc | `hdfs-architecture-1.2.1#staging#1` — allocation d'un bloc par le NameNode lors de l'écriture |
| E23 — ajout à `invalidSet` après suppression | Aucun — l'ensemble interne `invalidSet` n'est pas décrit |
| E24 — retrait de `neededReplications` car le bloc n'appartient à aucun fichier | Aucun — ce détail de gestion interne n'est pas décrit |
| E25 — demande de réplication | `hdfs-architecture-1.2.1#data-disk-failure-heartbeats-and-re-replication#1` — suivi et lancement de la réplication nécessaire |
| E26 — mise à jour du `blockMap` par `addStoredBlock` | Aucun — cette mise à jour interne n'est pas détaillée |
| E27 — demande `addStoredBlock` redondante | Aucun |
| E28 — demande `addStoredBlock` pour un bloc sans fichier | Aucun |
| E29 — expiration du délai de réplication en attente | Aucun — le guide ne décrit pas ce délai ni ce message |

Les sections de références composées de listes de liens sont exclues du corpus : `hdfs-architecture-1.2.1#references` et `hdfs-users-1.2.1#related-documentation`. Les empreintes SHA-256 des pages HTML sources sont enregistrées par identifiant de source dans [`chunking_comparison.json`](../../volet_b/rag/corpus/chunking_comparison.json), afin de repérer une modification des pages téléchargées.

## Comparaison des découpages

Le script a comparé deux stratégies sur les mêmes deux pages, avec une limite de 1 600 caractères et un chevauchement de 200 caractères pour les fenêtres glissantes :

| Stratégie | Passages | Longueur moyenne | Longueur médiane | Passages traversant plusieurs sections |
|---|---:|---:|---:|---:|
| Par section, avec subdivision des sections longues | 51 | 736 caractères | 666 caractères | 0 |
| Fenêtre glissante | 28 | 1 562 caractères | 1 595 caractères | 26 |

Le corpus retient le découpage par section : les passages gardent leur titre et leur sujet, ce qui rend les citations C6 plus faciles à relire. Les sections qui dépassent la limite sont subdivisées aux frontières de texte, sans chevauchement et sans mélanger deux sections. Les mesures reproductibles sont conservées dans [`chunking_comparison.json`](../../volet_b/rag/corpus/chunking_comparison.json).

## Reproduire le corpus

Depuis la racine du dépôt :

```powershell
python .\volet_b\rag\build_corpus.py
```

La commande télécharge les deux pages officielles si elles sont absentes, compare les deux stratégies, écrit les métriques dans `volet_b/rag/corpus/chunking_comparison.json` et produit le C6 par section dans `volet_b/rag/corpus/chunks.jsonl`.

Pour reconstruire à partir des pages déjà présentes dans `corpus/raw/` sans réseau :

```powershell
python .\volet_b\rag\build_corpus.py --no-download
```

Pour écrire les passages à fenêtre glissante et garder le résultat par section comme stratégie recommandée dans le rapport :

```powershell
python .\volet_b\rag\build_corpus.py --strategy sliding-window
```

## Limites d’interprétation

- Le label `normal` ou `anomaly` de Loghub n’est pas une preuve documentaire et ne doit pas remplacer les événements visibles dans la trace.
- Un `WARN`, une exception ou un événement de suppression ne démontre pas seul une panne ; il faut examiner la séquence entière et les faits associés au bloc.
- Les guides décrivent des mécanismes historiques. Les détails qui peuvent avoir changé entre versions doivent être présentés comme dépendants de la version, pas comme des certitudes sur le cluster observé.
- Si aucun passage du corpus ne justifie une explication documentaire, citer `sources: []` plutôt que d’inventer un identifiant ou une cause.
