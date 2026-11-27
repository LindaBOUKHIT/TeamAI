# SCRUM-35 — Relecture des annotations C5

> Document de travail : les réponses sont des brouillons non validés. Ne pas utiliser pour entraîner ou ajuster le modèle.

## test-0001 — blk_686986449611901412

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081110 120238 10709 INFO dfs.DataNode$DataXceiver: Receiving block blk_686986449611901412 src: /10.251.199.86:47631 dest: /10.251.199.86:50010
[E22] 081110 120238 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/randtxt2/_temporary/_task_200811101024_0002_m_000817_0/part-00817. blk_686986449611901412
[E5] 081110 120239 10296 INFO dfs.DataNode$DataXceiver: Receiving block blk_686986449611901412 src: /10.251.122.38:49272 dest: /10.251.122.38:50010
[E5] 081110 120239 10796 INFO dfs.DataNode$DataXceiver: Receiving block blk_686986449611901412 src: /10.251.199.86:57937 dest: /10.251.199.86:50010
[E11] 081110 120356 10297 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_686986449611901412 terminating
[E9] 081110 120356 10297 INFO dfs.DataNode$PacketResponder: Received block blk_686986449611901412 of size 67108864 from /10.251.122.38
[E11] 081110 120356 10710 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_686986449611901412 terminating
[E9] 081110 120356 10710 INFO dfs.DataNode$PacketResponder: Received block blk_686986449611901412 of size 67108864 from /10.251.199.86
[E11] 081110 120356 10797 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_686986449611901412 terminating
[E9] 081110 120356 10797 INFO dfs.DataNode$PacketResponder: Received block blk_686986449611901412 of size 67108864 from /10.251.199.86
[E26] 081110 120356 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.199.86:50010 is added to blk_686986449611901412 size 67108864
[E26] 081110 120356 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.202.134:50010 is added to blk_686986449611901412 size 67108864
[E26] 081110 120356 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.122.38:50010 is added to blk_686986449611901412 size 67108864
[E3] 081110 175331 13423 INFO dfs.DataNode$DataXceiver: 10.251.202.134:50010 Served block blk_686986449611901412 to /10.251.202.134
[E4] 081110 175508 13430 WARN dfs.DataNode$DataXceiver: 10.251.202.134:50010:Got exception while serving blk_686986449611901412 to /10.250.10.223:
[E3] 081110 175730 13867 INFO dfs.DataNode$DataXceiver: 10.251.199.86:50010 Served block blk_686986449611901412 to /10.251.199.86
[E3] 081111 005045 16933 INFO dfs.DataNode$DataXceiver: 10.251.202.134:50010 Served block blk_686986449611901412 to /10.251.202.134
[E4] 081111 005127 17421 WARN dfs.DataNode$DataXceiver: 10.251.122.38:50010:Got exception while serving blk_686986449611901412 to /10.250.10.223:
[E3] 081111 005424 16939 INFO dfs.DataNode$DataXceiver: 10.251.202.134:50010 Served block blk_686986449611901412 to /10.251.122.79
[E23] 081111 023021 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_686986449611901412 is added to invalidSet of 10.251.122.38:50010
[E23] 081111 023021 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_686986449611901412 is added to invalidSet of 10.251.199.86:50010
[E23] 081111 023021 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_686986449611901412 is added to invalidSet of 10.251.202.134:50010
[E21] 081111 023232 19 INFO dfs.FSDataset: Deleting block blk_686986449611901412 file /mnt/hadoop/dfs/data/current/subdir29/blk_686986449611901412
[E21] 081111 023244 19 INFO dfs.FSDataset: Deleting block blk_686986449611901412 file /mnt/hadoop/dfs/data/current/subdir23/blk_686986449611901412
[E21] 081111 023302 19 INFO dfs.FSDataset: Deleting block blk_686986449611901412 file /mnt/hadoop/dfs/data/current/subdir57/blk_686986449611901412
```

### Résumé proposé

Le bloc est allou? puis re?u avec une taille de 67108864 octets. Trois DataNodes sont enregistr?s comme d?tenteurs du bloc. Plusieurs services du bloc sont journalis?s, avec deux avertissements signalant des exceptions lors du service au client 10.250.10.223. Le bloc est ensuite invalid? sur trois DataNodes, puis trois suppressions locales sont journalis?es.

### Faits observés

- E22 : allocation du bloc pour le fichier part-00817.
- E9 : trois r?ceptions du bloc de 67108864 octets sont journalis?es.
- E26 : trois DataNodes sont enregistr?s comme d?tenteurs du bloc.
- E3 : plusieurs services du bloc sont journalis?s.
- E4 : deux avertissements concernent le service du bloc au client 10.250.10.223.
- E23 : trois invalidations sont demand?es.
- E21 : trois suppressions locales sont journalis?es.

### Hypothèses


### Informations manquantes

- Nature des deux exceptions signal?es dans les avertissements.
- Raison de l'invalidation et de la suppression du bloc.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0002 — blk_1292583462119209881

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E22] 081110 011942 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/randtxt/_temporary/_task_200811092030_0003_m_000484_0/part-00484. blk_1292583462119209881
[E5] 081110 011942 5231 INFO dfs.DataNode$DataXceiver: Receiving block blk_1292583462119209881 src: /10.251.194.147:60970 dest: /10.251.194.147:50010
[E5] 081110 011943 5400 INFO dfs.DataNode$DataXceiver: Receiving block blk_1292583462119209881 src: /10.251.194.147:36211 dest: /10.251.194.147:50010
[E5] 081110 011943 5405 INFO dfs.DataNode$DataXceiver: Receiving block blk_1292583462119209881 src: /10.251.195.33:38461 dest: /10.251.195.33:50010
[E26] 081110 012020 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.195.33:50010 is added to blk_1292583462119209881 size 67108864
[E26] 081110 012020 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.7.32:50010 is added to blk_1292583462119209881 size 67108864
[E26] 081110 012020 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.194.147:50010 is added to blk_1292583462119209881 size 67108864
[E11] 081110 012020 5232 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_1292583462119209881 terminating
[E9] 081110 012020 5232 INFO dfs.DataNode$PacketResponder: Received block blk_1292583462119209881 of size 67108864 from /10.251.194.147
[E11] 081110 012020 5401 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_1292583462119209881 terminating
[E9] 081110 012020 5401 INFO dfs.DataNode$PacketResponder: Received block blk_1292583462119209881 of size 67108864 from /10.251.194.147
[E11] 081110 012020 5406 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_1292583462119209881 terminating
[E9] 081110 012020 5406 INFO dfs.DataNode$PacketResponder: Received block blk_1292583462119209881 of size 67108864 from /10.251.195.33
[E3] 081110 030605 6540 INFO dfs.DataNode$DataXceiver: 10.250.7.32:50010 Served block blk_1292583462119209881 to /10.250.7.32
[E4] 081110 030825 6546 WARN dfs.DataNode$DataXceiver: 10.250.7.32:50010:Got exception while serving blk_1292583462119209881 to /10.250.9.207:
[E3] 081110 030847 6381 INFO dfs.DataNode$DataXceiver: 10.251.194.147:50010 Served block blk_1292583462119209881 to /10.251.30.6
[E3] 081110 070252 7509 INFO dfs.DataNode$DataXceiver: 10.250.7.32:50010 Served block blk_1292583462119209881 to /10.250.7.32
[E4] 081110 070313 7614 WARN dfs.DataNode$DataXceiver: 10.251.195.33:50010:Got exception while serving blk_1292583462119209881 to /10.251.214.175:
[E3] 081110 070317 7388 INFO dfs.DataNode$DataXceiver: 10.251.194.147:50010 Served block blk_1292583462119209881 to /10.251.194.147
[E3] 081110 081108 8126 INFO dfs.DataNode$DataXceiver: 10.250.7.32:50010 Served block blk_1292583462119209881 to /10.250.7.32
[E3] 081110 081138 8281 INFO dfs.DataNode$DataXceiver: 10.251.195.33:50010 Served block blk_1292583462119209881 to /10.251.30.6
[E4] 081110 081141 8131 WARN dfs.DataNode$DataXceiver: 10.250.7.32:50010:Got exception while serving blk_1292583462119209881 to /10.250.9.207:
[E3] 081110 092557 8760 INFO dfs.DataNode$DataXceiver: 10.250.7.32:50010 Served block blk_1292583462119209881 to /10.250.7.32
[E4] 081110 092628 8672 WARN dfs.DataNode$DataXceiver: 10.251.194.147:50010:Got exception while serving blk_1292583462119209881 to /10.251.214.175:
[E3] 081110 092640 8676 INFO dfs.DataNode$DataXceiver: 10.251.194.147:50010 Served block blk_1292583462119209881 to /10.251.194.147
[E23] 081110 103031 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_1292583462119209881 is added to invalidSet of 10.250.7.32:50010
[E23] 081110 103031 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_1292583462119209881 is added to invalidSet of 10.251.194.147:50010
[E23] 081110 103031 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_1292583462119209881 is added to invalidSet of 10.251.195.33:50010
[E21] 081110 103126 19 INFO dfs.FSDataset: Deleting block blk_1292583462119209881 file /mnt/hadoop/dfs/data/current/subdir16/blk_1292583462119209881
[E21] 081110 103607 19 INFO dfs.FSDataset: Deleting block blk_1292583462119209881 file /mnt/hadoop/dfs/data/current/subdir33/blk_1292583462119209881
[E21] 081110 103617 19 INFO dfs.FSDataset: Deleting block blk_1292583462119209881 file /mnt/hadoop/dfs/data/current/subdir28/blk_1292583462119209881
```

### Résumé proposé

Le bloc est allou? puis re?u sur plusieurs DataNodes. Trois DataNodes sont enregistr?s pour ce bloc de 67108864 octets. Neuf op?rations de service r?ussies sont journalis?es, ainsi que quatre avertissements signalant des exceptions pendant le service. Le bloc est ensuite ajout? aux ensembles d'invalidation de trois DataNodes, puis trois suppressions locales sont journalis?es.

### Faits observés

- E22 : allocation du bloc pour le fichier part-00484.
- E5 : trois d?buts de r?ception sont journalis?s.
- E26 : trois DataNodes sont enregistr?s pour le bloc.
- E9 : trois confirmations de r?ception de 67108864 octets.
- E3 : neuf op?rations de service r?ussies sont journalis?es.
- E4 : quatre avertissements signalent des exceptions pendant le service.
- E23 : le bloc est ajout? aux ensembles d'invalidation de trois DataNodes.
- E21 : trois suppressions locales sont journalis?es.

### Hypothèses


### Informations manquantes

- Type et cause des quatre exceptions.
- Contexte des clients concern?s par les avertissements.
- Motif des invalidations et suppressions.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0003 — blk_-4363450704911283441

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E22] 081111 091248 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand8/_temporary/_task_200811101024_0015_m_000545_0/part-00545. blk_-4363450704911283441
[E5] 081111 091249 25194 INFO dfs.DataNode$DataXceiver: Receiving block blk_-4363450704911283441 src: /10.250.14.38:58959 dest: /10.250.14.38:50010
[E5] 081111 091249 25258 INFO dfs.DataNode$DataXceiver: Receiving block blk_-4363450704911283441 src: /10.251.127.191:54485 dest: /10.251.127.191:50010
[E5] 081111 091249 25273 INFO dfs.DataNode$DataXceiver: Receiving block blk_-4363450704911283441 src: /10.250.14.38:53942 dest: /10.250.14.38:50010
[E11] 081111 091336 25195 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-4363450704911283441 terminating
[E9] 081111 091336 25195 INFO dfs.DataNode$PacketResponder: Received block blk_-4363450704911283441 of size 67108864 from /10.250.14.38
[E11] 081111 091336 25259 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-4363450704911283441 terminating
[E9] 081111 091336 25259 INFO dfs.DataNode$PacketResponder: Received block blk_-4363450704911283441 of size 67108864 from /10.251.127.191
[E11] 081111 091336 25274 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-4363450704911283441 terminating
[E9] 081111 091336 25274 INFO dfs.DataNode$PacketResponder: Received block blk_-4363450704911283441 of size 67108864 from /10.250.14.38
[E26] 081111 091336 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.11.100:50010 is added to blk_-4363450704911283441 size 67108864
[E26] 081111 091336 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.127.191:50010 is added to blk_-4363450704911283441 size 67108864
[E26] 081111 091336 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.14.38:50010 is added to blk_-4363450704911283441 size 67108864
```

### Résumé proposé

La trace montre la réception et l'allocation d'un bloc HDFS, suivies de confirmations de réception et de son enregistrement sur trois DataNodes.

### Faits observés

- E5 : trois débuts de réception du bloc sont journalisés.
- E22 : une allocation du bloc est journalisée.
- E9 : trois confirmations de réception sont journalisées.
- E26 : le bloc est enregistré sur trois DataNodes.

### Hypothèses


### Informations manquantes

- Contexte applicatif complet de l'opération.

### Sources C6 candidates

hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0004 — blk_1422210367847367358

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 060149 21326 INFO dfs.DataNode$DataXceiver: Receiving block blk_1422210367847367358 src: /10.251.107.227:54654 dest: /10.251.107.227:50010
[E5] 081111 060149 21589 INFO dfs.DataNode$DataXceiver: Receiving block blk_1422210367847367358 src: /10.251.107.227:45795 dest: /10.251.107.227:50010
[E5] 081111 060149 21661 INFO dfs.DataNode$DataXceiver: Receiving block blk_1422210367847367358 src: /10.251.194.147:59623 dest: /10.251.194.147:50010
[E22] 081111 060149 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/randtxt5/_temporary/_task_200811101024_0012_m_000450_0/part-00450. blk_1422210367847367358
[E11] 081111 060228 21327 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_1422210367847367358 terminating
[E9] 081111 060228 21327 INFO dfs.DataNode$PacketResponder: Received block blk_1422210367847367358 of size 67108864 from /10.251.107.227
[E11] 081111 060228 21591 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_1422210367847367358 terminating
[E9] 081111 060228 21591 INFO dfs.DataNode$PacketResponder: Received block blk_1422210367847367358 of size 67108864 from /10.251.107.227
[E11] 081111 060228 21662 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_1422210367847367358 terminating
[E9] 081111 060228 21662 INFO dfs.DataNode$PacketResponder: Received block blk_1422210367847367358 of size 67108864 from /10.251.194.147
[E26] 081111 060228 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.194.147:50010 is added to blk_1422210367847367358 size 67108864
[E26] 081111 060228 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.107.227:50010 is added to blk_1422210367847367358 size 67108864
[E26] 081111 060228 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.7.32:50010 is added to blk_1422210367847367358 size 67108864
[E23] 081111 065209 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_1422210367847367358 is added to invalidSet of 10.250.7.32:50010
[E23] 081111 065209 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_1422210367847367358 is added to invalidSet of 10.251.107.227:50010
[E23] 081111 065209 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_1422210367847367358 is added to invalidSet of 10.251.194.147:50010
[E21] 081111 065407 19 INFO dfs.FSDataset: Deleting block blk_1422210367847367358 file /mnt/hadoop/dfs/data/current/subdir21/blk_1422210367847367358
[E21] 081111 065431 19 INFO dfs.FSDataset: Deleting block blk_1422210367847367358 file /mnt/hadoop/dfs/data/current/subdir28/blk_1422210367847367358
[E21] 081111 065434 19 INFO dfs.FSDataset: Deleting block blk_1422210367847367358 file /mnt/hadoop/dfs/data/current/subdir37/blk_1422210367847367358
```

### Résumé proposé

La trace montre la réception et l'allocation d'un bloc HDFS, suivies de confirmations de réception et de son enregistrement sur trois DataNodes. Le bloc est ensuite ajouté aux ensembles d'invalidation de trois DataNodes. Des suppressions locales du bloc sont ensuite journalisées.

### Faits observés

- E5 : trois débuts de réception du bloc sont journalisés.
- E22 : une allocation du bloc est journalisée.
- E9 : trois confirmations de réception sont journalisées.
- E26 : le bloc est enregistré sur trois DataNodes.
- E23 : trois ajouts aux ensembles d'invalidation sont journalisés.
- E21 : 3 suppressions locales sont journalisées.

### Hypothèses


### Informations manquantes

- Motif des invalidations et suppressions.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0005 — blk_-4941825985900076949

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081110 215227 15529 INFO dfs.DataNode$DataXceiver: Receiving block blk_-4941825985900076949 src: /10.251.195.70:52596 dest: /10.251.195.70:50010
[E5] 081110 215227 15595 INFO dfs.DataNode$DataXceiver: Receiving block blk_-4941825985900076949 src: /10.251.195.70:46342 dest: /10.251.195.70:50010
[E22] 081110 215227 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand3/_temporary/_task_200811101024_0005_m_001625_0/part-01625. blk_-4941825985900076949
[E5] 081110 215230 15014 INFO dfs.DataNode$DataXceiver: Receiving block blk_-4941825985900076949 src: /10.251.195.33:48783 dest: /10.251.195.33:50010
[E11] 081110 215314 15015 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-4941825985900076949 terminating
[E9] 081110 215314 15015 INFO dfs.DataNode$PacketResponder: Received block blk_-4941825985900076949 of size 67108864 from /10.251.195.33
[E11] 081110 215314 15530 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-4941825985900076949 terminating
[E9] 081110 215314 15530 INFO dfs.DataNode$PacketResponder: Received block blk_-4941825985900076949 of size 67108864 from /10.251.195.70
[E11] 081110 215314 15596 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-4941825985900076949 terminating
[E9] 081110 215314 15596 INFO dfs.DataNode$PacketResponder: Received block blk_-4941825985900076949 of size 67108864 from /10.251.195.70
[E26] 081110 215314 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.75.228:50010 is added to blk_-4941825985900076949 size 67108864
[E26] 081110 215314 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.195.33:50010 is added to blk_-4941825985900076949 size 67108864
[E26] 081110 215314 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.195.70:50010 is added to blk_-4941825985900076949 size 67108864
[E23] 081110 220654 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-4941825985900076949 is added to invalidSet of 10.251.195.33:50010
[E23] 081110 220654 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-4941825985900076949 is added to invalidSet of 10.251.195.70:50010
[E23] 081110 220654 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-4941825985900076949 is added to invalidSet of 10.251.75.228:50010
[E21] 081110 220810 19 INFO dfs.FSDataset: Deleting block blk_-4941825985900076949 file /mnt/hadoop/dfs/data/current/subdir45/blk_-4941825985900076949
[E21] 081110 220839 19 INFO dfs.FSDataset: Deleting block blk_-4941825985900076949 file /mnt/hadoop/dfs/data/current/subdir50/blk_-4941825985900076949
[E21] 081110 220909 19 INFO dfs.FSDataset: Deleting block blk_-4941825985900076949 file /mnt/hadoop/dfs/data/current/subdir62/blk_-4941825985900076949
```

### Résumé proposé

La trace montre la réception et l'allocation d'un bloc HDFS, suivies de confirmations de réception et de son enregistrement sur trois DataNodes. Le bloc est ensuite ajouté aux ensembles d'invalidation de trois DataNodes. Des suppressions locales du bloc sont ensuite journalisées.

### Faits observés

- E5 : trois débuts de réception du bloc sont journalisés.
- E22 : une allocation du bloc est journalisée.
- E9 : trois confirmations de réception sont journalisées.
- E26 : le bloc est enregistré sur trois DataNodes.
- E23 : trois ajouts aux ensembles d'invalidation sont journalisés.
- E21 : 3 suppressions locales sont journalisées.

### Hypothèses


### Informations manquantes

- Motif des invalidations et suppressions.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0006 — blk_-8329374239364666178

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 042848 19664 INFO dfs.DataNode$DataXceiver: Receiving block blk_-8329374239364666178 src: /10.251.214.32:47573 dest: /10.251.214.32:50010
[E5] 081111 042848 19893 INFO dfs.DataNode$DataXceiver: Receiving block blk_-8329374239364666178 src: /10.251.214.32:52117 dest: /10.251.214.32:50010
[E22] 081111 042848 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/randtxt4/_temporary/_task_200811101024_0010_m_001731_0/part-01731. blk_-8329374239364666178
[E5] 081111 042849 19859 INFO dfs.DataNode$DataXceiver: Receiving block blk_-8329374239364666178 src: /10.251.126.5:46921 dest: /10.251.126.5:50010
[E11] 081111 042934 19665 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-8329374239364666178 terminating
[E9] 081111 042934 19665 INFO dfs.DataNode$PacketResponder: Received block blk_-8329374239364666178 of size 67108864 from /10.251.214.32
[E11] 081111 042934 19862 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-8329374239364666178 terminating
[E9] 081111 042934 19862 INFO dfs.DataNode$PacketResponder: Received block blk_-8329374239364666178 of size 67108864 from /10.251.126.5
[E11] 081111 042934 19894 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-8329374239364666178 terminating
[E9] 081111 042934 19894 INFO dfs.DataNode$PacketResponder: Received block blk_-8329374239364666178 of size 67108864 from /10.251.214.32
[E26] 081111 042934 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.214.32:50010 is added to blk_-8329374239364666178 size 67108864
[E26] 081111 042934 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.90.239:50010 is added to blk_-8329374239364666178 size 67108864
[E26] 081111 042935 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.126.5:50010 is added to blk_-8329374239364666178 size 67108864
```

### Résumé proposé

La trace montre la réception et l'allocation d'un bloc HDFS, suivies de confirmations de réception et de son enregistrement sur trois DataNodes.

### Faits observés

- E5 : trois débuts de réception du bloc sont journalisés.
- E22 : une allocation du bloc est journalisée.
- E9 : trois confirmations de réception sont journalisées.
- E26 : le bloc est enregistré sur trois DataNodes.

### Hypothèses


### Informations manquantes

- Contexte applicatif complet de l'opération.

### Sources C6 candidates

hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0007 — blk_3781831724064867719

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081110 214631 15416 INFO dfs.DataNode$DataXceiver: Receiving block blk_3781831724064867719 src: /10.251.37.240:56970 dest: /10.251.37.240:50010
[E5] 081110 214631 15486 INFO dfs.DataNode$DataXceiver: Receiving block blk_3781831724064867719 src: /10.251.37.240:50117 dest: /10.251.37.240:50010
[E22] 081110 214631 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand3/_temporary/_task_200811101024_0005_m_001639_0/part-01639. blk_3781831724064867719
[E5] 081110 214632 15251 INFO dfs.DataNode$DataXceiver: Receiving block blk_3781831724064867719 src: /10.251.126.22:38760 dest: /10.251.126.22:50010
[E11] 081110 214728 15252 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_3781831724064867719 terminating
[E9] 081110 214728 15252 INFO dfs.DataNode$PacketResponder: Received block blk_3781831724064867719 of size 67108864 from /10.251.126.22
[E11] 081110 214728 15418 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_3781831724064867719 terminating
[E9] 081110 214728 15418 INFO dfs.DataNode$PacketResponder: Received block blk_3781831724064867719 of size 67108864 from /10.251.37.240
[E11] 081110 214728 15487 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_3781831724064867719 terminating
[E9] 081110 214728 15487 INFO dfs.DataNode$PacketResponder: Received block blk_3781831724064867719 of size 67108864 from /10.251.37.240
[E26] 081110 214728 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.215.70:50010 is added to blk_3781831724064867719 size 67108864
[E26] 081110 214729 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.37.240:50010 is added to blk_3781831724064867719 size 67108864
[E26] 081110 214729 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.126.22:50010 is added to blk_3781831724064867719 size 67108864
[E23] 081110 220654 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_3781831724064867719 is added to invalidSet of 10.251.126.22:50010
[E23] 081110 220654 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_3781831724064867719 is added to invalidSet of 10.251.215.70:50010
[E23] 081110 220654 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_3781831724064867719 is added to invalidSet of 10.251.37.240:50010
[E21] 081110 220906 19 INFO dfs.FSDataset: Deleting block blk_3781831724064867719 file /mnt/hadoop/dfs/data/current/subdir22/blk_3781831724064867719
[E21] 081110 220909 19 INFO dfs.FSDataset: Deleting block blk_3781831724064867719 file /mnt/hadoop/dfs/data/current/subdir22/blk_3781831724064867719
[E21] 081110 220936 19 INFO dfs.FSDataset: Deleting block blk_3781831724064867719 file /mnt/hadoop/dfs/data/current/subdir50/blk_3781831724064867719
```

### Résumé proposé

La trace montre la réception et l'allocation d'un bloc HDFS, suivies de confirmations de réception et de son enregistrement sur trois DataNodes. Le bloc est ensuite ajouté aux ensembles d'invalidation de trois DataNodes. Des suppressions locales du bloc sont ensuite journalisées.

### Faits observés

- E5 : trois débuts de réception du bloc sont journalisés.
- E22 : une allocation du bloc est journalisée.
- E9 : trois confirmations de réception sont journalisées.
- E26 : le bloc est enregistré sur trois DataNodes.
- E23 : trois ajouts aux ensembles d'invalidation sont journalisés.
- E21 : 3 suppressions locales sont journalisées.

### Hypothèses


### Informations manquantes

- Motif des invalidations et suppressions.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0008 — blk_-7453557116554566888

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 054009 15763 INFO dfs.DataNode$DataXceiver: Receiving block blk_-7453557116554566888 src: /10.251.123.33:53770 dest: /10.251.123.33:50010
[E5] 081111 054009 21031 INFO dfs.DataNode$DataXceiver: Receiving block blk_-7453557116554566888 src: /10.251.123.33:48829 dest: /10.251.123.33:50010
[E22] 081111 054009 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand5/_temporary/_task_200811101024_0011_m_001033_0/part-01033. blk_-7453557116554566888
[E5] 081111 054010 21149 INFO dfs.DataNode$DataXceiver: Receiving block blk_-7453557116554566888 src: /10.251.39.209:40761 dest: /10.251.39.209:50010
[E11] 081111 054104 15764 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-7453557116554566888 terminating
[E9] 081111 054104 15764 INFO dfs.DataNode$PacketResponder: Received block blk_-7453557116554566888 of size 67108864 from /10.251.123.33
[E11] 081111 054104 21032 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-7453557116554566888 terminating
[E9] 081111 054104 21032 INFO dfs.DataNode$PacketResponder: Received block blk_-7453557116554566888 of size 67108864 from /10.251.123.33
[E11] 081111 054104 21150 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-7453557116554566888 terminating
[E9] 081111 054104 21150 INFO dfs.DataNode$PacketResponder: Received block blk_-7453557116554566888 of size 67108864 from /10.251.39.209
[E26] 081111 054104 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.123.33:50010 is added to blk_-7453557116554566888 size 67108864
[E26] 081111 054104 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.39.209:50010 is added to blk_-7453557116554566888 size 67108864
[E26] 081111 054104 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.91.159:50010 is added to blk_-7453557116554566888 size 67108864
[E23] 081111 075628 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-7453557116554566888 is added to invalidSet of 10.251.123.33:50010
[E23] 081111 075628 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-7453557116554566888 is added to invalidSet of 10.251.39.209:50010
[E23] 081111 075628 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-7453557116554566888 is added to invalidSet of 10.251.91.159:50010
[E21] 081111 075750 18 INFO dfs.FSDataset: Deleting block blk_-7453557116554566888 file /mnt/hadoop/dfs/data/current/subdir44/blk_-7453557116554566888
[E21] 081111 075754 19 INFO dfs.FSDataset: Deleting block blk_-7453557116554566888 file /mnt/hadoop/dfs/data/current/subdir34/blk_-7453557116554566888
[E21] 081111 075810 19 INFO dfs.FSDataset: Deleting block blk_-7453557116554566888 file /mnt/hadoop/dfs/data/current/subdir3/blk_-7453557116554566888
```

### Résumé proposé

La trace montre la réception et l'allocation d'un bloc HDFS, suivies de confirmations de réception et de son enregistrement sur trois DataNodes. Le bloc est ensuite ajouté aux ensembles d'invalidation de trois DataNodes. Des suppressions locales du bloc sont ensuite journalisées.

### Faits observés

- E5 : trois débuts de réception du bloc sont journalisés.
- E22 : une allocation du bloc est journalisée.
- E9 : trois confirmations de réception sont journalisées.
- E26 : le bloc est enregistré sur trois DataNodes.
- E23 : trois ajouts aux ensembles d'invalidation sont journalisés.
- E21 : 3 suppressions locales sont journalisées.

### Hypothèses


### Informations manquantes

- Motif des invalidations et suppressions.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0009 — blk_7345670855121510431

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 033145 19143 INFO dfs.DataNode$DataXceiver: Receiving block blk_7345670855121510431 src: /10.250.6.191:52032 dest: /10.250.6.191:50010
[E22] 081111 033145 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand4/_temporary/_task_200811101024_0009_m_001731_0/part-01731. blk_7345670855121510431
[E5] 081111 033146 18572 INFO dfs.DataNode$DataXceiver: Receiving block blk_7345670855121510431 src: /10.251.106.214:50282 dest: /10.251.106.214:50010
[E5] 081111 033146 18606 INFO dfs.DataNode$DataXceiver: Receiving block blk_7345670855121510431 src: /10.250.6.191:48694 dest: /10.250.6.191:50010
[E11] 081111 033235 18573 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_7345670855121510431 terminating
[E9] 081111 033235 18573 INFO dfs.DataNode$PacketResponder: Received block blk_7345670855121510431 of size 67108864 from /10.251.106.214
[E11] 081111 033235 18607 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_7345670855121510431 terminating
[E9] 081111 033235 18607 INFO dfs.DataNode$PacketResponder: Received block blk_7345670855121510431 of size 67108864 from /10.250.6.191
[E11] 081111 033235 19144 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_7345670855121510431 terminating
[E9] 081111 033235 19144 INFO dfs.DataNode$PacketResponder: Received block blk_7345670855121510431 of size 67108864 from /10.250.6.191
[E26] 081111 033235 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.6.191:50010 is added to blk_7345670855121510431 size 67108864
[E26] 081111 033235 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.14.224:50010 is added to blk_7345670855121510431 size 67108864
[E26] 081111 033235 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.106.214:50010 is added to blk_7345670855121510431 size 67108864
[E23] 081111 044322 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_7345670855121510431 is added to invalidSet of 10.250.14.224:50010
[E23] 081111 044322 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_7345670855121510431 is added to invalidSet of 10.250.6.191:50010
[E23] 081111 044322 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_7345670855121510431 is added to invalidSet of 10.251.106.214:50010
[E21] 081111 044753 19 INFO dfs.FSDataset: Deleting block blk_7345670855121510431 file /mnt/hadoop/dfs/data/current/subdir58/blk_7345670855121510431
[E21] 081111 044754 19 INFO dfs.FSDataset: Deleting block blk_7345670855121510431 file /mnt/hadoop/dfs/data/current/subdir17/blk_7345670855121510431
[E21] 081111 044816 19 INFO dfs.FSDataset: Deleting block blk_7345670855121510431 file /mnt/hadoop/dfs/data/current/subdir26/blk_7345670855121510431
```

### Résumé proposé

La trace montre la réception et l'allocation d'un bloc HDFS, suivies de confirmations de réception et de son enregistrement sur trois DataNodes. Le bloc est ensuite ajouté aux ensembles d'invalidation de trois DataNodes. Des suppressions locales du bloc sont ensuite journalisées.

### Faits observés

- E5 : trois débuts de réception du bloc sont journalisés.
- E22 : une allocation du bloc est journalisée.
- E9 : trois confirmations de réception sont journalisées.
- E26 : le bloc est enregistré sur trois DataNodes.
- E23 : trois ajouts aux ensembles d'invalidation sont journalisés.
- E21 : 3 suppressions locales sont journalisées.

### Hypothèses


### Informations manquantes

- Motif des invalidations et suppressions.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0010 — blk_-2575947670106144473

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E22] 081111 045515 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand5/_temporary/_task_200811101024_0011_m_000072_0/part-00072. blk_-2575947670106144473
[E5] 081111 045516 20348 INFO dfs.DataNode$DataXceiver: Receiving block blk_-2575947670106144473 src: /10.251.193.224:39823 dest: /10.251.193.224:50010
[E5] 081111 045516 20481 INFO dfs.DataNode$DataXceiver: Receiving block blk_-2575947670106144473 src: /10.251.193.224:48677 dest: /10.251.193.224:50010
[E5] 081111 045519 20284 INFO dfs.DataNode$DataXceiver: Receiving block blk_-2575947670106144473 src: /10.251.199.245:55216 dest: /10.251.199.245:50010
[E11] 081111 045559 20285 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-2575947670106144473 terminating
[E9] 081111 045559 20285 INFO dfs.DataNode$PacketResponder: Received block blk_-2575947670106144473 of size 67108864 from /10.251.199.245
[E11] 081111 045559 20351 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-2575947670106144473 terminating
[E9] 081111 045559 20351 INFO dfs.DataNode$PacketResponder: Received block blk_-2575947670106144473 of size 67108864 from /10.251.193.224
[E11] 081111 045559 20482 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-2575947670106144473 terminating
[E9] 081111 045559 20482 INFO dfs.DataNode$PacketResponder: Received block blk_-2575947670106144473 of size 67108864 from /10.251.193.224
[E26] 081111 045559 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.193.224:50010 is added to blk_-2575947670106144473 size 67108864
[E26] 081111 045559 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.199.245:50010 is added to blk_-2575947670106144473 size 67108864
[E26] 081111 045559 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.199.150:50010 is added to blk_-2575947670106144473 size 67108864
[E23] 081111 075617 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-2575947670106144473 is added to invalidSet of 10.251.193.224:50010
[E23] 081111 075617 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-2575947670106144473 is added to invalidSet of 10.251.199.150:50010
[E23] 081111 075617 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-2575947670106144473 is added to invalidSet of 10.251.199.245:50010
[E21] 081111 075837 19 INFO dfs.FSDataset: Deleting block blk_-2575947670106144473 file /mnt/hadoop/dfs/data/current/subdir28/blk_-2575947670106144473
[E21] 081111 075859 19 INFO dfs.FSDataset: Deleting block blk_-2575947670106144473 file /mnt/hadoop/dfs/data/current/blk_-2575947670106144473
[E21] 081111 075912 19 INFO dfs.FSDataset: Deleting block blk_-2575947670106144473 file /mnt/hadoop/dfs/data/current/subdir52/blk_-2575947670106144473
```

### Résumé proposé

La trace montre la réception et l'allocation d'un bloc HDFS, suivies de confirmations de réception et de son enregistrement sur trois DataNodes. Le bloc est ensuite ajouté aux ensembles d'invalidation de trois DataNodes. Des suppressions locales du bloc sont ensuite journalisées.

### Faits observés

- E5 : trois débuts de réception du bloc sont journalisés.
- E22 : une allocation du bloc est journalisée.
- E9 : trois confirmations de réception sont journalisées.
- E26 : le bloc est enregistré sur trois DataNodes.
- E23 : trois ajouts aux ensembles d'invalidation sont journalisés.
- E21 : 3 suppressions locales sont journalisées.

### Hypothèses


### Informations manquantes

- Motif des invalidations et suppressions.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0011 — blk_6263807359485750335

**Label officiel :** 0

**Abstention proposée :** True

### Trace originale

```text
[E22] 081109 204549 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand/_temporary/_task_200811092030_0001_m_000440_0/part-00440. blk_6263807359485750335
[E5] 081109 204549 531 INFO dfs.DataNode$DataXceiver: Receiving block blk_6263807359485750335 src: /10.251.74.227:57112 dest: /10.251.74.227:50010
[E5] 081109 204549 539 INFO dfs.DataNode$DataXceiver: Receiving block blk_6263807359485750335 src: /10.251.74.227:57803 dest: /10.251.74.227:50010
[E5] 081109 204550 515 INFO dfs.DataNode$DataXceiver: Receiving block blk_6263807359485750335 src: /10.251.110.68:36478 dest: /10.251.110.68:50010
[E26] 081109 204633 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.215.70:50010 is added to blk_6263807359485750335 size 67108864
[E26] 081109 204633 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.110.68:50010 is added to blk_6263807359485750335 size 67108864
[E26] 081109 204633 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.74.227:50010 is added to blk_6263807359485750335 size 67108864
[E11] 081109 204633 518 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_6263807359485750335 terminating
[E9] 081109 204633 518 INFO dfs.DataNode$PacketResponder: Received block blk_6263807359485750335 of size 67108864 from /10.251.110.68
[E11] 081109 204633 533 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_6263807359485750335 terminating
[E9] 081109 204633 533 INFO dfs.DataNode$PacketResponder: Received block blk_6263807359485750335 of size 67108864 from /10.251.74.227
[E11] 081109 204633 540 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_6263807359485750335 terminating
[E9] 081109 204633 540 INFO dfs.DataNode$PacketResponder: Received block blk_6263807359485750335 of size 67108864 from /10.251.74.227
[E4] 081109 214025 2594 WARN dfs.DataNode$DataXceiver: 10.251.110.68:50010:Got exception while serving blk_6263807359485750335 to /10.250.7.244:
[E4] 081109 215201 2919 WARN dfs.DataNode$DataXceiver: 10.251.215.70:50010:Got exception while serving blk_6263807359485750335 to /10.251.30.6:
[E4] 081109 215209 2909 WARN dfs.DataNode$DataXceiver: 10.251.74.227:50010:Got exception while serving blk_6263807359485750335 to /10.251.31.160:
[E4] 081109 215229 2940 WARN dfs.DataNode$DataXceiver: 10.251.215.70:50010:Got exception while serving blk_6263807359485750335 to /10.251.110.8:
[E4] 081109 215237 2947 WARN dfs.DataNode$DataXceiver: 10.251.215.70:50010:Got exception while serving blk_6263807359485750335 to /10.251.203.149:
[E4] 081109 215239 2925 WARN dfs.DataNode$DataXceiver: 10.251.110.68:50010:Got exception while serving blk_6263807359485750335 to /10.251.202.209:
[E4] 081109 215245 2952 WARN dfs.DataNode$DataXceiver: 10.251.215.70:50010:Got exception while serving blk_6263807359485750335 to /10.251.30.6:
[E4] 081109 215256 2961 WARN dfs.DataNode$DataXceiver: 10.251.215.70:50010:Got exception while serving blk_6263807359485750335 to /10.251.43.210:
[E3] 081109 215258 2958 INFO dfs.DataNode$DataXceiver: 10.251.215.70:50010 Served block blk_6263807359485750335 to /10.251.215.70
[E4] 081109 215302 2941 WARN dfs.DataNode$DataXceiver: 10.251.74.227:50010:Got exception while serving blk_6263807359485750335 to /10.251.74.227:
[E4] 081109 215320 2953 WARN dfs.DataNode$DataXceiver: 10.251.74.227:50010:Got exception while serving blk_6263807359485750335 to /10.251.127.191:
[E4] 081109 215322 2971 WARN dfs.DataNode$DataXceiver: 10.251.215.70:50010:Got exception while serving blk_6263807359485750335 to /10.251.126.5:
[E4] 081109 215328 2979 WARN dfs.DataNode$DataXceiver: 10.251.215.70:50010:Got exception while serving blk_6263807359485750335 to /10.251.75.79:
[E4] 081109 215334 2961 WARN dfs.DataNode$DataXceiver: 10.251.74.227:50010:Got exception while serving blk_6263807359485750335 to /10.251.89.155:
[E4] 081109 215403 2976 WARN dfs.DataNode$DataXceiver: 10.251.74.227:50010:Got exception while serving blk_6263807359485750335 to /10.251.193.224:
[E4] 081109 215435 2989 WARN dfs.DataNode$DataXceiver: 10.251.74.227:50010:Got exception while serving blk_6263807359485750335 to /10.251.74.227:
[E2] 081110 005350 13 INFO dfs.DataBlockScanner: Verification succeeded for blk_6263807359485750335
[E2] 081110 075153 13 INFO dfs.DataBlockScanner: Verification succeeded for blk_6263807359485750335
[E23] 081110 103059 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_6263807359485750335 is added to invalidSet of 10.251.110.68:50010
[E23] 081110 103059 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_6263807359485750335 is added to invalidSet of 10.251.215.70:50010
[E23] 081110 103059 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_6263807359485750335 is added to invalidSet of 10.251.74.227:50010
[E21] 081110 103514 19 INFO dfs.FSDataset: Deleting block blk_6263807359485750335 file /mnt/hadoop/dfs/data/current/subdir6/blk_6263807359485750335
[E21] 081110 103658 19 INFO dfs.FSDataset: Deleting block blk_6263807359485750335 file /mnt/hadoop/dfs/data/current/subdir36/blk_6263807359485750335
[E21] 081110 103729 19 INFO dfs.FSDataset: Deleting block blk_6263807359485750335 file /mnt/hadoop/dfs/data/current/subdir36/blk_6263807359485750335
```

### Résumé proposé

Le bloc est allou? puis re?u et enregistr? sur trois DataNodes. Quinze avertissements signalent des exceptions pendant le service du bloc ? diff?rents clients, tandis qu'une op?ration de service r?ussie est journalis?e. Deux v?rifications du bloc r?ussissent ensuite. Le bloc est finalement ajout? aux ensembles d'invalidation de trois DataNodes, puis trois suppressions locales sont journalis?es. La cause des exceptions ne peut pas ?tre d?termin?e ? partir de cette trace.

### Faits observés

- E22 : allocation du bloc pour le fichier part-00440.
- E5 : trois d?buts de r?ception sont journalis?s.
- E26 : trois DataNodes sont enregistr?s pour le bloc.
- E9 : trois confirmations de r?ception de 67108864 octets.
- E4 : quinze avertissements d'exception pendant le service du bloc.
- E3 : une op?ration de service r?ussie est journalis?e.
- E2 : deux messages indiquent Verification succeeded.
- E23 : trois ajouts aux ensembles d'invalidation.
- E21 : trois suppressions locales sont journalis?es.

### Hypothèses


### Informations manquantes

- Type et cause des exceptions pendant le service.
- ?tat des connexions et des clients concern?s.
- Relation ?ventuelle entre les exceptions et les v?rifications r?ussies.
- Motif des invalidations et suppressions.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0012 — blk_-8023362441095933590

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081110 220027 15310 INFO dfs.DataNode$DataXceiver: Receiving block blk_-8023362441095933590 src: /10.250.13.188:59015 dest: /10.250.13.188:50010
[E5] 081110 220027 15615 INFO dfs.DataNode$DataXceiver: Receiving block blk_-8023362441095933590 src: /10.251.194.102:37583 dest: /10.251.194.102:50010
[E5] 081110 220027 15719 INFO dfs.DataNode$DataXceiver: Receiving block blk_-8023362441095933590 src: /10.251.194.102:38940 dest: /10.251.194.102:50010
[E22] 081110 220027 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand3/_temporary/_task_200811101024_0005_m_001810_0/part-01810. blk_-8023362441095933590
[E11] 081110 220030 15311 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-8023362441095933590 terminating
[E9] 081110 220030 15311 INFO dfs.DataNode$PacketResponder: Received block blk_-8023362441095933590 of size 3535780 from /10.250.13.188
[E11] 081110 220030 15616 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-8023362441095933590 terminating
[E9] 081110 220030 15616 INFO dfs.DataNode$PacketResponder: Received block blk_-8023362441095933590 of size 3535780 from /10.251.194.102
[E11] 081110 220030 15720 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-8023362441095933590 terminating
[E9] 081110 220030 15720 INFO dfs.DataNode$PacketResponder: Received block blk_-8023362441095933590 of size 3535780 from /10.251.194.102
[E26] 081110 220030 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.194.102:50010 is added to blk_-8023362441095933590 size 3535780
[E26] 081110 220030 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.13.188:50010 is added to blk_-8023362441095933590 size 3535780
[E26] 081110 220030 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.203.166:50010 is added to blk_-8023362441095933590 size 3535780
[E23] 081110 220656 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-8023362441095933590 is added to invalidSet of 10.250.13.188:50010
[E23] 081110 220656 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-8023362441095933590 is added to invalidSet of 10.251.194.102:50010
[E23] 081110 220656 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-8023362441095933590 is added to invalidSet of 10.251.203.166:50010
[E21] 081110 220734 19 INFO dfs.FSDataset: Deleting block blk_-8023362441095933590 file /mnt/hadoop/dfs/data/current/subdir31/blk_-8023362441095933590
[E21] 081110 220833 19 INFO dfs.FSDataset: Deleting block blk_-8023362441095933590 file /mnt/hadoop/dfs/data/current/subdir4/blk_-8023362441095933590
[E21] 081110 220847 19 INFO dfs.FSDataset: Deleting block blk_-8023362441095933590 file /mnt/hadoop/dfs/data/current/subdir13/blk_-8023362441095933590
```

### Résumé proposé

La trace contient les événements suivants : E5 (3), E22 (1), E11 (3), E9 (3), E26 (3), E23 (3), E21 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).
- E23 : ajout du bloc à un ensemble d'invalidation (3 occurrence(s) dans la trace).
- E21 : suppression locale du bloc (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes


### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0013 — blk_2090914087051952031

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E22] 081111 081532 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand7/_temporary/_task_200811101024_0014_m_000718_0/part-00718. blk_2090914087051952031
[E5] 081111 081533 23715 INFO dfs.DataNode$DataXceiver: Receiving block blk_2090914087051952031 src: /10.251.203.4:53154 dest: /10.251.203.4:50010
[E5] 081111 081533 24188 INFO dfs.DataNode$DataXceiver: Receiving block blk_2090914087051952031 src: /10.251.203.4:50317 dest: /10.251.203.4:50010
[E5] 081111 081536 24108 INFO dfs.DataNode$DataXceiver: Receiving block blk_2090914087051952031 src: /10.251.75.143:41748 dest: /10.251.75.143:50010
[E11] 081111 081611 24109 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_2090914087051952031 terminating
[E9] 081111 081611 24109 INFO dfs.DataNode$PacketResponder: Received block blk_2090914087051952031 of size 67108864 from /10.251.75.143
[E26] 081111 081611 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.194.102:50010 is added to blk_2090914087051952031 size 67108864
[E11] 081111 081612 23718 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_2090914087051952031 terminating
[E9] 081111 081612 23718 INFO dfs.DataNode$PacketResponder: Received block blk_2090914087051952031 of size 67108864 from /10.251.203.4
[E11] 081111 081612 24189 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_2090914087051952031 terminating
[E9] 081111 081612 24189 INFO dfs.DataNode$PacketResponder: Received block blk_2090914087051952031 of size 67108864 from /10.251.203.4
[E26] 081111 081612 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.75.143:50010 is added to blk_2090914087051952031 size 67108864
[E26] 081111 081612 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.203.4:50010 is added to blk_2090914087051952031 size 67108864
```

### Résumé proposé

La trace contient les événements suivants : E22 (1), E5 (3), E11 (3), E9 (3), E26 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes


### Sources C6 candidates

hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0014 — blk_7842450760472974441

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 101517 26120 INFO dfs.DataNode$DataXceiver: Receiving block blk_7842450760472974441 src: /10.250.10.213:42421 dest: /10.250.10.213:50010
[E5] 081111 101517 26504 INFO dfs.DataNode$DataXceiver: Receiving block blk_7842450760472974441 src: /10.250.10.213:54128 dest: /10.250.10.213:50010
[E22] 081111 101517 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/randtxt9/_temporary/_task_200811101024_0016_m_000720_0/part-00720. blk_7842450760472974441
[E5] 081111 101518 26162 INFO dfs.DataNode$DataXceiver: Receiving block blk_7842450760472974441 src: /10.251.39.209:38022 dest: /10.251.39.209:50010
[E11] 081111 101550 26121 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_7842450760472974441 terminating
[E9] 081111 101550 26121 INFO dfs.DataNode$PacketResponder: Received block blk_7842450760472974441 of size 67108864 from /10.250.10.213
[E11] 081111 101550 26163 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_7842450760472974441 terminating
[E9] 081111 101550 26163 INFO dfs.DataNode$PacketResponder: Received block blk_7842450760472974441 of size 67108864 from /10.251.39.209
[E11] 081111 101550 26505 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_7842450760472974441 terminating
[E9] 081111 101550 26505 INFO dfs.DataNode$PacketResponder: Received block blk_7842450760472974441 of size 67108864 from /10.250.10.213
[E26] 081111 101550 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.214.225:50010 is added to blk_7842450760472974441 size 67108864
[E26] 081111 101550 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.39.209:50010 is added to blk_7842450760472974441 size 67108864
[E26] 081111 101550 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.10.213:50010 is added to blk_7842450760472974441 size 67108864
[E23] 081111 110433 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_7842450760472974441 is added to invalidSet of 10.250.10.213:50010
[E23] 081111 110433 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_7842450760472974441 is added to invalidSet of 10.251.214.225:50010
[E23] 081111 110433 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_7842450760472974441 is added to invalidSet of 10.251.39.209:50010
[E21] 081111 110605 19 INFO dfs.FSDataset: Deleting block blk_7842450760472974441 file /mnt/hadoop/dfs/data/current/subdir60/blk_7842450760472974441
[E21] 081111 110608 18 INFO dfs.FSDataset: Deleting block blk_7842450760472974441 file /mnt/hadoop/dfs/data/current/subdir14/blk_7842450760472974441
[E21] 081111 110610 19 INFO dfs.FSDataset: Deleting block blk_7842450760472974441 file /mnt/hadoop/dfs/data/current/subdir4/blk_7842450760472974441
```

### Résumé proposé

La trace contient les événements suivants : E5 (3), E22 (1), E11 (3), E9 (3), E26 (3), E23 (3), E21 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).
- E23 : ajout du bloc à un ensemble d'invalidation (3 occurrence(s) dans la trace).
- E21 : suppression locale du bloc (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes


### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0015 — blk_-3470499101952745743

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E22] 081110 105056 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand/_temporary/_task_200811101024_0001_m_000570_0/part-00570. blk_-3470499101952745743
[E5] 081110 105057 9259 INFO dfs.DataNode$DataXceiver: Receiving block blk_-3470499101952745743 src: /10.251.126.22:60879 dest: /10.251.126.22:50010
[E5] 081110 105101 9104 INFO dfs.DataNode$DataXceiver: Receiving block blk_-3470499101952745743 src: /10.251.214.130:50385 dest: /10.251.214.130:50010
[E5] 081110 105101 9197 INFO dfs.DataNode$DataXceiver: Receiving block blk_-3470499101952745743 src: /10.251.126.22:45308 dest: /10.251.126.22:50010
[E26] 081110 105154 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.214.130:50010 is added to blk_-3470499101952745743 size 67108864
[E26] 081110 105154 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.126.22:50010 is added to blk_-3470499101952745743 size 67108864
[E26] 081110 105154 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.202.181:50010 is added to blk_-3470499101952745743 size 67108864
[E11] 081110 105154 9105 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-3470499101952745743 terminating
[E9] 081110 105154 9105 INFO dfs.DataNode$PacketResponder: Received block blk_-3470499101952745743 of size 67108864 from /10.251.214.130
[E11] 081110 105154 9198 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-3470499101952745743 terminating
[E9] 081110 105154 9198 INFO dfs.DataNode$PacketResponder: Received block blk_-3470499101952745743 of size 67108864 from /10.251.126.22
[E11] 081110 105154 9260 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-3470499101952745743 terminating
[E9] 081110 105154 9260 INFO dfs.DataNode$PacketResponder: Received block blk_-3470499101952745743 of size 67108864 from /10.251.126.22
[E4] 081110 130439 11498 WARN dfs.DataNode$DataXceiver: 10.251.214.130:50010:Got exception while serving blk_-3470499101952745743 to /10.251.203.80:
[E4] 081110 130500 11624 WARN dfs.DataNode$DataXceiver: 10.251.126.22:50010:Got exception while serving blk_-3470499101952745743 to /10.251.127.47:
[E3] 081110 130509 11625 INFO dfs.DataNode$DataXceiver: 10.251.126.22:50010 Served block blk_-3470499101952745743 to /10.251.127.47
[E2] 081110 162933 13 INFO dfs.DataBlockScanner: Verification succeeded for blk_-3470499101952745743
[E23] 081110 210145 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-3470499101952745743 is added to invalidSet of 10.251.126.22:50010
[E23] 081110 210145 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-3470499101952745743 is added to invalidSet of 10.251.202.181:50010
[E23] 081110 210145 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-3470499101952745743 is added to invalidSet of 10.251.214.130:50010
[E21] 081110 210448 19 INFO dfs.FSDataset: Deleting block blk_-3470499101952745743 file /mnt/hadoop/dfs/data/current/subdir22/blk_-3470499101952745743
[E21] 081110 210451 19 INFO dfs.FSDataset: Deleting block blk_-3470499101952745743 file /mnt/hadoop/dfs/data/current/subdir8/blk_-3470499101952745743
[E21] 081110 210515 18 INFO dfs.FSDataset: Deleting block blk_-3470499101952745743 file /mnt/hadoop/dfs/data/current/subdir23/blk_-3470499101952745743
```

### Résumé proposé

La trace contient les événements suivants : E22 (1), E5 (3), E26 (3), E11 (3), E9 (3), E4 (2), E3 (1), E2 (1), E23 (3), E21 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E4 : avertissement d'exception pendant le service (2 occurrence(s) dans la trace).
- E3 : service du bloc (1 occurrence(s) dans la trace).
- E2 : vérification du bloc à examiner dans les logs (1 occurrence(s) dans la trace).
- E23 : ajout du bloc à un ensemble d'invalidation (3 occurrence(s) dans la trace).
- E21 : suppression locale du bloc (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes

- Nature des avertissements ou erreurs à examiner.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0016 — blk_2034555571908900806

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 031744 18493 INFO dfs.DataNode$DataXceiver: Receiving block blk_2034555571908900806 src: /10.251.75.143:35140 dest: /10.251.75.143:50010
[E5] 081111 031744 18579 INFO dfs.DataNode$DataXceiver: Receiving block blk_2034555571908900806 src: /10.251.75.143:38832 dest: /10.251.75.143:50010
[E22] 081111 031744 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand4/_temporary/_task_200811101024_0009_m_001487_0/part-01487. blk_2034555571908900806
[E5] 081111 031745 18642 INFO dfs.DataNode$DataXceiver: Receiving block blk_2034555571908900806 src: /10.251.91.159:40235 dest: /10.251.91.159:50010
[E26] 081111 031817 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.91.159:50010 is added to blk_2034555571908900806 size 67108864
[E26] 081111 031817 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.39.179:50010 is added to blk_2034555571908900806 size 67108864
[E11] 081111 031818 18494 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_2034555571908900806 terminating
[E9] 081111 031818 18494 INFO dfs.DataNode$PacketResponder: Received block blk_2034555571908900806 of size 67108864 from /10.251.75.143
[E11] 081111 031818 18580 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_2034555571908900806 terminating
[E9] 081111 031818 18580 INFO dfs.DataNode$PacketResponder: Received block blk_2034555571908900806 of size 67108864 from /10.251.75.143
[E11] 081111 031818 18643 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_2034555571908900806 terminating
[E9] 081111 031818 18643 INFO dfs.DataNode$PacketResponder: Received block blk_2034555571908900806 of size 67108864 from /10.251.91.159
[E26] 081111 031818 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.75.143:50010 is added to blk_2034555571908900806 size 67108864
[E23] 081111 044319 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_2034555571908900806 is added to invalidSet of 10.251.39.179:50010
[E23] 081111 044319 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_2034555571908900806 is added to invalidSet of 10.251.75.143:50010
[E23] 081111 044319 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_2034555571908900806 is added to invalidSet of 10.251.91.159:50010
[E21] 081111 044634 19 INFO dfs.FSDataset: Deleting block blk_2034555571908900806 file /mnt/hadoop/dfs/data/current/subdir15/blk_2034555571908900806
[E21] 081111 044713 19 INFO dfs.FSDataset: Deleting block blk_2034555571908900806 file /mnt/hadoop/dfs/data/current/subdir50/blk_2034555571908900806
[E21] 081111 044758 19 INFO dfs.FSDataset: Deleting block blk_2034555571908900806 file /mnt/hadoop/dfs/data/current/subdir12/blk_2034555571908900806
```

### Résumé proposé

La trace contient les événements suivants : E5 (3), E22 (1), E26 (3), E11 (3), E9 (3), E23 (3), E21 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E23 : ajout du bloc à un ensemble d'invalidation (3 occurrence(s) dans la trace).
- E21 : suppression locale du bloc (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes


### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0017 — blk_-12138228845474377

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 044450 15097 INFO dfs.DataNode$DataXceiver: Receiving block blk_-12138228845474377 src: /10.251.123.33:39004 dest: /10.251.123.33:50010
[E5] 081111 044450 20229 INFO dfs.DataNode$DataXceiver: Receiving block blk_-12138228845474377 src: /10.251.123.33:35121 dest: /10.251.123.33:50010
[E5] 081111 044450 20286 INFO dfs.DataNode$DataXceiver: Receiving block blk_-12138228845474377 src: /10.251.110.8:33505 dest: /10.251.110.8:50010
[E22] 081111 044450 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand5/_temporary/_task_200811101024_0011_m_000352_0/part-00352. blk_-12138228845474377
[E11] 081111 044526 15098 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-12138228845474377 terminating
[E9] 081111 044526 15098 INFO dfs.DataNode$PacketResponder: Received block blk_-12138228845474377 of size 67108864 from /10.251.123.33
[E11] 081111 044526 20231 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-12138228845474377 terminating
[E9] 081111 044526 20231 INFO dfs.DataNode$PacketResponder: Received block blk_-12138228845474377 of size 67108864 from /10.251.123.33
[E11] 081111 044526 20287 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-12138228845474377 terminating
[E9] 081111 044526 20287 INFO dfs.DataNode$PacketResponder: Received block blk_-12138228845474377 of size 67108864 from /10.251.110.8
[E26] 081111 044818 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.110.8:50010 is added to blk_-12138228845474377 size 67108864
[E26] 081111 044942 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.214.112:50010 is added to blk_-12138228845474377 size 67108864
[E26] 081111 050545 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.123.33:50010 is added to blk_-12138228845474377 size 67108864
[E23] 081111 075620 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-12138228845474377 is added to invalidSet of 10.251.110.8:50010
[E23] 081111 075620 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-12138228845474377 is added to invalidSet of 10.251.123.33:50010
[E23] 081111 075620 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-12138228845474377 is added to invalidSet of 10.251.214.112:50010
[E21] 081111 075833 19 INFO dfs.FSDataset: Deleting block blk_-12138228845474377 file /mnt/hadoop/dfs/data/current/blk_-12138228845474377
[E21] 081111 075839 19 INFO dfs.FSDataset: Deleting block blk_-12138228845474377 file /mnt/hadoop/dfs/data/current/subdir31/blk_-12138228845474377
[E21] 081111 075856 19 INFO dfs.FSDataset: Deleting block blk_-12138228845474377 file /mnt/hadoop/dfs/data/current/subdir14/blk_-12138228845474377
```

### Résumé proposé

La trace contient les événements suivants : E5 (3), E22 (1), E11 (3), E9 (3), E26 (3), E23 (3), E21 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).
- E23 : ajout du bloc à un ensemble d'invalidation (3 occurrence(s) dans la trace).
- E21 : suppression locale du bloc (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes


### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0018 — blk_5954640055410099815

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 024647 17785 INFO dfs.DataNode$DataXceiver: Receiving block blk_5954640055410099815 src: /10.251.66.102:44513 dest: /10.251.66.102:50010
[E5] 081111 024647 17854 INFO dfs.DataNode$DataXceiver: Receiving block blk_5954640055410099815 src: /10.250.14.196:37818 dest: /10.250.14.196:50010
[E5] 081111 024647 17978 INFO dfs.DataNode$DataXceiver: Receiving block blk_5954640055410099815 src: /10.250.14.196:40414 dest: /10.250.14.196:50010
[E22] 081111 024647 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand4/_temporary/_task_200811101024_0009_m_000341_0/part-00341. blk_5954640055410099815
[E11] 081111 024709 17786 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_5954640055410099815 terminating
[E9] 081111 024709 17786 INFO dfs.DataNode$PacketResponder: Received block blk_5954640055410099815 of size 67108864 from /10.251.66.102
[E11] 081111 024709 17979 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_5954640055410099815 terminating
[E9] 081111 024709 17979 INFO dfs.DataNode$PacketResponder: Received block blk_5954640055410099815 of size 67108864 from /10.250.14.196
[E26] 081111 024709 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.123.132:50010 is added to blk_5954640055410099815 size 67108864
[E26] 081111 024709 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.66.102:50010 is added to blk_5954640055410099815 size 67108864
[E11] 081111 024710 17855 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_5954640055410099815 terminating
[E9] 081111 024710 17855 INFO dfs.DataNode$PacketResponder: Received block blk_5954640055410099815 of size 67108864 from /10.250.14.196
[E26] 081111 024710 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.14.196:50010 is added to blk_5954640055410099815 size 67108864
[E23] 081111 044306 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_5954640055410099815 is added to invalidSet of 10.250.14.196:50010
[E23] 081111 044306 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_5954640055410099815 is added to invalidSet of 10.251.123.132:50010
[E23] 081111 044306 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_5954640055410099815 is added to invalidSet of 10.251.66.102:50010
[E21] 081111 044811 19 INFO dfs.FSDataset: Deleting block blk_5954640055410099815 file /mnt/hadoop/dfs/data/current/subdir23/blk_5954640055410099815
[E21] 081111 044816 19 INFO dfs.FSDataset: Deleting block blk_5954640055410099815 file /mnt/hadoop/dfs/data/current/subdir28/blk_5954640055410099815
[E21] 081111 044846 19 INFO dfs.FSDataset: Deleting block blk_5954640055410099815 file /mnt/hadoop/dfs/data/current/subdir55/blk_5954640055410099815
```

### Résumé proposé

La trace contient les événements suivants : E5 (3), E22 (1), E11 (3), E9 (3), E26 (3), E23 (3), E21 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).
- E23 : ajout du bloc à un ensemble d'invalidation (3 occurrence(s) dans la trace).
- E21 : suppression locale du bloc (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes


### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0019 — blk_-1280277122957483102

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081110 144606 12635 INFO dfs.DataNode$DataXceiver: Receiving block blk_-1280277122957483102 src: /10.251.214.112:39429 dest: /10.251.214.112:50010
[E5] 081110 144606 12648 INFO dfs.DataNode$DataXceiver: Receiving block blk_-1280277122957483102 src: /10.251.215.192:60740 dest: /10.251.215.192:50010
[E5] 081110 144606 12948 INFO dfs.DataNode$DataXceiver: Receiving block blk_-1280277122957483102 src: /10.251.214.112:33461 dest: /10.251.214.112:50010
[E22] 081110 144606 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/sortrand2/_temporary/_task_200811101024_0003_r_000277_0/part-00277. blk_-1280277122957483102
[E11] 081110 144720 12636 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-1280277122957483102 terminating
[E9] 081110 144720 12636 INFO dfs.DataNode$PacketResponder: Received block blk_-1280277122957483102 of size 67108864 from /10.251.214.112
[E11] 081110 144720 12649 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-1280277122957483102 terminating
[E9] 081110 144720 12649 INFO dfs.DataNode$PacketResponder: Received block blk_-1280277122957483102 of size 67108864 from /10.251.215.192
[E11] 081110 144720 12949 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-1280277122957483102 terminating
[E9] 081110 144720 12949 INFO dfs.DataNode$PacketResponder: Received block blk_-1280277122957483102 of size 67108864 from /10.251.214.112
[E26] 081110 144720 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.215.192:50010 is added to blk_-1280277122957483102 size 67108864
[E26] 081110 144720 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.214.112:50010 is added to blk_-1280277122957483102 size 67108864
[E26] 081110 144720 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.127.47:50010 is added to blk_-1280277122957483102 size 67108864
[E23] 081110 210130 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-1280277122957483102 is added to invalidSet of 10.251.127.47:50010
[E23] 081110 210130 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-1280277122957483102 is added to invalidSet of 10.251.214.112:50010
[E23] 081110 210130 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-1280277122957483102 is added to invalidSet of 10.251.215.192:50010
[E21] 081110 210512 19 INFO dfs.FSDataset: Deleting block blk_-1280277122957483102 file /mnt/hadoop/dfs/data/current/subdir10/blk_-1280277122957483102
[E21] 081110 210516 19 INFO dfs.FSDataset: Deleting block blk_-1280277122957483102 file /mnt/hadoop/dfs/data/current/subdir49/blk_-1280277122957483102
[E21] 081110 210522 19 INFO dfs.FSDataset: Deleting block blk_-1280277122957483102 file /mnt/hadoop/dfs/data/current/subdir9/blk_-1280277122957483102
```

### Résumé proposé

La trace contient les événements suivants : E5 (3), E22 (1), E11 (3), E9 (3), E26 (3), E23 (3), E21 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).
- E23 : ajout du bloc à un ensemble d'invalidation (3 occurrence(s) dans la trace).
- E21 : suppression locale du bloc (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes


### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0020 — blk_-3469211513507921496

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 104855 27170 INFO dfs.DataNode$DataXceiver: Receiving block blk_-3469211513507921496 src: /10.251.110.160:47409 dest: /10.251.110.160:50010
[E5] 081111 104855 27186 INFO dfs.DataNode$DataXceiver: Receiving block blk_-3469211513507921496 src: /10.251.110.160:42285 dest: /10.251.110.160:50010
[E5] 081111 104855 27516 INFO dfs.DataNode$DataXceiver: Receiving block blk_-3469211513507921496 src: /10.251.65.237:60446 dest: /10.251.65.237:50010
[E22] 081111 104855 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/randtxt9/_temporary/_task_200811101024_0016_m_001576_0/part-01576. blk_-3469211513507921496
[E26] 081111 104900 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.11.53:50010 is added to blk_-3469211513507921496 size 3533472
[E11] 081111 104900 27517 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-3469211513507921496 terminating
[E9] 081111 104900 27517 INFO dfs.DataNode$PacketResponder: Received block blk_-3469211513507921496 of size 3533472 from /10.251.65.237
[E11] 081111 104901 27171 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-3469211513507921496 terminating
[E9] 081111 104901 27171 INFO dfs.DataNode$PacketResponder: Received block blk_-3469211513507921496 of size 3533472 from /10.251.110.160
[E11] 081111 104901 27188 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-3469211513507921496 terminating
[E9] 081111 104901 27188 INFO dfs.DataNode$PacketResponder: Received block blk_-3469211513507921496 of size 3533472 from /10.251.110.160
[E26] 081111 104901 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.65.237:50010 is added to blk_-3469211513507921496 size 3533472
[E26] 081111 104901 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.110.160:50010 is added to blk_-3469211513507921496 size 3533472
[E23] 081111 110443 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-3469211513507921496 is added to invalidSet of 10.250.11.53:50010
[E23] 081111 110443 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-3469211513507921496 is added to invalidSet of 10.251.110.160:50010
[E23] 081111 110443 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-3469211513507921496 is added to invalidSet of 10.251.65.237:50010
[E21] 081111 110520 19 INFO dfs.FSDataset: Deleting block blk_-3469211513507921496 file /mnt/hadoop/dfs/data/current/subdir20/blk_-3469211513507921496
[E21] 081111 110543 19 INFO dfs.FSDataset: Deleting block blk_-3469211513507921496 file /mnt/hadoop/dfs/data/current/subdir48/blk_-3469211513507921496
[E21] 081111 110556 19 INFO dfs.FSDataset: Deleting block blk_-3469211513507921496 file /mnt/hadoop/dfs/data/current/subdir8/blk_-3469211513507921496
```

### Résumé proposé

La trace contient les événements suivants : E5 (3), E22 (1), E26 (3), E11 (3), E9 (3), E23 (3), E21 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E23 : ajout du bloc à un ensemble d'invalidation (3 occurrence(s) dans la trace).
- E21 : suppression locale du bloc (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes


### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0021 — blk_5444836772391403403

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 030609 18103 INFO dfs.DataNode$DataXceiver: Receiving block blk_5444836772391403403 src: /10.251.107.196:44304 dest: /10.251.107.196:50010
[E5] 081111 030609 18305 INFO dfs.DataNode$DataXceiver: Receiving block blk_5444836772391403403 src: /10.251.214.67:38472 dest: /10.251.214.67:50010
[E5] 081111 030609 18324 INFO dfs.DataNode$DataXceiver: Receiving block blk_5444836772391403403 src: /10.251.214.67:59848 dest: /10.251.214.67:50010
[E22] 081111 030609 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand4/_temporary/_task_200811101024_0009_m_001096_0/part-01096. blk_5444836772391403403
[E11] 081111 030644 18104 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_5444836772391403403 terminating
[E9] 081111 030644 18104 INFO dfs.DataNode$PacketResponder: Received block blk_5444836772391403403 of size 67108864 from /10.251.107.196
[E11] 081111 030644 18306 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_5444836772391403403 terminating
[E9] 081111 030644 18306 INFO dfs.DataNode$PacketResponder: Received block blk_5444836772391403403 of size 67108864 from /10.251.214.67
[E11] 081111 030644 18325 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_5444836772391403403 terminating
[E9] 081111 030644 18325 INFO dfs.DataNode$PacketResponder: Received block blk_5444836772391403403 of size 67108864 from /10.251.214.67
[E26] 081111 030644 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.73.220:50010 is added to blk_5444836772391403403 size 67108864
[E26] 081111 030644 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.214.67:50010 is added to blk_5444836772391403403 size 67108864
[E26] 081111 030644 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.107.196:50010 is added to blk_5444836772391403403 size 67108864
[E23] 081111 044315 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_5444836772391403403 is added to invalidSet of 10.251.107.196:50010
[E23] 081111 044315 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_5444836772391403403 is added to invalidSet of 10.251.214.67:50010
[E23] 081111 044315 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_5444836772391403403 is added to invalidSet of 10.251.73.220:50010
[E21] 081111 044645 19 INFO dfs.FSDataset: Deleting block blk_5444836772391403403 file /mnt/hadoop/dfs/data/current/subdir51/blk_5444836772391403403
[E21] 081111 044725 19 INFO dfs.FSDataset: Deleting block blk_5444836772391403403 file /mnt/hadoop/dfs/data/current/subdir31/blk_5444836772391403403
[E21] 081111 044820 19 INFO dfs.FSDataset: Deleting block blk_5444836772391403403 file /mnt/hadoop/dfs/data/current/subdir10/blk_5444836772391403403
```

### Résumé proposé

La trace contient les événements suivants : E5 (3), E22 (1), E11 (3), E9 (3), E26 (3), E23 (3), E21 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).
- E23 : ajout du bloc à un ensemble d'invalidation (3 occurrence(s) dans la trace).
- E21 : suppression locale du bloc (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes


### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0022 — blk_2284131606093448390

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 060456 21280 INFO dfs.DataNode$DataXceiver: Receiving block blk_2284131606093448390 src: /10.251.107.242:47891 dest: /10.251.107.242:50010
[E5] 081111 060456 21410 INFO dfs.DataNode$DataXceiver: Receiving block blk_2284131606093448390 src: /10.250.6.4:33905 dest: /10.250.6.4:50010
[E5] 081111 060456 21707 INFO dfs.DataNode$DataXceiver: Receiving block blk_2284131606093448390 src: /10.251.107.242:43536 dest: /10.251.107.242:50010
[E22] 081111 060456 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/randtxt5/_temporary/_task_200811101024_0012_m_000585_0/part-00585. blk_2284131606093448390
[E11] 081111 060612 21411 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_2284131606093448390 terminating
[E9] 081111 060612 21411 INFO dfs.DataNode$PacketResponder: Received block blk_2284131606093448390 of size 67108864 from /10.250.6.4
[E26] 081111 060612 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.109.236:50010 is added to blk_2284131606093448390 size 67108864
[E11] 081111 060613 21281 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_2284131606093448390 terminating
[E9] 081111 060613 21281 INFO dfs.DataNode$PacketResponder: Received block blk_2284131606093448390 of size 67108864 from /10.251.107.242
[E11] 081111 060613 21708 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_2284131606093448390 terminating
[E9] 081111 060613 21708 INFO dfs.DataNode$PacketResponder: Received block blk_2284131606093448390 of size 67108864 from /10.251.107.242
[E26] 081111 060613 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.6.4:50010 is added to blk_2284131606093448390 size 67108864
[E26] 081111 060613 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.107.242:50010 is added to blk_2284131606093448390 size 67108864
[E23] 081111 065210 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_2284131606093448390 is added to invalidSet of 10.250.6.4:50010
[E23] 081111 065210 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_2284131606093448390 is added to invalidSet of 10.251.107.242:50010
[E23] 081111 065210 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_2284131606093448390 is added to invalidSet of 10.251.109.236:50010
[E21] 081111 065454 19 INFO dfs.FSDataset: Deleting block blk_2284131606093448390 file /mnt/hadoop/dfs/data/current/subdir18/blk_2284131606093448390
[E21] 081111 065501 19 INFO dfs.FSDataset: Deleting block blk_2284131606093448390 file /mnt/hadoop/dfs/data/current/subdir22/blk_2284131606093448390
[E21] 081111 065513 19 INFO dfs.FSDataset: Deleting block blk_2284131606093448390 file /mnt/hadoop/dfs/data/current/subdir19/blk_2284131606093448390
```

### Résumé proposé

La trace contient les événements suivants : E5 (3), E22 (1), E11 (3), E9 (3), E26 (3), E23 (3), E21 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).
- E23 : ajout du bloc à un ensemble d'invalidation (3 occurrence(s) dans la trace).
- E21 : suppression locale du bloc (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes


### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0023 — blk_-1651189670830362760

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 060935 21748 INFO dfs.DataNode$DataXceiver: Receiving block blk_-1651189670830362760 src: /10.250.14.38:43597 dest: /10.250.14.38:50010
[E5] 081111 060935 21822 INFO dfs.DataNode$DataXceiver: Receiving block blk_-1651189670830362760 src: /10.251.110.196:48192 dest: /10.251.110.196:50010
[E5] 081111 060935 21954 INFO dfs.DataNode$DataXceiver: Receiving block blk_-1651189670830362760 src: /10.251.110.196:40058 dest: /10.251.110.196:50010
[E22] 081111 060935 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/randtxt5/_temporary/_task_200811101024_0012_m_000638_0/part-00638. blk_-1651189670830362760
[E11] 081111 061003 21823 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-1651189670830362760 terminating
[E9] 081111 061003 21823 INFO dfs.DataNode$PacketResponder: Received block blk_-1651189670830362760 of size 67108864 from /10.251.110.196
[E11] 081111 061004 21749 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-1651189670830362760 terminating
[E9] 081111 061004 21749 INFO dfs.DataNode$PacketResponder: Received block blk_-1651189670830362760 of size 67108864 from /10.250.14.38
[E11] 081111 061004 21955 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-1651189670830362760 terminating
[E9] 081111 061004 21955 INFO dfs.DataNode$PacketResponder: Received block blk_-1651189670830362760 of size 67108864 from /10.251.110.196
[E26] 081111 061004 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.110.196:50010 is added to blk_-1651189670830362760 size 67108864
[E26] 081111 061004 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.10.223:50010 is added to blk_-1651189670830362760 size 67108864
[E26] 081111 061004 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.14.38:50010 is added to blk_-1651189670830362760 size 67108864
[E23] 081111 065211 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-1651189670830362760 is added to invalidSet of 10.250.10.223:50010
[E23] 081111 065211 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-1651189670830362760 is added to invalidSet of 10.250.14.38:50010
[E23] 081111 065211 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-1651189670830362760 is added to invalidSet of 10.251.110.196:50010
[E21] 081111 065435 19 INFO dfs.FSDataset: Deleting block blk_-1651189670830362760 file /mnt/hadoop/dfs/data/current/subdir19/blk_-1651189670830362760
[E21] 081111 065436 19 INFO dfs.FSDataset: Deleting block blk_-1651189670830362760 file /mnt/hadoop/dfs/data/current/subdir38/blk_-1651189670830362760
[E21] 081111 065502 19 INFO dfs.FSDataset: Deleting block blk_-1651189670830362760 file /mnt/hadoop/dfs/data/current/subdir7/blk_-1651189670830362760
```

### Résumé proposé

La trace contient les événements suivants : E5 (3), E22 (1), E11 (3), E9 (3), E26 (3), E23 (3), E21 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).
- E23 : ajout du bloc à un ensemble d'invalidation (3 occurrence(s) dans la trace).
- E21 : suppression locale du bloc (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes


### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0024 — blk_1435042286855114919

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 034605 19095 INFO dfs.DataNode$DataXceiver: Receiving block blk_1435042286855114919 src: /10.251.74.192:55300 dest: /10.251.74.192:50010
[E5] 081111 034605 19098 INFO dfs.DataNode$DataXceiver: Receiving block blk_1435042286855114919 src: /10.251.74.192:43420 dest: /10.251.74.192:50010
[E5] 081111 034605 19331 INFO dfs.DataNode$DataXceiver: Receiving block blk_1435042286855114919 src: /10.251.65.237:43284 dest: /10.251.65.237:50010
[E22] 081111 034605 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/randtxt4/_temporary/_task_200811101024_0010_m_000053_0/part-00053. blk_1435042286855114919
[E11] 081111 034634 19096 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_1435042286855114919 terminating
[E9] 081111 034634 19096 INFO dfs.DataNode$PacketResponder: Received block blk_1435042286855114919 of size 67108864 from /10.251.74.192
[E11] 081111 034634 19099 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_1435042286855114919 terminating
[E9] 081111 034634 19099 INFO dfs.DataNode$PacketResponder: Received block blk_1435042286855114919 of size 67108864 from /10.251.74.192
[E11] 081111 034634 19332 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_1435042286855114919 terminating
[E9] 081111 034634 19332 INFO dfs.DataNode$PacketResponder: Received block blk_1435042286855114919 of size 67108864 from /10.251.65.237
[E26] 081111 034634 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.74.192:50010 is added to blk_1435042286855114919 size 67108864
[E26] 081111 034634 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.65.237:50010 is added to blk_1435042286855114919 size 67108864
[E26] 081111 034634 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.18.114:50010 is added to blk_1435042286855114919 size 67108864
```

### Résumé proposé

La trace contient les événements suivants : E5 (3), E22 (1), E11 (3), E9 (3), E26 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes


### Sources C6 candidates

hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0025 — blk_546683699916768046

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081110 223208 16140 INFO dfs.DataNode$DataXceiver: Receiving block blk_546683699916768046 src: /10.251.37.240:54571 dest: /10.251.37.240:50010
[E5] 081110 223208 16218 INFO dfs.DataNode$DataXceiver: Receiving block blk_546683699916768046 src: /10.251.37.240:40386 dest: /10.251.37.240:50010
[E5] 081110 223208 16355 INFO dfs.DataNode$DataXceiver: Receiving block blk_546683699916768046 src: /10.251.30.179:42396 dest: /10.251.30.179:50010
[E22] 081110 223208 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/randtxt3/_temporary/_task_200811101024_0007_m_000942_0/part-00942. blk_546683699916768046
[E11] 081110 223248 16359 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_546683699916768046 terminating
[E9] 081110 223248 16359 INFO dfs.DataNode$PacketResponder: Received block blk_546683699916768046 of size 67108864 from /10.251.30.179
[E11] 081110 223249 16141 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_546683699916768046 terminating
[E9] 081110 223249 16141 INFO dfs.DataNode$PacketResponder: Received block blk_546683699916768046 of size 67108864 from /10.251.37.240
[E11] 081110 223249 16219 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_546683699916768046 terminating
[E9] 081110 223249 16219 INFO dfs.DataNode$PacketResponder: Received block blk_546683699916768046 of size 67108864 from /10.251.37.240
[E26] 081110 223249 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.30.179:50010 is added to blk_546683699916768046 size 67108864
[E26] 081110 223249 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.37.240:50010 is added to blk_546683699916768046 size 67108864
[E26] 081110 223249 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.66.3:50010 is added to blk_546683699916768046 size 67108864
[E23] 081111 044339 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_546683699916768046 is added to invalidSet of 10.251.30.179:50010
[E23] 081111 044339 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_546683699916768046 is added to invalidSet of 10.251.37.240:50010
[E23] 081111 044339 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_546683699916768046 is added to invalidSet of 10.251.66.3:50010
[E21] 081111 044722 19 INFO dfs.FSDataset: Deleting block blk_546683699916768046 file /mnt/hadoop/dfs/data/current/subdir26/blk_546683699916768046
[E21] 081111 044750 19 INFO dfs.FSDataset: Deleting block blk_546683699916768046 file /mnt/hadoop/dfs/data/current/subdir32/blk_546683699916768046
[E21] 081111 044754 19 INFO dfs.FSDataset: Deleting block blk_546683699916768046 file /mnt/hadoop/dfs/data/current/subdir45/blk_546683699916768046
```

### Résumé proposé

La trace contient les événements suivants : E5 (3), E22 (1), E11 (3), E9 (3), E26 (3), E23 (3), E21 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).
- E23 : ajout du bloc à un ensemble d'invalidation (3 occurrence(s) dans la trace).
- E21 : suppression locale du bloc (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes


### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0026 — blk_-2320691444482384830

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081110 224251 15894 INFO dfs.DataNode$DataXceiver: Receiving block blk_-2320691444482384830 src: /10.251.75.228:34553 dest: /10.251.75.228:50010
[E5] 081110 224251 16346 INFO dfs.DataNode$DataXceiver: Receiving block blk_-2320691444482384830 src: /10.251.71.193:43412 dest: /10.251.71.193:50010
[E5] 081110 224251 16570 INFO dfs.DataNode$DataXceiver: Receiving block blk_-2320691444482384830 src: /10.251.75.228:50714 dest: /10.251.75.228:50010
[E22] 081110 224251 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/randtxt3/_temporary/_task_200811101024_0007_m_001241_0/part-01241. blk_-2320691444482384830
[E11] 081110 224324 15895 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-2320691444482384830 terminating
[E9] 081110 224324 15895 INFO dfs.DataNode$PacketResponder: Received block blk_-2320691444482384830 of size 67108864 from /10.251.75.228
[E11] 081110 224324 16347 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-2320691444482384830 terminating
[E9] 081110 224324 16347 INFO dfs.DataNode$PacketResponder: Received block blk_-2320691444482384830 of size 67108864 from /10.251.71.193
[E11] 081110 224324 16571 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-2320691444482384830 terminating
[E9] 081110 224324 16571 INFO dfs.DataNode$PacketResponder: Received block blk_-2320691444482384830 of size 67108864 from /10.251.75.228
[E26] 081110 224324 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.74.192:50010 is added to blk_-2320691444482384830 size 67108864
[E26] 081110 224324 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.75.228:50010 is added to blk_-2320691444482384830 size 67108864
[E26] 081110 224324 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.71.193:50010 is added to blk_-2320691444482384830 size 67108864
[E23] 081111 044342 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-2320691444482384830 is added to invalidSet of 10.251.71.193:50010
[E23] 081111 044342 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-2320691444482384830 is added to invalidSet of 10.251.74.192:50010
[E23] 081111 044342 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-2320691444482384830 is added to invalidSet of 10.251.75.228:50010
[E21] 081111 044645 19 INFO dfs.FSDataset: Deleting block blk_-2320691444482384830 file /mnt/hadoop/dfs/data/current/subdir51/blk_-2320691444482384830
[E21] 081111 044653 19 INFO dfs.FSDataset: Deleting block blk_-2320691444482384830 file /mnt/hadoop/dfs/data/current/subdir50/blk_-2320691444482384830
[E21] 081111 044720 18 INFO dfs.FSDataset: Deleting block blk_-2320691444482384830 file /mnt/hadoop/dfs/data/current/subdir23/blk_-2320691444482384830
```

### Résumé proposé

La trace contient les événements suivants : E5 (3), E22 (1), E11 (3), E9 (3), E26 (3), E23 (3), E21 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).
- E23 : ajout du bloc à un ensemble d'invalidation (3 occurrence(s) dans la trace).
- E21 : suppression locale du bloc (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes


### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0027 — blk_-1597964280753970618

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 050943 20164 INFO dfs.DataNode$DataXceiver: Receiving block blk_-1597964280753970618 src: /10.251.202.181:48064 dest: /10.251.202.181:50010
[E22] 081111 050943 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand5/_temporary/_task_200811101024_0011_m_000752_0/part-00752. blk_-1597964280753970618
[E5] 081111 050944 20076 INFO dfs.DataNode$DataXceiver: Receiving block blk_-1597964280753970618 src: /10.250.6.191:52261 dest: /10.250.6.191:50010
[E5] 081111 050944 21004 INFO dfs.DataNode$DataXceiver: Receiving block blk_-1597964280753970618 src: /10.251.202.181:45070 dest: /10.251.202.181:50010
[E9] 081111 051040 20077 INFO dfs.DataNode$PacketResponder: Received block blk_-1597964280753970618 of size 67108864 from /10.250.6.191
[E26] 081111 051040 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.91.32:50010 is added to blk_-1597964280753970618 size 67108864
[E11] 081111 051041 20077 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-1597964280753970618 terminating
[E11] 081111 051041 20166 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-1597964280753970618 terminating
[E9] 081111 051041 20166 INFO dfs.DataNode$PacketResponder: Received block blk_-1597964280753970618 of size 67108864 from /10.251.202.181
[E11] 081111 051041 21006 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-1597964280753970618 terminating
[E9] 081111 051041 21006 INFO dfs.DataNode$PacketResponder: Received block blk_-1597964280753970618 of size 67108864 from /10.251.202.181
[E26] 081111 051041 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.202.181:50010 is added to blk_-1597964280753970618 size 67108864
[E26] 081111 051041 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.6.191:50010 is added to blk_-1597964280753970618 size 67108864
[E23] 081111 075625 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-1597964280753970618 is added to invalidSet of 10.250.6.191:50010
[E23] 081111 075625 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-1597964280753970618 is added to invalidSet of 10.251.202.181:50010
[E23] 081111 075625 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-1597964280753970618 is added to invalidSet of 10.251.91.32:50010
[E21] 081111 075841 19 INFO dfs.FSDataset: Deleting block blk_-1597964280753970618 file /mnt/hadoop/dfs/data/current/subdir38/blk_-1597964280753970618
[E21] 081111 075853 19 INFO dfs.FSDataset: Deleting block blk_-1597964280753970618 file /mnt/hadoop/dfs/data/current/subdir61/blk_-1597964280753970618
[E21] 081111 075900 19 INFO dfs.FSDataset: Deleting block blk_-1597964280753970618 file /mnt/hadoop/dfs/data/current/subdir58/blk_-1597964280753970618
```

### Résumé proposé

La trace contient les événements suivants : E5 (3), E22 (1), E9 (3), E26 (3), E11 (3), E23 (3), E21 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E23 : ajout du bloc à un ensemble d'invalidation (3 occurrence(s) dans la trace).
- E21 : suppression locale du bloc (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes


### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0028 — blk_-7022782725882588627

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 072341 22621 INFO dfs.DataNode$DataXceiver: Receiving block blk_-7022782725882588627 src: /10.251.193.224:58991 dest: /10.251.193.224:50010
[E5] 081111 072341 23110 INFO dfs.DataNode$DataXceiver: Receiving block blk_-7022782725882588627 src: /10.251.193.224:39426 dest: /10.251.193.224:50010
[E22] 081111 072341 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand6/_temporary/_task_200811101024_0013_m_000847_0/part-00847. blk_-7022782725882588627
[E5] 081111 072343 23105 INFO dfs.DataNode$DataXceiver: Receiving block blk_-7022782725882588627 src: /10.251.203.179:47420 dest: /10.251.203.179:50010
[E11] 081111 072427 22622 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-7022782725882588627 terminating
[E9] 081111 072427 22622 INFO dfs.DataNode$PacketResponder: Received block blk_-7022782725882588627 of size 67108864 from /10.251.193.224
[E11] 081111 072427 23106 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-7022782725882588627 terminating
[E9] 081111 072427 23106 INFO dfs.DataNode$PacketResponder: Received block blk_-7022782725882588627 of size 67108864 from /10.251.203.179
[E11] 081111 072427 23111 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-7022782725882588627 terminating
[E9] 081111 072427 23111 INFO dfs.DataNode$PacketResponder: Received block blk_-7022782725882588627 of size 67108864 from /10.251.193.224
[E26] 081111 072427 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.193.224:50010 is added to blk_-7022782725882588627 size 67108864
[E26] 081111 072427 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.203.179:50010 is added to blk_-7022782725882588627 size 67108864
[E26] 081111 072427 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.66.192:50010 is added to blk_-7022782725882588627 size 67108864
[E23] 081111 085915 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-7022782725882588627 is added to invalidSet of 10.251.193.224:50010
[E23] 081111 085915 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-7022782725882588627 is added to invalidSet of 10.251.203.179:50010
[E23] 081111 085915 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-7022782725882588627 is added to invalidSet of 10.251.66.192:50010
[E21] 081111 090023 19 INFO dfs.FSDataset: Deleting block blk_-7022782725882588627 file /mnt/hadoop/dfs/data/current/subdir59/blk_-7022782725882588627
[E21] 081111 090052 19 INFO dfs.FSDataset: Deleting block blk_-7022782725882588627 file /mnt/hadoop/dfs/data/current/subdir8/blk_-7022782725882588627
[E21] 081111 090054 19 INFO dfs.FSDataset: Deleting block blk_-7022782725882588627 file /mnt/hadoop/dfs/data/current/subdir30/blk_-7022782725882588627
```

### Résumé proposé

La trace contient les événements suivants : E5 (3), E22 (1), E11 (3), E9 (3), E26 (3), E23 (3), E21 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).
- E23 : ajout du bloc à un ensemble d'invalidation (3 occurrence(s) dans la trace).
- E21 : suppression locale du bloc (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes


### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0029 — blk_1015583120777869036

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 054158 21056 INFO dfs.DataNode$DataXceiver: Receiving block blk_1015583120777869036 src: /10.251.107.19:56791 dest: /10.251.107.19:50010
[E5] 081111 054158 21455 INFO dfs.DataNode$DataXceiver: Receiving block blk_1015583120777869036 src: /10.251.107.19:50671 dest: /10.251.107.19:50010
[E22] 081111 054158 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand5/_temporary/_task_200811101024_0011_m_001978_0/part-01978. blk_1015583120777869036
[E5] 081111 054159 21315 INFO dfs.DataNode$DataXceiver: Receiving block blk_1015583120777869036 src: /10.251.197.161:47412 dest: /10.251.197.161:50010
[E11] 081111 054225 21057 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_1015583120777869036 terminating
[E9] 081111 054225 21057 INFO dfs.DataNode$PacketResponder: Received block blk_1015583120777869036 of size 67108864 from /10.251.107.19
[E11] 081111 054225 21316 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_1015583120777869036 terminating
[E9] 081111 054225 21316 INFO dfs.DataNode$PacketResponder: Received block blk_1015583120777869036 of size 67108864 from /10.251.197.161
[E26] 081111 054225 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.197.161:50010 is added to blk_1015583120777869036 size 67108864
[E26] 081111 054225 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.66.63:50010 is added to blk_1015583120777869036 size 67108864
[E11] 081111 054226 21456 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_1015583120777869036 terminating
[E9] 081111 054226 21456 INFO dfs.DataNode$PacketResponder: Received block blk_1015583120777869036 of size 67108864 from /10.251.107.19
[E26] 081111 054226 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.107.19:50010 is added to blk_1015583120777869036 size 67108864
[E23] 081111 075639 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_1015583120777869036 is added to invalidSet of 10.251.107.19:50010
[E23] 081111 075639 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_1015583120777869036 is added to invalidSet of 10.251.197.161:50010
[E23] 081111 075639 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_1015583120777869036 is added to invalidSet of 10.251.66.63:50010
[E21] 081111 075839 19 INFO dfs.FSDataset: Deleting block blk_1015583120777869036 file /mnt/hadoop/dfs/data/current/subdir16/blk_1015583120777869036
[E21] 081111 075854 19 INFO dfs.FSDataset: Deleting block blk_1015583120777869036 file /mnt/hadoop/dfs/data/current/subdir41/blk_1015583120777869036
[E21] 081111 075858 18 INFO dfs.FSDataset: Deleting block blk_1015583120777869036 file /mnt/hadoop/dfs/data/current/subdir23/blk_1015583120777869036
```

### Résumé proposé

La trace contient les événements suivants : E5 (3), E22 (1), E11 (3), E9 (3), E26 (3), E23 (3), E21 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).
- E23 : ajout du bloc à un ensemble d'invalidation (3 occurrence(s) dans la trace).
- E21 : suppression locale du bloc (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes


### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0030 — blk_-3011708218918868670

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 024426 17846 INFO dfs.DataNode$DataXceiver: Receiving block blk_-3011708218918868670 src: /10.251.75.79:47070 dest: /10.251.75.79:50010
[E5] 081111 024426 17994 INFO dfs.DataNode$DataXceiver: Receiving block blk_-3011708218918868670 src: /10.251.75.79:48143 dest: /10.251.75.79:50010
[E22] 081111 024426 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand4/_temporary/_task_200811101024_0009_m_000429_0/part-00429. blk_-3011708218918868670
[E5] 081111 024427 17757 INFO dfs.DataNode$DataXceiver: Receiving block blk_-3011708218918868670 src: /10.251.70.5:59438 dest: /10.251.70.5:50010
[E11] 081111 024511 17758 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-3011708218918868670 terminating
[E9] 081111 024511 17758 INFO dfs.DataNode$PacketResponder: Received block blk_-3011708218918868670 of size 67108864 from /10.251.70.5
[E11] 081111 024511 17847 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-3011708218918868670 terminating
[E9] 081111 024511 17847 INFO dfs.DataNode$PacketResponder: Received block blk_-3011708218918868670 of size 67108864 from /10.251.75.79
[E11] 081111 024511 17995 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-3011708218918868670 terminating
[E9] 081111 024511 17995 INFO dfs.DataNode$PacketResponder: Received block blk_-3011708218918868670 of size 67108864 from /10.251.75.79
[E26] 081111 024511 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.75.79:50010 is added to blk_-3011708218918868670 size 67108864
[E26] 081111 024511 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.10.100:50010 is added to blk_-3011708218918868670 size 67108864
[E26] 081111 024511 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.70.5:50010 is added to blk_-3011708218918868670 size 67108864
[E23] 081111 044307 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-3011708218918868670 is added to invalidSet of 10.250.10.100:50010
[E23] 081111 044307 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-3011708218918868670 is added to invalidSet of 10.251.70.5:50010
[E23] 081111 044307 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-3011708218918868670 is added to invalidSet of 10.251.75.79:50010
[E21] 081111 044641 19 INFO dfs.FSDataset: Deleting block blk_-3011708218918868670 file /mnt/hadoop/dfs/data/current/subdir0/blk_-3011708218918868670
[E21] 081111 044709 19 INFO dfs.FSDataset: Deleting block blk_-3011708218918868670 file /mnt/hadoop/dfs/data/current/subdir4/blk_-3011708218918868670
[E21] 081111 044830 19 INFO dfs.FSDataset: Deleting block blk_-3011708218918868670 file /mnt/hadoop/dfs/data/current/subdir50/blk_-3011708218918868670
```

### Résumé proposé

La trace contient les événements suivants : E5 (3), E22 (1), E11 (3), E9 (3), E26 (3), E23 (3), E21 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).
- E23 : ajout du bloc à un ensemble d'invalidation (3 occurrence(s) dans la trace).
- E21 : suppression locale du bloc (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes


### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0031 — blk_-5022333932770048663

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081110 144426 12603 INFO dfs.DataNode$DataXceiver: Receiving block blk_-5022333932770048663 src: /10.251.195.33:60468 dest: /10.251.195.33:50010
[E5] 081110 144426 12645 INFO dfs.DataNode$DataXceiver: Receiving block blk_-5022333932770048663 src: /10.251.195.33:53343 dest: /10.251.195.33:50010
[E5] 081110 144426 12821 INFO dfs.DataNode$DataXceiver: Receiving block blk_-5022333932770048663 src: /10.250.14.38:43919 dest: /10.250.14.38:50010
[E22] 081110 144426 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/sortrand2/_temporary/_task_200811101024_0003_r_000077_0/part-00077. blk_-5022333932770048663
[E11] 081110 144446 12604 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-5022333932770048663 terminating
[E9] 081110 144446 12604 INFO dfs.DataNode$PacketResponder: Received block blk_-5022333932770048663 of size 67108864 from /10.251.195.33
[E11] 081110 144446 12646 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-5022333932770048663 terminating
[E9] 081110 144446 12646 INFO dfs.DataNode$PacketResponder: Received block blk_-5022333932770048663 of size 67108864 from /10.251.195.33
[E11] 081110 144446 12822 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-5022333932770048663 terminating
[E9] 081110 144446 12822 INFO dfs.DataNode$PacketResponder: Received block blk_-5022333932770048663 of size 67108864 from /10.250.14.38
[E26] 081110 144446 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.14.38:50010 is added to blk_-5022333932770048663 size 67108864
[E26] 081110 144446 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.6.191:50010 is added to blk_-5022333932770048663 size 67108864
[E26] 081110 144446 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.195.33:50010 is added to blk_-5022333932770048663 size 67108864
[E23] 081110 210117 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-5022333932770048663 is added to invalidSet of 10.250.14.38:50010
[E23] 081110 210117 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-5022333932770048663 is added to invalidSet of 10.250.6.191:50010
[E23] 081110 210117 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-5022333932770048663 is added to invalidSet of 10.251.195.33:50010
[E21] 081110 210432 19 INFO dfs.FSDataset: Deleting block blk_-5022333932770048663 file /mnt/hadoop/dfs/data/current/subdir56/blk_-5022333932770048663
[E21] 081110 210502 19 INFO dfs.FSDataset: Deleting block blk_-5022333932770048663 file /mnt/hadoop/dfs/data/current/subdir50/blk_-5022333932770048663
[E21] 081110 210532 19 INFO dfs.FSDataset: Deleting block blk_-5022333932770048663 file /mnt/hadoop/dfs/data/current/subdir63/blk_-5022333932770048663
```

### Résumé proposé

La trace contient les événements suivants : E5 (3), E22 (1), E11 (3), E9 (3), E26 (3), E23 (3), E21 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).
- E23 : ajout du bloc à un ensemble d'invalidation (3 occurrence(s) dans la trace).
- E21 : suppression locale du bloc (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes


### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0032 — blk_1430640213223799092

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 071719 23273 INFO dfs.DataNode$DataXceiver: Receiving block blk_1430640213223799092 src: /10.251.107.19:36744 dest: /10.251.107.19:50010
[E22] 081111 071719 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand6/_temporary/_task_200811101024_0013_m_000979_0/part-00979. blk_1430640213223799092
[E5] 081111 071720 22963 INFO dfs.DataNode$DataXceiver: Receiving block blk_1430640213223799092 src: /10.251.107.19:47848 dest: /10.251.107.19:50010
[E5] 081111 071720 23022 INFO dfs.DataNode$DataXceiver: Receiving block blk_1430640213223799092 src: /10.251.29.239:58283 dest: /10.251.29.239:50010
[E11] 081111 071755 22964 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_1430640213223799092 terminating
[E9] 081111 071755 22964 INFO dfs.DataNode$PacketResponder: Received block blk_1430640213223799092 of size 67108864 from /10.251.107.19
[E11] 081111 071755 23023 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_1430640213223799092 terminating
[E9] 081111 071755 23023 INFO dfs.DataNode$PacketResponder: Received block blk_1430640213223799092 of size 67108864 from /10.251.29.239
[E26] 081111 071755 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.14.38:50010 is added to blk_1430640213223799092 size 67108864
[E11] 081111 071756 23274 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_1430640213223799092 terminating
[E9] 081111 071756 23274 INFO dfs.DataNode$PacketResponder: Received block blk_1430640213223799092 of size 67108864 from /10.251.107.19
[E26] 081111 071756 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.107.19:50010 is added to blk_1430640213223799092 size 67108864
[E26] 081111 071756 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.29.239:50010 is added to blk_1430640213223799092 size 67108864
[E23] 081111 085917 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_1430640213223799092 is added to invalidSet of 10.250.14.38:50010
[E23] 081111 085917 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_1430640213223799092 is added to invalidSet of 10.251.107.19:50010
[E23] 081111 085917 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_1430640213223799092 is added to invalidSet of 10.251.29.239:50010
[E21] 081111 090137 19 INFO dfs.FSDataset: Deleting block blk_1430640213223799092 file /mnt/hadoop/dfs/data/current/subdir28/blk_1430640213223799092
[E21] 081111 090148 19 INFO dfs.FSDataset: Deleting block blk_1430640213223799092 file /mnt/hadoop/dfs/data/current/subdir46/blk_1430640213223799092
[E21] 081111 090156 19 INFO dfs.FSDataset: Deleting block blk_1430640213223799092 file /mnt/hadoop/dfs/data/current/subdir52/blk_1430640213223799092
```

### Résumé proposé

La trace contient les événements suivants : E5 (3), E22 (1), E11 (3), E9 (3), E26 (3), E23 (3), E21 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).
- E23 : ajout du bloc à un ensemble d'invalidation (3 occurrence(s) dans la trace).
- E21 : suppression locale du bloc (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes


### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0033 — blk_-5197282817719548999

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 024943 17979 INFO dfs.DataNode$DataXceiver: Receiving block blk_-5197282817719548999 src: /10.251.65.237:52547 dest: /10.251.65.237:50010
[E5] 081111 024943 18004 INFO dfs.DataNode$DataXceiver: Receiving block blk_-5197282817719548999 src: /10.251.193.175:40974 dest: /10.251.193.175:50010
[E5] 081111 024943 18128 INFO dfs.DataNode$DataXceiver: Receiving block blk_-5197282817719548999 src: /10.251.193.175:53791 dest: /10.251.193.175:50010
[E22] 081111 024943 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand4/_temporary/_task_200811101024_0009_m_000592_0/part-00592. blk_-5197282817719548999
[E11] 081111 025054 17980 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-5197282817719548999 terminating
[E9] 081111 025054 17980 INFO dfs.DataNode$PacketResponder: Received block blk_-5197282817719548999 of size 67108864 from /10.251.65.237
[E26] 081111 025054 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.38.214:50010 is added to blk_-5197282817719548999 size 67108864
[E11] 081111 025055 18005 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-5197282817719548999 terminating
[E9] 081111 025055 18005 INFO dfs.DataNode$PacketResponder: Received block blk_-5197282817719548999 of size 67108864 from /10.251.193.175
[E11] 081111 025055 18129 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-5197282817719548999 terminating
[E9] 081111 025055 18129 INFO dfs.DataNode$PacketResponder: Received block blk_-5197282817719548999 of size 67108864 from /10.251.193.175
[E26] 081111 025055 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.193.175:50010 is added to blk_-5197282817719548999 size 67108864
[E26] 081111 025055 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.65.237:50010 is added to blk_-5197282817719548999 size 67108864
[E23] 081111 044309 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-5197282817719548999 is added to invalidSet of 10.251.193.175:50010
[E23] 081111 044309 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-5197282817719548999 is added to invalidSet of 10.251.38.214:50010
[E23] 081111 044309 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-5197282817719548999 is added to invalidSet of 10.251.65.237:50010
[E21] 081111 044630 19 INFO dfs.FSDataset: Deleting block blk_-5197282817719548999 file /mnt/hadoop/dfs/data/current/subdir33/blk_-5197282817719548999
[E21] 081111 044638 19 INFO dfs.FSDataset: Deleting block blk_-5197282817719548999 file /mnt/hadoop/dfs/data/current/subdir35/blk_-5197282817719548999
[E21] 081111 044722 19 INFO dfs.FSDataset: Deleting block blk_-5197282817719548999 file /mnt/hadoop/dfs/data/current/subdir12/blk_-5197282817719548999
```

### Résumé proposé

La trace contient les événements suivants : E5 (3), E22 (1), E11 (3), E9 (3), E26 (3), E23 (3), E21 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).
- E23 : ajout du bloc à un ensemble d'invalidation (3 occurrence(s) dans la trace).
- E21 : suppression locale du bloc (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes


### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0034 — blk_7304855330352525404

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E22] 081110 014321 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/randtxt/_temporary/_task_200811092030_0003_m_001515_0/part-01515. blk_7304855330352525404
[E5] 081110 014321 5685 INFO dfs.DataNode$DataXceiver: Receiving block blk_7304855330352525404 src: /10.251.111.228:33284 dest: /10.251.111.228:50010
[E5] 081110 014321 5918 INFO dfs.DataNode$DataXceiver: Receiving block blk_7304855330352525404 src: /10.251.123.20:59388 dest: /10.251.123.20:50010
[E5] 081110 014321 5995 INFO dfs.DataNode$DataXceiver: Receiving block blk_7304855330352525404 src: /10.251.123.20:59082 dest: /10.251.123.20:50010
[E11] 081110 014402 5686 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_7304855330352525404 terminating
[E9] 081110 014402 5686 INFO dfs.DataNode$PacketResponder: Received block blk_7304855330352525404 of size 67108864 from /10.251.111.228
[E26] 081110 014403 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.111.228:50010 is added to blk_7304855330352525404 size 67108864
[E26] 081110 014403 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.123.20:50010 is added to blk_7304855330352525404 size 67108864
[E26] 081110 014403 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.107.98:50010 is added to blk_7304855330352525404 size 67108864
[E11] 081110 014403 5919 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_7304855330352525404 terminating
[E9] 081110 014403 5919 INFO dfs.DataNode$PacketResponder: Received block blk_7304855330352525404 of size 67108864 from /10.251.123.20
[E11] 081110 014403 5996 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_7304855330352525404 terminating
[E9] 081110 014403 5996 INFO dfs.DataNode$PacketResponder: Received block blk_7304855330352525404 of size 67108864 from /10.251.123.20
[E3] 081110 050746 7102 INFO dfs.DataNode$DataXceiver: 10.251.111.228:50010 Served block blk_7304855330352525404 to /10.251.203.129
[E3] 081110 051139 6842 INFO dfs.DataNode$DataXceiver: 10.251.107.98:50010 Served block blk_7304855330352525404 to /10.251.107.98
[E4] 081110 051239 7077 WARN dfs.DataNode$DataXceiver: 10.251.123.20:50010:Got exception while serving blk_7304855330352525404 to /10.251.194.213:
[E3] 081110 071713 7610 INFO dfs.DataNode$DataXceiver: 10.251.107.98:50010 Served block blk_7304855330352525404 to /10.251.203.129
[E4] 081110 071746 7917 WARN dfs.DataNode$DataXceiver: 10.251.111.228:50010:Got exception while serving blk_7304855330352525404 to /10.251.67.4:
[E3] 081110 071800 7637 INFO dfs.DataNode$DataXceiver: 10.251.107.98:50010 Served block blk_7304855330352525404 to /10.251.107.98
[E3] 081110 082520 8272 INFO dfs.DataNode$DataXceiver: 10.251.107.98:50010 Served block blk_7304855330352525404 to /10.251.203.129
[E4] 081110 082605 8294 WARN dfs.DataNode$DataXceiver: 10.251.107.98:50010:Got exception while serving blk_7304855330352525404 to /10.251.67.4:
[E3] 081110 082611 8490 INFO dfs.DataNode$DataXceiver: 10.251.123.20:50010 Served block blk_7304855330352525404 to /10.251.123.20
[E23] 081110 103044 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_7304855330352525404 is added to invalidSet of 10.251.107.98:50010
[E23] 081110 103044 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_7304855330352525404 is added to invalidSet of 10.251.111.228:50010
[E23] 081110 103044 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_7304855330352525404 is added to invalidSet of 10.251.123.20:50010
[E21] 081110 103611 19 INFO dfs.FSDataset: Deleting block blk_7304855330352525404 file /mnt/hadoop/dfs/data/current/subdir58/blk_7304855330352525404
[E21] 081110 103720 19 INFO dfs.FSDataset: Deleting block blk_7304855330352525404 file /mnt/hadoop/dfs/data/current/subdir49/blk_7304855330352525404
[E21] 081110 104030 19 INFO dfs.FSDataset: Deleting block blk_7304855330352525404 file /mnt/hadoop/dfs/data/current/subdir27/blk_7304855330352525404
```

### Résumé proposé

La trace contient les événements suivants : E22 (1), E5 (3), E11 (3), E9 (3), E26 (3), E3 (6), E4 (3), E23 (3), E21 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).
- E3 : service du bloc (6 occurrence(s) dans la trace).
- E4 : avertissement d'exception pendant le service (3 occurrence(s) dans la trace).
- E23 : ajout du bloc à un ensemble d'invalidation (3 occurrence(s) dans la trace).
- E21 : suppression locale du bloc (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes

- Nature des avertissements ou erreurs à examiner.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0035 — blk_-2873397174621066796

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 073801 23459 INFO dfs.DataNode$DataXceiver: Receiving block blk_-2873397174621066796 src: /10.251.26.177:54637 dest: /10.251.26.177:50010
[E22] 081111 073801 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand6/_temporary/_task_200811101024_0013_m_001751_0/part-01751. blk_-2873397174621066796
[E5] 081111 073802 23362 INFO dfs.DataNode$DataXceiver: Receiving block blk_-2873397174621066796 src: /10.251.43.192:55059 dest: /10.251.43.192:50010
[E5] 081111 073802 23767 INFO dfs.DataNode$DataXceiver: Receiving block blk_-2873397174621066796 src: /10.251.26.177:42997 dest: /10.251.26.177:50010
[E11] 081111 073832 23363 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-2873397174621066796 terminating
[E9] 081111 073832 23363 INFO dfs.DataNode$PacketResponder: Received block blk_-2873397174621066796 of size 67108864 from /10.251.43.192
[E26] 081111 073832 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.43.21:50010 is added to blk_-2873397174621066796 size 67108864
[E11] 081111 073833 23461 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-2873397174621066796 terminating
[E9] 081111 073833 23461 INFO dfs.DataNode$PacketResponder: Received block blk_-2873397174621066796 of size 67108864 from /10.251.26.177
[E11] 081111 073833 23771 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-2873397174621066796 terminating
[E9] 081111 073833 23771 INFO dfs.DataNode$PacketResponder: Received block blk_-2873397174621066796 of size 67108864 from /10.251.26.177
[E26] 081111 073833 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.26.177:50010 is added to blk_-2873397174621066796 size 67108864
[E26] 081111 073833 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.43.192:50010 is added to blk_-2873397174621066796 size 67108864
[E23] 081111 085926 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-2873397174621066796 is added to invalidSet of 10.251.26.177:50010
[E23] 081111 085926 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-2873397174621066796 is added to invalidSet of 10.251.43.192:50010
[E23] 081111 085926 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-2873397174621066796 is added to invalidSet of 10.251.43.21:50010
[E21] 081111 090120 19 INFO dfs.FSDataset: Deleting block blk_-2873397174621066796 file /mnt/hadoop/dfs/data/current/subdir9/blk_-2873397174621066796
[E21] 081111 090131 19 INFO dfs.FSDataset: Deleting block blk_-2873397174621066796 file /mnt/hadoop/dfs/data/current/subdir9/blk_-2873397174621066796
[E21] 081111 090138 19 INFO dfs.FSDataset: Deleting block blk_-2873397174621066796 file /mnt/hadoop/dfs/data/current/subdir48/blk_-2873397174621066796
```

### Résumé proposé

La trace contient les événements suivants : E5 (3), E22 (1), E11 (3), E9 (3), E26 (3), E23 (3), E21 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).
- E23 : ajout du bloc à un ensemble d'invalidation (3 occurrence(s) dans la trace).
- E21 : suppression locale du bloc (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes


### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0036 — blk_5005786149836572537

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 024621 17916 INFO dfs.DataNode$DataXceiver: Receiving block blk_5005786149836572537 src: /10.251.43.115:42255 dest: /10.251.43.115:50010
[E22] 081111 024621 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand4/_temporary/_task_200811101024_0009_m_000205_0/part-00205. blk_5005786149836572537
[E5] 081111 024622 17733 INFO dfs.DataNode$DataXceiver: Receiving block blk_5005786149836572537 src: /10.251.126.227:42843 dest: /10.251.126.227:50010
[E5] 081111 024622 17886 INFO dfs.DataNode$DataXceiver: Receiving block blk_5005786149836572537 src: /10.251.43.115:57124 dest: /10.251.43.115:50010
[E11] 081111 024651 17735 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_5005786149836572537 terminating
[E9] 081111 024651 17735 INFO dfs.DataNode$PacketResponder: Received block blk_5005786149836572537 of size 67108864 from /10.251.126.227
[E11] 081111 024651 17887 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_5005786149836572537 terminating
[E9] 081111 024651 17887 INFO dfs.DataNode$PacketResponder: Received block blk_5005786149836572537 of size 67108864 from /10.251.43.115
[E11] 081111 024651 17918 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_5005786149836572537 terminating
[E9] 081111 024651 17918 INFO dfs.DataNode$PacketResponder: Received block blk_5005786149836572537 of size 67108864 from /10.251.43.115
[E26] 081111 024651 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.201.204:50010 is added to blk_5005786149836572537 size 67108864
[E26] 081111 024651 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.43.115:50010 is added to blk_5005786149836572537 size 67108864
[E26] 081111 024651 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.126.227:50010 is added to blk_5005786149836572537 size 67108864
[E23] 081111 044305 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_5005786149836572537 is added to invalidSet of 10.251.126.227:50010
[E23] 081111 044305 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_5005786149836572537 is added to invalidSet of 10.251.201.204:50010
[E23] 081111 044305 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_5005786149836572537 is added to invalidSet of 10.251.43.115:50010
[E21] 081111 044733 19 INFO dfs.FSDataset: Deleting block blk_5005786149836572537 file /mnt/hadoop/dfs/data/current/subdir60/blk_5005786149836572537
[E21] 081111 044806 19 INFO dfs.FSDataset: Deleting block blk_5005786149836572537 file /mnt/hadoop/dfs/data/current/subdir49/blk_5005786149836572537
[E21] 081111 044858 19 INFO dfs.FSDataset: Deleting block blk_5005786149836572537 file /mnt/hadoop/dfs/data/current/subdir31/blk_5005786149836572537
```

### Résumé proposé

La trace contient les événements suivants : E5 (3), E22 (1), E11 (3), E9 (3), E26 (3), E23 (3), E21 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).
- E23 : ajout du bloc à un ensemble d'invalidation (3 occurrence(s) dans la trace).
- E21 : suppression locale du bloc (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes


### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0037 — blk_1953997662556956187

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 033435 18751 INFO dfs.DataNode$DataXceiver: Receiving block blk_1953997662556956187 src: /10.251.126.22:53295 dest: /10.251.126.22:50010
[E5] 081111 033435 18980 INFO dfs.DataNode$DataXceiver: Receiving block blk_1953997662556956187 src: /10.251.199.245:54575 dest: /10.251.199.245:50010
[E5] 081111 033435 19061 INFO dfs.DataNode$DataXceiver: Receiving block blk_1953997662556956187 src: /10.251.199.245:58124 dest: /10.251.199.245:50010
[E22] 081111 033435 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand4/_temporary/_task_200811101024_0009_m_001959_0/part-01959. blk_1953997662556956187
[E11] 081111 033456 18752 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_1953997662556956187 terminating
[E9] 081111 033456 18752 INFO dfs.DataNode$PacketResponder: Received block blk_1953997662556956187 of size 67108864 from /10.251.126.22
[E11] 081111 033456 18981 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_1953997662556956187 terminating
[E9] 081111 033456 18981 INFO dfs.DataNode$PacketResponder: Received block blk_1953997662556956187 of size 67108864 from /10.251.199.245
[E11] 081111 033456 19062 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_1953997662556956187 terminating
[E9] 081111 033456 19062 INFO dfs.DataNode$PacketResponder: Received block blk_1953997662556956187 of size 67108864 from /10.251.199.245
[E26] 081111 033456 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.126.22:50010 is added to blk_1953997662556956187 size 67108864
[E26] 081111 033456 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.199.245:50010 is added to blk_1953997662556956187 size 67108864
[E26] 081111 033456 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.30.134:50010 is added to blk_1953997662556956187 size 67108864
[E23] 081111 044325 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_1953997662556956187 is added to invalidSet of 10.251.126.22:50010
[E23] 081111 044325 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_1953997662556956187 is added to invalidSet of 10.251.199.245:50010
[E23] 081111 044325 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_1953997662556956187 is added to invalidSet of 10.251.30.134:50010
[E21] 081111 044721 19 INFO dfs.FSDataset: Deleting block blk_1953997662556956187 file /mnt/hadoop/dfs/data/current/subdir3/blk_1953997662556956187
[E21] 081111 044742 19 INFO dfs.FSDataset: Deleting block blk_1953997662556956187 file /mnt/hadoop/dfs/data/current/subdir46/blk_1953997662556956187
[E21] 081111 044747 19 INFO dfs.FSDataset: Deleting block blk_1953997662556956187 file /mnt/hadoop/dfs/data/current/subdir43/blk_1953997662556956187
```

### Résumé proposé

La trace contient les événements suivants : E5 (3), E22 (1), E11 (3), E9 (3), E26 (3), E23 (3), E21 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).
- E23 : ajout du bloc à un ensemble d'invalidation (3 occurrence(s) dans la trace).
- E21 : suppression locale du bloc (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes


### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0038 — blk_-3126046394980374282

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081109 213231 2293 INFO dfs.DataNode$DataXceiver: Receiving block blk_-3126046394980374282 src: /10.251.30.101:54465 dest: /10.251.30.101:50010
[E5] 081109 213231 2308 INFO dfs.DataNode$DataXceiver: Receiving block blk_-3126046394980374282 src: /10.251.91.229:58937 dest: /10.251.91.229:50010
[E5] 081109 213231 2335 INFO dfs.DataNode$DataXceiver: Receiving block blk_-3126046394980374282 src: /10.251.30.101:52283 dest: /10.251.30.101:50010
[E22] 081109 213231 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand/_temporary/_task_200811092030_0001_m_001873_1/part-01873. blk_-3126046394980374282
[E11] 081109 213317 2294 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-3126046394980374282 terminating
[E9] 081109 213317 2294 INFO dfs.DataNode$PacketResponder: Received block blk_-3126046394980374282 of size 67108864 from /10.251.30.101
[E11] 081109 213317 2309 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-3126046394980374282 terminating
[E9] 081109 213317 2309 INFO dfs.DataNode$PacketResponder: Received block blk_-3126046394980374282 of size 67108864 from /10.251.91.229
[E11] 081109 213317 2336 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-3126046394980374282 terminating
[E9] 081109 213317 2336 INFO dfs.DataNode$PacketResponder: Received block blk_-3126046394980374282 of size 67108864 from /10.251.30.101
[E26] 081109 213317 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.91.229:50010 is added to blk_-3126046394980374282 size 67108864
[E26] 081109 213317 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.30.101:50010 is added to blk_-3126046394980374282 size 67108864
[E26] 081109 213318 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.214.18:50010 is added to blk_-3126046394980374282 size 67108864
[E23] 081109 213814 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-3126046394980374282 is added to invalidSet of 10.251.214.18:50010
[E23] 081109 213814 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-3126046394980374282 is added to invalidSet of 10.251.30.101:50010
[E23] 081109 213814 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-3126046394980374282 is added to invalidSet of 10.251.91.229:50010
[E21] 081109 213835 19 INFO dfs.FSDataset: Deleting block blk_-3126046394980374282 file /mnt/hadoop/dfs/data/current/subdir15/blk_-3126046394980374282
[E21] 081109 213836 19 INFO dfs.FSDataset: Deleting block blk_-3126046394980374282 file /mnt/hadoop/dfs/data/current/subdir0/blk_-3126046394980374282
[E21] 081109 213840 19 INFO dfs.FSDataset: Deleting block blk_-3126046394980374282 file /mnt/hadoop/dfs/data/current/subdir12/blk_-3126046394980374282
```

### Résumé proposé

La trace contient les événements suivants : E5 (3), E22 (1), E11 (3), E9 (3), E26 (3), E23 (3), E21 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).
- E23 : ajout du bloc à un ensemble d'invalidation (3 occurrence(s) dans la trace).
- E21 : suppression locale du bloc (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes


### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0039 — blk_-8545253910745733560

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 082036 24335 INFO dfs.DataNode$DataXceiver: Receiving block blk_-8545253910745733560 src: /10.251.199.245:54757 dest: /10.251.199.245:50010
[E22] 081111 082036 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand7/_temporary/_task_200811101024_0014_m_001013_0/part-01013. blk_-8545253910745733560
[E5] 081111 082037 23705 INFO dfs.DataNode$DataXceiver: Receiving block blk_-8545253910745733560 src: /10.251.91.159:33775 dest: /10.251.91.159:50010
[E5] 081111 082037 24187 INFO dfs.DataNode$DataXceiver: Receiving block blk_-8545253910745733560 src: /10.251.199.245:59314 dest: /10.251.199.245:50010
[E11] 081111 082058 23706 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-8545253910745733560 terminating
[E9] 081111 082058 23706 INFO dfs.DataNode$PacketResponder: Received block blk_-8545253910745733560 of size 67108864 from /10.251.91.159
[E11] 081111 082058 24188 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-8545253910745733560 terminating
[E9] 081111 082058 24188 INFO dfs.DataNode$PacketResponder: Received block blk_-8545253910745733560 of size 67108864 from /10.251.199.245
[E11] 081111 082058 24338 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-8545253910745733560 terminating
[E9] 081111 082058 24338 INFO dfs.DataNode$PacketResponder: Received block blk_-8545253910745733560 of size 67108864 from /10.251.199.245
[E26] 081111 082058 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.126.255:50010 is added to blk_-8545253910745733560 size 67108864
[E26] 081111 082058 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.199.245:50010 is added to blk_-8545253910745733560 size 67108864
[E26] 081111 082058 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.91.159:50010 is added to blk_-8545253910745733560 size 67108864
```

### Résumé proposé

La trace contient les événements suivants : E5 (3), E22 (1), E11 (3), E9 (3), E26 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes


### Sources C6 candidates

hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0040 — blk_-5116091373247376102

**Label officiel :** 0

**Abstention proposée :** False

### Trace originale

```text
[E22] 081110 013044 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/randtxt/_temporary/_task_200811092030_0003_m_000926_0/part-00926. blk_-5116091373247376102
[E5] 081110 013044 5302 INFO dfs.DataNode$DataXceiver: Receiving block blk_-5116091373247376102 src: /10.251.214.32:35283 dest: /10.251.214.32:50010
[E5] 081110 013044 5605 INFO dfs.DataNode$DataXceiver: Receiving block blk_-5116091373247376102 src: /10.251.214.32:35126 dest: /10.251.214.32:50010
[E5] 081110 013045 5686 INFO dfs.DataNode$DataXceiver: Receiving block blk_-5116091373247376102 src: /10.251.39.192:39350 dest: /10.251.39.192:50010
[E26] 081110 013122 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.214.32:50010 is added to blk_-5116091373247376102 size 67108864
[E26] 081110 013122 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.39.192:50010 is added to blk_-5116091373247376102 size 67108864
[E26] 081110 013122 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.39.242:50010 is added to blk_-5116091373247376102 size 67108864
[E11] 081110 013122 5304 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-5116091373247376102 terminating
[E9] 081110 013122 5304 INFO dfs.DataNode$PacketResponder: Received block blk_-5116091373247376102 of size 67108864 from /10.251.214.32
[E11] 081110 013122 5606 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-5116091373247376102 terminating
[E9] 081110 013122 5606 INFO dfs.DataNode$PacketResponder: Received block blk_-5116091373247376102 of size 67108864 from /10.251.214.32
[E11] 081110 013122 5687 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-5116091373247376102 terminating
[E9] 081110 013122 5687 INFO dfs.DataNode$PacketResponder: Received block blk_-5116091373247376102 of size 67108864 from /10.251.39.192
[E3] 081110 035844 6785 INFO dfs.DataNode$DataXceiver: 10.251.39.242:50010 Served block blk_-5116091373247376102 to /10.251.39.242
[E4] 081110 040213 6457 WARN dfs.DataNode$DataXceiver: 10.251.214.32:50010:Got exception while serving blk_-5116091373247376102 to /10.250.11.100:
[E3] 081110 040220 6724 INFO dfs.DataNode$DataXceiver: 10.251.39.192:50010 Served block blk_-5116091373247376102 to /10.251.91.159
[E3] 081110 070919 7359 INFO dfs.DataNode$DataXceiver: 10.251.214.32:50010 Served block blk_-5116091373247376102 to /10.251.214.32
[E4] 081110 070930 7361 WARN dfs.DataNode$DataXceiver: 10.251.214.32:50010:Got exception while serving blk_-5116091373247376102 to /10.251.214.32:
[E3] 081110 070943 7593 INFO dfs.DataNode$DataXceiver: 10.251.39.192:50010 Served block blk_-5116091373247376102 to /10.251.194.245
[E3] 081110 081718 8195 INFO dfs.DataNode$DataXceiver: 10.251.39.192:50010 Served block blk_-5116091373247376102 to /10.251.39.192
[E4] 081110 081740 8315 WARN dfs.DataNode$DataXceiver: 10.251.39.242:50010:Got exception while serving blk_-5116091373247376102 to /10.251.39.144:
[E3] 081110 081745 7998 INFO dfs.DataNode$DataXceiver: 10.251.214.32:50010 Served block blk_-5116091373247376102 to /10.251.91.159
[E3] 081110 094408 8871 INFO dfs.DataNode$DataXceiver: 10.251.39.192:50010 Served block blk_-5116091373247376102 to /10.251.39.192
[E4] 081110 094437 8658 WARN dfs.DataNode$DataXceiver: 10.251.214.32:50010:Got exception while serving blk_-5116091373247376102 to /10.250.11.100:
[E3] 081110 094452 8991 INFO dfs.DataNode$DataXceiver: 10.251.39.242:50010 Served block blk_-5116091373247376102 to /10.251.194.245
[E23] 081110 103037 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-5116091373247376102 is added to invalidSet of 10.251.214.32:50010
[E23] 081110 103037 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-5116091373247376102 is added to invalidSet of 10.251.39.192:50010
[E23] 081110 103037 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-5116091373247376102 is added to invalidSet of 10.251.39.242:50010
[E21] 081110 103508 19 INFO dfs.FSDataset: Deleting block blk_-5116091373247376102 file /mnt/hadoop/dfs/data/current/subdir28/blk_-5116091373247376102
[E21] 081110 103529 18 INFO dfs.FSDataset: Deleting block blk_-5116091373247376102 file /mnt/hadoop/dfs/data/current/subdir49/blk_-5116091373247376102
[E21] 081110 103615 19 INFO dfs.FSDataset: Deleting block blk_-5116091373247376102 file /mnt/hadoop/dfs/data/current/subdir46/blk_-5116091373247376102
```

### Résumé proposé

La trace contient les événements suivants : E22 (1), E5 (3), E26 (3), E11 (3), E9 (3), E3 (8), E4 (4), E23 (3), E21 (3). Leur interprétation chronologique reste à vérifier.

### Faits observés

- E22 : allocation du bloc (1 occurrence(s) dans la trace).
- E5 : début de réception du bloc (3 occurrence(s) dans la trace).
- E26 : enregistrement du bloc sur un DataNode (3 occurrence(s) dans la trace).
- E11 : terminaison d'un PacketResponder (3 occurrence(s) dans la trace).
- E9 : réception du bloc confirmée (3 occurrence(s) dans la trace).
- E3 : service du bloc (8 occurrence(s) dans la trace).
- E4 : avertissement d'exception pendant le service (4 occurrence(s) dans la trace).
- E23 : ajout du bloc à un ensemble d'invalidation (3 occurrence(s) dans la trace).
- E21 : suppression locale du bloc (3 occurrence(s) dans la trace).

### Hypothèses


### Informations manquantes

- Nature des avertissements ou erreurs à examiner.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0041 — blk_8778690542254370358

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E22] 081110 014325 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/randtxt/_temporary/_task_200811092030_0003_m_001440_0/part-01440. blk_8778690542254370358
[E5] 081110 014326 5796 INFO dfs.DataNode$DataXceiver: Receiving block blk_8778690542254370358 src: /10.251.195.70:54247 dest: /10.251.195.70:50010
[E5] 081110 014326 5817 INFO dfs.DataNode$DataXceiver: Receiving block blk_8778690542254370358 src: /10.251.42.16:39544 dest: /10.251.42.16:50010
[E5] 081110 014326 5909 INFO dfs.DataNode$DataXceiver: Receiving block blk_8778690542254370358 src: /10.251.195.70:59401 dest: /10.251.195.70:50010
[E26] 081110 014354 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.42.16:50010 is added to blk_8778690542254370358 size 67108864
[E26] 081110 014354 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.65.237:50010 is added to blk_8778690542254370358 size 67108864
[E11] 081110 014354 5797 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_8778690542254370358 terminating
[E9] 081110 014354 5797 INFO dfs.DataNode$PacketResponder: Received block blk_8778690542254370358 of size 67108864 from /10.251.195.70
[E11] 081110 014354 5818 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_8778690542254370358 terminating
[E9] 081110 014354 5818 INFO dfs.DataNode$PacketResponder: Received block blk_8778690542254370358 of size 67108864 from /10.251.42.16
[E11] 081110 014354 5910 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_8778690542254370358 terminating
[E9] 081110 014354 5910 INFO dfs.DataNode$PacketResponder: Received block blk_8778690542254370358 of size 67108864 from /10.251.195.70
[E26] 081110 014355 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.195.70:50010 is added to blk_8778690542254370358 size 67108864
[E3] 081110 050043 6893 INFO dfs.DataNode$DataXceiver: 10.251.65.237:50010 Served block blk_8778690542254370358 to /10.251.65.237
[E4] 081110 050305 7016 WARN dfs.DataNode$DataXceiver: 10.251.195.70:50010:Got exception while serving blk_8778690542254370358 to /10.251.38.214:
[E3] 081110 050517 7017 INFO dfs.DataNode$DataXceiver: 10.251.195.70:50010 Served block blk_8778690542254370358 to /10.251.31.5
[E4] 081110 071636 7614 WARN dfs.DataNode$DataXceiver: 10.251.42.16:50010:Got exception while serving blk_8778690542254370358 to /10.251.38.214:
[E3] 081110 071645 7623 INFO dfs.DataNode$DataXceiver: 10.251.42.16:50010 Served block blk_8778690542254370358 to /10.251.42.16
[E3] 081110 071646 7686 INFO dfs.DataNode$DataXceiver: 10.251.65.237:50010 Served block blk_8778690542254370358 to /10.250.5.237
[E3] 081110 082449 8335 INFO dfs.DataNode$DataXceiver: 10.251.65.237:50010 Served block blk_8778690542254370358 to /10.251.65.237
[E4] 081110 082457 8412 WARN dfs.DataNode$DataXceiver: 10.251.195.70:50010:Got exception while serving blk_8778690542254370358 to /10.251.38.214:
[E3] 081110 082503 8337 INFO dfs.DataNode$DataXceiver: 10.251.65.237:50010 Served block blk_8778690542254370358 to /10.250.5.237
[E23] 081110 103043 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_8778690542254370358 is added to invalidSet of 10.251.195.70:50010
[E23] 081110 103043 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_8778690542254370358 is added to invalidSet of 10.251.42.16:50010
[E23] 081110 103043 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_8778690542254370358 is added to invalidSet of 10.251.65.237:50010
[E21] 081110 103125 19 INFO dfs.FSDataset: Deleting block blk_8778690542254370358 file /mnt/hadoop/dfs/data/current/subdir19/blk_8778690542254370358
[E21] 081110 103728 19 INFO dfs.FSDataset: Deleting block blk_8778690542254370358 file /mnt/hadoop/dfs/data/current/subdir35/blk_8778690542254370358
[E20] 081110 103733 19 WARN dfs.FSDataset: Unexpected error trying to delete block blk_8778690542254370358. BlockInfo not found in volumeMap.
[E21] 081110 103957 19 INFO dfs.FSDataset: Deleting block blk_8778690542254370358 file /mnt/hadoop/dfs/data/current/subdir38/blk_8778690542254370358
```

### Résumé proposé

La trace contient des opérations HDFS sur le bloc, notamment : exception signalée pendant le service du bloc; erreur de suppression : BlockInfo absent de volumeMap. Les autres opérations sont détaillées dans les faits observés.

### Faits observés

- E22 : 1 occurrence(s) — allocation du bloc.
- E5 : 3 occurrence(s) — début de réception.
- E26 : 3 occurrence(s) — enregistrement du bloc.
- E11 : 3 occurrence(s) — fin d'un PacketResponder.
- E9 : 3 occurrence(s) — confirmation de réception.
- E3 : 6 occurrence(s) — service du bloc à un client.
- E4 : 3 occurrence(s) — exception signalée pendant le service du bloc.
- E23 : 3 occurrence(s) — ajout aux ensembles d'invalidation.
- E21 : 3 occurrence(s) — suppression locale journalisée.
- E20 : 1 occurrence(s) — erreur de suppression : BlockInfo absent de volumeMap.

### Hypothèses


### Informations manquantes

- Nature et cause des exceptions pendant le service.
- Cause de l'absence de BlockInfo dans volumeMap.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0042 — blk_-3771718347651612577

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 043703 19716 INFO dfs.DataNode$DataXceiver: Receiving block blk_-3771718347651612577 src: /10.251.123.195:55206 dest: /10.251.123.195:50010
[E5] 081111 043703 19724 INFO dfs.DataNode$DataXceiver: Receiving block blk_-3771718347651612577 src: /10.251.123.1:55270 dest: /10.251.123.1:50010
[E5] 081111 043703 20118 INFO dfs.DataNode$DataXceiver: Receiving block blk_-3771718347651612577 src: /10.251.123.1:39561 dest: /10.251.123.1:50010
[E22] 081111 043703 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/randtxt4/_temporary/_task_200811101024_0010_m_001867_1/part-01867. blk_-3771718347651612577
[E11] 081111 043739 19717 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-3771718347651612577 terminating
[E9] 081111 043739 19717 INFO dfs.DataNode$PacketResponder: Received block blk_-3771718347651612577 of size 67108864 from /10.251.123.195
[E11] 081111 043739 19725 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-3771718347651612577 terminating
[E9] 081111 043739 19725 INFO dfs.DataNode$PacketResponder: Received block blk_-3771718347651612577 of size 67108864 from /10.251.123.1
[E11] 081111 043739 20119 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-3771718347651612577 terminating
[E9] 081111 043739 20119 INFO dfs.DataNode$PacketResponder: Received block blk_-3771718347651612577 of size 67108864 from /10.251.123.1
[E26] 081111 043739 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.123.1:50010 is added to blk_-3771718347651612577 size 67108864
[E26] 081111 043739 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.203.80:50010 is added to blk_-3771718347651612577 size 67108864
[E26] 081111 043739 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.123.195:50010 is added to blk_-3771718347651612577 size 67108864
[E23] 081111 044256 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-3771718347651612577 is added to invalidSet of 10.251.123.1:50010
[E23] 081111 044256 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-3771718347651612577 is added to invalidSet of 10.251.123.195:50010
[E23] 081111 044256 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-3771718347651612577 is added to invalidSet of 10.251.203.80:50010
[E21] 081111 044303 19 INFO dfs.FSDataset: Deleting block blk_-3771718347651612577 file /mnt/hadoop/dfs/data/current/subdir24/blk_-3771718347651612577
[E21] 081111 044648 19 INFO dfs.FSDataset: Deleting block blk_-3771718347651612577 file /mnt/hadoop/dfs/data/current/subdir4/blk_-3771718347651612577
[E20] 081111 044705 19 WARN dfs.FSDataset: Unexpected error trying to delete block blk_-3771718347651612577. BlockInfo not found in volumeMap.
[E21] 081111 044707 18 INFO dfs.FSDataset: Deleting block blk_-3771718347651612577 file /mnt/hadoop/dfs/data/current/subdir18/blk_-3771718347651612577
```

### Résumé proposé

Le bloc est alloué, puis trois réceptions de 67 108 864 octets sont confirmées et trois DataNodes sont enregistrés. Le bloc est ensuite ajouté aux ensembles d'invalidation de ces trois DataNodes. Deux suppressions locales sont journalisées, puis un avertissement E20 signale que BlockInfo est introuvable dans volumeMap lors d'une tentative de suppression. Une troisième suppression locale est ensuite journalisée.

### Faits observés

- E22 et E5 : une allocation et trois débuts de réception.
- E9 et E26 : trois confirmations de réception et trois enregistrements.
- E23 : trois ajouts aux ensembles d'invalidation.
- E21 : trois suppressions locales journalisées.
- E20 : avertissement 'BlockInfo not found in volumeMap' entre la deuxième et la troisième suppression.

### Hypothèses


### Informations manquantes

- Raison de l'absence de BlockInfo dans volumeMap.
- État exact des métadonnées et des répliques au moment de l'avertissement.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0043 — blk_-5727850177555687571

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E22] 081110 103700 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand/_temporary/_task_200811101024_0001_m_000333_0/part-00333. blk_-5727850177555687571
[E5] 081110 103700 9068 INFO dfs.DataNode$DataXceiver: Receiving block blk_-5727850177555687571 src: /10.251.31.242:57962 dest: /10.251.31.242:50010
[E5] 081110 103700 9199 INFO dfs.DataNode$DataXceiver: Receiving block blk_-5727850177555687571 src: /10.251.31.242:41030 dest: /10.251.31.242:50010
[E5] 081110 103701 9129 INFO dfs.DataNode$DataXceiver: Receiving block blk_-5727850177555687571 src: /10.251.123.20:46790 dest: /10.251.123.20:50010
[E11] 081110 103740 9071 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-5727850177555687571 terminating
[E9] 081110 103740 9071 INFO dfs.DataNode$PacketResponder: Received block blk_-5727850177555687571 of size 67108864 from /10.251.31.242
[E11] 081110 103740 9130 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-5727850177555687571 terminating
[E9] 081110 103740 9130 INFO dfs.DataNode$PacketResponder: Received block blk_-5727850177555687571 of size 67108864 from /10.251.123.20
[E11] 081110 103740 9200 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-5727850177555687571 terminating
[E9] 081110 103740 9200 INFO dfs.DataNode$PacketResponder: Received block blk_-5727850177555687571 of size 67108864 from /10.251.31.242
[E26] 081110 103835 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.31.242:50010 is added to blk_-5727850177555687571 size 67108864
[E26] 081110 104141 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.123.20:50010 is added to blk_-5727850177555687571 size 67108864
[E25] 081110 104537 19 INFO dfs.FSNamesystem: BLOCK* ask 10.251.123.20:50010 to replicate blk_-5727850177555687571 to datanode(s) 10.251.109.236:50010
[E18] 081110 104538 19 INFO dfs.DataNode: 10.251.123.20:50010 Starting thread to transfer block blk_-5727850177555687571 to 10.251.109.236:50010
[E5] 081110 104539 8970 INFO dfs.DataNode$DataXceiver: Receiving block blk_-5727850177555687571 src: /10.251.123.20:36981 dest: /10.251.123.20:50010
[E26] 081110 104557 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.109.236:50010 is added to blk_-5727850177555687571 size 67108864
[E6] 081110 104557 8970 INFO dfs.DataNode$DataXceiver: Received block blk_-5727850177555687571 src: /10.251.123.20:36981 dest: /10.251.123.20:50010 of size 67108864
[E16] 081110 104557 9357 INFO dfs.DataNode$DataTransfer: 10.251.123.20:50010:Transmitted block blk_-5727850177555687571 to /10.251.109.236:50010
[E26] 081110 104606 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.199.225:50010 is added to blk_-5727850177555687571 size 67108864
[E21] 081110 104621 19 INFO dfs.FSDataset: Deleting block blk_-5727850177555687571 file /mnt/hadoop/dfs/data/current/blk_-5727850177555687571
[E2] 081110 124315 13 INFO dfs.DataBlockScanner: Verification succeeded for blk_-5727850177555687571
[E4] 081110 125419 11732 WARN dfs.DataNode$DataXceiver: 10.251.123.20:50010:Got exception while serving blk_-5727850177555687571 to /10.251.37.240:
[E4] 081110 125446 11285 WARN dfs.DataNode$DataXceiver: 10.251.109.236:50010:Got exception while serving blk_-5727850177555687571 to /10.251.110.68:
[E3] 081110 125550 11286 INFO dfs.DataNode$DataXceiver: 10.251.109.236:50010 Served block blk_-5727850177555687571 to /10.251.110.68
[E2] 081110 154016 13 INFO dfs.DataBlockScanner: Verification succeeded for blk_-5727850177555687571
[E2] 081110 183756 13 INFO dfs.DataBlockScanner: Verification succeeded for blk_-5727850177555687571
[E23] 081110 210142 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-5727850177555687571 is added to invalidSet of 10.251.109.236:50010
[E23] 081110 210142 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-5727850177555687571 is added to invalidSet of 10.251.123.20:50010
[E23] 081110 210142 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-5727850177555687571 is added to invalidSet of 10.251.31.242:50010
[E21] 081110 210452 19 INFO dfs.FSDataset: Deleting block blk_-5727850177555687571 file /mnt/hadoop/dfs/data/current/blk_-5727850177555687571
[E21] 081110 210504 19 INFO dfs.FSDataset: Deleting block blk_-5727850177555687571 file /mnt/hadoop/dfs/data/current/subdir19/blk_-5727850177555687571
[E21] 081110 210505 19 INFO dfs.FSDataset: Deleting block blk_-5727850177555687571 file /mnt/hadoop/dfs/data/current/blk_-5727850177555687571
```

### Résumé proposé

La trace contient des opérations HDFS sur le bloc, notamment : exception signalée pendant le service du bloc. Les autres opérations sont détaillées dans les faits observés.

### Faits observés

- E22 : 1 occurrence(s) — allocation du bloc.
- E5 : 4 occurrence(s) — début de réception.
- E11 : 3 occurrence(s) — fin d'un PacketResponder.
- E9 : 3 occurrence(s) — confirmation de réception.
- E26 : 4 occurrence(s) — enregistrement du bloc.
- E25 : 1 occurrence(s) — demande de réplication.
- E18 : 1 occurrence(s) — démarrage d'un transfert.
- E6 : 1 occurrence(s) — réception du bloc transféré.
- E16 : 1 occurrence(s) — transmission du bloc.
- E21 : 4 occurrence(s) — suppression locale journalisée.
- E2 : 3 occurrence(s) — vérification réussie du bloc.
- E4 : 2 occurrence(s) — exception signalée pendant le service du bloc.
- E3 : 1 occurrence(s) — service du bloc à un client.
- E23 : 3 occurrence(s) — ajout aux ensembles d'invalidation.

### Hypothèses


### Informations manquantes

- Nature et cause des exceptions pendant le service.

### Sources C6 candidates

hdfs-architecture-1.2.1#data-replication#1;hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0044 — blk_8465015266040628194

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 045248 20274 INFO dfs.DataNode$DataXceiver: Receiving block blk_8465015266040628194 src: /10.250.5.161:44389 dest: /10.250.5.161:50010
[E5] 081111 045248 20309 INFO dfs.DataNode$DataXceiver: Receiving block blk_8465015266040628194 src: /10.251.75.49:34986 dest: /10.251.75.49:50010
[E5] 081111 045248 20379 INFO dfs.DataNode$DataXceiver: Receiving block blk_8465015266040628194 src: /10.251.75.49:53908 dest: /10.251.75.49:50010
[E22] 081111 045248 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand5/_temporary/_task_200811101024_0011_m_000038_0/part-00038. blk_8465015266040628194
[E11] 081111 045322 20275 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_8465015266040628194 terminating
[E9] 081111 045322 20275 INFO dfs.DataNode$PacketResponder: Received block blk_8465015266040628194 of size 67108864 from /10.250.5.161
[E11] 081111 045322 20310 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_8465015266040628194 terminating
[E9] 081111 045322 20310 INFO dfs.DataNode$PacketResponder: Received block blk_8465015266040628194 of size 67108864 from /10.251.75.49
[E11] 081111 045322 20380 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_8465015266040628194 terminating
[E9] 081111 045322 20380 INFO dfs.DataNode$PacketResponder: Received block blk_8465015266040628194 of size 67108864 from /10.251.75.49
[E26] 081111 045322 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.5.161:50010 is added to blk_8465015266040628194 size 67108864
[E26] 081111 045322 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.75.49:50010 is added to blk_8465015266040628194 size 67108864
[E26] 081111 045322 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.10.223:50010 is added to blk_8465015266040628194 size 67108864
[E23] 081111 075617 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_8465015266040628194 is added to invalidSet of 10.250.10.223:50010
[E23] 081111 075617 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_8465015266040628194 is added to invalidSet of 10.250.5.161:50010
[E23] 081111 075617 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_8465015266040628194 is added to invalidSet of 10.251.75.49:50010
[E21] 081111 075757 19 INFO dfs.FSDataset: Deleting block blk_8465015266040628194 file /mnt/hadoop/dfs/data/current/blk_8465015266040628194
[E21] 081111 075914 19 INFO dfs.FSDataset: Deleting block blk_8465015266040628194 file /mnt/hadoop/dfs/data/current/blk_8465015266040628194
[E21] 081111 075924 19 INFO dfs.FSDataset: Deleting block blk_8465015266040628194 file /mnt/hadoop/dfs/data/current/blk_8465015266040628194
[E20] 081111 075945 19 WARN dfs.FSDataset: Unexpected error trying to delete block blk_8465015266040628194. BlockInfo not found in volumeMap.
```

### Résumé proposé

La trace contient des opérations HDFS sur le bloc, notamment : erreur de suppression : BlockInfo absent de volumeMap. Les autres opérations sont détaillées dans les faits observés.

### Faits observés

- E5 : 3 occurrence(s) — début de réception.
- E22 : 1 occurrence(s) — allocation du bloc.
- E11 : 3 occurrence(s) — fin d'un PacketResponder.
- E9 : 3 occurrence(s) — confirmation de réception.
- E26 : 3 occurrence(s) — enregistrement du bloc.
- E23 : 3 occurrence(s) — ajout aux ensembles d'invalidation.
- E21 : 3 occurrence(s) — suppression locale journalisée.
- E20 : 1 occurrence(s) — erreur de suppression : BlockInfo absent de volumeMap.

### Hypothèses


### Informations manquantes

- Cause de l'absence de BlockInfo dans volumeMap.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0045 — blk_6979810746045389129

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 052236 19230 INFO dfs.DataNode$DataXceiver: Receiving block blk_6979810746045389129 src: /10.251.67.113:46703 dest: /10.251.67.113:50010
[E5] 081111 052236 20668 INFO dfs.DataNode$DataXceiver: Receiving block blk_6979810746045389129 src: /10.251.127.47:49027 dest: /10.251.127.47:50010
[E5] 081111 052236 21044 INFO dfs.DataNode$DataXceiver: Receiving block blk_6979810746045389129 src: /10.251.127.47:36759 dest: /10.251.127.47:50010
[E22] 081111 052236 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand5/_temporary/_task_200811101024_0011_m_001503_0/part-01503. blk_6979810746045389129
[E11] 081111 052313 19231 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_6979810746045389129 terminating
[E9] 081111 052313 19231 INFO dfs.DataNode$PacketResponder: Received block blk_6979810746045389129 of size 67108864 from /10.251.67.113
[E11] 081111 052313 20669 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_6979810746045389129 terminating
[E9] 081111 052313 20669 INFO dfs.DataNode$PacketResponder: Received block blk_6979810746045389129 of size 67108864 from /10.251.127.47
[E11] 081111 052313 21045 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_6979810746045389129 terminating
[E9] 081111 052313 21045 INFO dfs.DataNode$PacketResponder: Received block blk_6979810746045389129 of size 67108864 from /10.251.127.47
[E26] 081111 052313 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.107.50:50010 is added to blk_6979810746045389129 size 67108864
[E26] 081111 052313 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.127.47:50010 is added to blk_6979810746045389129 size 67108864
[E26] 081111 052313 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.67.113:50010 is added to blk_6979810746045389129 size 67108864
[E25] 081111 070442 19 INFO dfs.FSNamesystem: BLOCK* ask 10.251.67.113:50010 to replicate blk_6979810746045389129 to datanode(s) 10.250.15.101:50010
[E18] 081111 070509 19 INFO dfs.DataNode: 10.251.67.113:50010 Starting thread to transfer block blk_6979810746045389129 to 10.250.15.101:50010
[E5] 081111 070509 22718 INFO dfs.DataNode$DataXceiver: Receiving block blk_6979810746045389129 src: /10.251.67.113:45457 dest: /10.251.67.113:50010
[E16] 081111 070523 22593 INFO dfs.DataNode$DataTransfer: 10.251.67.113:50010:Transmitted block blk_6979810746045389129 to /10.250.15.101:50010
[E6] 081111 070523 22718 INFO dfs.DataNode$DataXceiver: Received block blk_6979810746045389129 src: /10.251.67.113:45457 dest: /10.251.67.113:50010 of size 67108864
[E26] 081111 070523 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.15.101:50010 is added to blk_6979810746045389129 size 67108864
[E26] 081111 072344 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.107.50:50010 is added to blk_6979810746045389129 size 67108864
[E21] 081111 072407 19 INFO dfs.FSDataset: Deleting block blk_6979810746045389129 file /mnt/hadoop/dfs/data/current/subdir45/blk_6979810746045389129
[E23] 081111 075634 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_6979810746045389129 is added to invalidSet of 10.250.15.101:50010
[E23] 081111 075634 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_6979810746045389129 is added to invalidSet of 10.251.107.50:50010
[E23] 081111 075634 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_6979810746045389129 is added to invalidSet of 10.251.127.47:50010
[E23] 081111 075634 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_6979810746045389129 is added to invalidSet of 10.251.67.113:50010
[E20] 081111 075920 19 WARN dfs.FSDataset: Unexpected error trying to delete block blk_6979810746045389129. BlockInfo not found in volumeMap.
[E21] 081111 075933 19 INFO dfs.FSDataset: Deleting block blk_6979810746045389129 file /mnt/hadoop/dfs/data/current/subdir48/blk_6979810746045389129
[E21] 081111 075945 19 INFO dfs.FSDataset: Deleting block blk_6979810746045389129 file /mnt/hadoop/dfs/data/current/subdir0/blk_6979810746045389129
[E21] 081111 080210 19 INFO dfs.FSDataset: Deleting block blk_6979810746045389129 file /mnt/hadoop/dfs/data/current/subdir19/blk_6979810746045389129
```

### Résumé proposé

La trace contient des opérations HDFS sur le bloc, notamment : erreur de suppression : BlockInfo absent de volumeMap. Les autres opérations sont détaillées dans les faits observés.

### Faits observés

- E5 : 4 occurrence(s) — début de réception.
- E22 : 1 occurrence(s) — allocation du bloc.
- E11 : 3 occurrence(s) — fin d'un PacketResponder.
- E9 : 3 occurrence(s) — confirmation de réception.
- E26 : 5 occurrence(s) — enregistrement du bloc.
- E25 : 1 occurrence(s) — demande de réplication.
- E18 : 1 occurrence(s) — démarrage d'un transfert.
- E16 : 1 occurrence(s) — transmission du bloc.
- E6 : 1 occurrence(s) — réception du bloc transféré.
- E21 : 4 occurrence(s) — suppression locale journalisée.
- E23 : 4 occurrence(s) — ajout aux ensembles d'invalidation.
- E20 : 1 occurrence(s) — erreur de suppression : BlockInfo absent de volumeMap.

### Hypothèses


### Informations manquantes

- Cause de l'absence de BlockInfo dans volumeMap.

### Sources C6 candidates

hdfs-architecture-1.2.1#data-replication#1;hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0046 — blk_7892512089437196598

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E22] 081110 110718 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand/_temporary/_task_200811101024_0001_m_001103_0/part-01103. blk_7892512089437196598
[E5] 081110 110718 9535 INFO dfs.DataNode$DataXceiver: Receiving block blk_7892512089437196598 src: /10.251.39.179:54169 dest: /10.251.39.179:50010
[E5] 081110 110718 9646 INFO dfs.DataNode$DataXceiver: Receiving block blk_7892512089437196598 src: /10.251.214.175:51376 dest: /10.251.214.175:50010
[E5] 081110 110718 9704 INFO dfs.DataNode$DataXceiver: Receiving block blk_7892512089437196598 src: /10.251.39.179:53880 dest: /10.251.39.179:50010
[E26] 081110 110753 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.39.179:50010 is added to blk_7892512089437196598 size 67108864
[E26] 081110 110753 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.90.239:50010 is added to blk_7892512089437196598 size 67108864
[E26] 081110 110753 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.214.175:50010 is added to blk_7892512089437196598 size 67108864
[E11] 081110 110753 9536 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_7892512089437196598 terminating
[E9] 081110 110753 9536 INFO dfs.DataNode$PacketResponder: Received block blk_7892512089437196598 of size 67108864 from /10.251.39.179
[E11] 081110 110753 9647 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_7892512089437196598 terminating
[E9] 081110 110753 9647 INFO dfs.DataNode$PacketResponder: Received block blk_7892512089437196598 of size 67108864 from /10.251.214.175
[E11] 081110 110754 9705 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_7892512089437196598 terminating
[E9] 081110 110754 9705 INFO dfs.DataNode$PacketResponder: Received block blk_7892512089437196598 of size 67108864 from /10.251.39.179
[E4] 081110 132457 11694 WARN dfs.DataNode$DataXceiver: 10.251.214.175:50010:Got exception while serving blk_7892512089437196598 to /10.251.91.84:
[E3] 081110 132515 11695 INFO dfs.DataNode$DataXceiver: 10.251.214.175:50010 Served block blk_7892512089437196598 to /10.251.91.84
[E4] 081110 132539 11843 WARN dfs.DataNode$DataXceiver: 10.251.39.179:50010:Got exception while serving blk_7892512089437196598 to /10.251.71.68:
[E2] 081110 190254 13 INFO dfs.DataBlockScanner: Verification succeeded for blk_7892512089437196598
[E23] 081110 210151 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_7892512089437196598 is added to invalidSet of 10.251.214.175:50010
[E23] 081110 210151 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_7892512089437196598 is added to invalidSet of 10.251.39.179:50010
[E23] 081110 210151 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_7892512089437196598 is added to invalidSet of 10.251.90.239:50010
[E21] 081110 210305 19 INFO dfs.FSDataset: Deleting block blk_7892512089437196598 file /mnt/hadoop/dfs/data/current/subdir8/blk_7892512089437196598
[E20] 081110 210610 19 WARN dfs.FSDataset: Unexpected error trying to delete block blk_7892512089437196598. BlockInfo not found in volumeMap.
[E21] 081110 210621 18 INFO dfs.FSDataset: Deleting block blk_7892512089437196598 file /mnt/hadoop/dfs/data/current/subdir51/blk_7892512089437196598
[E21] 081110 210657 19 INFO dfs.FSDataset: Deleting block blk_7892512089437196598 file /mnt/hadoop/dfs/data/current/subdir39/blk_7892512089437196598
```

### Résumé proposé

La trace contient des opérations HDFS sur le bloc, notamment : exception signalée pendant le service du bloc; erreur de suppression : BlockInfo absent de volumeMap. Les autres opérations sont détaillées dans les faits observés.

### Faits observés

- E22 : 1 occurrence(s) — allocation du bloc.
- E5 : 3 occurrence(s) — début de réception.
- E26 : 3 occurrence(s) — enregistrement du bloc.
- E11 : 3 occurrence(s) — fin d'un PacketResponder.
- E9 : 3 occurrence(s) — confirmation de réception.
- E4 : 2 occurrence(s) — exception signalée pendant le service du bloc.
- E3 : 1 occurrence(s) — service du bloc à un client.
- E2 : 1 occurrence(s) — vérification réussie du bloc.
- E23 : 3 occurrence(s) — ajout aux ensembles d'invalidation.
- E21 : 3 occurrence(s) — suppression locale journalisée.
- E20 : 1 occurrence(s) — erreur de suppression : BlockInfo absent de volumeMap.

### Hypothèses


### Informations manquantes

- Nature et cause des exceptions pendant le service.
- Cause de l'absence de BlockInfo dans volumeMap.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0047 — blk_4284099996556810257

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E5] 081110 211412 14321 INFO dfs.DataNode$DataXceiver: Receiving block blk_4284099996556810257 src: /10.251.195.70:58350 dest: /10.251.195.70:50010
[E5] 081110 211412 14770 INFO dfs.DataNode$DataXceiver: Receiving block blk_4284099996556810257 src: /10.251.195.70:56735 dest: /10.251.195.70:50010
[E22] 081110 211412 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand3/_temporary/_task_200811101024_0005_m_000125_0/part-00125. blk_4284099996556810257
[E7] 081110 211415 14770 INFO dfs.DataNode$DataXceiver: writeBlock blk_4284099996556810257 received exception java.io.IOException: Could not read from stream
```

### Résumé proposé

Deux débuts de réception et une allocation du bloc sont journalisés. Trois secondes plus tard, writeBlock signale une IOException avec le message 'Could not read from stream'. Aucune confirmation de réception n'apparaît dans cette trace.

### Faits observés

- E5 : deux débuts de réception.
- E22 : allocation du bloc.
- E7 : IOException pendant writeBlock, avec le message 'Could not read from stream'.
- Aucun événement E9 n'est présent dans la trace fournie.

### Hypothèses


### Informations manquantes

- Cause initiale de l'IOException.
- État final du transfert et éventuelles tentatives ultérieures.

### Sources C6 candidates

hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0048 — blk_6263928820321107232

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 070423 22822 INFO dfs.DataNode$DataXceiver: Receiving block blk_6263928820321107232 src: /10.251.38.197:49282 dest: /10.251.38.197:50010
[E5] 081111 070423 22835 INFO dfs.DataNode$DataXceiver: Receiving block blk_6263928820321107232 src: /10.251.38.197:49969 dest: /10.251.38.197:50010
[E22] 081111 070423 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand6/_temporary/_task_200811101024_0013_m_000194_0/part-00194. blk_6263928820321107232
[E5] 081111 070424 22604 INFO dfs.DataNode$DataXceiver: Receiving block blk_6263928820321107232 src: /10.251.215.192:37857 dest: /10.251.215.192:50010
[E11] 081111 070518 22605 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_6263928820321107232 terminating
[E9] 081111 070518 22605 INFO dfs.DataNode$PacketResponder: Received block blk_6263928820321107232 of size 67108864 from /10.251.215.192
[E11] 081111 070518 22823 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_6263928820321107232 terminating
[E9] 081111 070518 22823 INFO dfs.DataNode$PacketResponder: Received block blk_6263928820321107232 of size 67108864 from /10.251.38.197
[E26] 081111 070518 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.215.192:50010 is added to blk_6263928820321107232 size 67108864
[E26] 081111 070518 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.42.9:50010 is added to blk_6263928820321107232 size 67108864
[E11] 081111 070519 22836 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_6263928820321107232 terminating
[E9] 081111 070519 22836 INFO dfs.DataNode$PacketResponder: Received block blk_6263928820321107232 of size 67108864 from /10.251.38.197
[E26] 081111 070519 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.38.197:50010 is added to blk_6263928820321107232 size 67108864
[E23] 081111 085908 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_6263928820321107232 is added to invalidSet of 10.251.215.192:50010
[E23] 081111 085908 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_6263928820321107232 is added to invalidSet of 10.251.38.197:50010
[E23] 081111 085908 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_6263928820321107232 is added to invalidSet of 10.251.42.9:50010
[E21] 081111 090028 19 INFO dfs.FSDataset: Deleting block blk_6263928820321107232 file /mnt/hadoop/dfs/data/current/subdir26/blk_6263928820321107232
[E20] 081111 090151 19 WARN dfs.FSDataset: Unexpected error trying to delete block blk_6263928820321107232. BlockInfo not found in volumeMap.
[E21] 081111 090152 19 INFO dfs.FSDataset: Deleting block blk_6263928820321107232 file /mnt/hadoop/dfs/data/current/subdir60/blk_6263928820321107232
[E21] 081111 090308 19 INFO dfs.FSDataset: Deleting block blk_6263928820321107232 file /mnt/hadoop/dfs/data/current/subdir31/blk_6263928820321107232
```

### Résumé proposé

La trace contient des opérations HDFS sur le bloc, notamment : erreur de suppression : BlockInfo absent de volumeMap. Les autres opérations sont détaillées dans les faits observés.

### Faits observés

- E5 : 3 occurrence(s) — début de réception.
- E22 : 1 occurrence(s) — allocation du bloc.
- E11 : 3 occurrence(s) — fin d'un PacketResponder.
- E9 : 3 occurrence(s) — confirmation de réception.
- E26 : 3 occurrence(s) — enregistrement du bloc.
- E23 : 3 occurrence(s) — ajout aux ensembles d'invalidation.
- E21 : 3 occurrence(s) — suppression locale journalisée.
- E20 : 1 occurrence(s) — erreur de suppression : BlockInfo absent de volumeMap.

### Hypothèses


### Informations manquantes

- Cause de l'absence de BlockInfo dans volumeMap.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0049 — blk_6161225427189509238

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 065922 22551 INFO dfs.DataNode$DataXceiver: Receiving block blk_6161225427189509238 src: /10.251.111.80:52524 dest: /10.251.111.80:50010
[E5] 081111 065922 22649 INFO dfs.DataNode$DataXceiver: Receiving block blk_6161225427189509238 src: /10.251.111.80:55856 dest: /10.251.111.80:50010
[E22] 081111 065922 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand6/_temporary/_task_200811101024_0013_m_000050_0/part-00050. blk_6161225427189509238
[E5] 081111 065923 22695 INFO dfs.DataNode$DataXceiver: Receiving block blk_6161225427189509238 src: /10.251.38.214:34981 dest: /10.251.38.214:50010
[E11] 081111 065954 22552 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_6161225427189509238 terminating
[E9] 081111 065954 22552 INFO dfs.DataNode$PacketResponder: Received block blk_6161225427189509238 of size 67108864 from /10.251.111.80
[E11] 081111 065954 22650 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_6161225427189509238 terminating
[E9] 081111 065954 22650 INFO dfs.DataNode$PacketResponder: Received block blk_6161225427189509238 of size 67108864 from /10.251.111.80
[E11] 081111 065954 22696 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_6161225427189509238 terminating
[E9] 081111 065954 22696 INFO dfs.DataNode$PacketResponder: Received block blk_6161225427189509238 of size 67108864 from /10.251.38.214
[E26] 081111 065954 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.110.8:50010 is added to blk_6161225427189509238 size 67108864
[E26] 081111 065954 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.38.214:50010 is added to blk_6161225427189509238 size 67108864
[E26] 081111 065954 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.111.80:50010 is added to blk_6161225427189509238 size 67108864
[E23] 081111 085906 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_6161225427189509238 is added to invalidSet of 10.251.110.8:50010
[E23] 081111 085906 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_6161225427189509238 is added to invalidSet of 10.251.111.80:50010
[E23] 081111 085906 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_6161225427189509238 is added to invalidSet of 10.251.38.214:50010
[E21] 081111 090040 19 INFO dfs.FSDataset: Deleting block blk_6161225427189509238 file /mnt/hadoop/dfs/data/current/subdir0/blk_6161225427189509238
[E21] 081111 090155 19 INFO dfs.FSDataset: Deleting block blk_6161225427189509238 file /mnt/hadoop/dfs/data/current/subdir29/blk_6161225427189509238
[E20] 081111 090256 19 WARN dfs.FSDataset: Unexpected error trying to delete block blk_6161225427189509238. BlockInfo not found in volumeMap.
[E21] 081111 090324 19 INFO dfs.FSDataset: Deleting block blk_6161225427189509238 file /mnt/hadoop/dfs/data/current/subdir38/blk_6161225427189509238
```

### Résumé proposé

La trace contient des opérations HDFS sur le bloc, notamment : erreur de suppression : BlockInfo absent de volumeMap. Les autres opérations sont détaillées dans les faits observés.

### Faits observés

- E5 : 3 occurrence(s) — début de réception.
- E22 : 1 occurrence(s) — allocation du bloc.
- E11 : 3 occurrence(s) — fin d'un PacketResponder.
- E9 : 3 occurrence(s) — confirmation de réception.
- E26 : 3 occurrence(s) — enregistrement du bloc.
- E23 : 3 occurrence(s) — ajout aux ensembles d'invalidation.
- E21 : 3 occurrence(s) — suppression locale journalisée.
- E20 : 1 occurrence(s) — erreur de suppression : BlockInfo absent de volumeMap.

### Hypothèses


### Informations manquantes

- Cause de l'absence de BlockInfo dans volumeMap.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0050 — blk_-2316392385510876816

**Label officiel :** 1

**Abstention proposée :** True

### Trace originale

```text
[E22] 081110 110853 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand/_temporary/_task_200811101024_0001_m_001365_0/part-01365. blk_-2316392385510876816
[E5] 081110 110853 9736 INFO dfs.DataNode$DataXceiver: Receiving block blk_-2316392385510876816 src: /10.250.14.196:52214 dest: /10.250.14.196:50010
```

### Résumé proposé

Une allocation du bloc et un début de réception sont journalisés. Aucun événement ultérieur ne permet de confirmer la fin de la réception ou de déterminer son issue.

### Faits observés

- E22 : allocation du bloc.
- E5 : début de réception du bloc.
- Aucune confirmation E9 ni erreur explicite dans la trace fournie.

### Hypothèses


### Informations manquantes

- Issue réelle de la réception.
- Événements ultérieurs et état final du bloc.
- Contexte expliquant pourquoi la trace s'arrête après le début de réception.

### Sources C6 candidates

hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0051 — blk_2415622095534006294

**Label officiel :** 1

**Abstention proposée :** True

### Trace originale

```text
[E22] 081110 014037 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/randtxt/_temporary/_task_200811092030_0003_m_001434_0/part-01434. blk_2415622095534006294
[E5] 081110 014037 5660 INFO dfs.DataNode$DataXceiver: Receiving block blk_2415622095534006294 src: /10.251.91.32:47335 dest: /10.251.91.32:50010
```

### Résumé proposé

Une allocation du bloc HDFS et un début de réception sont journalisés. La trace ne contient aucune confirmation de réception, ni message d'erreur explicite. L'issue de l'opération ne peut pas être déterminée.

### Faits observés

- E22 : une allocation du bloc est journalisée.
- E5 : un début de réception du bloc est journalisé.
- Aucun événement E9 de confirmation de réception n'apparaît dans la trace.
- Aucun message d'erreur explicite n'apparaît dans la trace.

### Hypothèses


### Informations manquantes

- Résultat final de la réception du bloc.
- Éventuels événements ultérieurs de confirmation ou d'échec.
- Contexte permettant d'expliquer l'absence de suite dans la trace.

### Sources C6 candidates

hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0052 — blk_8968730668433643962

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 073448 23633 INFO dfs.DataNode$DataXceiver: Receiving block blk_8968730668433643962 src: /10.251.199.86:47550 dest: /10.251.199.86:50010
[E22] 081111 073448 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand6/_temporary/_task_200811101024_0013_m_001197_0/part-01197. blk_8968730668433643962
[E5] 081111 073452 23120 INFO dfs.DataNode$DataXceiver: Receiving block blk_8968730668433643962 src: /10.251.66.192:51710 dest: /10.251.66.192:50010
[E5] 081111 073452 23330 INFO dfs.DataNode$DataXceiver: Receiving block blk_8968730668433643962 src: /10.251.199.86:53094 dest: /10.251.199.86:50010
[E11] 081111 073551 23121 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_8968730668433643962 terminating
[E9] 081111 073551 23121 INFO dfs.DataNode$PacketResponder: Received block blk_8968730668433643962 of size 67108864 from /10.251.66.192
[E11] 081111 073551 23333 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_8968730668433643962 terminating
[E9] 081111 073551 23333 INFO dfs.DataNode$PacketResponder: Received block blk_8968730668433643962 of size 67108864 from /10.251.199.86
[E11] 081111 073551 23638 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_8968730668433643962 terminating
[E9] 081111 073551 23638 INFO dfs.DataNode$PacketResponder: Received block blk_8968730668433643962 of size 67108864 from /10.251.199.86
[E26] 081111 073551 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.199.86:50010 is added to blk_8968730668433643962 size 67108864
[E26] 081111 073551 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.66.192:50010 is added to blk_8968730668433643962 size 67108864
[E26] 081111 073551 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.107.227:50010 is added to blk_8968730668433643962 size 67108864
[E23] 081111 085919 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_8968730668433643962 is added to invalidSet of 10.251.107.227:50010
[E23] 081111 085919 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_8968730668433643962 is added to invalidSet of 10.251.199.86:50010
[E23] 081111 085919 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_8968730668433643962 is added to invalidSet of 10.251.66.192:50010
[E21] 081111 085932 19 INFO dfs.FSDataset: Deleting block blk_8968730668433643962 file /mnt/hadoop/dfs/data/current/subdir40/blk_8968730668433643962
[E21] 081111 090200 19 INFO dfs.FSDataset: Deleting block blk_8968730668433643962 file /mnt/hadoop/dfs/data/current/subdir32/blk_8968730668433643962
[E20] 081111 090224 19 WARN dfs.FSDataset: Unexpected error trying to delete block blk_8968730668433643962. BlockInfo not found in volumeMap.
[E21] 081111 090330 19 INFO dfs.FSDataset: Deleting block blk_8968730668433643962 file /mnt/hadoop/dfs/data/current/subdir22/blk_8968730668433643962
```

### Résumé proposé

La trace contient des opérations HDFS sur le bloc, notamment : erreur de suppression : BlockInfo absent de volumeMap. Les autres opérations sont détaillées dans les faits observés.

### Faits observés

- E5 : 3 occurrence(s) — début de réception.
- E22 : 1 occurrence(s) — allocation du bloc.
- E11 : 3 occurrence(s) — fin d'un PacketResponder.
- E9 : 3 occurrence(s) — confirmation de réception.
- E26 : 3 occurrence(s) — enregistrement du bloc.
- E23 : 3 occurrence(s) — ajout aux ensembles d'invalidation.
- E21 : 3 occurrence(s) — suppression locale journalisée.
- E20 : 1 occurrence(s) — erreur de suppression : BlockInfo absent de volumeMap.

### Hypothèses


### Informations manquantes

- Cause de l'absence de BlockInfo dans volumeMap.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0053 — blk_7266811683079569880

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 044808 20078 INFO dfs.DataNode$DataXceiver: Receiving block blk_7266811683079569880 src: /10.251.105.189:41785 dest: /10.251.105.189:50010
[E5] 081111 044808 20220 INFO dfs.DataNode$DataXceiver: Receiving block blk_7266811683079569880 src: /10.250.10.223:47852 dest: /10.250.10.223:50010
[E5] 081111 044808 20237 INFO dfs.DataNode$DataXceiver: Receiving block blk_7266811683079569880 src: /10.250.10.223:49967 dest: /10.250.10.223:50010
[E22] 081111 044808 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand5/_temporary/_task_200811101024_0011_m_000031_0/part-00031. blk_7266811683079569880
[E11] 081111 044825 20079 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_7266811683079569880 terminating
[E9] 081111 044825 20079 INFO dfs.DataNode$PacketResponder: Received block blk_7266811683079569880 of size 67108864 from /10.251.105.189
[E11] 081111 044826 20221 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_7266811683079569880 terminating
[E9] 081111 044826 20221 INFO dfs.DataNode$PacketResponder: Received block blk_7266811683079569880 of size 67108864 from /10.250.10.223
[E11] 081111 044826 20238 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_7266811683079569880 terminating
[E9] 081111 044826 20238 INFO dfs.DataNode$PacketResponder: Received block blk_7266811683079569880 of size 67108864 from /10.250.10.223
[E26] 081111 044908 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.105.189:50010 is added to blk_7266811683079569880 size 67108864
[E26] 081111 044914 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.10.223:50010 is added to blk_7266811683079569880 size 67108864
[E26] 081111 044921 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.39.192:50010 is added to blk_7266811683079569880 size 67108864
[E23] 081111 075617 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_7266811683079569880 is added to invalidSet of 10.250.10.223:50010
[E23] 081111 075617 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_7266811683079569880 is added to invalidSet of 10.251.105.189:50010
[E23] 081111 075617 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_7266811683079569880 is added to invalidSet of 10.251.39.192:50010
[E21] 081111 075817 19 INFO dfs.FSDataset: Deleting block blk_7266811683079569880 file /mnt/hadoop/dfs/data/current/blk_7266811683079569880
[E21] 081111 075927 18 INFO dfs.FSDataset: Deleting block blk_7266811683079569880 file /mnt/hadoop/dfs/data/current/blk_7266811683079569880
[E21] 081111 075928 18 INFO dfs.FSDataset: Deleting block blk_7266811683079569880 file /mnt/hadoop/dfs/data/current/blk_7266811683079569880
[E20] 081111 075945 19 WARN dfs.FSDataset: Unexpected error trying to delete block blk_7266811683079569880. BlockInfo not found in volumeMap.
```

### Résumé proposé

La trace contient des opérations HDFS sur le bloc, notamment : erreur de suppression : BlockInfo absent de volumeMap. Les autres opérations sont détaillées dans les faits observés.

### Faits observés

- E5 : 3 occurrence(s) — début de réception.
- E22 : 1 occurrence(s) — allocation du bloc.
- E11 : 3 occurrence(s) — fin d'un PacketResponder.
- E9 : 3 occurrence(s) — confirmation de réception.
- E26 : 3 occurrence(s) — enregistrement du bloc.
- E23 : 3 occurrence(s) — ajout aux ensembles d'invalidation.
- E21 : 3 occurrence(s) — suppression locale journalisée.
- E20 : 1 occurrence(s) — erreur de suppression : BlockInfo absent de volumeMap.

### Hypothèses


### Informations manquantes

- Cause de l'absence de BlockInfo dans volumeMap.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0054 — blk_8019465173337710476

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 072421 22814 INFO dfs.DataNode$DataXceiver: Receiving block blk_8019465173337710476 src: /10.251.202.134:50600 dest: /10.251.202.134:50010
[E5] 081111 072421 22973 INFO dfs.DataNode$DataXceiver: Receiving block blk_8019465173337710476 src: /10.251.214.130:52934 dest: /10.251.214.130:50010
[E5] 081111 072421 23150 INFO dfs.DataNode$DataXceiver: Receiving block blk_8019465173337710476 src: /10.251.202.134:38255 dest: /10.251.202.134:50010
[E22] 081111 072421 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand6/_temporary/_task_200811101024_0013_m_001207_0/part-01207. blk_8019465173337710476
[E11] 081111 072511 22815 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_8019465173337710476 terminating
[E9] 081111 072511 22815 INFO dfs.DataNode$PacketResponder: Received block blk_8019465173337710476 of size 67108864 from /10.251.202.134
[E11] 081111 072511 22974 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_8019465173337710476 terminating
[E9] 081111 072511 22974 INFO dfs.DataNode$PacketResponder: Received block blk_8019465173337710476 of size 67108864 from /10.251.214.130
[E11] 081111 072511 23151 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_8019465173337710476 terminating
[E9] 081111 072511 23151 INFO dfs.DataNode$PacketResponder: Received block blk_8019465173337710476 of size 67108864 from /10.251.202.134
[E26] 081111 072511 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.214.130:50010 is added to blk_8019465173337710476 size 67108864
[E26] 081111 072511 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.123.99:50010 is added to blk_8019465173337710476 size 67108864
[E26] 081111 072512 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.202.134:50010 is added to blk_8019465173337710476 size 67108864
[E23] 081111 085919 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_8019465173337710476 is added to invalidSet of 10.251.123.99:50010
[E23] 081111 085919 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_8019465173337710476 is added to invalidSet of 10.251.202.134:50010
[E23] 081111 085919 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_8019465173337710476 is added to invalidSet of 10.251.214.130:50010
[E21] 081111 090003 19 INFO dfs.FSDataset: Deleting block blk_8019465173337710476 file /mnt/hadoop/dfs/data/current/subdir28/blk_8019465173337710476
[E20] 081111 090158 19 WARN dfs.FSDataset: Unexpected error trying to delete block blk_8019465173337710476. BlockInfo not found in volumeMap.
[E21] 081111 090244 19 INFO dfs.FSDataset: Deleting block blk_8019465173337710476 file /mnt/hadoop/dfs/data/current/subdir5/blk_8019465173337710476
[E21] 081111 090250 18 INFO dfs.FSDataset: Deleting block blk_8019465173337710476 file /mnt/hadoop/dfs/data/current/subdir31/blk_8019465173337710476
```

### Résumé proposé

La trace contient des opérations HDFS sur le bloc, notamment : erreur de suppression : BlockInfo absent de volumeMap. Les autres opérations sont détaillées dans les faits observés.

### Faits observés

- E5 : 3 occurrence(s) — début de réception.
- E22 : 1 occurrence(s) — allocation du bloc.
- E11 : 3 occurrence(s) — fin d'un PacketResponder.
- E9 : 3 occurrence(s) — confirmation de réception.
- E26 : 3 occurrence(s) — enregistrement du bloc.
- E23 : 3 occurrence(s) — ajout aux ensembles d'invalidation.
- E21 : 3 occurrence(s) — suppression locale journalisée.
- E20 : 1 occurrence(s) — erreur de suppression : BlockInfo absent de volumeMap.

### Hypothèses


### Informations manquantes

- Cause de l'absence de BlockInfo dans volumeMap.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0055 — blk_8554401366568742969

**Label officiel :** 1

**Abstention proposée :** True

### Trace originale

```text
[E22] 081109 205507 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand/_temporary/_task_200811092030_0001_m_000670_0/part-00670. blk_8554401366568742969
[E5] 081109 205507 901 INFO dfs.DataNode$DataXceiver: Receiving block blk_8554401366568742969 src: /10.251.214.67:39782 dest: /10.251.214.67:50010
```

### Résumé proposé

Une allocation du bloc HDFS et un début de réception sont journalisés. La trace ne contient aucune confirmation de réception, ni message d'erreur explicite. L'issue de l'opération ne peut pas être déterminée.

### Faits observés

- E22 : une allocation du bloc est journalisée.
- E5 : un début de réception du bloc est journalisé.
- Aucun événement E9 de confirmation de réception n'apparaît dans la trace.
- Aucun message d'erreur explicite n'apparaît dans la trace.

### Hypothèses


### Informations manquantes

- Résultat final de la réception du bloc.
- Éventuels événements ultérieurs de confirmation ou d'échec.
- Contexte permettant d'expliquer l'absence de suite dans la trace.

### Sources C6 candidates

hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0056 — blk_-2705986310204860977

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E5] 081110 214729 15383 INFO dfs.DataNode$DataXceiver: Receiving block blk_-2705986310204860977 src: /10.251.38.53:50134 dest: /10.251.38.53:50010
[E5] 081110 214729 15385 INFO dfs.DataNode$DataXceiver: Receiving block blk_-2705986310204860977 src: /10.251.71.97:36842 dest: /10.251.71.97:50010
[E5] 081110 214729 15518 INFO dfs.DataNode$DataXceiver: Receiving block blk_-2705986310204860977 src: /10.251.38.53:45915 dest: /10.251.38.53:50010
[E22] 081110 214729 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand3/_temporary/_task_200811101024_0005_m_001560_0/part-01560. blk_-2705986310204860977
[E11] 081110 214806 15384 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-2705986310204860977 terminating
[E9] 081110 214806 15384 INFO dfs.DataNode$PacketResponder: Received block blk_-2705986310204860977 of size 67108864 from /10.251.38.53
[E11] 081110 214806 15386 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-2705986310204860977 terminating
[E9] 081110 214806 15386 INFO dfs.DataNode$PacketResponder: Received block blk_-2705986310204860977 of size 67108864 from /10.251.71.97
[E11] 081110 214806 15520 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-2705986310204860977 terminating
[E9] 081110 214806 15520 INFO dfs.DataNode$PacketResponder: Received block blk_-2705986310204860977 of size 67108864 from /10.251.38.53
[E26] 081110 214806 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.38.53:50010 is added to blk_-2705986310204860977 size 67108864
[E26] 081110 214806 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.71.97:50010 is added to blk_-2705986310204860977 size 67108864
[E26] 081110 214808 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.214.67:50010 is added to blk_-2705986310204860977 size 67108864
[E27] 081110 214808 34 WARN dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: Redundant addStoredBlock request received for blk_-2705986310204860977 on 10.251.214.67:50010 size 67108864
[E23] 081110 220653 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-2705986310204860977 is added to invalidSet of 10.251.214.67:50010
[E23] 081110 220653 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-2705986310204860977 is added to invalidSet of 10.251.38.53:50010
[E23] 081110 220653 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-2705986310204860977 is added to invalidSet of 10.251.71.97:50010
[E21] 081110 220835 19 INFO dfs.FSDataset: Deleting block blk_-2705986310204860977 file /mnt/hadoop/dfs/data/current/subdir38/blk_-2705986310204860977
[E21] 081110 220919 19 INFO dfs.FSDataset: Deleting block blk_-2705986310204860977 file /mnt/hadoop/dfs/data/current/subdir36/blk_-2705986310204860977
[E21] 081110 221011 19 INFO dfs.FSDataset: Deleting block blk_-2705986310204860977 file /mnt/hadoop/dfs/data/current/subdir7/blk_-2705986310204860977
```

### Résumé proposé

Après l'allocation du bloc, trois réceptions de 67 108 864 octets sont confirmées et trois DataNodes sont enregistrés. Un avertissement E27 signale ensuite une requête addStoredBlock redondante pour le DataNode 10.251.214.67:50010, déjà enregistré. Le bloc est ensuite invalidé sur trois DataNodes, puis trois suppressions locales sont journalisées.

### Faits observés

- E22 et E5 : allocation et trois débuts de réception.
- E9 : trois confirmations de réception.
- E26 : trois enregistrements de DataNodes.
- E27 : requête addStoredBlock redondante pour 10.251.214.67:50010.
- E23 : trois ajouts aux ensembles d'invalidation.
- E21 : trois suppressions locales journalisées.

### Hypothèses


### Informations manquantes

- Cause de la requête addStoredBlock redondante.
- Contexte des notifications envoyées au NameNode.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0057 — blk_-5175697911062105497

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E22] 081110 114944 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/randtxt2/_temporary/_task_200811101024_0002_m_000403_0/part-00403. blk_-5175697911062105497
[E5] 081110 114944 7935 INFO dfs.DataNode$DataXceiver: Receiving block blk_-5175697911062105497 src: /10.251.123.33:53907 dest: /10.251.123.33:50010
[E5] 081110 114945 10356 INFO dfs.DataNode$DataXceiver: Receiving block blk_-5175697911062105497 src: /10.251.123.33:33639 dest: /10.251.123.33:50010
[E5] 081110 114946 10588 INFO dfs.DataNode$DataXceiver: Receiving block blk_-5175697911062105497 src: /10.251.214.67:39727 dest: /10.251.214.67:50010
[E11] 081110 115034 10358 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-5175697911062105497 terminating
[E9] 081110 115034 10358 INFO dfs.DataNode$PacketResponder: Received block blk_-5175697911062105497 of size 67108864 from /10.251.123.33
[E11] 081110 115034 10589 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-5175697911062105497 terminating
[E9] 081110 115034 10589 INFO dfs.DataNode$PacketResponder: Received block blk_-5175697911062105497 of size 67108864 from /10.251.214.67
[E26] 081110 115034 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.214.67:50010 is added to blk_-5175697911062105497 size 67108864
[E26] 081110 115034 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.91.15:50010 is added to blk_-5175697911062105497 size 67108864
[E26] 081110 115035 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.123.33:50010 is added to blk_-5175697911062105497 size 67108864
[E11] 081110 115035 7936 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-5175697911062105497 terminating
[E9] 081110 115035 7936 INFO dfs.DataNode$PacketResponder: Received block blk_-5175697911062105497 of size 67108864 from /10.251.123.33
[E3] 081110 170426 13732 INFO dfs.DataNode$DataXceiver: 10.251.91.15:50010 Served block blk_-5175697911062105497 to /10.251.91.15
[E4] 081110 170434 10421 WARN dfs.DataNode$DataXceiver: 10.251.123.33:50010:Got exception while serving blk_-5175697911062105497 to /10.251.123.33:
[E3] 081110 170506 10413 INFO dfs.DataNode$DataXceiver: 10.251.123.33:50010 Served block blk_-5175697911062105497 to /10.251.123.33
[E5] 081110 211435 14576 INFO dfs.DataNode$DataXceiver: Receiving block blk_-5175697911062105497 src: /10.251.91.15:39456 dest: /10.251.91.15:50010
[E18] 081110 211435 19 INFO dfs.DataNode: 10.251.91.15:50010 Starting thread to transfer block blk_-5175697911062105497 to 10.251.111.37:50010
[E25] 081110 211435 19 INFO dfs.FSNamesystem: BLOCK* ask 10.251.91.15:50010 to replicate blk_-5175697911062105497 to datanode(s) 10.251.111.37:50010
[E6] 081110 211520 14576 INFO dfs.DataNode$DataXceiver: Received block blk_-5175697911062105497 src: /10.251.91.15:39456 dest: /10.251.91.15:50010 of size 67108864
[E16] 081110 211520 14833 INFO dfs.DataNode$DataTransfer: 10.251.91.15:50010:Transmitted block blk_-5175697911062105497 to /10.251.111.37:50010
[E26] 081110 211520 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.111.37:50010 is added to blk_-5175697911062105497 size 67108864
[E26] 081110 212509 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.123.33:50010 is added to blk_-5175697911062105497 size 67108864
[E21] 081110 212514 19 INFO dfs.FSDataset: Deleting block blk_-5175697911062105497 file /mnt/hadoop/dfs/data/current/subdir59/blk_-5175697911062105497
[E25] 081110 221938 19 INFO dfs.FSNamesystem: BLOCK* ask 10.251.214.67:50010 to replicate blk_-5175697911062105497 to datanode(s) 10.251.215.192:50010
[E5] 081110 221939 16119 INFO dfs.DataNode$DataXceiver: Receiving block blk_-5175697911062105497 src: /10.251.214.67:53972 dest: /10.251.214.67:50010
[E18] 081110 221939 19 INFO dfs.DataNode: 10.251.214.67:50010 Starting thread to transfer block blk_-5175697911062105497 to 10.251.215.192:50010
[E16] 081110 222001 15963 INFO dfs.DataNode$DataTransfer: 10.251.214.67:50010:Transmitted block blk_-5175697911062105497 to /10.251.215.192:50010
[E6] 081110 222001 16119 INFO dfs.DataNode$DataXceiver: Received block blk_-5175697911062105497 src: /10.251.214.67:53972 dest: /10.251.214.67:50010 of size 67108864
[E26] 081110 222001 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.215.192:50010 is added to blk_-5175697911062105497 size 67108864
[E26] 081110 222720 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.123.33:50010 is added to blk_-5175697911062105497 size 67108864
[E21] 081110 222723 19 INFO dfs.FSDataset: Deleting block blk_-5175697911062105497 file /mnt/hadoop/dfs/data/current/subdir19/blk_-5175697911062105497
[E3] 081111 000008 17304 INFO dfs.DataNode$DataXceiver: 10.251.215.192:50010 Served block blk_-5175697911062105497 to /10.251.215.192
[E4] 081111 000113 12920 WARN dfs.DataNode$DataXceiver: 10.251.123.33:50010:Got exception while serving blk_-5175697911062105497 to /10.251.123.33:
[E3] 081111 000236 12914 INFO dfs.DataNode$DataXceiver: 10.251.123.33:50010 Served block blk_-5175697911062105497 to /10.251.123.33
[E23] 081111 023015 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-5175697911062105497 is added to invalidSet of 10.251.111.37:50010
[E23] 081111 023015 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-5175697911062105497 is added to invalidSet of 10.251.123.33:50010
[E23] 081111 023015 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-5175697911062105497 is added to invalidSet of 10.251.215.192:50010
[E21] 081111 023134 19 INFO dfs.FSDataset: Deleting block blk_-5175697911062105497 file /mnt/hadoop/dfs/data/current/subdir29/blk_-5175697911062105497
[E21] 081111 023232 19 INFO dfs.FSDataset: Deleting block blk_-5175697911062105497 file /mnt/hadoop/dfs/data/current/subdir21/blk_-5175697911062105497
[E21] 081111 023247 19 INFO dfs.FSDataset: Deleting block blk_-5175697911062105497 file /mnt/hadoop/dfs/data/current/subdir2/blk_-5175697911062105497
```

### Résumé proposé

La trace contient des opérations HDFS sur le bloc, notamment : exception signalée pendant le service du bloc. Les autres opérations sont détaillées dans les faits observés.

### Faits observés

- E22 : 1 occurrence(s) — allocation du bloc.
- E5 : 5 occurrence(s) — début de réception.
- E11 : 3 occurrence(s) — fin d'un PacketResponder.
- E9 : 3 occurrence(s) — confirmation de réception.
- E26 : 7 occurrence(s) — enregistrement du bloc.
- E3 : 4 occurrence(s) — service du bloc à un client.
- E4 : 2 occurrence(s) — exception signalée pendant le service du bloc.
- E18 : 2 occurrence(s) — démarrage d'un transfert.
- E25 : 2 occurrence(s) — demande de réplication.
- E6 : 2 occurrence(s) — réception du bloc transféré.
- E16 : 2 occurrence(s) — transmission du bloc.
- E21 : 5 occurrence(s) — suppression locale journalisée.
- E23 : 3 occurrence(s) — ajout aux ensembles d'invalidation.

### Hypothèses


### Informations manquantes

- Nature et cause des exceptions pendant le service.

### Sources C6 candidates

hdfs-architecture-1.2.1#data-replication#1;hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0058 — blk_4682079352953027867

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E22] 081109 211808 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand/_temporary/_task_200811092030_0001_m_001588_0/part-01588. blk_4682079352953027867
[E5] 081109 211809 1637 INFO dfs.DataNode$DataXceiver: Receiving block blk_4682079352953027867 src: /10.250.11.53:48320 dest: /10.250.11.53:50010
[E5] 081109 211809 1725 INFO dfs.DataNode$DataXceiver: Receiving block blk_4682079352953027867 src: /10.251.203.166:38388 dest: /10.251.203.166:50010
[E5] 081109 211809 1767 INFO dfs.DataNode$DataXceiver: Receiving block blk_4682079352953027867 src: /10.251.203.166:40268 dest: /10.251.203.166:50010
[E11] 081109 211849 1638 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_4682079352953027867 terminating
[E9] 081109 211849 1638 INFO dfs.DataNode$PacketResponder: Received block blk_4682079352953027867 of size 67108864 from /10.250.11.53
[E11] 081109 211849 1726 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_4682079352953027867 terminating
[E9] 081109 211849 1726 INFO dfs.DataNode$PacketResponder: Received block blk_4682079352953027867 of size 67108864 from /10.251.203.166
[E11] 081109 211849 1768 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_4682079352953027867 terminating
[E9] 081109 211849 1768 INFO dfs.DataNode$PacketResponder: Received block blk_4682079352953027867 of size 67108864 from /10.251.203.166
[E26] 081109 211849 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.203.166:50010 is added to blk_4682079352953027867 size 67108864
[E26] 081109 211849 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.11.53:50010 is added to blk_4682079352953027867 size 67108864
[E26] 081109 211849 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.106.10:50010 is added to blk_4682079352953027867 size 67108864
[E4] 081109 223629 3543 WARN dfs.DataNode$DataXceiver: 10.250.11.53:50010:Got exception while serving blk_4682079352953027867 to /10.250.15.198:
[E3] 081109 223637 3544 INFO dfs.DataNode$DataXceiver: 10.250.11.53:50010 Served block blk_4682079352953027867 to /10.250.15.198
[E4] 081109 223802 3565 WARN dfs.DataNode$DataXceiver: 10.250.11.53:50010:Got exception while serving blk_4682079352953027867 to /10.251.71.16:
[E2] 081110 054001 13 INFO dfs.DataBlockScanner: Verification succeeded for blk_4682079352953027867
[E23] 081110 103114 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_4682079352953027867 is added to invalidSet of 10.250.11.53:50010
[E23] 081110 103114 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_4682079352953027867 is added to invalidSet of 10.251.106.10:50010
[E23] 081110 103114 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_4682079352953027867 is added to invalidSet of 10.251.203.166:50010
[E21] 081110 103636 19 INFO dfs.FSDataset: Deleting block blk_4682079352953027867 file /mnt/hadoop/dfs/data/current/subdir29/blk_4682079352953027867
[E21] 081110 103757 19 INFO dfs.FSDataset: Deleting block blk_4682079352953027867 file /mnt/hadoop/dfs/data/current/subdir21/blk_4682079352953027867
[E28] 081110 104629 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: addStoredBlock request received for blk_4682079352953027867 on 10.251.106.10:50010 size 67108864 But it does not belong to any file.
[E26] 081110 104629 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.106.10:50010 is added to blk_4682079352953027867 size 67108864
[E21] 081110 105415 19 INFO dfs.FSDataset: Deleting block blk_4682079352953027867 file /mnt/hadoop/dfs/data/current/subdir61/blk_4682079352953027867
```

### Résumé proposé

La trace contient des opérations HDFS sur le bloc, notamment : exception signalée pendant le service du bloc; requête addStoredBlock pour un bloc sans fichier associé. Les autres opérations sont détaillées dans les faits observés.

### Faits observés

- E22 : 1 occurrence(s) — allocation du bloc.
- E5 : 3 occurrence(s) — début de réception.
- E11 : 3 occurrence(s) — fin d'un PacketResponder.
- E9 : 3 occurrence(s) — confirmation de réception.
- E26 : 4 occurrence(s) — enregistrement du bloc.
- E4 : 2 occurrence(s) — exception signalée pendant le service du bloc.
- E3 : 1 occurrence(s) — service du bloc à un client.
- E2 : 1 occurrence(s) — vérification réussie du bloc.
- E23 : 3 occurrence(s) — ajout aux ensembles d'invalidation.
- E21 : 3 occurrence(s) — suppression locale journalisée.
- E28 : 1 occurrence(s) — requête addStoredBlock pour un bloc sans fichier associé.

### Hypothèses


### Informations manquantes

- Nature et cause des exceptions pendant le service.
- Cause de la notification d'un bloc sans fichier associé.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0059 — blk_8482590428431422891

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E5] 081109 203610 174 INFO dfs.DataNode$DataXceiver: Receiving block blk_8482590428431422891 src: /10.250.19.16:45201 dest: /10.250.19.16:50010
[E5] 081109 203610 174 INFO dfs.DataNode$DataXceiver: Receiving block blk_8482590428431422891 src: /10.251.214.225:53308 dest: /10.251.214.225:50010
[E5] 081109 203610 184 INFO dfs.DataNode$DataXceiver: Receiving block blk_8482590428431422891 src: /10.251.214.225:33203 dest: /10.251.214.225:50010
[E22] 081109 203610 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand/_temporary/_task_200811092030_0001_m_000031_0/part-00031. blk_8482590428431422891
[E11] 081109 203645 175 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_8482590428431422891 terminating
[E9] 081109 203645 175 INFO dfs.DataNode$PacketResponder: Received block blk_8482590428431422891 of size 67108864 from /10.250.19.16
[E11] 081109 203645 185 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_8482590428431422891 terminating
[E9] 081109 203645 185 INFO dfs.DataNode$PacketResponder: Received block blk_8482590428431422891 of size 67108864 from /10.251.214.225
[E26] 081109 203645 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.19.16:50010 is added to blk_8482590428431422891 size 67108864
[E26] 081109 203645 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.203.179:50010 is added to blk_8482590428431422891 size 67108864
[E11] 081109 203646 175 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_8482590428431422891 terminating
[E9] 081109 203646 175 INFO dfs.DataNode$PacketResponder: Received block blk_8482590428431422891 of size 67108864 from /10.251.214.225
[E26] 081109 203646 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.214.225:50010 is added to blk_8482590428431422891 size 67108864
[E2] 081109 205018 13 INFO dfs.DataBlockScanner: Verification succeeded for blk_8482590428431422891
[E2] 081109 211733 13 INFO dfs.DataBlockScanner: Verification succeeded for blk_8482590428431422891
[E4] 081109 214152 2620 WARN dfs.DataNode$DataXceiver: 10.250.19.16:50010:Got exception while serving blk_8482590428431422891 to /10.251.106.214:
[E4] 081109 214154 2622 WARN dfs.DataNode$DataXceiver: 10.250.19.16:50010:Got exception while serving blk_8482590428431422891 to /10.251.106.214:
[E3] 081109 214234 2621 INFO dfs.DataNode$DataXceiver: 10.250.19.16:50010 Served block blk_8482590428431422891 to /10.251.106.214
[E2] 081109 214416 13 INFO dfs.DataBlockScanner: Verification succeeded for blk_8482590428431422891
[E23] 081110 103054 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_8482590428431422891 is added to invalidSet of 10.250.19.16:50010
[E23] 081110 103054 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_8482590428431422891 is added to invalidSet of 10.251.203.179:50010
[E23] 081110 103054 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_8482590428431422891 is added to invalidSet of 10.251.214.225:50010
[E21] 081110 103201 19 INFO dfs.FSDataset: Deleting block blk_8482590428431422891 file /mnt/hadoop/dfs/data/current/blk_8482590428431422891
[E21] 081110 103641 19 INFO dfs.FSDataset: Deleting block blk_8482590428431422891 file /mnt/hadoop/dfs/data/current/blk_8482590428431422891
[E21] 081110 103721 19 INFO dfs.FSDataset: Deleting block blk_8482590428431422891 file /mnt/hadoop/dfs/data/current/blk_8482590428431422891
[E20] 081110 103801 19 WARN dfs.FSDataset: Unexpected error trying to delete block blk_8482590428431422891. BlockInfo not found in volumeMap.
```

### Résumé proposé

La trace contient des opérations HDFS sur le bloc, notamment : exception signalée pendant le service du bloc; erreur de suppression : BlockInfo absent de volumeMap. Les autres opérations sont détaillées dans les faits observés.

### Faits observés

- E5 : 3 occurrence(s) — début de réception.
- E22 : 1 occurrence(s) — allocation du bloc.
- E11 : 3 occurrence(s) — fin d'un PacketResponder.
- E9 : 3 occurrence(s) — confirmation de réception.
- E26 : 3 occurrence(s) — enregistrement du bloc.
- E2 : 3 occurrence(s) — vérification réussie du bloc.
- E4 : 2 occurrence(s) — exception signalée pendant le service du bloc.
- E3 : 1 occurrence(s) — service du bloc à un client.
- E23 : 3 occurrence(s) — ajout aux ensembles d'invalidation.
- E21 : 3 occurrence(s) — suppression locale journalisée.
- E20 : 1 occurrence(s) — erreur de suppression : BlockInfo absent de volumeMap.

### Hypothèses


### Informations manquantes

- Nature et cause des exceptions pendant le service.
- Cause de l'absence de BlockInfo dans volumeMap.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0060 — blk_7563971601695995553

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E5] 081110 151209 12831 INFO dfs.DataNode$DataXceiver: Receiving block blk_7563971601695995553 src: /10.250.5.161:55741 dest: /10.250.5.161:50010
[E5] 081110 151209 12941 INFO dfs.DataNode$DataXceiver: Receiving block blk_7563971601695995553 src: /10.250.5.161:34258 dest: /10.250.5.161:50010
[E22] 081110 151209 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/sortrand2/_temporary/_task_200811101024_0003_r_000185_0/part-00185. blk_7563971601695995553
[E5] 081110 151211 13144 INFO dfs.DataNode$DataXceiver: Receiving block blk_7563971601695995553 src: /10.251.91.32:36026 dest: /10.251.91.32:50010
[E11] 081110 151318 12836 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_7563971601695995553 terminating
[E9] 081110 151318 12836 INFO dfs.DataNode$PacketResponder: Received block blk_7563971601695995553 of size 67108864 from /10.250.5.161
[E11] 081110 151318 12942 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_7563971601695995553 terminating
[E9] 081110 151318 12942 INFO dfs.DataNode$PacketResponder: Received block blk_7563971601695995553 of size 67108864 from /10.250.5.161
[E11] 081110 151318 13145 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_7563971601695995553 terminating
[E9] 081110 151318 13145 INFO dfs.DataNode$PacketResponder: Received block blk_7563971601695995553 of size 67108864 from /10.251.91.32
[E26] 081110 151318 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.5.161:50010 is added to blk_7563971601695995553 size 67108864
[E26] 081110 151318 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.6.214:50010 is added to blk_7563971601695995553 size 67108864
[E26] 081110 151318 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.91.32:50010 is added to blk_7563971601695995553 size 67108864
[E23] 081110 210124 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_7563971601695995553 is added to invalidSet of 10.250.5.161:50010
[E23] 081110 210124 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_7563971601695995553 is added to invalidSet of 10.250.6.214:50010
[E23] 081110 210124 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_7563971601695995553 is added to invalidSet of 10.251.91.32:50010
[E21] 081110 210141 19 INFO dfs.FSDataset: Deleting block blk_7563971601695995553 file /mnt/hadoop/dfs/data/current/subdir25/blk_7563971601695995553
[E21] 081110 210623 19 INFO dfs.FSDataset: Deleting block blk_7563971601695995553 file /mnt/hadoop/dfs/data/current/subdir44/blk_7563971601695995553
[E20] 081110 210633 19 WARN dfs.FSDataset: Unexpected error trying to delete block blk_7563971601695995553. BlockInfo not found in volumeMap.
[E21] 081110 211057 19 INFO dfs.FSDataset: Deleting block blk_7563971601695995553 file /mnt/hadoop/dfs/data/current/subdir59/blk_7563971601695995553
```

### Résumé proposé

La trace contient des opérations HDFS sur le bloc, notamment : erreur de suppression : BlockInfo absent de volumeMap. Les autres opérations sont détaillées dans les faits observés.

### Faits observés

- E5 : 3 occurrence(s) — début de réception.
- E22 : 1 occurrence(s) — allocation du bloc.
- E11 : 3 occurrence(s) — fin d'un PacketResponder.
- E9 : 3 occurrence(s) — confirmation de réception.
- E26 : 3 occurrence(s) — enregistrement du bloc.
- E23 : 3 occurrence(s) — ajout aux ensembles d'invalidation.
- E21 : 3 occurrence(s) — suppression locale journalisée.
- E20 : 1 occurrence(s) — erreur de suppression : BlockInfo absent de volumeMap.

### Hypothèses


### Informations manquantes

- Cause de l'absence de BlockInfo dans volumeMap.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0061 — blk_-4450005625926126372

**Label officiel :** 1

**Abstention proposée :** True

### Trace originale

```text
[E5] 081111 074604 23457 INFO dfs.DataNode$DataXceiver: Receiving block blk_-4450005625926126372 src: /10.251.30.134:45829 dest: /10.251.30.134:50010
[E22] 081111 074604 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand6/_temporary/_task_200811101024_0013_m_001671_0/part-01671. blk_-4450005625926126372
```

### Résumé proposé

Une allocation du bloc HDFS et un début de réception sont journalisés. La trace ne contient aucune confirmation de réception, ni message d'erreur explicite. L'issue de l'opération ne peut pas être déterminée.

### Faits observés

- E22 : une allocation du bloc est journalisée.
- E5 : un début de réception du bloc est journalisé.
- Aucun événement E9 de confirmation de réception n'apparaît dans la trace.
- Aucun message d'erreur explicite n'apparaît dans la trace.

### Hypothèses


### Informations manquantes

- Résultat final de la réception du bloc.
- Éventuels événements ultérieurs de confirmation ou d'échec.
- Contexte permettant d'expliquer l'absence de suite dans la trace.

### Sources C6 candidates

hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0062 — blk_-3646517331515187756

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E22] 081110 014726 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/randtxt/_temporary/_task_200811092030_0003_m_001360_0/part-01360. blk_-3646517331515187756
[E5] 081110 014726 6026 INFO dfs.DataNode$DataXceiver: Receiving block blk_-3646517331515187756 src: /10.250.5.237:55563 dest: /10.250.5.237:50010
[E5] 081110 014727 5845 INFO dfs.DataNode$DataXceiver: Receiving block blk_-3646517331515187756 src: /10.250.5.237:36726 dest: /10.250.5.237:50010
[E5] 081110 014727 5893 INFO dfs.DataNode$DataXceiver: Receiving block blk_-3646517331515187756 src: /10.251.214.67:34555 dest: /10.251.214.67:50010
[E26] 081110 014800 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.5.237:50010 is added to blk_-3646517331515187756 size 28491064
[E26] 081110 014800 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.11.85:50010 is added to blk_-3646517331515187756 size 28491064
[E11] 081110 014800 5849 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-3646517331515187756 terminating
[E9] 081110 014800 5849 INFO dfs.DataNode$PacketResponder: Received block blk_-3646517331515187756 of size 28491064 from /10.250.5.237
[E11] 081110 014800 5894 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-3646517331515187756 terminating
[E9] 081110 014800 5894 INFO dfs.DataNode$PacketResponder: Received block blk_-3646517331515187756 of size 28491064 from /10.251.214.67
[E11] 081110 014800 6027 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-3646517331515187756 terminating
[E9] 081110 014800 6027 INFO dfs.DataNode$PacketResponder: Received block blk_-3646517331515187756 of size 28491064 from /10.250.5.237
[E25] 081110 014802 19 INFO dfs.FSNamesystem: BLOCK* ask 10.250.11.85:50010 to replicate blk_-3646517331515187756 to datanode(s) 10.251.202.134:50010
[E26] 081110 014802 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.214.67:50010 is added to blk_-3646517331515187756 size 28491064
[E18] 081110 014804 19 INFO dfs.DataNode: 10.250.11.85:50010 Starting thread to transfer block blk_-3646517331515187756 to 10.251.202.134:50010
[E5] 081110 014804 5515 INFO dfs.DataNode$DataXceiver: Receiving block blk_-3646517331515187756 src: /10.250.11.85:54083 dest: /10.250.11.85:50010
[E26] 081110 014811 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.202.134:50010 is added to blk_-3646517331515187756 size 28491064
[E6] 081110 014811 5515 INFO dfs.DataNode$DataXceiver: Received block blk_-3646517331515187756 src: /10.250.11.85:54083 dest: /10.250.11.85:50010 of size 28491064
[E16] 081110 014811 5907 INFO dfs.DataNode$DataTransfer: 10.250.11.85:50010:Transmitted block blk_-3646517331515187756 to /10.251.202.134:50010
[E21] 081110 014815 19 INFO dfs.FSDataset: Deleting block blk_-3646517331515187756 file /mnt/hadoop/dfs/data/current/subdir24/blk_-3646517331515187756
[E4] 081110 045639 6904 WARN dfs.DataNode$DataXceiver: 10.250.11.85:50010:Got exception while serving blk_-3646517331515187756 to /10.251.214.32:
[E3] 081110 061758 7249 INFO dfs.DataNode$DataXceiver: 10.250.11.85:50010 Served block blk_-3646517331515187756 to /10.250.11.85
[E4] 081110 071554 7710 WARN dfs.DataNode$DataXceiver: 10.250.11.85:50010:Got exception while serving blk_-3646517331515187756 to /10.251.214.32:
[E3] 081110 072552 7914 INFO dfs.DataNode$DataXceiver: 10.250.11.85:50010 Served block blk_-3646517331515187756 to /10.250.11.85
[E4] 081110 082412 8001 WARN dfs.DataNode$DataXceiver: 10.251.202.134:50010:Got exception while serving blk_-3646517331515187756 to /10.251.35.1:
[E3] 081110 083359 8180 INFO dfs.DataNode$DataXceiver: 10.251.202.134:50010 Served block blk_-3646517331515187756 to /10.251.202.134
[E23] 081110 103042 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-3646517331515187756 is added to invalidSet of 10.250.11.85:50010
[E23] 081110 103042 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-3646517331515187756 is added to invalidSet of 10.251.202.134:50010
[E23] 081110 103042 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-3646517331515187756 is added to invalidSet of 10.251.214.67:50010
[E21] 081110 103110 19 INFO dfs.FSDataset: Deleting block blk_-3646517331515187756 file /mnt/hadoop/dfs/data/current/subdir8/blk_-3646517331515187756
[E21] 081110 103448 19 INFO dfs.FSDataset: Deleting block blk_-3646517331515187756 file /mnt/hadoop/dfs/data/current/subdir16/blk_-3646517331515187756
[E21] 081110 103719 19 INFO dfs.FSDataset: Deleting block blk_-3646517331515187756 file /mnt/hadoop/dfs/data/current/subdir9/blk_-3646517331515187756
```

### Résumé proposé

La trace contient des opérations HDFS sur le bloc, notamment : exception signalée pendant le service du bloc. Les autres opérations sont détaillées dans les faits observés.

### Faits observés

- E22 : 1 occurrence(s) — allocation du bloc.
- E5 : 4 occurrence(s) — début de réception.
- E26 : 4 occurrence(s) — enregistrement du bloc.
- E11 : 3 occurrence(s) — fin d'un PacketResponder.
- E9 : 3 occurrence(s) — confirmation de réception.
- E25 : 1 occurrence(s) — demande de réplication.
- E18 : 1 occurrence(s) — démarrage d'un transfert.
- E6 : 1 occurrence(s) — réception du bloc transféré.
- E16 : 1 occurrence(s) — transmission du bloc.
- E21 : 4 occurrence(s) — suppression locale journalisée.
- E4 : 3 occurrence(s) — exception signalée pendant le service du bloc.
- E3 : 3 occurrence(s) — service du bloc à un client.
- E23 : 3 occurrence(s) — ajout aux ensembles d'invalidation.

### Hypothèses


### Informations manquantes

- Nature et cause des exceptions pendant le service.

### Sources C6 candidates

hdfs-architecture-1.2.1#data-replication#1;hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0063 — blk_5964358685159409651

**Label officiel :** 1

**Abstention proposée :** True

### Trace originale

```text
[E5] 081109 212852 2168 INFO dfs.DataNode$DataXceiver: Receiving block blk_5964358685159409651 src: /10.251.214.130:55622 dest: /10.251.214.130:50010
[E22] 081109 212852 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand/_temporary/_task_200811092030_0001_m_002006_0/part-02006. blk_5964358685159409651
```

### Résumé proposé

Une allocation du bloc HDFS et un début de réception sont journalisés. La trace ne contient aucune confirmation de réception, ni message d'erreur explicite. L'issue de l'opération ne peut pas être déterminée.

### Faits observés

- E22 : une allocation du bloc est journalisée.
- E5 : un début de réception du bloc est journalisé.
- Aucun événement E9 de confirmation de réception n'apparaît dans la trace.
- Aucun message d'erreur explicite n'apparaît dans la trace.

### Hypothèses


### Informations manquantes

- Résultat final de la réception du bloc.
- Éventuels événements ultérieurs de confirmation ou d'échec.
- Contexte permettant d'expliquer l'absence de suite dans la trace.

### Sources C6 candidates

hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0064 — blk_6456148978944478207

**Label officiel :** 1

**Abstention proposée :** True

### Trace originale

```text
[E5] 081110 112651 10000 INFO dfs.DataNode$DataXceiver: Receiving block blk_6456148978944478207 src: /10.251.67.4:43618 dest: /10.251.67.4:50010
[E22] 081110 112651 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand/_temporary/_task_200811101024_0001_m_001618_0/part-01618. blk_6456148978944478207
```

### Résumé proposé

Une allocation du bloc HDFS et un début de réception sont journalisés. La trace ne contient aucune confirmation de réception, ni message d'erreur explicite. L'issue de l'opération ne peut pas être déterminée.

### Faits observés

- E22 : une allocation du bloc est journalisée.
- E5 : un début de réception du bloc est journalisé.
- Aucun événement E9 de confirmation de réception n'apparaît dans la trace.
- Aucun message d'erreur explicite n'apparaît dans la trace.

### Hypothèses


### Informations manquantes

- Résultat final de la réception du bloc.
- Éventuels événements ultérieurs de confirmation ou d'échec.
- Contexte permettant d'expliquer l'absence de suite dans la trace.

### Sources C6 candidates

hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0065 — blk_-8254791135193474574

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 072634 23103 INFO dfs.DataNode$DataXceiver: Receiving block blk_-8254791135193474574 src: /10.251.39.64:52439 dest: /10.251.39.64:50010
[E22] 081111 072634 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand6/_temporary/_task_200811101024_0013_m_001271_0/part-01271. blk_-8254791135193474574
[E5] 081111 072638 22722 INFO dfs.DataNode$DataXceiver: Receiving block blk_-8254791135193474574 src: /10.251.39.64:57520 dest: /10.251.39.64:50010
[E5] 081111 072638 23157 INFO dfs.DataNode$DataXceiver: Receiving block blk_-8254791135193474574 src: /10.251.126.255:36690 dest: /10.251.126.255:50010
[E11] 081111 072716 22723 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-8254791135193474574 terminating
[E9] 081111 072716 22723 INFO dfs.DataNode$PacketResponder: Received block blk_-8254791135193474574 of size 67108864 from /10.251.39.64
[E11] 081111 072716 23104 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-8254791135193474574 terminating
[E9] 081111 072716 23104 INFO dfs.DataNode$PacketResponder: Received block blk_-8254791135193474574 of size 67108864 from /10.251.39.64
[E11] 081111 072716 23158 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-8254791135193474574 terminating
[E9] 081111 072716 23158 INFO dfs.DataNode$PacketResponder: Received block blk_-8254791135193474574 of size 67108864 from /10.251.126.255
[E26] 081111 072716 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.194.147:50010 is added to blk_-8254791135193474574 size 67108864
[E26] 081111 072716 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.126.255:50010 is added to blk_-8254791135193474574 size 67108864
[E26] 081111 072718 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.39.64:50010 is added to blk_-8254791135193474574 size 67108864
[E27] 081111 072718 28 WARN dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: Redundant addStoredBlock request received for blk_-8254791135193474574 on 10.251.39.64:50010 size 67108864
[E23] 081111 085920 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-8254791135193474574 is added to invalidSet of 10.251.126.255:50010
[E23] 081111 085920 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-8254791135193474574 is added to invalidSet of 10.251.194.147:50010
[E23] 081111 085920 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-8254791135193474574 is added to invalidSet of 10.251.39.64:50010
[E21] 081111 090004 18 INFO dfs.FSDataset: Deleting block blk_-8254791135193474574 file /mnt/hadoop/dfs/data/current/subdir55/blk_-8254791135193474574
[E21] 081111 090014 19 INFO dfs.FSDataset: Deleting block blk_-8254791135193474574 file /mnt/hadoop/dfs/data/current/subdir34/blk_-8254791135193474574
[E21] 081111 090023 19 INFO dfs.FSDataset: Deleting block blk_-8254791135193474574 file /mnt/hadoop/dfs/data/current/subdir47/blk_-8254791135193474574
```

### Résumé proposé

La trace contient des opérations HDFS sur le bloc, notamment : requête addStoredBlock redondante. Les autres opérations sont détaillées dans les faits observés.

### Faits observés

- E5 : 3 occurrence(s) — début de réception.
- E22 : 1 occurrence(s) — allocation du bloc.
- E11 : 3 occurrence(s) — fin d'un PacketResponder.
- E9 : 3 occurrence(s) — confirmation de réception.
- E26 : 3 occurrence(s) — enregistrement du bloc.
- E27 : 1 occurrence(s) — requête addStoredBlock redondante.
- E23 : 3 occurrence(s) — ajout aux ensembles d'invalidation.
- E21 : 3 occurrence(s) — suppression locale journalisée.

### Hypothèses


### Informations manquantes

- Cause de la requête addStoredBlock redondante.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0066 — blk_6994139817440918018

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 104239 26763 INFO dfs.DataNode$DataXceiver: Receiving block blk_6994139817440918018 src: /10.251.106.50:58243 dest: /10.251.106.50:50010
[E5] 081111 104239 26885 INFO dfs.DataNode$DataXceiver: Receiving block blk_6994139817440918018 src: /10.251.106.50:36268 dest: /10.251.106.50:50010
[E22] 081111 104239 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/randtxt9/_temporary/_task_200811101024_0016_m_001539_0/part-01539. blk_6994139817440918018
[E7] 081111 104243 26885 INFO dfs.DataNode$DataXceiver: writeBlock blk_6994139817440918018 received exception java.io.IOException: Could not read from stream
```

### Résumé proposé

Deux débuts de réception et une allocation du bloc HDFS sont journalisés. Une exception java.io.IOException indiquant Could not read from stream est ensuite signalée pendant writeBlock. La trace ne contient aucune confirmation de réception et ne permet pas d'identifier la cause initiale de l'exception.

### Faits observés

- E5 : deux débuts de réception du bloc sont journalisés.
- E22 : une allocation du bloc est journalisée.
- E7 : writeBlock signale java.io.IOException: Could not read from stream.
- Aucun événement E9 de confirmation de réception n'apparaît dans la trace.

### Hypothèses


### Informations manquantes

- Cause initiale de l'exception de lecture du flux.
- État final du transfert et du bloc.
- Éventuelles tentatives ultérieures.

### Sources C6 candidates

hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0067 — blk_612453853187326054

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 094617 25605 INFO dfs.DataNode$DataXceiver: Receiving block blk_612453853187326054 src: /10.250.14.196:42546 dest: /10.250.14.196:50010
[E5] 081111 094617 25846 INFO dfs.DataNode$DataXceiver: Receiving block blk_612453853187326054 src: /10.250.14.196:40901 dest: /10.250.14.196:50010
[E22] 081111 094617 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand8/_temporary/_task_200811101024_0015_m_001768_0/part-01768. blk_612453853187326054
[E7] 081111 094621 25846 INFO dfs.DataNode$DataXceiver: writeBlock blk_612453853187326054 received exception java.io.IOException: Could not read from stream
```

### Résumé proposé

Deux débuts de réception et une allocation du bloc HDFS sont journalisés. Une exception java.io.IOException indiquant Could not read from stream est ensuite signalée pendant writeBlock. La trace ne contient aucune confirmation de réception et ne permet pas d'identifier la cause initiale de l'exception.

### Faits observés

- E5 : deux débuts de réception du bloc sont journalisés.
- E22 : une allocation du bloc est journalisée.
- E7 : writeBlock signale java.io.IOException: Could not read from stream.
- Aucun événement E9 de confirmation de réception n'apparaît dans la trace.

### Hypothèses


### Informations manquantes

- Cause initiale de l'exception de lecture du flux.
- État final du transfert et du bloc.
- Éventuelles tentatives ultérieures.

### Sources C6 candidates

hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0068 — blk_-141157622640736106

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 053223 19423 INFO dfs.DataNode$DataXceiver: Receiving block blk_-141157622640736106 src: /10.251.107.50:60994 dest: /10.251.107.50:50010
[E5] 081111 053223 21228 INFO dfs.DataNode$DataXceiver: Receiving block blk_-141157622640736106 src: /10.251.107.50:40349 dest: /10.251.107.50:50010
[E22] 081111 053223 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand5/_temporary/_task_200811101024_0011_m_001530_0/part-01530. blk_-141157622640736106
[E5] 081111 053224 21636 INFO dfs.DataNode$DataXceiver: Receiving block blk_-141157622640736106 src: /10.251.31.5:57075 dest: /10.251.31.5:50010
[E11] 081111 053313 19427 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-141157622640736106 terminating
[E9] 081111 053313 19427 INFO dfs.DataNode$PacketResponder: Received block blk_-141157622640736106 of size 67108864 from /10.251.107.50
[E11] 081111 053313 21229 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-141157622640736106 terminating
[E9] 081111 053313 21229 INFO dfs.DataNode$PacketResponder: Received block blk_-141157622640736106 of size 67108864 from /10.251.107.50
[E11] 081111 053313 21637 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-141157622640736106 terminating
[E9] 081111 053313 21637 INFO dfs.DataNode$PacketResponder: Received block blk_-141157622640736106 of size 67108864 from /10.251.31.5
[E26] 081111 053313 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.11.194:50010 is added to blk_-141157622640736106 size 67108864
[E26] 081111 053313 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.107.50:50010 is added to blk_-141157622640736106 size 67108864
[E26] 081111 053313 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.31.5:50010 is added to blk_-141157622640736106 size 67108864
[E25] 081111 070439 19 INFO dfs.FSNamesystem: BLOCK* ask 10.251.31.5:50010 to replicate blk_-141157622640736106 to datanode(s) 10.250.10.100:50010
[E18] 081111 070512 19 INFO dfs.DataNode: 10.251.31.5:50010 Starting thread to transfer block blk_-141157622640736106 to 10.250.10.100:50010
[E5] 081111 070512 22666 INFO dfs.DataNode$DataXceiver: Receiving block blk_-141157622640736106 src: /10.251.31.5:52234 dest: /10.251.31.5:50010
[E6] 081111 070553 22666 INFO dfs.DataNode$DataXceiver: Received block blk_-141157622640736106 src: /10.251.31.5:52234 dest: /10.251.31.5:50010 of size 67108864
[E16] 081111 070553 22910 INFO dfs.DataNode$DataTransfer: 10.251.31.5:50010:Transmitted block blk_-141157622640736106 to /10.250.10.100:50010
[E26] 081111 070553 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.10.100:50010 is added to blk_-141157622640736106 size 67108864
[E26] 081111 072344 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.107.50:50010 is added to blk_-141157622640736106 size 67108864
[E21] 081111 072400 19 INFO dfs.FSDataset: Deleting block blk_-141157622640736106 file /mnt/hadoop/dfs/data/current/subdir38/blk_-141157622640736106
[E23] 081111 075634 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-141157622640736106 is added to invalidSet of 10.250.10.100:50010
[E23] 081111 075634 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-141157622640736106 is added to invalidSet of 10.251.107.50:50010
[E23] 081111 075634 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-141157622640736106 is added to invalidSet of 10.251.31.5:50010
[E21] 081111 075843 19 INFO dfs.FSDataset: Deleting block blk_-141157622640736106 file /mnt/hadoop/dfs/data/current/subdir5/blk_-141157622640736106
[E21] 081111 075907 19 INFO dfs.FSDataset: Deleting block blk_-141157622640736106 file /mnt/hadoop/dfs/data/current/subdir32/blk_-141157622640736106
[E21] 081111 075926 19 INFO dfs.FSDataset: Deleting block blk_-141157622640736106 file /mnt/hadoop/dfs/data/current/subdir21/blk_-141157622640736106
```

### Résumé proposé

La trace contient des opérations d'allocation, de réception, d'enregistrement ou de réplication du bloc. Les événements observés ne permettent pas, à eux seuls, d'établir la cause du label d'anomalie.

### Faits observés

- E5 : 4 occurrence(s) — début de réception.
- E22 : 1 occurrence(s) — allocation du bloc.
- E11 : 3 occurrence(s) — fin d'un PacketResponder.
- E9 : 3 occurrence(s) — confirmation de réception.
- E26 : 5 occurrence(s) — enregistrement du bloc.
- E25 : 1 occurrence(s) — demande de réplication.
- E18 : 1 occurrence(s) — démarrage d'un transfert.
- E6 : 1 occurrence(s) — réception du bloc transféré.
- E16 : 1 occurrence(s) — transmission du bloc.
- E21 : 4 occurrence(s) — suppression locale journalisée.
- E23 : 3 occurrence(s) — ajout aux ensembles d'invalidation.

### Hypothèses


### Informations manquantes

- Éléments permettant d'expliquer le label d'anomalie.

### Sources C6 candidates

hdfs-architecture-1.2.1#data-replication#1;hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0069 — blk_224524725647401101

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 070717 17744 INFO dfs.DataNode$DataXceiver: Receiving block blk_224524725647401101 src: /10.251.39.160:44182 dest: /10.251.39.160:50010
[E5] 081111 070717 22890 INFO dfs.DataNode$DataXceiver: Receiving block blk_224524725647401101 src: /10.251.39.160:51929 dest: /10.251.39.160:50010
[E22] 081111 070717 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand6/_temporary/_task_200811101024_0013_m_000280_0/part-00280. blk_224524725647401101
[E5] 081111 070718 23055 INFO dfs.DataNode$DataXceiver: Receiving block blk_224524725647401101 src: /10.251.214.67:51163 dest: /10.251.214.67:50010
[E11] 081111 070740 17745 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_224524725647401101 terminating
[E9] 081111 070740 17745 INFO dfs.DataNode$PacketResponder: Received block blk_224524725647401101 of size 67108864 from /10.251.39.160
[E11] 081111 070740 22891 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_224524725647401101 terminating
[E9] 081111 070740 22891 INFO dfs.DataNode$PacketResponder: Received block blk_224524725647401101 of size 67108864 from /10.251.39.160
[E11] 081111 070740 23056 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_224524725647401101 terminating
[E9] 081111 070740 23056 INFO dfs.DataNode$PacketResponder: Received block blk_224524725647401101 of size 67108864 from /10.251.214.67
[E26] 081111 070740 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.214.67:50010 is added to blk_224524725647401101 size 67108864
[E26] 081111 070740 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.75.79:50010 is added to blk_224524725647401101 size 67108864
[E26] 081111 070823 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.39.160:50010 is added to blk_224524725647401101 size 67108864
[E25] 081111 081001 19 INFO dfs.FSNamesystem: BLOCK* ask 10.251.214.67:50010 to replicate blk_224524725647401101 to datanode(s) 10.251.197.226:50010
[E18] 081111 081057 19 INFO dfs.DataNode: 10.251.214.67:50010 Starting thread to transfer block blk_224524725647401101 to 10.251.197.226:50010
[E5] 081111 081059 24319 INFO dfs.DataNode$DataXceiver: Receiving block blk_224524725647401101 src: /10.251.214.67:36449 dest: /10.251.214.67:50010
[E16] 081111 081151 24107 INFO dfs.DataNode$DataTransfer: 10.251.214.67:50010:Transmitted block blk_224524725647401101 to /10.251.197.226:50010
[E6] 081111 081151 24319 INFO dfs.DataNode$DataXceiver: Received block blk_224524725647401101 src: /10.251.214.67:36449 dest: /10.251.214.67:50010 of size 67108864
[E26] 081111 081152 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.197.226:50010 is added to blk_224524725647401101 size 67108864
[E26] 081111 081403 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.39.160:50010 is added to blk_224524725647401101 size 67108864
[E21] 081111 081416 19 INFO dfs.FSDataset: Deleting block blk_224524725647401101 file /mnt/hadoop/dfs/data/current/subdir36/blk_224524725647401101
[E23] 081111 085909 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_224524725647401101 is added to invalidSet of 10.251.197.226:50010
[E23] 081111 085909 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_224524725647401101 is added to invalidSet of 10.251.214.67:50010
[E23] 081111 085909 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_224524725647401101 is added to invalidSet of 10.251.39.160:50010
[E21] 081111 090117 19 INFO dfs.FSDataset: Deleting block blk_224524725647401101 file /mnt/hadoop/dfs/data/current/subdir17/blk_224524725647401101
[E21] 081111 090126 19 INFO dfs.FSDataset: Deleting block blk_224524725647401101 file /mnt/hadoop/dfs/data/current/subdir47/blk_224524725647401101
[E21] 081111 091618 19 INFO dfs.FSDataset: Deleting block blk_224524725647401101 file /mnt/hadoop/dfs/data/current/subdir41/blk_224524725647401101
```

### Résumé proposé

La trace contient des opérations d'allocation, de réception, d'enregistrement ou de réplication du bloc. Les événements observés ne permettent pas, à eux seuls, d'établir la cause du label d'anomalie.

### Faits observés

- E5 : 4 occurrence(s) — début de réception.
- E22 : 1 occurrence(s) — allocation du bloc.
- E11 : 3 occurrence(s) — fin d'un PacketResponder.
- E9 : 3 occurrence(s) — confirmation de réception.
- E26 : 5 occurrence(s) — enregistrement du bloc.
- E25 : 1 occurrence(s) — demande de réplication.
- E18 : 1 occurrence(s) — démarrage d'un transfert.
- E16 : 1 occurrence(s) — transmission du bloc.
- E6 : 1 occurrence(s) — réception du bloc transféré.
- E21 : 4 occurrence(s) — suppression locale journalisée.
- E23 : 3 occurrence(s) — ajout aux ensembles d'invalidation.

### Hypothèses


### Informations manquantes

- Éléments permettant d'expliquer le label d'anomalie.

### Sources C6 candidates

hdfs-architecture-1.2.1#data-replication#1;hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0070 — blk_8859444356326017799

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 030501 18214 INFO dfs.DataNode$DataXceiver: Receiving block blk_8859444356326017799 src: /10.250.14.196:54044 dest: /10.250.14.196:50010
[E5] 081111 030501 18363 INFO dfs.DataNode$DataXceiver: Receiving block blk_8859444356326017799 src: /10.250.14.196:36095 dest: /10.250.14.196:50010
[E5] 081111 030501 18422 INFO dfs.DataNode$DataXceiver: Receiving block blk_8859444356326017799 src: /10.250.10.213:37210 dest: /10.250.10.213:50010
[E22] 081111 030501 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand4/_temporary/_task_200811101024_0009_m_001202_0/part-01202. blk_8859444356326017799
[E11] 081111 030542 18215 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_8859444356326017799 terminating
[E9] 081111 030542 18215 INFO dfs.DataNode$PacketResponder: Received block blk_8859444356326017799 of size 67108864 from /10.250.14.196
[E11] 081111 030542 18364 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_8859444356326017799 terminating
[E9] 081111 030542 18364 INFO dfs.DataNode$PacketResponder: Received block blk_8859444356326017799 of size 67108864 from /10.250.14.196
[E11] 081111 030542 18423 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_8859444356326017799 terminating
[E9] 081111 030542 18423 INFO dfs.DataNode$PacketResponder: Received block blk_8859444356326017799 of size 67108864 from /10.250.10.213
[E26] 081111 030542 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.75.79:50010 is added to blk_8859444356326017799 size 67108864
[E26] 081111 030542 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.10.213:50010 is added to blk_8859444356326017799 size 67108864
[E26] 081111 030542 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.14.196:50010 is added to blk_8859444356326017799 size 67108864
[E23] 081111 044316 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_8859444356326017799 is added to invalidSet of 10.250.10.213:50010
[E23] 081111 044316 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_8859444356326017799 is added to invalidSet of 10.250.14.196:50010
[E23] 081111 044316 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_8859444356326017799 is added to invalidSet of 10.251.75.79:50010
[E21] 081111 044355 19 INFO dfs.FSDataset: Deleting block blk_8859444356326017799 file /mnt/hadoop/dfs/data/current/subdir25/blk_8859444356326017799
[E21] 081111 044753 19 INFO dfs.FSDataset: Deleting block blk_8859444356326017799 file /mnt/hadoop/dfs/data/current/subdir6/blk_8859444356326017799
[E20] 081111 044821 19 WARN dfs.FSDataset: Unexpected error trying to delete block blk_8859444356326017799. BlockInfo not found in volumeMap.
[E21] 081111 044851 19 INFO dfs.FSDataset: Deleting block blk_8859444356326017799 file /mnt/hadoop/dfs/data/current/subdir7/blk_8859444356326017799
```

### Résumé proposé

La trace contient des opérations HDFS sur le bloc, notamment : erreur de suppression : BlockInfo absent de volumeMap. Les autres opérations sont détaillées dans les faits observés.

### Faits observés

- E5 : 3 occurrence(s) — début de réception.
- E22 : 1 occurrence(s) — allocation du bloc.
- E11 : 3 occurrence(s) — fin d'un PacketResponder.
- E9 : 3 occurrence(s) — confirmation de réception.
- E26 : 3 occurrence(s) — enregistrement du bloc.
- E23 : 3 occurrence(s) — ajout aux ensembles d'invalidation.
- E21 : 3 occurrence(s) — suppression locale journalisée.
- E20 : 1 occurrence(s) — erreur de suppression : BlockInfo absent de volumeMap.

### Hypothèses


### Informations manquantes

- Cause de l'absence de BlockInfo dans volumeMap.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0071 — blk_-915200491894200388

**Label officiel :** 1

**Abstention proposée :** True

### Trace originale

```text
[E22] 081109 235843 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/sortrand/_temporary/_task_200811092030_0002_r_000010_0/part-00010. blk_-915200491894200388
[E5] 081109 235843 4546 INFO dfs.DataNode$DataXceiver: Receiving block blk_-915200491894200388 src: /10.250.11.100:55200 dest: /10.250.11.100:50010
```

### Résumé proposé

Une allocation du bloc HDFS et un début de réception sont journalisés. La trace ne contient aucune confirmation de réception, ni message d'erreur explicite. L'issue de l'opération ne peut pas être déterminée.

### Faits observés

- E22 : une allocation du bloc est journalisée.
- E5 : un début de réception du bloc est journalisé.
- Aucun événement E9 de confirmation de réception n'apparaît dans la trace.
- Aucun message d'erreur explicite n'apparaît dans la trace.

### Hypothèses


### Informations manquantes

- Résultat final de la réception du bloc.
- Éventuels événements ultérieurs de confirmation ou d'échec.
- Contexte permettant d'expliquer l'absence de suite dans la trace.

### Sources C6 candidates

hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0072 — blk_1836315969441717271

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E22] 081111 105734 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/randtxt9/_temporary/_task_200811101024_0016_m_001805_0/part-01805. blk_1836315969441717271
[E5] 081111 105735 27364 INFO dfs.DataNode$DataXceiver: Receiving block blk_1836315969441717271 src: /10.251.126.83:43200 dest: /10.251.126.83:50010
[E5] 081111 105735 27542 INFO dfs.DataNode$DataXceiver: Receiving block blk_1836315969441717271 src: /10.251.126.83:39024 dest: /10.251.126.83:50010
[E7] 081111 105738 27542 INFO dfs.DataNode$DataXceiver: writeBlock blk_1836315969441717271 received exception java.io.IOException: Could not read from stream
```

### Résumé proposé

Deux débuts de réception et une allocation du bloc HDFS sont journalisés. Une exception java.io.IOException indiquant Could not read from stream est ensuite signalée pendant writeBlock. La trace ne contient aucune confirmation de réception et ne permet pas d'identifier la cause initiale de l'exception.

### Faits observés

- E5 : deux débuts de réception du bloc sont journalisés.
- E22 : une allocation du bloc est journalisée.
- E7 : writeBlock signale java.io.IOException: Could not read from stream.
- Aucun événement E9 de confirmation de réception n'apparaît dans la trace.

### Hypothèses


### Informations manquantes

- Cause initiale de l'exception de lecture du flux.
- État final du transfert et du bloc.
- Éventuelles tentatives ultérieures.

### Sources C6 candidates

hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0073 — blk_8817374089832812292

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E22] 081109 211549 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand/_temporary/_task_200811092030_0001_m_001540_0/part-01540. blk_8817374089832812292
[E5] 081109 211550 1690 INFO dfs.DataNode$DataXceiver: Receiving block blk_8817374089832812292 src: /10.251.39.209:35101 dest: /10.251.39.209:50010
[E5] 081109 211551 1676 INFO dfs.DataNode$DataXceiver: Receiving block blk_8817374089832812292 src: /10.251.39.209:50754 dest: /10.251.39.209:50010
[E5] 081109 211552 1660 INFO dfs.DataNode$DataXceiver: Receiving block blk_8817374089832812292 src: /10.251.127.47:34539 dest: /10.251.127.47:50010
[E11] 081109 211646 1661 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_8817374089832812292 terminating
[E9] 081109 211646 1661 INFO dfs.DataNode$PacketResponder: Received block blk_8817374089832812292 of size 67108864 from /10.251.127.47
[E11] 081109 211646 1677 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_8817374089832812292 terminating
[E9] 081109 211646 1677 INFO dfs.DataNode$PacketResponder: Received block blk_8817374089832812292 of size 67108864 from /10.251.39.209
[E11] 081109 211646 1691 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_8817374089832812292 terminating
[E9] 081109 211646 1691 INFO dfs.DataNode$PacketResponder: Received block blk_8817374089832812292 of size 67108864 from /10.251.39.209
[E26] 081109 211646 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.6.223:50010 is added to blk_8817374089832812292 size 67108864
[E26] 081109 211646 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.39.209:50010 is added to blk_8817374089832812292 size 67108864
[E26] 081109 211647 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.127.47:50010 is added to blk_8817374089832812292 size 67108864
[E4] 081109 223515 3602 WARN dfs.DataNode$DataXceiver: 10.250.6.223:50010:Got exception while serving blk_8817374089832812292 to /10.251.67.4:
[E4] 081109 223542 3594 WARN dfs.DataNode$DataXceiver: 10.251.127.47:50010:Got exception while serving blk_8817374089832812292 to /10.251.126.5:
[E3] 081109 223604 3603 INFO dfs.DataNode$DataXceiver: 10.250.6.223:50010 Served block blk_8817374089832812292 to /10.251.67.4
[E23] 081110 103114 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_8817374089832812292 is added to invalidSet of 10.250.6.223:50010
[E23] 081110 103114 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_8817374089832812292 is added to invalidSet of 10.251.127.47:50010
[E23] 081110 103114 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_8817374089832812292 is added to invalidSet of 10.251.39.209:50010
[E21] 081110 103228 18 INFO dfs.FSDataset: Deleting block blk_8817374089832812292 file /mnt/hadoop/dfs/data/current/subdir31/blk_8817374089832812292
[E21] 081110 103709 19 INFO dfs.FSDataset: Deleting block blk_8817374089832812292 file /mnt/hadoop/dfs/data/current/subdir11/blk_8817374089832812292
[E21] 081110 103726 19 INFO dfs.FSDataset: Deleting block blk_8817374089832812292 file /mnt/hadoop/dfs/data/current/subdir36/blk_8817374089832812292
[E20] 081110 103731 18 WARN dfs.FSDataset: Unexpected error trying to delete block blk_8817374089832812292. BlockInfo not found in volumeMap.
```

### Résumé proposé

La trace contient des opérations HDFS sur le bloc, notamment : exception signalée pendant le service du bloc; erreur de suppression : BlockInfo absent de volumeMap. Les autres opérations sont détaillées dans les faits observés.

### Faits observés

- E22 : 1 occurrence(s) — allocation du bloc.
- E5 : 3 occurrence(s) — début de réception.
- E11 : 3 occurrence(s) — fin d'un PacketResponder.
- E9 : 3 occurrence(s) — confirmation de réception.
- E26 : 3 occurrence(s) — enregistrement du bloc.
- E4 : 2 occurrence(s) — exception signalée pendant le service du bloc.
- E3 : 1 occurrence(s) — service du bloc à un client.
- E23 : 3 occurrence(s) — ajout aux ensembles d'invalidation.
- E21 : 3 occurrence(s) — suppression locale journalisée.
- E20 : 1 occurrence(s) — erreur de suppression : BlockInfo absent de volumeMap.

### Hypothèses


### Informations manquantes

- Nature et cause des exceptions pendant le service.
- Cause de l'absence de BlockInfo dans volumeMap.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0074 — blk_-7264616954252932491

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 081157 23933 INFO dfs.DataNode$DataXceiver: Receiving block blk_-7264616954252932491 src: /10.251.125.193:48788 dest: /10.251.125.193:50010
[E5] 081111 081157 23993 INFO dfs.DataNode$DataXceiver: Receiving block blk_-7264616954252932491 src: /10.251.125.193:42422 dest: /10.251.125.193:50010
[E22] 081111 081157 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand7/_temporary/_task_200811101024_0014_m_000780_0/part-00780. blk_-7264616954252932491
[E7] 081111 081200 23933 INFO dfs.DataNode$DataXceiver: writeBlock blk_-7264616954252932491 received exception java.io.IOException: Could not read from stream
```

### Résumé proposé

Deux débuts de réception et une allocation du bloc HDFS sont journalisés. Une exception java.io.IOException indiquant Could not read from stream est ensuite signalée pendant writeBlock. La trace ne contient aucune confirmation de réception et ne permet pas d'identifier la cause initiale de l'exception.

### Faits observés

- E5 : deux débuts de réception du bloc sont journalisés.
- E22 : une allocation du bloc est journalisée.
- E7 : writeBlock signale java.io.IOException: Could not read from stream.
- Aucun événement E9 de confirmation de réception n'apparaît dans la trace.

### Hypothèses


### Informations manquantes

- Cause initiale de l'exception de lecture du flux.
- État final du transfert et du bloc.
- Éventuelles tentatives ultérieures.

### Sources C6 candidates

hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0075 — blk_-1777743352508736546

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E22] 081110 013739 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/randtxt/_temporary/_task_200811092030_0003_m_001390_0/part-01390. blk_-1777743352508736546
[E5] 081110 013739 5702 INFO dfs.DataNode$DataXceiver: Receiving block blk_-1777743352508736546 src: /10.250.13.188:56918 dest: /10.250.13.188:50010
[E5] 081110 013739 5755 INFO dfs.DataNode$DataXceiver: Receiving block blk_-1777743352508736546 src: /10.250.13.188:55449 dest: /10.250.13.188:50010
[E7] 081110 013742 5702 INFO dfs.DataNode$DataXceiver: writeBlock blk_-1777743352508736546 received exception java.io.IOException: Could not read from stream
```

### Résumé proposé

Deux débuts de réception et une allocation du bloc HDFS sont journalisés. Une exception java.io.IOException indiquant Could not read from stream est ensuite signalée pendant writeBlock. La trace ne contient aucune confirmation de réception et ne permet pas d'identifier la cause initiale de l'exception.

### Faits observés

- E5 : deux débuts de réception du bloc sont journalisés.
- E22 : une allocation du bloc est journalisée.
- E7 : writeBlock signale java.io.IOException: Could not read from stream.
- Aucun événement E9 de confirmation de réception n'apparaît dans la trace.

### Hypothèses


### Informations manquantes

- Cause initiale de l'exception de lecture du flux.
- État final du transfert et du bloc.
- Éventuelles tentatives ultérieures.

### Sources C6 candidates

hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0076 — blk_-3817638410645019494

**Label officiel :** 1

**Abstention proposée :** True

### Trace originale

```text
[E22] 081109 235209 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/sortrand/_temporary/_task_200811092030_0002_r_000096_0/part-00096. blk_-3817638410645019494
[E5] 081109 235209 4362 INFO dfs.DataNode$DataXceiver: Receiving block blk_-3817638410645019494 src: /10.251.39.209:39653 dest: /10.251.39.209:50010
```

### Résumé proposé

Une allocation du bloc HDFS et un début de réception sont journalisés. La trace ne contient aucune confirmation de réception, ni message d'erreur explicite. L'issue de l'opération ne peut pas être déterminée.

### Faits observés

- E22 : une allocation du bloc est journalisée.
- E5 : un début de réception du bloc est journalisé.
- Aucun événement E9 de confirmation de réception n'apparaît dans la trace.
- Aucun message d'erreur explicite n'apparaît dans la trace.

### Hypothèses


### Informations manquantes

- Résultat final de la réception du bloc.
- Éventuels événements ultérieurs de confirmation ou d'échec.
- Contexte permettant d'expliquer l'absence de suite dans la trace.

### Sources C6 candidates

hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0077 — blk_-4346736380428326495

**Label officiel :** 1

**Abstention proposée :** True

### Trace originale

```text
[E22] 081110 121850 33 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/randtxt2/_temporary/_task_200811101024_0002_m_001300_0/part-01300. blk_-4346736380428326495
[E5] 081110 121851 11050 INFO dfs.DataNode$DataXceiver: Receiving block blk_-4346736380428326495 src: /10.251.39.179:50728 dest: /10.251.39.179:50010
```

### Résumé proposé

Une allocation du bloc HDFS et un début de réception sont journalisés. La trace ne contient aucune confirmation de réception, ni message d'erreur explicite. L'issue de l'opération ne peut pas être déterminée.

### Faits observés

- E22 : une allocation du bloc est journalisée.
- E5 : un début de réception du bloc est journalisé.
- Aucun événement E9 de confirmation de réception n'apparaît dans la trace.
- Aucun message d'erreur explicite n'apparaît dans la trace.

### Hypothèses


### Informations manquantes

- Résultat final de la réception du bloc.
- Éventuels événements ultérieurs de confirmation ou d'échec.
- Contexte permettant d'expliquer l'absence de suite dans la trace.

### Sources C6 candidates

hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0078 — blk_-5216731224772621734

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E22] 081110 001030 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/sortrand/_temporary/_task_200811092030_0002_r_000093_0/part-00093. blk_-5216731224772621734
[E5] 081110 001030 4249 INFO dfs.DataNode$DataXceiver: Receiving block blk_-5216731224772621734 src: /10.251.31.5:60118 dest: /10.251.31.5:50010
[E5] 081110 001030 4684 INFO dfs.DataNode$DataXceiver: Receiving block blk_-5216731224772621734 src: /10.251.106.10:42258 dest: /10.251.106.10:50010
[E5] 081110 001030 4874 INFO dfs.DataNode$DataXceiver: Receiving block blk_-5216731224772621734 src: /10.251.31.5:50285 dest: /10.251.31.5:50010
[E26] 081110 001049 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.106.10:50010 is added to blk_-5216731224772621734 size 67108864
[E26] 081110 001049 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.31.5:50010 is added to blk_-5216731224772621734 size 67108864
[E26] 081110 001049 34 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.203.80:50010 is added to blk_-5216731224772621734 size 67108864
[E11] 081110 001049 4250 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-5216731224772621734 terminating
[E9] 081110 001049 4250 INFO dfs.DataNode$PacketResponder: Received block blk_-5216731224772621734 of size 67108864 from /10.251.31.5
[E11] 081110 001049 4685 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-5216731224772621734 terminating
[E9] 081110 001049 4685 INFO dfs.DataNode$PacketResponder: Received block blk_-5216731224772621734 of size 67108864 from /10.251.106.10
[E11] 081110 001049 4875 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-5216731224772621734 terminating
[E9] 081110 001049 4875 INFO dfs.DataNode$PacketResponder: Received block blk_-5216731224772621734 of size 67108864 from /10.251.31.5
[E2] 081110 030944 13 INFO dfs.DataBlockScanner: Verification succeeded for blk_-5216731224772621734
[E23] 081110 103132 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-5216731224772621734 is added to invalidSet of 10.251.106.10:50010
[E23] 081110 103132 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-5216731224772621734 is added to invalidSet of 10.251.203.80:50010
[E23] 081110 103132 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-5216731224772621734 is added to invalidSet of 10.251.31.5:50010
[E21] 081110 103511 19 INFO dfs.FSDataset: Deleting block blk_-5216731224772621734 file /mnt/hadoop/dfs/data/current/subdir1/blk_-5216731224772621734
[E21] 081110 103543 19 INFO dfs.FSDataset: Deleting block blk_-5216731224772621734 file /mnt/hadoop/dfs/data/current/subdir29/blk_-5216731224772621734
[E28] 081110 104628 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: addStoredBlock request received for blk_-5216731224772621734 on 10.251.106.10:50010 size 67108864 But it does not belong to any file.
[E26] 081110 104628 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.106.10:50010 is added to blk_-5216731224772621734 size 67108864
[E21] 081110 104854 19 INFO dfs.FSDataset: Deleting block blk_-5216731224772621734 file /mnt/hadoop/dfs/data/current/subdir4/blk_-5216731224772621734
```

### Résumé proposé

Le bloc est alloué, reçu et enregistré sur trois DataNodes. Une vérification du bloc réussit. Le bloc est ensuite ajouté aux ensembles d'invalidation de trois DataNodes, et deux suppressions locales sont journalisées. Une nouvelle requête addStoredBlock arrive alors pour 10.251.106.10:50010 : le NameNode indique que le bloc n'appartient à aucun fichier. Un nouvel enregistrement E26 et une troisième suppression locale sont ensuite journalisés.

### Faits observés

- E22 et E5 : allocation et trois débuts de réception.
- E9 : trois confirmations de réception.
- E26 : trois enregistrements initiaux, puis un quatrième après E28.
- E2 : vérification du bloc réussie.
- E23 : trois ajouts aux ensembles d'invalidation.
- E21 : deux suppressions locales avant E28, puis une troisième après.
- E28 : addStoredBlock signale un bloc qui n'appartient à aucun fichier.

### Hypothèses


### Informations manquantes

- Cause de la notification addStoredBlock après l'invalidation.
- État exact des métadonnées du bloc au moment de E28.

### Sources C6 candidates

hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0079 — blk_-7356422865929660798

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 045612 18723 INFO dfs.DataNode$DataXceiver: Receiving block blk_-7356422865929660798 src: /10.250.15.67:38398 dest: /10.250.15.67:50010
[E5] 081111 045612 20057 INFO dfs.DataNode$DataXceiver: Receiving block blk_-7356422865929660798 src: /10.250.15.67:50376 dest: /10.250.15.67:50010
[E22] 081111 045612 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/rand5/_temporary/_task_200811101024_0011_m_000519_0/part-00519. blk_-7356422865929660798
[E5] 081111 045613 20452 INFO dfs.DataNode$DataXceiver: Receiving block blk_-7356422865929660798 src: /10.251.107.50:46291 dest: /10.251.107.50:50010
[E11] 081111 045655 18724 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-7356422865929660798 terminating
[E9] 081111 045655 18724 INFO dfs.DataNode$PacketResponder: Received block blk_-7356422865929660798 of size 67108864 from /10.250.15.67
[E11] 081111 045655 20058 INFO dfs.DataNode$PacketResponder: PacketResponder 2 for block blk_-7356422865929660798 terminating
[E9] 081111 045655 20058 INFO dfs.DataNode$PacketResponder: Received block blk_-7356422865929660798 of size 67108864 from /10.250.15.67
[E11] 081111 045655 20453 INFO dfs.DataNode$PacketResponder: PacketResponder 0 for block blk_-7356422865929660798 terminating
[E9] 081111 045655 20453 INFO dfs.DataNode$PacketResponder: Received block blk_-7356422865929660798 of size 67108864 from /10.251.107.50
[E26] 081111 045655 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.107.50:50010 is added to blk_-7356422865929660798 size 67108864
[E26] 081111 045655 30 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.15.67:50010 is added to blk_-7356422865929660798 size 67108864
[E26] 081111 045656 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.11.100:50010 is added to blk_-7356422865929660798 size 67108864
[E25] 081111 070436 19 INFO dfs.FSNamesystem: BLOCK* ask 10.250.11.100:50010 to replicate blk_-7356422865929660798 to datanode(s) 10.251.75.228:50010
[E18] 081111 070438 19 INFO dfs.DataNode: 10.250.11.100:50010 Starting thread to transfer block blk_-7356422865929660798 to 10.251.75.228:50010
[E5] 081111 070438 22366 INFO dfs.DataNode$DataXceiver: Receiving block blk_-7356422865929660798 src: /10.250.11.100:33594 dest: /10.250.11.100:50010
[E6] 081111 070516 22366 INFO dfs.DataNode$DataXceiver: Received block blk_-7356422865929660798 src: /10.250.11.100:33594 dest: /10.250.11.100:50010 of size 67108864
[E16] 081111 070516 22870 INFO dfs.DataNode$DataTransfer: 10.250.11.100:50010:Transmitted block blk_-7356422865929660798 to /10.251.75.228:50010
[E26] 081111 070516 31 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.75.228:50010 is added to blk_-7356422865929660798 size 67108864
[E26] 081111 072344 26 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.107.50:50010 is added to blk_-7356422865929660798 size 67108864
[E21] 081111 072348 19 INFO dfs.FSDataset: Deleting block blk_-7356422865929660798 file /mnt/hadoop/dfs/data/current/subdir23/blk_-7356422865929660798
[E23] 081111 075622 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-7356422865929660798 is added to invalidSet of 10.250.11.100:50010
[E23] 081111 075622 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-7356422865929660798 is added to invalidSet of 10.250.15.67:50010
[E23] 081111 075622 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-7356422865929660798 is added to invalidSet of 10.251.107.50:50010
[E23] 081111 075622 28 INFO dfs.FSNamesystem: BLOCK* NameSystem.delete: blk_-7356422865929660798 is added to invalidSet of 10.251.75.228:50010
[E21] 081111 075745 18 INFO dfs.FSDataset: Deleting block blk_-7356422865929660798 file /mnt/hadoop/dfs/data/current/subdir30/blk_-7356422865929660798
[E20] 081111 075752 19 WARN dfs.FSDataset: Unexpected error trying to delete block blk_-7356422865929660798. BlockInfo not found in volumeMap.
[E21] 081111 075832 19 INFO dfs.FSDataset: Deleting block blk_-7356422865929660798 file /mnt/hadoop/dfs/data/current/subdir16/blk_-7356422865929660798
[E21] 081111 075905 19 INFO dfs.FSDataset: Deleting block blk_-7356422865929660798 file /mnt/hadoop/dfs/data/current/subdir35/blk_-7356422865929660798
```

### Résumé proposé

La trace contient des opérations HDFS sur le bloc, notamment : erreur de suppression : BlockInfo absent de volumeMap. Les autres opérations sont détaillées dans les faits observés.

### Faits observés

- E5 : 4 occurrence(s) — début de réception.
- E22 : 1 occurrence(s) — allocation du bloc.
- E11 : 3 occurrence(s) — fin d'un PacketResponder.
- E9 : 3 occurrence(s) — confirmation de réception.
- E26 : 5 occurrence(s) — enregistrement du bloc.
- E25 : 1 occurrence(s) — demande de réplication.
- E18 : 1 occurrence(s) — démarrage d'un transfert.
- E6 : 1 occurrence(s) — réception du bloc transféré.
- E16 : 1 occurrence(s) — transmission du bloc.
- E21 : 4 occurrence(s) — suppression locale journalisée.
- E23 : 4 occurrence(s) — ajout aux ensembles d'invalidation.
- E20 : 1 occurrence(s) — erreur de suppression : BlockInfo absent de volumeMap.

### Hypothèses


### Informations manquantes

- Cause de l'absence de BlockInfo dans volumeMap.

### Sources C6 candidates

hdfs-architecture-1.2.1#data-replication#1;hdfs-architecture-1.2.1#file-deletes-and-undeletes#1;hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

## test-0080 — blk_-1965250832942158890

**Label officiel :** 1

**Abstention proposée :** False

### Trace originale

```text
[E5] 081111 102839 26524 INFO dfs.DataNode$DataXceiver: Receiving block blk_-1965250832942158890 src: /10.251.39.192:53426 dest: /10.251.39.192:50010
[E5] 081111 102839 26811 INFO dfs.DataNode$DataXceiver: Receiving block blk_-1965250832942158890 src: /10.251.39.192:43729 dest: /10.251.39.192:50010
[E22] 081111 102839 32 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /user/root/randtxt9/_temporary/_task_200811101024_0016_m_000926_0/part-00926. blk_-1965250832942158890
[E7] 081111 102842 26524 INFO dfs.DataNode$DataXceiver: writeBlock blk_-1965250832942158890 received exception java.io.IOException: Could not read from stream
```

### Résumé proposé

Deux débuts de réception et une allocation du bloc HDFS sont journalisés. Une exception java.io.IOException indiquant Could not read from stream est ensuite signalée pendant writeBlock. La trace ne contient aucune confirmation de réception et ne permet pas d'identifier la cause initiale de l'exception.

### Faits observés

- E5 : deux débuts de réception du bloc sont journalisés.
- E22 : une allocation du bloc est journalisée.
- E7 : writeBlock signale java.io.IOException: Could not read from stream.
- Aucun événement E9 de confirmation de réception n'apparaît dans la trace.

### Hypothèses


### Informations manquantes

- Cause initiale de l'exception de lecture du flux.
- État final du transfert et du bloc.
- Éventuelles tentatives ultérieures.

### Sources C6 candidates

hdfs-architecture-1.2.1#namenode-and-datanodes#1;hdfs-architecture-1.2.1#replication-pipelining#1

### Validation humaine

- [ ] Faits vérifiés dans les logs
- [ ] Résumé fidèle et chronologique
- [ ] Abstention justifiée
- [ ] Sources C6 vérifiées
- [ ] Relecture indépendante effectuée

---

