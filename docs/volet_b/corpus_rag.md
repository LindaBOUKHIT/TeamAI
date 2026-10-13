# Corpus documentaire HDFS pour le RAG

Ce corpus apporte du contexte documentaire pour expliquer les traces du volet B. Les faits concernant un bloc doivent toujours venir de ses lignes HDFS et de ses événements ; les documents servent à expliquer le fonctionnement général de HDFS. Ils ne permettent pas, à eux seuls, d’établir la cause d’un incident dans une trace particulière.

## Sources et version

Le corpus indexe deux guides officiels Apache HDFS : le guide d’architecture et le guide utilisateur, consultés dans la documentation Hadoop 1.2.1. Ils portent un copyright 2008, cohérent avec la période des logs, mais cette documentation ne permet pas d’affirmer que le système qui a produit HDFS_v1 exécutait Hadoop 1.2.1. La version du binaire n’est pas précisée dans les références Loghub consultées.

Les guides couvrent les rôles NameNode/DataNode, les blocs, la réplication, les heartbeats, les block reports, l’intégrité des données, les pannes DataNode/NameNode et le diagnostic `fsck`. Les publications utilisées pour vérifier la provenance et les différences de taille du jeu sont répertoriées, mais ne sont pas copiées dans le corpus. Les URL, versions et informations de licence sont détaillées dans [`sources.md`](../../volet_b/rag/corpus/sources.md).

Les fichiers HTML téléchargés vont dans `volet_b/rag/corpus/raw/`, ignoré par Git. Le fichier versionné [`chunks.jsonl`](../../volet_b/rag/corpus/chunks.jsonl) respecte C6 ; ses identifiants ont la forme `document#section#numéro`. Le champ `version` décrit la documentation consultée et ne prétend pas identifier la version du cluster ayant produit les logs.

## Comparaison des découpages

Le script a comparé deux stratégies sur les mêmes deux pages, avec une limite de 1 600 caractères et un chevauchement de 200 caractères pour les fenêtres glissantes :

| Stratégie | Passages | Longueur moyenne | Longueur médiane | Passages traversant plusieurs sections |
|---|---:|---:|---:|---:|
| Par section, avec subdivision des sections longues | 53 | 727 caractères | 666 caractères | 0 |
| Fenêtre glissante | 29 | 1 551 caractères | 1 595 caractères | 26 |

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
