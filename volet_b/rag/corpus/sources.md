# Sources du corpus documentaire HDFS

Dernière vérification des références : 2026-10-13.

## Documents indexés

| Identifiant C6 | Document et périmètre | Version/date indiquée | Licence et usage |
|---|---|---|---|
| `hdfs-architecture-1.2.1` | [HDFS Architecture Guide](https://hadoop.apache.org/docs/stable1/hdfs_design.html) : NameNode, DataNodes, blocs, réplication, heartbeats, block reports, intégrité et défaillances | Servi dans la documentation Hadoop 1.2.1 ; le guide porte un copyright 2008. Cela décrit la date du document, pas la version exacte du binaire ayant produit HDFS_v1. | La [politique Apache](https://www.apache.org/licenses/LICENSE-2.0.html) indique Apache License 2.0 pour les distributions Apache sauf mention contraire ; la page porte un copyright 2008. Le corpus conserve l’attribution, la version et l’URL. |
| `hdfs-users-1.2.1` | [HDFS Users Guide](https://hadoop.apache.org/docs/stable1/hdfs_user_guide.html) : diagnostic, état du cluster, Safemode et `fsck` | Documentation Hadoop 1.2.1 ; copyright 2008. Ce n’est pas une preuve de la version HDFS utilisée pour collecter les logs. | La [politique Apache](https://www.apache.org/licenses/LICENSE-2.0.html) indique Apache License 2.0 pour les distributions Apache sauf mention contraire ; la page porte un copyright 2008. Le corpus conserve l’attribution, la version et l’URL. |

Les deux pages originales sont téléchargées dans `volet_b/rag/corpus/raw/`, répertoire ignoré par Git. Le script de construction peut les retélécharger depuis les URL officielles. Les passages versionnés dans `chunks.jsonl` gardent l’URL, le nom du document et la mention de version pour permettre de retrouver leur contexte.

## Références de provenance, non indexées

| Référence | Version/date | Information retenue | Licence / traitement |
|---|---|---|---|
| [Loghub — HDFS README](https://github.com/logpai/loghub/blob/master/HDFS/README.md) | Branche `master`, consultée le 2026-10-13 | Décrit HDFS_v1 comme un jeu de logs Hadoop segmentés par BlockId et étiquetés normal/anomalie ; donne les fichiers préparés et demande de citer les publications associées. | Le README autorise l’usage pour la recherche et l’enseignement, mais ne donne pas d’identifiant de licence SPDX. Utilisé ici pour la provenance et les citations, pas recopié dans C6. |
| [Xu et al., SOSP 2009](https://people.eecs.berkeley.edu/~jordan/papers/xu-etal-sosp09.pdf) | Publication SOSP 2009 | Décrit une expérience HDFS sur 203 nœuds pendant 48 heures et rapporte 24 396 061 messages. | La copie liée par Loghub ne précise pas de licence de redistribution. Elle est référencée pour comparer la provenance, mais n’est pas téléchargée ni indexée dans C6. |
| [Loghub, ISSRE 2023](https://arxiv.org/abs/2008.06448) | Publication ISSRE 2023 | Publication de référence de la collection Loghub. | Référence bibliographique uniquement ; non indexée. |

## Écart de version et limites connues

La documentation HDFS choisie porte un copyright 2008, proche de la période du jeu. Le site qui la sert est celui de la documentation Hadoop 1.2.1. La page Loghub et l’article de Xu et al. ne donnent pas la version exacte du binaire Hadoop qui a produit les fichiers HDFS_v1 actuellement distribués. Nous ne présentons donc pas Hadoop 1.2.1 comme la version du système observé ; c’est la version de la documentation consultée.

Les chiffres de l’article de 2009 (48 h, 24 396 061 messages) diffèrent de ceux de la fiche Loghub HDFS_v1 (38,7 h, 11 175 629 lignes). Les sources consultées ne permettent pas de confirmer si le jeu actuel est un sous-ensemble ou une autre préparation des logs de l’article. Le corpus traite ces deux références séparément et ne les fusionne pas.

Les guides expliquent l’architecture et les diagnostics HDFS, pas la cause de chaque message présent dans HDFS_v1. Une ligne `WARN` ou `ERROR` seule ne suffit donc pas à conclure qu’un bloc est en anomalie ni à identifier sa cause.
