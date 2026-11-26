# Pré-relecture du lot de Linda — SCRUM-36

Récapitulatif : 56 ok / 4 corriger / 0 rejet.
Ids à corriger : linda-001, linda-002, linda-006, linda-008.

### linda-001 — corriger
À vérifier : [L01] établit l’absence de BlockInfo dans volumeMap, sans prouver qu’une opération a retiré une entrée auparavant présente, contrairement au présupposé de la question.
Correction proposée : Remplacer l’unique question de infos_manquantes par « Pourquoi l’entrée BlockInfo est-elle absente de volumeMap pour ce réplica [L01] ? ».

### linda-002 — corriger
À vérifier : [L01] constate BlockInfo introuvable à 04:49:15, sans établir une disparition antérieure dont on pourrait rechercher la date.
Correction proposée : Remplacer l’unique question de infos_manquantes par « Les journaux du DataNode expliquent-ils l’absence de l’entrée BlockInfo dans volumeMap lors de cette demande [L01] ? ».

### linda-003 — ok
À vérifier : [F03], [F04] et [F10] comptent chacun trois occurrences, et [L01] confirme l’erreur de suppression à 07:59:45 sans renseigner l’état du fichier local demandé dans la question.
Correction proposée : aucune

### linda-004 — ok
À vérifier : [F06] compte deux occurrences et [L01][L02] confirment les horaires et BlockInfo absent sans identifier les DataNodes, ce qui justifie la question.
Correction proposée : aucune

### linda-005 — ok
À vérifier : [F03][F04] comptent trois débuts d’écriture et trois réceptions, et [L01] confirme BlockInfo absent à 04:47:45 sans expliquer cette absence.
Correction proposée : aucune

### linda-006 — corriger
À vérifier : [L01] signale une absence de BlockInfo à 21:06:52 et ne démontre pas la « disparition » présupposée dans infos_manquantes.
Correction proposée : Remplacer l’unique question de infos_manquantes par « Pourquoi l’entrée BlockInfo est-elle absente de volumeMap lors de la demande de suppression à 21:06:52 [L01] ? ».

### linda-007 — ok
À vérifier : [F01] donne 16 min 14 s et [L01][L02] confirment deux erreurs à 22:09:39 et 22:10:57 sans permettre d’attribuer les deux messages au même DataNode.
Correction proposée : aucune

### linda-008 — corriger
À vérifier : [L03] constate BlockInfo absent sans établir qu’une entrée était présente auparavant, alors que la deuxième question dit « ne contenait plus son entrée ».
Correction proposée : Remplacer la deuxième question de infos_manquantes par « Quel était l’état du fichier local du bloc sur le DataNode au moment de l’erreur de suppression [L03] ? ».

### linda-009 — ok
À vérifier : [F03][F04] comptent trois lectures et trois exceptions, [L04] confirme BlockInfo absent, et la suppression locale antérieure est seulement interrogée comme explication possible.
Correction proposée : aucune

### linda-010 — ok
À vérifier : [F12] décrit une demande redondante, [F04] compte deux exceptions et [L01][L02][L03] n’en précisent pas les causes, conformément aux questions et à hypotheses vide.
Correction proposée : aucune

### linda-011 — ok
À vérifier : [L01] situe la demande addStoredBlock redondante à 05:24:01 sans en expliquer l’origine, et [F09] compte trois messages blockMap.
Correction proposée : aucune

### linda-012 — ok
À vérifier : [F03] compte deux vérifications réussies, [F13] une demande redondante et [F05] deux exceptions dont [L01][L02][L03] ne donnent pas la cause.
Correction proposée : aucune

### linda-013 — ok
À vérifier : [L01] confirme la demande redondante à 05:28:04, sans cause explicite ni ordre établi entre les événements de cette seconde dans [F12].
Correction proposée : aucune

### linda-014 — ok
À vérifier : [F05] décrit trois fins de PacketResponder sans erreur implicite et [L01] confirme la demande redondante à 23:02:12 sans en indiquer l’origine.
Correction proposée : aucune

### linda-015 — ok
À vérifier : [F13] et [L03] décrivent un bloc sans fichier associé sans en expliquer la cause, tandis que [F05] compte deux exceptions d’envoi.
Correction proposée : aucune

### linda-016 — ok
À vérifier : [F09] compte quatre messages blockMap sans garantir quatre réplicas distincts et [L01] constate seulement l’absence d’association à un fichier.
Correction proposée : aucune

### linda-017 — ok
À vérifier : [F03] atteste une vérification réussie et [F11][L01] décrivent la demande pour un bloc sans fichier, dont l’historique reste inconnu.
Correction proposée : aucune

### linda-018 — ok
À vérifier : [L01] donne 10:46:29 et l’absence de fichier associé sans renseigner l’existence d’un fichier local sur le DataNode, objet de la question.
Correction proposée : aucune

### linda-019 — ok
À vérifier : [F03] compte huit lectures, [F04] quatre exceptions et [F12][L05] une demande pour un bloc sans fichier sans établir de cause commune.
Correction proposée : aucune

### linda-020 — ok
À vérifier : [F03] compte trois vérifications, [F12] quatre opérations Deleting et [L01][L02] montrent le même DataNode avec deux adresses clientes différentes.
Correction proposée : aucune

### linda-021 — ok
À vérifier : [F03][F06] comptent quatre lectures et deux copies reçues, et [L01][L02] montrent le même couple DataNode-client aux deux horaires cités.
Correction proposée : aucune

### linda-022 — ok
À vérifier : [F11] atteste seulement le démarrage d’un transfert et [L01][L02] confirment le même DataNode, deux clients et les horaires 12:47:23 et 12:47:26.
Correction proposée : aucune

### linda-023 — ok
À vérifier : [F03] compte trois vérifications réussies et [L01][L02] indiquent deux DataNodes distincts vers la même adresse cliente sans détail d’exception.
Correction proposée : aucune

### linda-024 — ok
À vérifier : [F03] compte six lectures et [L01][L02][L03] montrent le même client, avec le même DataNode dans les deux premiers messages à des secondes distinctes.
Correction proposée : aucune

### linda-025 — ok
À vérifier : [F04] compte trois exceptions et [L01][L02] confirment le même couple DataNode-client, alors que [L03] concerne un autre couple.
Correction proposée : aucune

### linda-026 — ok
À vérifier : [L01][L02] désignent bien le DataNode 10.250.17.177 et deux clients distincts, sans renseigner les observations côté client demandées dans infos_manquantes.
Correction proposée : aucune

### linda-027 — ok
À vérifier : [F01] couvre cinq secondes, [F03] compte deux débuts d’écriture et [L01] contient Could not read from stream sans identifier le fournisseur du flux.
Correction proposée : aucune

### linda-028 — ok
À vérifier : [F01] donne six secondes et [L01] confirme IOException à 08:33:55 avec Could not read from stream, détail auquel se limite l’hypothèse autorisée.
Correction proposée : aucune

### linda-029 — ok
À vérifier : [F01] donne quatre lignes entre 10:06:49 et 10:06:54 et [L01] justifie seulement l’impossibilité de lire le flux, sans état de connexion connu.
Correction proposée : aucune

### linda-030 — ok
À vérifier : [F03][F05] attestent deux débuts d’écriture et une allocation sans imposer leur ordre, et [L01] confirme l’exception à 08:52:46.
Correction proposée : aucune

### linda-031 — ok
À vérifier : [F01] donne cinq secondes et [L01] contient l’impossibilité de lire le flux, tandis qu’une fermeture côté émetteur reste une question et non une cause affirmée.
Correction proposée : aucune

### linda-032 — ok
À vérifier : [F01] couvre 01:24:00 à 01:24:03 et [L01] mentionne explicitement IOException et Could not read from stream sans en fournir l’origine.
Correction proposée : aucune

### linda-033 — ok
À vérifier : [F05] place E5 et E22 à 01:11:33 le 10 novembre sans ordre déterminable, et le prompt ne reconnaît aucun indice d’incident justifiant des questions.
Correction proposée : aucune

### linda-034 — ok
À vérifier : [F18] regroupe E6, E16 et E26 à 22:23:59 sans ordre établi, et [F12][F10] distinguent trois demandes de suppression de quatre opérations locales.
Correction proposée : aucune

### linda-035 — ok
À vérifier : [F17] regroupe quatre E23 à 04:43:29 sans ordre interne, et [F09] compte quatre messages Deleting sans prouver la suppression de toutes les copies.
Correction proposée : aucune

### linda-036 — ok
À vérifier : [F03][F04] ne décrivent qu’un début d’écriture et une allocation, tous deux placés par [F05] au 9 novembre à 23:32:38 sans ordre relatif.
Correction proposée : aucune

### linda-037 — ok
À vérifier : [F01] compte deux lignes et [F05] situe E5 et E22 dans la même seconde 01:05:31 sans permettre de conclure à une réception aboutie.
Correction proposée : aucune

### linda-038 — ok
À vérifier : [F05] situe l’allocation et le début d’écriture à 01:18:04 le 10 novembre sans ordre établi ni indice d’incident reconnu.
Correction proposée : aucune

### linda-039 — ok
À vérifier : [F01] donne 58 secondes et [F09] regroupe trois E9, trois E11 et trois E26 à 09:48:06 sans ordre interne ni erreur implicite du PacketResponder.
Correction proposée : aucune

### linda-040 — ok
À vérifier : [F12] compte trois E23 à 07:56:27 et [F06] atteste trois opérations Deleting dont le résumé laisse l’achèvement indéterminé.
Correction proposée : aucune

### linda-041 — ok
À vérifier : [F11] regroupe trois réceptions, trois fins de PacketResponder et trois mises à jour à 07:16:28, et [F12] situe les demandes de suppression à 08:59:15.
Correction proposée : aucune

### linda-042 — ok
À vérifier : [F01] donne 9 min 17 s et [F13] regroupe trois demandes de suppression à 22:06:56 sans attester l’achèvement des opérations Deleting de [F06].
Correction proposée : aucune

### linda-043 — ok
À vérifier : [F12] regroupe les trois demandes à 11:04:44 sans ordre relatif et [F06] limite les trois Deleting à des opérations locales sans achèvement prouvé.
Correction proposée : aucune

### linda-044 — ok
À vérifier : [F11] situe trois réceptions et trois fins de PacketResponder à 07:45:45 et [F12] trois inscriptions dans invalidSet à 08:59:25, sans état final global établi.
Correction proposée : aucune

### linda-045 — ok
À vérifier : [F01] donne 34 secondes et [F10] regroupe trois réceptions, trois fins de PacketResponder et trois mises à jour blockMap à 08:30:55 sans ordre relatif.
Correction proposée : aucune

### linda-046 — ok
À vérifier : [F01] donne 29 min 02 s et [F13] situe les trois demandes dans invalidSet à 06:52:17, sans résultat final de suppression dans [F06].
Correction proposée : aucune

### linda-047 — ok
À vérifier : [F06] compte trois paquets vides et [L01][L02][L03] confirment 03:03:26 sans préciser leur rôle protocolaire ni établir de panne.
Correction proposée : aucune

### linda-048 — ok
À vérifier : [F08] compte deux réouvertures, [F03] deux ajouts de bloc déjà existant et [L01] une véritable exception PacketResponder Broken pipe, distincte des fins ordinaires E11.
Correction proposée : aucune

### linda-049 — ok
À vérifier : [F06][L01][L02][L03] attestent trois messages de paquets vides à 05:42:01 sans en expliquer le rôle ni démontrer un échec de réception.
Correction proposée : aucune

### linda-050 — ok
À vérifier : [F09] impose l’absence d’ordre à 03:32:55 et [L01][L02][L03][L04] distinguent EOFException, SocketTimeoutException et Connection reset by peer sans lien causal établi.
Correction proposée : aucune

### linda-051 — ok
À vérifier : [F21] place E20 et E21 à 11:36:57 sans ordre établi et [L01] ne permet pas d’attribuer l’absence de BlockInfo à une suppression locale.
Correction proposée : aucune

### linda-052 — ok
À vérifier : [L01] confirme BlockInfo introuvable à 09:02:33 sans établir l’état du fichier local que la question propose de rechercher.
Correction proposée : aucune

### linda-053 — ok
À vérifier : [F03][F06][F09] comptent quatre lectures, deux copies reçues et deux transmissions, tandis que [L02] concerne la demande redondante et [L01][L03] les exceptions d’envoi.
Correction proposée : aucune

### linda-054 — ok
À vérifier : [F09] compte quatre messages blockMap sans garantir quatre réplicas distincts et [L01] constate un bloc sans fichier associé à 10:46:29 sans explication.
Correction proposée : aucune

### linda-055 — ok
À vérifier : [L01][L02] confirment le même DataNode vers des clients différents à 12:43:37 et 12:44:26, et [F12] compte quatre opérations Deleting pour trois demandes dans [F14].
Correction proposée : aucune

### linda-056 — ok
À vérifier : [F04] compte quatre lectures et [L01][L02] montrent des DataNodes et clients différents à 16:42:41 et 23:39:55 sans fournir les observations côté client.
Correction proposée : aucune

### linda-057 — ok
À vérifier : [F01] donne quatre lignes sur quatre secondes et [L01] ancre l’hypothèse dans Could not read from stream à 21:29:11 sans identifier l’état du pair.
Correction proposée : aucune

### linda-058 — ok
À vérifier : [F16] regroupe réception de copie, transmission et mise à jour blockMap à 08:10:13 sans ordre établi, et [F11][F09] comptent trois demandes et quatre Deleting.
Correction proposée : aucune

### linda-059 — ok
À vérifier : [F12] situe trois E23 au 11 novembre à 04:43:39 et [F06] ne certifie pas la suppression complète malgré trois messages Deleting.
Correction proposée : aucune

### linda-060 — ok
À vérifier : [F05] décrit trois fins ordinaires de PacketResponder et [F12] trois demandes de suppression à 21:01:35, sans achèvement garanti par les Deleting de [F06].
Correction proposée : aucune
