# Proposition de projet NLP 2

**Assistant de support : classification en navigateur et réponse sourcée par SLM multi-agent**  
Groupe TeamAI : Alain, Nassim, Bachar et Linda  
Proposition du 21 septembre 2026

## 1. Problématique et intérêt du projet

Les demandes adressées à un service de support sont souvent formulées de manière variable et parfois incomplète. Leur traitement nécessite d'identifier l'intention, de retrouver une procédure pertinente et de formuler une réponse qui respecte les informations disponibles.

Nous proposons deux applications indépendantes sur ce domaine : une application web de classification des demandes et une application locale de préparation de réponses sourcées. L'objectif scientifique est d'étudier dans quelle mesure un petit modèle de langage (SLM), adapté au domaine et organisé en plusieurs agents spécialisés, améliore la qualité des réponses par rapport au même modèle utilisé dans une chaîne simple.

Le projet mobilise la classification de texte, les représentations vectorielles, la recherche documentaire, la génération conditionnée par des sources, l'adaptation d'un modèle et l'évaluation expérimentale. Le gain apporté par le multi-agent constitue une hypothèse à tester.

## 2. Données et périmètre initial

Nous envisageons un corpus public de demandes de support disponible sur Kaggle. Un premier candidat est **Bitext Gen AI Chatbot Customer Support Dataset**. La fiche publiée par Bitext présente des données en anglais, avec des champs de demande, catégorie, intention et réponse. Ce candidat n'a pas encore été téléchargé ni audité par notre groupe ; son adoption reste conditionnée à la vérification de la version, de la licence, des doublons et de la qualité des annotations.

Pour maîtriser la charge de travail, nous proposons un premier périmètre de **6 à 8 intentions**, **3 000 à 5 000 demandes au maximum**, et une seule langue de traitement, l'anglais. Les intentions exactes seront fixées après inspection du corpus. L'interface et le rapport pourront être rédigés en français.

Nous distinguerons deux ressources :

- Le jeu de demandes annotées, utilisé pour entraîner et évaluer la classification, ainsi que pour préparer l'adaptation du SLM.
- Une base documentaire de **20 à 40 fiches de procédures**, rédigées et validées par le groupe pour un service fictif. Chaque fiche disposera d'un identifiant stable et constituera une source de référence pour le RAG.

Les réponses du dataset ne seront pas considérées automatiquement comme des règles métier fiables. Les exemples d'adaptation seront alignés sur les procédures du service fictif. Le système proposera uniquement des réponses : il ne réalisera aucune opération réelle sur des commandes, comptes ou paiements.

## 3. Volet A — Application web de classification

L'utilisateur pourra saisir une demande ou importer un fichier CSV. L'application affichera l'intention prédite, les trois classes les mieux classées et leurs scores, ainsi qu'un tableau exportable pour le traitement par lot. Ces scores seront présentés comme des sorties du modèle, sans les assimiler à des probabilités calibrées.

Nous entraînerons un petit modèle de classification, de type BiLSTM, sur le corpus sélectionné. Une référence TF-IDF avec régression logistique permettra de vérifier l'intérêt du modèle neuronal. Le modèle retenu sera exporté en ONNX et exécuté dans le navigateur avec ONNX Runtime Web. L'export et la cohérence entre prédictions Python et navigateur seront testés dès le premier prototype.

Le site sera public, hébergé gratuitement sous forme de fichiers statiques. Le traitement des demandes s'effectuera côté client, sans serveur d'inférence ni API payante. Ce volet correspond à une adaptation du cas A1 au domaine du support client, soumise à validation pédagogique.

## 4. Volet B — Application locale avec SLM, RAG et agents spécialisés

L'application locale préparera une réponse courte à partir d'une demande et des procédures retrouvées. Elle affichera la réponse, les références utilisées et, lorsque l'information manque, une demande de précision ou une abstention.

Le modèle candidat est **SmolLM2-1.7B-Instruct**, sous réserve d'un essai sur la machine disponible. Nous prévoyons une adaptation supervisée légère par **LoRA**, sur des exemples contrôlés de réponse avec sources et d'abstention. Le RAG et les consignes de rôle ne seront pas présentés comme un substitut à cette adaptation des paramètres.

L'architecture comprendra trois agents logiques partageant une même instance de modèle :

| Agent | Responsabilité et décisions autorisées |
|---|---|
| Recherche | Reformuler la demande, appeler l'outil de recherche et sélectionner les passages pertinents ; signaler les informations manquantes. |
| Rédaction | Construire une réponse à partir des passages sélectionnés, avec leurs identifiants ; proposer une clarification lorsque nécessaire. |
| Contrôle | Examiner l'appui des affirmations sur les sources et décider d'accepter, de demander une correction ou de s'abstenir. |

Un orchestrateur Python gérera les échanges structurés, les outils autorisés et la limite d'exécution. Une seule boucle de correction sera autorisée, avec au plus cinq appels au SLM par demande. Les agents s'exécuteront successivement afin d'éviter de charger plusieurs copies du modèle. Les références seront également contrôlées par du code ; l'avis de l'agent de contrôle ne constituera pas une preuve d'exactitude.

La recherche reposera sur des embeddings et un index local des fiches. Une interface locale affichera les résultats et une trace concise des étapes. Les deux applications ne communiqueront pas entre elles ; elles partageront uniquement le domaine, les données préparées et une partie du protocole d'évaluation.

## 5. Protocole d'évaluation

Les données seront dédupliquées puis séparées en apprentissage, validation et test. Les formulations très proches seront regroupées autant que possible avant la séparation pour limiter les fuites. Le jeu de test ne sera utilisé ni pour l'adaptation, ni pour le réglage des prompts ou des seuils.

Pour le volet A, nous mesurerons la macro-F1, les performances par classe, la matrice de confusion, la taille du modèle et la latence dans le navigateur, en distinguant chargement initial et exécution après mise en cache.

Pour le volet B, nous constituerons un jeu de **100 demandes de test**, dont environ 20 hors périmètre ou insuffisamment renseignées. Les fiches documentaires attendues et les éléments nécessaires à une réponse correcte seront annotés. Quatre configurations permettront de séparer les contributions :

1. SLM initial sans RAG.
2. SLM initial avec RAG et un seul agent.
3. SLM adapté avec RAG et un seul agent.
4. SLM adapté avec RAG et trois agents.

Les comparaisons conserveront les mêmes questions, le même corpus documentaire et des paramètres de génération fixés. Nous mesurerons la récupération de la bonne fiche dans les trois premiers résultats, l'exactitude des réponses, l'appui des affirmations sur les sources, l'abstention correcte, les abstentions injustifiées, la latence et la mémoire maximale. Le coût supplémentaire en appels sera rapporté pour le multi-agent.

Une grille humaine commune évaluera les réponses. Un sous-ensemble de 30 demandes, pour les quatre configurations, sera évalué indépendamment par deux membres puis arbitré en cas de désaccord. Nous ne supposerons pas qu'un système multi-agent surpasse automatiquement un système simple : une absence de gain sera un résultat documenté.

## 6. Organisation du groupe

Le groupe est composé d'Alain, Nassim, Bachar et Linda. Les responsabilités proposées sont les suivantes ; leur attribution nominative reste à convenir entre les quatre membres et sera inscrite dans le tableau de tâches. Les numéros ci-dessous ne préjugent pas de cette attribution.

| Membre | Responsabilité principale | Binôme secondaire |
|---|---|---|
| 1 | Audit du corpus, préparation des données et séparation des jeux | Protocole et annotations avec le membre 4 |
| 2 | Entraînement du classifieur, export ONNX et application web | Données avec le membre 1 |
| 3 | Inférence locale, adaptation LoRA et intégration du RAG | Orchestration avec le membre 4 |
| 4 | Orchestration multi-agent, interface locale et évaluation | Tests web avec le membre 2 |

Tous les membres participeront aux revues, à la documentation et à la préparation de la soutenance. Le groupe dispose du dépôt Git [TeamAI](https://github.com/LindaBOUKHIT/TeamAI). Le tableau de tâches n'est pas encore créé. Nous prévoyons un board associé au dépôt, avec les colonnes « À faire », « En cours », « À relire » et « Terminé », ainsi qu'un journal partagé des expériences et des usages d'IA. Chaque ticket précisera son responsable, son échéance et son critère de validation.

## 7. Faisabilité et calendrier

Le SLM sera exécuté localement sur la machine d'un membre du groupe. Ses caractéristiques restent à relever : système, processeur, RAM, carte graphique et VRAM disponible. Pour le modèle de 1,7 milliard de paramètres, le stockage brut des seuls poids représente environ **0,85 Go en 4 bits** ou **3,4 Go en 16 bits**, hors métadonnées, cache, activations et bibliothèques. Ces valeurs ne sont pas une estimation de la mémoire totale nécessaire. L'entraînement LoRA fera l'objet d'un essai distinct de l'inférence ; un succès en inférence ne garantit pas la faisabilité de l'adaptation.

- **21 septembre :** proposition, répartition initiale, déclaration de l'environnement et mise en place ou vérification des accès au board.
- **Sous 48 heures :** audit du corpus, choix des intentions, inventaire matériel, première inférence et test d'export navigateur. Vérification de l'accès à un GPU pour l'adaptation.
- **1er octobre :** version web minimale déployée, première inférence locale aboutie, tag Git et capture du board.
- **16 octobre :** volet A fonctionnel, adaptation engagée, première chaîne multi-agent et protocole de test figé.
- **Avant le 7 décembre :** expériences comparatives, rapport, supports et vidéo de secours ; site final en ligne avant la soutenance.

Le 1er octobre est retenu comme échéance de mi-parcours d'après la date explicite et le tableau du sujet, malgré la mention « mi-octobre » dans son intitulé.

## 8. Risques et critères de réussite

Les principaux risques sont les doublons et formulations artificielles du corpus, l'insuffisance du matériel pour l'adaptation, la fragilité de l'export ONNX et le surcoût des agents. Nous les traiterons en priorité par un audit limité du dataset, un essai matériel précoce, un prototype navigateur et une orchestration strictement bornée. Si nécessaire, nous réduirons la taille du modèle, le corpus d'adaptation et la longueur de contexte. Nous conserverons l'objectif d'adaptation et signalerons rapidement à l'enseignant toute impossibilité matérielle persistante.

Le projet sera considéré comme livré si les deux applications fonctionnent, si l'adaptation du SLM est mesurée avant et après sur un test réservé, et si la contribution des agents est évaluée face à une référence simple. Aucune performance chiffrée n'est annoncée avant expérimentation.

Nous sollicitons la validation du cas d'usage proposé, du périmètre anglophone et de l'organisation à quatre membres, le document de cadrage mentionnant des équipes de cinq.

## Références techniques

- [Dataset candidat sur Kaggle](https://www.kaggle.com/datasets/bitext/bitext-gen-ai-chatbot-customer-support-dataset).
- [Fiche du dataset publiée par Bitext](https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset).
- [Fiche du modèle SmolLM2-1.7B-Instruct](https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B-Instruct).
- [Documentation ONNX Runtime Web](https://onnxruntime.ai/docs/tutorials/web/).
- [Adaptation LoRA avec PEFT](https://huggingface.co/docs/peft/main/en/conceptual_guides/lora).

Les références identifient des candidats techniques. Le corpus et le modèle n'ont pas encore été validés expérimentalement par le groupe.
