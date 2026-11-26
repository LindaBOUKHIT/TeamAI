# Notebooks Kaggle sur GPU T4 — plateforme de calcul

- **Utilisé par / pour** : Alain et Nassim. Essai LoRA sur GPU T4 (SCRUM-61, notebook privé `wsear07/teamai-scrum61-lora`), comparaisons de SLM et runs à 3 agents sur des blocs de validation (SCRUM-42), entraînement LoRA final de 400 pas (SCRUM-39, `wsear07/teamai-scrum39-lora-final`) et évaluation du volet B sur son test réservé le 25/11 (SCRUM-45, notebooks privés `wsear07/teamai-scrum45-base-test` et `wsear07/teamai-scrum45-lora-test`). Résultat de l'essai LoRA consigné dans le [journal](../../projet/journal.md) (entrée SCRUM-29 du 08/11) et la PR [#23](https://github.com/LindaBOUKHIT/TeamAI/pull/23).
- **Temps d'appropriation constaté** : une soirée (08/11), avec trois versions du notebook avant un essai complet. La version 3 a duré environ 13 minutes. Le temps passé en heures n'a pas été relevé.
- **Ce qui a marché** :
  - Lancement du script sur T4 et suivi de l'exécution à distance.
  - Journal complet de l'exécution et liste des fichiers produits.
  - Téléchargement des sorties : adaptateur, métriques, journaux.
  - Les deux échecs ont été diagnostiqués depuis le journal de l'exécution : versions de torchvision et torchaudio à figer, puis métriques non sérialisables.
  - Résultat : 30 pas appliqués et un adaptateur GGUF exporté.
- **Ce qui a échoué ou déçu** :
  - Sur le poste d'Alain, la CLI Kaggle répondait 401 : le lancement passe par l'API de Kaggle.
  - Le nom du notebook doit inclure le propriétaire (`wsear07/…`), sinon l'enregistrement est refusé.
  - Joindre le code au script sous forme d'archive base64 (environ 64 Ko) était trop lourd. Le script télécharge maintenant les fichiers nécessaires depuis GitHub, au commit figé, et vérifie l'empreinte SHA-256 de chacun.
  - Les empreintes ne correspondaient pas tant que l'archive était construite depuis une copie de travail Windows en fins de ligne CRLF : il faut une copie en LF.
  - L'image Kaggle évolue (Python 3.13 relevé le 16/11) et le lien signé d'un fichier de sortie expire : la roue CUDA de llama.cpp doit être récupérée juste avant chaque lancement.
  - Le journal renvoyé est volumineux : il faut le lire dans un fichier.
- **Ce que la documentation omet** : le format du nom de notebook ; l'absence de moyen pratique de joindre plusieurs fichiers à un script ; l'expiration des liens de sortie ; la taille du journal renvoyé.
- **Comparaison avec l'outil utilisé avant** : avant, l'essai était lancé à la main par Nassim dans l'interface Kaggle, et les erreurs nous revenaient par message. Avec un lancement scripté, la boucle « corriger, relancer, lire le journal » se fait depuis le poste de travail. Le test du volet A ne part jamais sur Kaggle. Le test réservé du volet B y a été mesuré une seule fois, le 25/11, dans des notebooks privés, avec des entrées figées par SHA-256 et sans réglage après coup ; les entraînements et la sélection n'utilisent que train et val.
- **Verdict** : on garde Kaggle pour les essais GPU courts. Limite : la méthode repose sur un dépôt public. Avec un dépôt privé, il faudrait passer par un dataset Kaggle.
