# Relecture croisée du lot de Linda — SCRUM-36

Relecteur : Alain.

Résultat : 47 ok / 13 corrigés / 0 rejet. Contrôles `check_lots` : 0 erreur.

| Id | Motif |
|---|---|
| linda-008 | [L01][L02] montrent deux destinataires différents, `10.251.74.192` et `10.251.42.246`. La première question emploie un client au singulier. La question corrigée sur le fichier local [L03] est pertinente. |
| linda-010 | [L02][L03] visent `10.251.75.143` et `10.251.31.180`. Préciser ces deux destinations dans le résumé et la question. Le fait E27 est repris de [F12]. |
| linda-012 | [L02][L03] nomment `10.251.75.228` et `10.251.39.192`. Le résumé et la deuxième question doivent refléter les deux destinataires. Le fait E27 est repris de [F13]. |
| linda-015 | [L01][L02] visent `10.250.14.143` et `10.251.199.150`. [L03] donne déjà l’absence de fichier associé à l’instant de la demande. Interroger l’historique des métadonnées. |
| linda-018 | « Encore » suggère une présence antérieure du fichier local sur le DataNode indiqué. [F09] concerne la `blockMap` du NameNode et [L01] indique l’absence de fichier associé au bloc dans le message d’enregistrement. |
| linda-019 | [L01] à [L03] visent `10.251.126.5` et [L04] vise `10.251.203.166`. Le résumé et la question gagnent à désigner les envois au pluriel. [F12] couvre E28. |
| linda-026 | [L01][L02] confirment les deux destinations citées dans le résumé. La question suppose que chacun des clients a constaté une erreur, alors que les avertissements viennent du DataNode. |
| linda-027 | La trace E5 du même fil `5366` donne déjà l’adresse source `10.251.111.80:37547`. Demander ce qui a rendu le flux illisible garde la question centrée sur l’incertitude [L01]. |
| linda-030 | La trace E5 du même fil `24809` donne l’extrémité source `10.251.214.175:48219`. La question peut porter sur l’état de cette connexion lors de l’exception [L01]. |
| linda-048 | La question « Quel événement côté pair accompagne » présuppose un événement chez le pair, alors que [L01] et [F06] établissent uniquement une exception Broken pipe du PacketResponder sans documenter un tel événement. |
| linda-052 | [L01] confirme l’absence de BlockInfo à 09:02:33. « Encore » suppose que le fichier était auparavant présent sur le DataNode du WARN, que le message ne nomme pas. |
| linda-053 | [L01] et [L03] citent deux destinations distinctes (`10.250.10.176` et `10.251.70.37`). La première question doit couvrir les deux avertissements. [L02] concerne la demande E27. |
| linda-056 | [L01][L02] confirment les deux émetteurs, les deux destinations et les heures. Rien dans ces avertissements côté DataNode n’établit que les clients ont observé des erreurs. |
