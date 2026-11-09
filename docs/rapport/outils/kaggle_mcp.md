# Serveur MCP Kaggle — MCP

- **Utilisé par / pour** : Alain. Depuis l'agent, il lance et suit l'essai LoRA sur GPU T4 (SCRUM-61, notebook privé `wsear07/teamai-scrum61-lora`), puis récupère les sorties : adaptateur, métriques, journaux. Résultat consigné dans le [journal](../../projet/journal.md) (entrée SCRUM-29 du 08/11) et la PR [#23](https://github.com/LindaBOUKHIT/TeamAI/pull/23).
- **Temps d'appropriation constaté** : une soirée (08/11), avec trois versions du notebook avant un essai complet. La version 3 a duré environ 13 minutes. Le temps passé en heures n'a pas été relevé.
- **Ce qui a marché** :
  - Enregistrement et lancement du script sur T4.
  - Suivi de l'état, journal complet et liste des fichiers produits.
  - Téléchargement des sorties.
  - Les deux échecs ont été diagnostiqués depuis le journal de l'exécution : versions de torchvision et torchaudio à figer, puis métriques non sérialisables.
  - Résultat : 30 pas appliqués et un adaptateur GGUF exporté.
- **Ce qui a échoué ou déçu** :
  - Sur cette machine, la CLI Kaggle répondait 401 : le serveur MCP a servi de solution de contournement.
  - Le nom du notebook doit inclure le propriétaire (`wsear07/…`), sinon l'enregistrement est refusé.
  - Passer le code dans le script sous forme d'archive base64 (environ 64 Ko) était trop lourd pour le contexte de l'agent. Le script télécharge maintenant les fichiers nécessaires depuis GitHub, au commit figé, et vérifie l'empreinte SHA-256 de chacun.
  - Les empreintes ne correspondaient pas tant que l'archive était construite depuis une copie de travail Windows en fins de ligne CRLF : il faut une copie en LF.
  - Le journal renvoyé est volumineux : il faut le lire dans un fichier plutôt que dans la conversation.
- **Ce que la documentation omet** : le format du nom de notebook ; l'absence de moyen pratique de joindre plusieurs fichiers à un script ; la taille du journal renvoyé.
- **Comparaison avec l'outil utilisé avant** : avant, l'essai était lancé à la main par Nassim dans l'interface Kaggle, et les erreurs nous revenaient par message. Avec le MCP, la boucle « corriger, relancer, lire le journal » se fait dans la même session. Seules les traces train sont envoyées ; aucune donnée val ou test ne part sur Kaggle.
- **Verdict** : on garde ce serveur pour les essais GPU courts. Limite : la méthode repose sur un dépôt public. Avec un dépôt privé, il faudrait passer par un dataset Kaggle.
