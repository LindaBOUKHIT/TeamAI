# Relecture du lot de Bachar · SCRUM-36

Sur les 60 blocs du lot (50 train, 10 val), cette révision intègre **19 réponses corrigées** pour la consigne v16 (17 train, 2 val). Les **41 autres réponses** sont reconduites. Les champs de relecture humaine sont encore ouverts. Le décompte historique de 60 relectures signées sur 240 porte sur le lot de Linda.

[Comparaison avant/après des 19 corrections](#comparaison-des-19-corrections) · [Cibles complètes de la PR #87](propositions_bachar.jsonl) · [Lot source avec les traces](lot_bachar.jsonl)

## Cas où l’issue de l’écriture est inconnue

Pour six blocs, le journal contient une allocation et un début de réception dans la même seconde. Aucune ligne ne donne l’issue. La consigne v16 demande un résumé factuel, qui reste possible. Si la question porte sur la réussite de l’écriture, la grille C5 demande de conserver les deux faits et de s’abstenir sur l’issue. Cette décision suit l’exemple de calibration `calib-0003`.

Les [six variantes C5](abstentions_bachar_c5.jsonl) donnent la question exacte, la réponse et les numéros de ligne. Ce sont six usages possibles des mêmes blocs (5 train, 1 val). Le jeu d’adaptation utilisé pour l’expérience SCRUM-39 compte toujours 240 blocs et zéro abstention. Ces variantes nécessitent une relecture et une consigne compatible avant leur utilisation pour l’adaptation.

## Vérification par bloc

Chaque identifiant du tableau ouvre la réponse et sa trace complète dans le lot. Le relecteur peut indiquer sur la PR quels blocs il a vérifiés et quelles corrections il demande. Une fois ses décisions confirmées, reporter son nom dans `reviewed_by` pour les blocs concernés dans le [lot source](lot_bachar.jsonl). Depuis la racine du dépôt, régénérer les jeux et contrôler leur concordance.

```bash
python -m volet_b.slm.merge_lots
python -m volet_b.slm.merge_lots --check
```

Les numéros de ligne ci-dessous partent de 1 dans la trace du bloc. Ils permettent de retrouver des événements dans le journal brut. Les références `[Lxx]` des corrections gardent la numérotation propre au prompt.

| Bloc | Split | Lignes | Repères dans la trace | État de la réponse |
|---|---|---:|---|---|
| [bachar-001](lot_bachar.jsonl#L1) | train | 20 | L18 09:01:50 (E20) | Cible conservée |
| [bachar-002](lot_bachar.jsonl#L2) | train | 20 | L20 07:08:23 (E20) | Cible corrigée |
| [bachar-003](lot_bachar.jsonl#L3) | train | 20 | L19 09:01:58 (E20) | Cible conservée |
| [bachar-004](lot_bachar.jsonl#L4) | train | 20 | L20 10:37:54 (E20) | Cible conservée |
| [bachar-005](lot_bachar.jsonl#L5) | train | 20 | L19 10:37:54 (E20) | Cible corrigée |
| [bachar-006](lot_bachar.jsonl#L6) | train | 20 | L18 22:09:47 (E20) | Cible conservée |
| [bachar-007](lot_bachar.jsonl#L7) | train | 24 | L14 13:27:34 (E4) · L22 21:06:39 (E20) | Cible corrigée |
| [bachar-008](lot_bachar.jsonl#L8) | train | 25 | L14 22:35:19 (E4) · L25 10:43:18 (E20) | Cible corrigée |
| [bachar-009](lot_bachar.jsonl#L9) | train | 26 | L14 11:50:42 (E27) · L19 00:35:53 (E4) | Cible corrigée |
| [bachar-010](lot_bachar.jsonl#L10) | train | 20 | L14 07:00:30 (E27) | Cible corrigée |
| [bachar-011](lot_bachar.jsonl#L11) | train | 20 | L14 06:09:53 (E27) | Cible corrigée |
| [bachar-012](lot_bachar.jsonl#L12) | train | 20 | L14 21:59:53 (E27) | Cible conservée |
| [bachar-013](lot_bachar.jsonl#L13) | train | 20 | L14 14:59:58 (E27) | Cible conservée |
| [bachar-014](lot_bachar.jsonl#L14) | train | 33 | L16 02:58:31 (E4) · L31 10:46:29 (E28) | Cible corrigée |
| [bachar-015](lot_bachar.jsonl#L15) | train | 25 | L14 22:37:33 (E4) · L23 10:46:28 (E28) | Cible corrigée |
| [bachar-016](lot_bachar.jsonl#L16) | train | 27 | L14 21:48:48 (E4) · L25 10:46:29 (E28) | Cible corrigée |
| [bachar-017](lot_bachar.jsonl#L17) | train | 33 | L16 02:57:22 (E4) · L31 10:46:29 (E28) | Cible conservée |
| [bachar-018](lot_bachar.jsonl#L18) | train | 21 | L19 10:46:29 (E28) | Cible conservée |
| [bachar-019](lot_bachar.jsonl#L19) | train | 32 | L18 10:45:19 (E6) · L22 12:49:24 (E4) | Cible corrigée |
| [bachar-020](lot_bachar.jsonl#L20) | train | 35 | L19 01:49:26 (E6) · L27 08:25:02 (E4) | Cible conservée |
| [bachar-021](lot_bachar.jsonl#L21) | train | 41 | L16 17:33:54 (E4) · L35 00:31:52 (E4) | Cible corrigée |
| [bachar-022](lot_bachar.jsonl#L22) | train | 31 | L16 03:48:34 (E4) · L23 09:39:00 (E4) | Cible corrigée |
| [bachar-023](lot_bachar.jsonl#L23) | train | 28 | L15 04:18:41 (E4) · L21 08:19:28 (E4) | Cible conservée |
| [bachar-024](lot_bachar.jsonl#L24) | train | 24 | L16 12:57:07 (E4) · L18 12:58:34 (E4) | Cible corrigée |
| [bachar-025](lot_bachar.jsonl#L25) | train | 23 | L14 22:33:57 (E4) · L15 22:35:01 (E4) | Cible conservée |
| [bachar-026](lot_bachar.jsonl#L26) | train | 4 | L1 01:06:17 (E22) · L4 01:06:23 (E7) | Cible conservée |
| [bachar-027](lot_bachar.jsonl#L27) | train | 4 | L1 02:44:20 (E5) · L4 02:44:24 (E7) | Cible conservée |
| [bachar-028](lot_bachar.jsonl#L28) | train | 4 | L1 20:41:33 (E22) · L4 20:41:42 (E7) | Cible conservée |
| [bachar-029](lot_bachar.jsonl#L29) | train | 4 | L1 22:59:09 (E5) · L4 22:59:13 (E7) | Cible corrigée |
| [bachar-030](lot_bachar.jsonl#L30) | train | 4 | L1 20:41:23 (E22) · L4 20:41:27 (E7) | Cible conservée |
| [bachar-031](lot_bachar.jsonl#L31) | train | 4 | L1 21:08:34 (E5) · L4 21:08:37 (E7) | Cible conservée |
| [bachar-032](lot_bachar.jsonl#L32) | train | 2 | L1 04:51:42 (E5) · L2 04:51:42 (E22) | Cible conservée · variante C5 |
| [bachar-033](lot_bachar.jsonl#L33) | train | 27 | L18 22:52:53 (E6) | Cible conservée |
| [bachar-034](lot_bachar.jsonl#L34) | train | 29 | L17 20:46:18 (E6) | Cible conservée |
| [bachar-035](lot_bachar.jsonl#L35) | train | 2 | L1 22:55:45 (E5) · L2 22:55:45 (E22) | Cible conservée · variante C5 |
| [bachar-036](lot_bachar.jsonl#L36) | train | 2 | L1 20:44:13 (E22) · L2 20:44:13 (E5) | Cible conservée · variante C5 |
| [bachar-037](lot_bachar.jsonl#L37) | train | 2 | L1 14:38:17 (E5) · L2 14:38:17 (E22) | Cible conservée · variante C5 |
| [bachar-038](lot_bachar.jsonl#L38) | train | 2 | L1 01:40:23 (E22) · L2 01:40:23 (E5) | Cible conservée · variante C5 |
| [bachar-039](lot_bachar.jsonl#L39) | train | 19 | L1 11:34:24 (E22) · L19 11:36:56 (E21) | Cible conservée |
| [bachar-040](lot_bachar.jsonl#L40) | train | 13 | L1 08:51:16 (E5) · L13 08:51:56 (E26) | Cible conservée |
| [bachar-041](lot_bachar.jsonl#L41) | train | 13 | L1 08:34:32 (E5) · L13 08:35:09 (E26) | Cible conservée |
| [bachar-042](lot_bachar.jsonl#L42) | train | 19 | L1 14:43:52 (E5) · L19 21:05:50 (E21) | Cible conservée |
| [bachar-043](lot_bachar.jsonl#L43) | train | 19 | L1 03:30:49 (E5) · L19 04:47:21 (E21) | Cible conservée |
| [bachar-044](lot_bachar.jsonl#L44) | train | 19 | L1 02:52:27 (E5) · L19 04:47:54 (E21) | Cible conservée |
| [bachar-045](lot_bachar.jsonl#L45) | train | 19 | L1 07:12:06 (E5) · L19 09:02:43 (E21) | Cible conservée |
| [bachar-046](lot_bachar.jsonl#L46) | train | 44 | L15 18:00:17 (E4) · L38 00:57:56 (E4) | Cible corrigée |
| [bachar-047](lot_bachar.jsonl#L47) | train | 24 | L1 20:47:01 (E22) · L24 10:36:19 (E21) | Cible conservée |
| [bachar-048](lot_bachar.jsonl#L48) | train | 22 | L1 03:21:09 (E5) · L22 04:48:13 (E21) | Cible conservée |
| [bachar-049](lot_bachar.jsonl#L49) | train | 61 | L42 01:46:51 (E6) · L55 09:45:54 (E4) | Cible corrigée |
| [bachar-050](lot_bachar.jsonl#L50) | train | 28 | L1 07:36:04 (E5) · L28 09:02:56 (E21) | Cible conservée |
| [bachar-051](lot_bachar.jsonl#L51) | val | 20 | L19 22:09:30 (E20) | Cible conservée |
| [bachar-052](lot_bachar.jsonl#L52) | val | 26 | L14 21:58:34 (E4) · L26 10:38:06 (E20) | Cible conservée |
| [bachar-053](lot_bachar.jsonl#L53) | val | 33 | L15 03:56:10 (E4) · L31 10:46:29 (E28) | Cible corrigée |
| [bachar-054](lot_bachar.jsonl#L54) | val | 39 | L15 20:09:37 (E4) · L28 22:21:07 (E6) | Cible corrigée |
| [bachar-055](lot_bachar.jsonl#L55) | val | 25 | L16 18:24:41 (E4) · L18 01:18:10 (E4) | Cible conservée |
| [bachar-056](lot_bachar.jsonl#L56) | val | 4 | L1 20:48:48 (E22) · L4 20:48:51 (E7) | Cible conservée |
| [bachar-057](lot_bachar.jsonl#L57) | val | 2 | L1 04:30:49 (E5) · L2 04:30:49 (E22) | Cible conservée · variante C5 |
| [bachar-058](lot_bachar.jsonl#L58) | val | 27 | L16 21:18:14 (E6) | Cible conservée |
| [bachar-059](lot_bachar.jsonl#L59) | val | 13 | L1 08:05:56 (E22) · L13 08:06:43 (E26) | Cible conservée |
| [bachar-060](lot_bachar.jsonl#L60) | val | 23 | L1 21:20:05 (E5) · L23 10:36:39 (E21) | Cible conservée |

## Comparaison des 19 corrections

Chaque entrée reproduit le passage modifié et les lignes de la trace qui justifient le changement. Le numéro à gauche de chaque extrait est sa position dans le bloc. Les 60 réponses restent soumises à la relecture croisée.

<details>
<summary>bachar-002 · train</summary>

**Résumé**

- **Avant** · Le NameNode demande trois suppressions et les DataNodes journalisent trois opérations locales Deleting [F09][F07].
- **Après** · Le NameNode demande trois suppressions et trois opérations locales Deleting sont journalisées [F09][F07].

Les trois messages Deleting comptent des opérations locales et ne permettent pas de dénombrer les machines.

```text
17 | 081111 065519 19 INFO dfs.FSDataset: Deleting block blk_7201339501460340607 file /mnt/hadoop/dfs/data/current/subdir27/blk_7201339501460340607
18 | 081111 065542 19 INFO dfs.FSDataset: Deleting block blk_7201339501460340607 file /mnt/hadoop/dfs/data/current/subdir63/blk_7201339501460340607
19 | 081111 065657 19 INFO dfs.FSDataset: Deleting block blk_7201339501460340607 file /mnt/hadoop/dfs/data/current/subdir35/blk_7201339501460340607
```

</details>

<details>
<summary>bachar-005 · train</summary>

**Information recherchée**

- **Avant** · Les traces du DataNode documentent-elles l'état de volumeMap pour ce réplica lors de l'erreur de suppression [L01] ?
- **Après** · Quels éléments du journal de gestion du réplica expliquent l’absence de son entrée BlockInfo dans volumeMap [L01] ?

Le WARN donne déjà l’état de l’entrée. Son absence reste à expliquer.

```text
19 | 081110 103754 19 WARN dfs.FSDataset: Unexpected error trying to delete block blk_8863164562088434847. BlockInfo not found in volumeMap.
```

</details>

<details>
<summary>bachar-007 · train</summary>

**Résumé**

- **Avant** · Deux exceptions pendant l'envoi à des clients sont également relevées, de cause indéterminée [F05].
- **Après** · Deux exceptions pendant l'envoi vers deux adresses clientes distinctes sont également relevées, de cause indéterminée [F05][L01][L02].

Les deux lignes d’exception documentent les deux adresses clientes. Le compteur E4 donne le nombre de messages.

```text
14 | 081110 132734 11828 WARN dfs.DataNode$DataXceiver: 10.251.110.68:50010:Got exception while serving blk_7982193940539317320 to /10.251.126.22:
15 | 081110 132902 11856 WARN dfs.DataNode$DataXceiver: 10.251.110.68:50010:Got exception while serving blk_7982193940539317320 to /10.250.14.196:
```

</details>

<details>
<summary>bachar-008 · train</summary>

**Information recherchée**

- **Avant** · Un retrait de BlockInfo est-il documenté pour les demandes de suppression concernées [L03][L04] ?
- **Après** · Les journaux du DataNode expliquent-ils l’absence de BlockInfo signalée dans les deux messages de suppression [L03][L04] ?

Les deux messages constatent une absence. Aucun retrait antérieur n’est établi.

```text
24 | 081110 103800 18 WARN dfs.FSDataset: Unexpected error trying to delete block blk_8517699911881863286. BlockInfo not found in volumeMap.
25 | 081110 104318 19 WARN dfs.FSDataset: Unexpected error trying to delete block blk_8517699911881863286. BlockInfo not found in volumeMap.
```

</details>

<details>
<summary>bachar-009 · train</summary>

**Résumé**

- **Avant** · Une demande redondante d'enregistrement et deux exceptions d'envoi à un client sont de cause indéterminée [F12][F04].
- **Après** · Une demande redondante d'enregistrement et deux exceptions d’envoi vers la même adresse cliente sont de cause indéterminée [F12][F04][L02][L03].

Les deux lignes E4 donnent la même adresse cliente.

```text
17 | 081110 173828 13633 WARN dfs.DataNode$DataXceiver: 10.250.5.161:50010:Got exception while serving blk_-2457850663280039213 to /10.251.110.196:
19 | 081111 003553 17294 WARN dfs.DataNode$DataXceiver: 10.251.31.180:50010:Got exception while serving blk_-2457850663280039213 to /10.251.110.196:
```

</details>

<details>
<summary>bachar-010 · train</summary>

**Information recherchée**

- **Avant** · Quel enregistrement antérieur rend cette demande addStoredBlock redondante [L01] ?
- **Après** · Les journaux du DataNode précisent-ils pourquoi la demande d’enregistrement a été renouvelée [L01] ?

La trace contient déjà la mise à jour pour ce DataNode à 07:00:29.

```text
13 | 081111 070029 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.7.244:50010 is added to blk_-3375805297867187723 size 67108864
14 | 081111 070030 29 WARN dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: Redundant addStoredBlock request received for blk_-3375805297867187723 on 10.250.7.244:50010 size 67108864
```

</details>

<details>
<summary>bachar-011 · train</summary>

**Résumé**

- **Avant** · Le NameNode demande trois suppressions et les DataNodes journalisent trois opérations sur le fichier local [F08][F06].
- **Après** · Le NameNode demande trois suppressions et trois opérations sur le fichier local sont journalisées [F08][F06].

Les trois messages Deleting comptent des opérations locales et ne permettent pas de dénombrer les machines.

```text
18 | 081111 065340 19 INFO dfs.FSDataset: Deleting block blk_-5931560835175779080 file /mnt/hadoop/dfs/data/current/subdir29/blk_-5931560835175779080
19 | 081111 065357 19 INFO dfs.FSDataset: Deleting block blk_-5931560835175779080 file /mnt/hadoop/dfs/data/current/subdir42/blk_-5931560835175779080
20 | 081111 065408 18 INFO dfs.FSDataset: Deleting block blk_-5931560835175779080 file /mnt/hadoop/dfs/data/current/subdir21/blk_-5931560835175779080
```

</details>

<details>
<summary>bachar-014 · train</summary>

**Information recherchée**

- **Avant** · Quel historique d'association à un fichier est disponible pour le bloc enregistré [L05] ?
- **Après** · Les journaux du NameNode expliquent-ils pourquoi le bloc ne correspondait à aucun fichier lors de la demande [L05] ?

L05 décrit la réception de la demande. La mise à jour de blockMap figure sur une autre ligne.

```text
31 | 081110 104629 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: addStoredBlock request received for blk_-2418794814150809191 on 10.251.106.10:50010 size 67108864 But it does not belong to any file.
32 | 081110 104629 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.251.106.10:50010 is added to blk_-2418794814150809191 size 67108864
```

</details>

<details>
<summary>bachar-015 · train</summary>

**Résumé**

- **Avant** · Le NameNode inscrit trois demandes de suppression et les DataNodes journalisent trois opérations locales Deleting [F11][F09].
- **Après** · Le NameNode inscrit trois demandes de suppression et trois opérations locales Deleting sont journalisées [F11][F09].

**Information recherchée**

- **Avant** · Quel était le rattachement du bloc à un fichier au moment de la demande d'enregistrement [L03] ?
- **Après** · Quel élément du journal du NameNode explique l’absence de fichier correspondant lors de la demande [L03] ?

Les trois messages Deleting comptent des opérations locales et ne permettent pas de dénombrer les machines. L03 donne déjà l’état de l’association au fichier.

```text
21 | 081110 103301 19 INFO dfs.FSDataset: Deleting block blk_-9031164655223473108 file /mnt/hadoop/dfs/data/current/subdir61/blk_-9031164655223473108
22 | 081110 103304 19 INFO dfs.FSDataset: Deleting block blk_-9031164655223473108 file /mnt/hadoop/dfs/data/current/subdir14/blk_-9031164655223473108
23 | 081110 104628 27 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: addStoredBlock request received for blk_-9031164655223473108 on 10.251.106.10:50010 size 67108864 But it does not belong to any file.
25 | 081110 104706 19 INFO dfs.FSDataset: Deleting block blk_-9031164655223473108 file /mnt/hadoop/dfs/data/current/subdir62/blk_-9031164655223473108
```

</details>

<details>
<summary>bachar-016 · train</summary>

**Résumé**

- **Avant** · Deux exceptions d'envoi à des clients et une demande d'enregistrement sans fichier correspondant sont de cause indéterminée [F05][F13].
- **Après** · Deux exceptions d'envoi vers deux adresses clientes distinctes et une demande d'enregistrement sans fichier correspondant sont de cause indéterminée [F05][L01][L02][F13].

Les deux lignes d’exception documentent les deux adresses clientes. Le compteur E4 donne le nombre de messages.

```text
14 | 081109 214848 2668 WARN dfs.DataNode$DataXceiver: 10.251.106.10:50010:Got exception while serving blk_3708679726899046099 to /10.251.35.1:
16 | 081109 214919 2792 WARN dfs.DataNode$DataXceiver: 10.251.107.242:50010:Got exception while serving blk_3708679726899046099 to /10.251.89.155:
```

</details>

<details>
<summary>bachar-019 · train</summary>

**Résumé**

- **Avant** · Deux exceptions d'envoi à des clients sur 10.251.70.211:50010 sont de cause indéterminée [F05][L01][L02].
- **Après** · Deux exceptions d’envoi depuis le DataNode 10.251.70.211:50010 vers deux adresses clientes distinctes sont de cause indéterminée [F05][L01][L02].

L01 et L02 distinguent la source commune des deux destinataires.

```text
21 | 081110 124923 11591 WARN dfs.DataNode$DataXceiver: 10.251.70.211:50010:Got exception while serving blk_-4766159235599770128 to /10.251.74.227:
22 | 081110 124924 11592 WARN dfs.DataNode$DataXceiver: 10.251.70.211:50010:Got exception while serving blk_-4766159235599770128 to /10.251.203.4:
```

</details>

<details>
<summary>bachar-021 · train</summary>

**Résumé**

- **Avant** · Quatre lectures servies, deux demandes de nouvelle copie et deux transmissions à un autre DataNode sont enregistrées [F03][F14][F09].
- **Après** · Quatre lectures servies, deux demandes de nouvelle copie et deux transmissions de réplica entre DataNodes sont enregistrées [F03][F14][F09].

Les deux lignes E16 ont des destinataires distincts.

```text
20 | 081110 211539 14725 INFO dfs.DataNode$DataTransfer: 10.251.66.63:50010:Transmitted block blk_6655934270802948551 to /10.251.75.143:50010
28 | 081110 222219 16066 INFO dfs.DataNode$DataTransfer: 10.251.75.143:50010:Transmitted block blk_6655934270802948551 to /10.251.110.196:50010
```

</details>

<details>
<summary>bachar-022 · train</summary>

**Résumé**

- **Avant** · Le NameNode demande trois suppressions et les DataNodes journalisent trois opérations locales Deleting [F10][F08].
- **Après** · Le NameNode demande trois suppressions et trois opérations locales Deleting sont journalisées [F10][F08].

Les trois messages Deleting comptent des opérations locales et ne permettent pas de dénombrer les machines.

```text
29 | 081110 103508 19 INFO dfs.FSDataset: Deleting block blk_-4225696750965945415 file /mnt/hadoop/dfs/data/current/subdir12/blk_-4225696750965945415
30 | 081110 103514 19 INFO dfs.FSDataset: Deleting block blk_-4225696750965945415 file /mnt/hadoop/dfs/data/current/subdir27/blk_-4225696750965945415
31 | 081110 103519 19 INFO dfs.FSDataset: Deleting block blk_-4225696750965945415 file /mnt/hadoop/dfs/data/current/subdir47/blk_-4225696750965945415
```

</details>

<details>
<summary>bachar-024 · train</summary>

**Résumé**

- **Avant** · Les deux exceptions d'envoi vers des clients restent de cause indéterminée [F05].
- **Après** · Les deux exceptions d'envoi vers deux adresses clientes distinctes restent de cause indéterminée [F05][L01][L02].

Les deux lignes d’exception documentent les deux adresses clientes. Le compteur E4 donne le nombre de messages.

```text
16 | 081110 125707 11680 WARN dfs.DataNode$DataXceiver: 10.251.42.84:50010:Got exception while serving blk_1149495335521216780 to /10.251.91.84:
18 | 081110 125834 11522 WARN dfs.DataNode$DataXceiver: 10.251.31.180:50010:Got exception while serving blk_1149495335521216780 to /10.251.66.63:
```

</details>

<details>
<summary>bachar-029 · train</summary>

**Information recherchée**

- **Avant** · Les journaux de l'émetteur expliquent-ils l'interruption de lecture du flux [L01] ?
- **Après** · Quel diagnostic de la connexion permet de préciser l’impossibilité de lire le flux [L01] ?

L01 dit que la lecture est impossible. Le message ne caractérise pas une interruption.

```text
 4 | 081110 225913 16610 INFO dfs.DataNode$DataXceiver: writeBlock blk_3041842189638232351 received exception java.io.IOException: Could not read from stream
```

</details>

<details>
<summary>bachar-046 · train</summary>

**Résumé**

- **Avant** · Trois nouvelles copies sont demandées et deux transmissions à un autre DataNode sont consignées [F14][F09].
- **Après** · Trois nouvelles copies sont demandées et deux transmissions de réplica entre DataNodes sont consignées [F14][F09].

**Résumé**

- **Avant** · Deux exceptions d'envoi à des clients et un dépassement du délai de réplication restent de cause indéterminée [F04][F16].
- **Après** · Deux exceptions d'envoi vers deux adresses clientes distinctes et un dépassement du délai de réplication restent de cause indéterminée [F04][L01][L03][F16].

Les deux lignes d’exception documentent les deux adresses clientes. Le compteur E4 donne le nombre de messages. Les deux lignes E16 ont des destinataires distincts.

```text
15 | 081110 180017 10627 WARN dfs.DataNode$DataXceiver: 10.251.123.33:50010:Got exception while serving blk_-2526833798441848968 to /10.251.127.47:
24 | 081110 212454 15038 INFO dfs.DataNode$DataTransfer: 10.251.215.50:50010:Transmitted block blk_-2526833798441848968 to /10.251.199.245:50010
32 | 081110 222009 16019 INFO dfs.DataNode$DataTransfer: 10.251.199.245:50010:Transmitted block blk_-2526833798441848968 to /10.251.203.4:50010
38 | 081111 005756 17464 WARN dfs.DataNode$DataXceiver: 10.251.199.245:50010:Got exception while serving blk_-2526833798441848968 to /10.250.19.227:
```

</details>

<details>
<summary>bachar-049 · train</summary>

**Résumé**

- **Avant** · Deux interruptions de PacketResponder, trois exceptions du PacketResponder et quatre exceptions d'envoi vers deux clients différents sont aussi de cause indéterminée [F08][F10][F04][L18][L21].
- **Après** · Deux interruptions de PacketResponder, trois exceptions du PacketResponder et quatre exceptions d'envoi vers deux clients différents sont aussi de cause indéterminée [F08][F10][F04][L18][L19][L20][L21].

Les quatre messages E4 documentent deux adresses clientes distinctes.

```text
45 | 081110 040207 6735 WARN dfs.DataNode$DataXceiver: 10.251.39.192:50010:Got exception while serving blk_7008279672769077211 to /10.251.202.134:
49 | 081110 070920 7596 WARN dfs.DataNode$DataXceiver: 10.251.39.192:50010:Got exception while serving blk_7008279672769077211 to /10.251.202.134:
52 | 081110 081744 8195 WARN dfs.DataNode$DataXceiver: 10.251.91.159:50010:Got exception while serving blk_7008279672769077211 to /10.251.202.134:
55 | 081110 094554 8894 WARN dfs.DataNode$DataXceiver: 10.251.39.192:50010:Got exception while serving blk_7008279672769077211 to /10.251.110.196:
```

</details>

<details>
<summary>bachar-053 · val</summary>

**Résumé**

- **Avant** · Quatre exceptions d'envoi à un client et une demande d'enregistrement d'un bloc sans fichier correspondant sont de cause indéterminée [F04][F12].
- **Après** · Quatre exceptions d’envoi vers la même adresse cliente et une demande d’enregistrement pour un bloc sans fichier correspondant sont de cause indéterminée [F04][L01][L02][L03][L04][F12].

Les quatre lignes E4 donnent la même adresse cliente.

```text
15 | 081110 035610 6458 WARN dfs.DataNode$DataXceiver: 10.251.29.239:50010:Got exception while serving blk_4533254061725671644 to /10.251.214.67:
19 | 081110 070847 7597 WARN dfs.DataNode$DataXceiver: 10.251.199.86:50010:Got exception while serving blk_4533254061725671644 to /10.251.214.67:
22 | 081110 081700 7919 WARN dfs.DataNode$DataXceiver: 10.251.106.10:50010:Got exception while serving blk_4533254061725671644 to /10.251.214.67:
23 | 081110 094130 8649 WARN dfs.DataNode$DataXceiver: 10.251.29.239:50010:Got exception while serving blk_4533254061725671644 to /10.251.214.67:
```

</details>

<details>
<summary>bachar-054 · val</summary>

**Résumé**

- **Avant** · Le bloc compte deux lectures servies, deux demandes de nouvelle copie et deux transmissions à un autre DataNode [F04][F15][F10].
- **Après** · Le bloc compte deux lectures servies, deux demandes de nouvelle copie et deux transmissions de réplica entre DataNodes [F04][F15][F10].

Les deux lignes E16 ont des destinataires distincts.

```text
20 | 081110 211558 14706 INFO dfs.DataNode$DataTransfer: 10.251.203.149:50010:Transmitted block blk_-971328061059725603 to /10.250.19.16:50010
29 | 081110 222107 16163 INFO dfs.DataNode$DataTransfer: 10.250.19.16:50010:Transmitted block blk_-971328061059725603 to /10.251.202.181:50010
```

</details>
