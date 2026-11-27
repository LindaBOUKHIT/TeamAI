# Relecture du lot de Bachar · SCRUM-36

Le lot comprend 60 blocs (50 train, 10 val). La comparaison des cibles au texte des journaux et aux preuves du prompt conduit à **19 cibles corrigées** et **41 conservées** pour la consigne v16. Les champs de relecture humaine sont encore ouverts. Le décompte historique de 60 relectures signées sur 240 porte sur le lot de Linda.

[Corrections proposées, avec la cible complète et le motif pour chaque bloc](propositions_bachar.jsonl) · [Lot source avec les traces](lot_bachar.jsonl)

## Cas où l’issue de l’écriture est inconnue

Pour six blocs, le journal contient une allocation et un début de réception dans la même seconde. Aucune ligne ne donne l’issue. La consigne v16 demande un résumé factuel, qui reste possible. Si la question porte sur la réussite de l’écriture, la grille C5 demande de conserver les deux faits et de s’abstenir sur l’issue. Cette décision suit l’exemple de calibration `calib-0003`.

Les [six variantes C5](abstentions_bachar_c5.jsonl) donnent la question exacte, la réponse et les numéros de ligne. Ce sont six usages possibles des mêmes blocs (5 train, 1 val). Le jeu d’adaptation utilisé pour l’expérience SCRUM-39 compte toujours 240 blocs et zéro abstention. Ces variantes nécessitent une relecture et une consigne compatible avant leur utilisation pour l’adaptation.

## Vérification par bloc

Les numéros de ligne ci-dessous partent de 1 dans la trace du bloc. Ils permettent de retrouver des événements dans le journal brut. Les références `[Lxx]` des corrections gardent la numérotation propre au prompt.

| Bloc | Split | Lignes | Repères dans la trace | Décision proposée |
|---|---|---:|---|---|
| bachar-001 | train | 20 | L18 09:01:50 (E20) | Cible conservée |
| bachar-002 | train | 20 | L20 07:08:23 (E20) | Cible corrigée |
| bachar-003 | train | 20 | L19 09:01:58 (E20) | Cible conservée |
| bachar-004 | train | 20 | L20 10:37:54 (E20) | Cible conservée |
| bachar-005 | train | 20 | L19 10:37:54 (E20) | Cible corrigée |
| bachar-006 | train | 20 | L18 22:09:47 (E20) | Cible conservée |
| bachar-007 | train | 24 | L14 13:27:34 (E4) · L22 21:06:39 (E20) | Cible corrigée |
| bachar-008 | train | 25 | L14 22:35:19 (E4) · L25 10:43:18 (E20) | Cible corrigée |
| bachar-009 | train | 26 | L14 11:50:42 (E27) · L19 00:35:53 (E4) | Cible corrigée |
| bachar-010 | train | 20 | L14 07:00:30 (E27) | Cible corrigée |
| bachar-011 | train | 20 | L14 06:09:53 (E27) | Cible corrigée |
| bachar-012 | train | 20 | L14 21:59:53 (E27) | Cible conservée |
| bachar-013 | train | 20 | L14 14:59:58 (E27) | Cible conservée |
| bachar-014 | train | 33 | L16 02:58:31 (E4) · L31 10:46:29 (E28) | Cible corrigée |
| bachar-015 | train | 25 | L14 22:37:33 (E4) · L23 10:46:28 (E28) | Cible corrigée |
| bachar-016 | train | 27 | L14 21:48:48 (E4) · L25 10:46:29 (E28) | Cible corrigée |
| bachar-017 | train | 33 | L16 02:57:22 (E4) · L31 10:46:29 (E28) | Cible conservée |
| bachar-018 | train | 21 | L19 10:46:29 (E28) | Cible conservée |
| bachar-019 | train | 32 | L18 10:45:19 (E6) · L22 12:49:24 (E4) | Cible corrigée |
| bachar-020 | train | 35 | L19 01:49:26 (E6) · L27 08:25:02 (E4) | Cible conservée |
| bachar-021 | train | 41 | L16 17:33:54 (E4) · L35 00:31:52 (E4) | Cible corrigée |
| bachar-022 | train | 31 | L16 03:48:34 (E4) · L23 09:39:00 (E4) | Cible corrigée |
| bachar-023 | train | 28 | L15 04:18:41 (E4) · L21 08:19:28 (E4) | Cible conservée |
| bachar-024 | train | 24 | L16 12:57:07 (E4) · L18 12:58:34 (E4) | Cible corrigée |
| bachar-025 | train | 23 | L14 22:33:57 (E4) · L15 22:35:01 (E4) | Cible conservée |
| bachar-026 | train | 4 | L1 01:06:17 (E22) · L4 01:06:23 (E7) | Cible conservée |
| bachar-027 | train | 4 | L1 02:44:20 (E5) · L4 02:44:24 (E7) | Cible conservée |
| bachar-028 | train | 4 | L1 20:41:33 (E22) · L4 20:41:42 (E7) | Cible conservée |
| bachar-029 | train | 4 | L1 22:59:09 (E5) · L4 22:59:13 (E7) | Cible corrigée |
| bachar-030 | train | 4 | L1 20:41:23 (E22) · L4 20:41:27 (E7) | Cible conservée |
| bachar-031 | train | 4 | L1 21:08:34 (E5) · L4 21:08:37 (E7) | Cible conservée |
| bachar-032 | train | 2 | L1 04:51:42 (E5) · L2 04:51:42 (E22) | Cible conservée · variante C5 |
| bachar-033 | train | 27 | L18 22:52:53 (E6) | Cible conservée |
| bachar-034 | train | 29 | L17 20:46:18 (E6) | Cible conservée |
| bachar-035 | train | 2 | L1 22:55:45 (E5) · L2 22:55:45 (E22) | Cible conservée · variante C5 |
| bachar-036 | train | 2 | L1 20:44:13 (E22) · L2 20:44:13 (E5) | Cible conservée · variante C5 |
| bachar-037 | train | 2 | L1 14:38:17 (E5) · L2 14:38:17 (E22) | Cible conservée · variante C5 |
| bachar-038 | train | 2 | L1 01:40:23 (E22) · L2 01:40:23 (E5) | Cible conservée · variante C5 |
| bachar-039 | train | 19 | L1 11:34:24 (E22) · L19 11:36:56 (E21) | Cible conservée |
| bachar-040 | train | 13 | L1 08:51:16 (E5) · L13 08:51:56 (E26) | Cible conservée |
| bachar-041 | train | 13 | L1 08:34:32 (E5) · L13 08:35:09 (E26) | Cible conservée |
| bachar-042 | train | 19 | L1 14:43:52 (E5) · L19 21:05:50 (E21) | Cible conservée |
| bachar-043 | train | 19 | L1 03:30:49 (E5) · L19 04:47:21 (E21) | Cible conservée |
| bachar-044 | train | 19 | L1 02:52:27 (E5) · L19 04:47:54 (E21) | Cible conservée |
| bachar-045 | train | 19 | L1 07:12:06 (E5) · L19 09:02:43 (E21) | Cible conservée |
| bachar-046 | train | 44 | L15 18:00:17 (E4) · L38 00:57:56 (E4) | Cible corrigée |
| bachar-047 | train | 24 | L1 20:47:01 (E22) · L24 10:36:19 (E21) | Cible conservée |
| bachar-048 | train | 22 | L1 03:21:09 (E5) · L22 04:48:13 (E21) | Cible conservée |
| bachar-049 | train | 61 | L42 01:46:51 (E6) · L55 09:45:54 (E4) | Cible corrigée |
| bachar-050 | train | 28 | L1 07:36:04 (E5) · L28 09:02:56 (E21) | Cible conservée |
| bachar-051 | val | 20 | L19 22:09:30 (E20) | Cible conservée |
| bachar-052 | val | 26 | L14 21:58:34 (E4) · L26 10:38:06 (E20) | Cible conservée |
| bachar-053 | val | 33 | L15 03:56:10 (E4) · L31 10:46:29 (E28) | Cible corrigée |
| bachar-054 | val | 39 | L15 20:09:37 (E4) · L28 22:21:07 (E6) | Cible corrigée |
| bachar-055 | val | 25 | L16 18:24:41 (E4) · L18 01:18:10 (E4) | Cible conservée |
| bachar-056 | val | 4 | L1 20:48:48 (E22) · L4 20:48:51 (E7) | Cible conservée |
| bachar-057 | val | 2 | L1 04:30:49 (E5) · L2 04:30:49 (E22) | Cible conservée · variante C5 |
| bachar-058 | val | 27 | L16 21:18:14 (E6) | Cible conservée |
| bachar-059 | val | 13 | L1 08:05:56 (E22) · L13 08:06:43 (E26) | Cible conservée |
| bachar-060 | val | 23 | L1 21:20:05 (E5) · L23 10:36:39 (E21) | Cible conservée |
