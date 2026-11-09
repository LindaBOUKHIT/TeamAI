# TEAMAI — Rapport du projet NLP 2

Détection et aide à l’interprétation d’anomalies dans les journaux HDFS

Master 2 Data & Intelligence Artificielle  
Alain Evina · Bachar Ben Slama · Linda Boukhit · Nassim Mezzai

**Version 1 — brouillon de travail, 09/11/2026**

Les sections marquées « À rédiger » sont attendues des personnes nommées. Les contenus issus de PR non fusionnées sont signalés « en relecture, PR #n ». Ce document ne vaut pas validation collective.

Les chapitres 1 et 2 reprennent le texte du V0.1 de Linda (SCRUM-33), avec remise en forme et actualisations factuelles signalées. Source de ces deux chapitres : [rapport V0.1](TeamAI_Rapport_SCRUM33_V0.1.pdf). Les sources des ajouts sont précisées à leur emplacement. Les résultats finaux et les validations collectives restent à compléter.

## 1. Introduction et cadrage du projet

### 1.1 Contexte et problématique

Les systèmes informatiques distribués produisent de nombreux journaux d’événements (logs) qui retracent leur fonctionnement. Leur analyse permet de repérer des comportements inhabituels et d’aider à l’investigation d’incidents. Dans Hadoop Distributed File System (HDFS), les séquences d’événements associées aux blocs constituent une source d’information exploitable pour la détection d’anomalies.

Le projet TeamAI explore deux approches complémentaires : la classification automatique de traces HDFS à l’aide d’un modèle entraîné par l’équipe, puis l’aide à l’interprétation à partir d’un petit modèle de langage préentraîné, adapté et enrichi de documentation.

Problématique : comment détecter des anomalies dans les journaux HDFS et proposer une interprétation exploitable, tout en comparant la qualité, les ressources et le degré de maîtrise de deux approches d’intelligence artificielle ?

### 1.2 Objectifs

- Préparer un corpus HDFS reproductible et documenter ses partitions.
- Développer un classifieur normal/anomalie et le comparer à une baseline simple.
- Déployer une application web publique exécutant le modèle dans le navigateur, sans serveur d’inférence payant.
- Expérimenter un SLM local, son adaptation LoRA, un RAG documentaire et une organisation multi-agents.
- Comparer coût, latence, qualité, contrôle, explicabilité et dépendance fournisseur.

### 1.3 Périmètre

| Volet A — application web | Volet B — application locale |
|---|---|
| Classification binaire de traces HDFS complètes. Modèle BiLSTM envisagé, export ONNX et inférence dans le navigateur. | Interprétation de traces à l’aide d’un SLM open-weights, d’une adaptation LoRA, de récupération documentaire (RAG) et d’agents spécialisés. |
| Entrée : logs HDFS au format documenté. Sortie : classe et résultat exportable. | Entrée : trace HDFS. Sortie : analyse distinguant faits, hypothèses et informations manquantes, avec sources. |

Hors périmètre : supervision temps réel, collecte sur infrastructure de production, prise en charge de tous les formats de logs, correction automatique d’incidents et diagnostic causal garanti. Les deux applications restent utilisables indépendamment.

### 1.4 Hypothèses et contraintes

- Le corpus HDFS_v1 permet de construire des ensembles d’apprentissage, validation et test pertinents ; les déséquilibres et séquences répétées doivent être examinés.
- Le volet A doit respecter un budget d’hébergement nul et réaliser l’inférence côté client.
- Le volet B dépend du matériel disponible : la machine cible est désormais celle de Nassim, avec une RTX 3050 Laptop de 6 Go. Actualisation SCRUM-63 : journal de branche, entrée du 27/10/2026 (en relecture, PR [#41](https://github.com/LindaBOUKHIT/TeamAI/pull/41)) et trace SCRUM-63 (en relecture, PR [#40](https://github.com/LindaBOUKHIT/TeamAI/pull/40)). Le [relevé matériel](../projet/environnements.md) confirme ce GPU.
- Les évaluations doivent distinguer observations expérimentales, hypothèses et fonctionnalités encore prévues.

### 1.5 Risques et réponses prévues

| Risque | Réponse prévue |
|---|---|
| Fuite de données ou performance surestimée | Séparer par bloc, contrôler les répétitions, réserver le test final et rapporter les résultats sur séquences inédites. |
| Incompatibilité ou lenteur du modèle web | Vérifier tôt la parité Python / ONNX Runtime Web, puis optimiser la taille et le chargement. |
| SLM trop lent ou trop gourmand | Mesurer CPU/RAM/latence ; tester la quantification et, si nécessaire, des ressources GPU pour l’adaptation. |
| Interprétations non fiables | Évaluer les faits et les sources ; intégrer RAG, contrôle et possibilité d’abstention. |
| Retards et dépendances entre tâches | Utiliser Jira, des responsables identifiés, des revues croisées et un journal des décisions. |

### 1.6 Critères de réussite

- Application A publique, fonctionnelle, exécutant réellement un modèle dans le navigateur.
- Préparation des données reproductible et métriques finales sur un test réservé : précision, rappel, macro-F1 et matrice de confusion.
- Application B locale fournissant des interprétations sourcées et explicitant ses incertitudes.
- Adaptation effective du SLM, comparaison avant/après et mesure de l’apport du RAG et des agents.
- Scripts, configurations, décisions et limites suffisamment documentés pour reproduire les démonstrations.

Ces critères décrivent les objectifs du projet ; ils ne constituent pas des résultats déjà atteints.

## 2. Organisation et méthodologie

### 2.1 Équipe et responsabilités

| Membre | Domaine principal | Contribution croisée |
|---|---|---|
| Nassim Mezzai | Audit HDFS, parsing, splits et évaluation | Relecture des données et du classifieur |
| Bachar Ben Slama | Classification, export ONNX, application web | Contrôle des données et tests navigateur |
| Alain Evina | SLM, adaptation LoRA, expérimentation et rapport | Relecture du RAG et des agents |
| Linda Boukhit | Corpus documentaire, RAG, orchestration et interface locale | Évaluation et coordination des interfaces |

Cette répartition est issue du cadrage initial et de la feuille de route ; elle doit être ajustée aux contributions effectivement réalisées et validée par le groupe.

### 2.2 Planification et jalons

| Jalon | Date | Attendu |
|---|---|---|
| J2 | 21/09/2026 | Cadrage, étude des volets et organisation. |
| Mi-parcours | 01/10/2026 | Version minimale du volet A et première inférence locale. |
| J3 | 16/10/2026 | Volet A fonctionnel, adaptation engagée, supports préparés, rapport commencé. |
| Rapport V1 (interne) | Fin novembre 2026 | Consolidation du PDF et des expériences. |
| J4 — soutenance | 07/12/2026 | Présentation et démonstration des deux volets. |

Le jalon de mi-parcours a été déclaré non tenu dans la feuille de route du 6 octobre. Un sprint de rattrapage a donc été planifié. Cette situation doit être décrite sans confondre les objectifs initiaux avec les livrables effectivement disponibles.

### 2.3 Pilotage, Git et traçabilité

L’équipe utilise Jira pour structurer les tâches en epics et sprints, avec responsable, relecteur et critère de fin. Le dépôt GitHub TeamAI conserve les scripts, la documentation et les preuves expérimentales. La branche main est destinée à la production ; dev sert à l’intégration ; les travaux sont développés sur des branches dédiées aux tickets et soumis par Pull Request.

Les décisions et les usages d’assistants IA sont consignés dans docs/projet/journal.md. La feuille de route rappelle que Jira constitue la source de vérité pour l’état des tâches. Le journal consulté ne contient pas encore de compte rendu de réunion attesté : les pratiques collectives devront donc être documentées avec précision plutôt que supposées.

### 2.4 Préparation du corpus HDFS

La préparation s’appuie sur HDFS_v1 (Loghub). Les lignes brutes sont associées à des identifiants de blocs (blk_) puis transformées en séquences d’événements, issues de 29 templates. L’audit, le parsing et la séparation apprentissage/validation/test ont fait l’objet de travaux spécifiques.

Le protocole retenu sur dev sépare les blocs de manière stratifiée ; il signale également les séquences inédites (unseen_seq) afin de compléter l’interprétation des métriques. Les exemples publics de l’application doivent provenir de la validation et non du test réservé. Le test final n’est pas utilisé pour régler les modèles.

### 2.5 Développement et évaluation du volet A

La démarche compare d’abord une baseline simple à un modèle BiLSTM, puis vérifie l’export ONNX et la cohérence de l’inférence entre Python et le navigateur. Les mesures pertinentes comprennent précision, rappel, macro-F1, faux positifs, faux négatifs, taille du modèle et latence côté client.

Une baseline par régression logistique est documentée dans SCRUM-24. Un essai de parité Python / navigateur a été mené sur un BiLSTM jouet à poids aléatoires : il vérifie la compatibilité technique de l’export, mais ne démontre pas les performances du modèle final entraîné.

### 2.6 Développement et évaluation du volet B

Le volet B commence par une inférence locale avec SmolLM2-1.7B-Instruct, puis examine la quantification, l’adaptation LoRA, l’intégration du RAG et l’intérêt d’agents de recherche, rédaction et contrôle. Les comparaisons prévues doivent utiliser des jeux réservés et un protocole comparable, en mesurant notamment la fidélité aux faits, la pertinence des sources, l’abstention, la latence et la mémoire.

Actualisation : le modèle courant devient Gemma 4 E4B QAT sous llama.cpp (SCRUM-63), avec la machine de Nassim pour cible ; l’essai d’entraînement LoRA a abouti sur T4 Kaggle, tandis que l’inférence avec adaptateur sur RTX 3050 reste à faire (SCRUM-29/61). Sources : trace SCRUM-63 (en relecture, PR [#40](https://github.com/LindaBOUKHIT/TeamAI/pull/40)) et journal SCRUM-29, entrée du 08/11/2026 (en relecture, PR [#23](https://github.com/LindaBOUKHIT/TeamAI/pull/23)).

Les premières expériences montrent des temps de génération élevés sur CPU et des interprétations incomplètes ou inventées. Un essai GGUF 4 bits a réduit la mémoire observée et amélioré le débit dans une configuration donnée, mais le journal précise que ces mesures ne constituent pas une comparaison contrôlée. Les conclusions devront être confirmées sur plusieurs traces.

### 2.7 Reproductibilité et limites

Chaque expérience doit documenter la date, le responsable, le code, les données, les paramètres, la machine, les résultats et les erreurs. Les métriques finales, la validation collective des choix et les retours d’expérience individuels seront ajoutés après vérification. Aucune conclusion générale ne doit être tirée d’une seule trace ou d’un essai de faisabilité.

## 3. Présentation des solutions développées

### 3.1 Volet A — classification et application web

**À rédiger par Bachar.**

**Éléments attestés à reprendre**

- **SCRUM-24 — baseline.** Régression logistique. Les résultats de référence publiés par Nassim sont repris dans `eval/results/SCRUM-25-bilstm-v1/metrics.json`, champ `baseline_reference`. Sur la validation globale : macro-F1 **0,9897**, précision anomalie **0,9608**, rappel anomalie **1,0000**, **103** fausses alertes et **0** anomalie manquée. Sur les **1 929** blocs de validation à séquence inédite : macro-F1 **0,9618**. La baseline n’a pas été réentraînée pour cette comparaison. Source : [métriques SCRUM-25](../../eval/results/SCRUM-25-bilstm-v1/metrics.json).
- **SCRUM-25 — métriques de VALIDATION.** Au seuil **0,9900**, sur **86 259** blocs : macro-F1 **0,9955**, précision anomalie **0,9909**, rappel anomalie **0,9917**, **23** fausses alertes et **21** anomalies manquées. Sur les **1 929** blocs à séquence inédite : macro-F1 **0,9767**, précision anomalie **0,9646**, rappel anomalie **0,9682**. Source : `eval/results/SCRUM-25-bilstm-v1/metrics.json`, champs `validation`, `unseen` et `threshold`.
- **SCRUM-62 — seuil orienté rappel.** Sans changer les poids, le candidat **0,4081** donne sur la validation globale **1** anomalie manquée et **59** fausses alertes ; rappel anomalie **0,9996**, F1 anomalie **0,9883**, macro-F1 **0,9939**. Sur la validation inédite : **1** anomalie manquée, **41** fausses alertes, rappel **0,9981**, macro-F1 **0,9734**. Source : [analyse du seuil](../../eval/results/SCRUM-62_20261023T153242Z_690fcb/analysis.json), `candidates.max_fn_1.all_validation` et `candidates.max_fn_1.unseen`. Les seuils affichés ici sont arrondis ; les valeurs exactes restent dans le JSON.
- **SCRUM-62 — vérification navigateur.** WASM, modèle issu du cache, **10** cas distincts, batchs **1, 3 et 10**, **0** désaccord de classe ; vérification attribuée à Bachar dans `verified_by`. Source : [relevé navigateur](../../eval/results/SCRUM-62_20261023T153242Z_690fcb/browser_check.json). Ce relevé ne mesure ni latence ni mémoire. L’analyse porte `metadata_updated: false`, alors que le journal annonce des métadonnées actualisées : la version finale et son seuil doivent être identifiés pour SCRUM-44. Sources : même dossier, `analysis.json`, et [journal, entrée SCRUM-62](../projet/journal.md).

### 3.2 Volet B — interprétation locale

Rédaction : Alain ; contributions RAG et agents : Alain/Linda selon la répartition du ticket. Les responsabilités prévues ne valent pas relecture effectuée.

#### SLM et choix de Gemma — SCRUM-63

Le SLM explique les événements d’un bloc. Il ne remplace pas le détecteur binaire du volet A. Le modèle retenu est `google/gemma-4-E4B-it-qat-q4_0-gguf`, fichier `gemma-4-E4B_q4_0-it.gguf`, révision `4b4a2c1d584be7264f87aac328a1bc739ce81b6c`. Le choix repose sur l’exploration des réponses et leur conformité relative. Il ne démontre pas leur vérité générale. Source : trace SCRUM-63, choix du modèle (en relecture, PR [#40](https://github.com/LindaBOUKHIT/TeamAI/pull/40)).

Le prompt v16 est figé. La configuration utilise llama.cpp, réflexion désactivée, contexte de **4 096 tokens**, réponse de **800 tokens** au maximum, température **0**, seed **42** et pénalité de répétition **1,0**. La cible locale est le portable de Nassim : Ryzen 5 8645HS, **32 Go** de RAM, RTX 3050 Laptop **6 Go**. Les versions logicielles et les mesures locales restent à relever. Source : trace SCRUM-63 (en relecture, PR [#40](https://github.com/LindaBOUKHIT/TeamAI/pull/40)).

Les faits sont calculés depuis les lignes HDFS. Le glossaire est limité aux codes présents. Le schéma JSON transmis par `response_format` comporte `resume_evenements`, `faits_observes`, `hypotheses`, `infos_manquantes`, `sources` et `abstention`. Les hypothèses sont facultatives et limitées à des causes autorisées et ancrées. Les références F/T/L renvoient aux faits, à la chronologie et aux lignes. Dans cette configuration, `sources: []` est imposé : aucun document RAG n’est injecté. Les contrôles vérifient la forme, la copie des faits et les références ; ils ne prouvent pas la fidélité de toute la prose. Source : trace SCRUM-63, réglage et port (en relecture, PR [#40](https://github.com/LindaBOUKHIT/TeamAI/pull/40)).

Une correction unique est possible ; les deux réponses brutes sont conservées. Le port ajoute le rejet de **six** répétitions consécutives ou d’une réponse atteignant **95 %** du budget, soit **760/800 tokens**. Cet ajout est postérieur à la validation historique. Son effet correctif n’est pas mesuré dans les résultats copiés. Source : trace SCRUM-63, contrôle supplémentaire (en relecture, PR [#40](https://github.com/LindaBOUKHIT/TeamAI/pull/40)).

#### Historique SmolLM2 — SCRUM-28/57

SmolLM2-1.7B-Instruct a permis la première inférence locale sur CPU ; le cas documenté omet les avertissements et invente des informations ([preuve SCRUM-28](../../eval/results/SCRUM-28/README.md)).  
Le banc GGUF de SCRUM-57 a montré une réduction de mémoire, mais l’ordre de la consigne provoquait parfois une recopie des logs (journal de branche, entrées SCRUM-57 (en relecture, PR [#41](https://github.com/LindaBOUKHIT/TeamAI/pull/41))).  
Ces mesures restent historiques ; les différences de backend, quantification et protocole empêchent d’en déduire un gain contrôlé vers Gemma (trace SCRUM-63 (en relecture, PR [#40](https://github.com/LindaBOUKHIT/TeamAI/pull/40))).

#### Adaptation LoRA — SCRUM-29/61

L’essai courant charge `google/gemma-4-E4B-it-qat-q4_0-unquantized`, révision `476025a01dbf99361c062bbeca3d6a76bb4c4566`, en texte seul. Les réglages sont QLoRA NF4, calcul fp16, batch **1**, gradient checkpointing et rang **8** sur `q_proj`/`v_proj`. Les **20** exemples proviennent du train et du prompt v16. Leur relecture reste à refaire : les champs `reviewed_by` sont vides. Source : journal SCRUM-29, entrée du 27/10/2026 (en relecture, PR [#23](https://github.com/LindaBOUKHIT/TeamAI/pull/23)).

Les premiers essais T4 ont rencontré un dépassement mémoire et des gradients non finis. Les corrections portent sur la loss du suffixe supervisé et la gestion de GradScaler. Les versions de bibliothèques ont aussi dû être alignées. Le journal du **08/11/2026** décrit ensuite l’essai Kaggle au commit `c7947c1` : **30** pas appliqués, **0** sauté, échelle **1024** stable, loss moyenne **0,586** sur les **5** premiers pas et **0,052** sur les **5** derniers. Le coût est de **4,9 s/pas**, avec un pic VRAM de **10,24 Gio**, dont **8,63 Gio** au chargement, et **2 269 184** paramètres entraînables. Ces pertes concernent les exemples d’entraînement. Elles attestent une faisabilité, sans établir la qualité des explications. Source : journal SCRUM-29, essai T4 du 08/11/2026 (en relecture, PR [#23](https://github.com/LindaBOUKHIT/TeamAI/pull/23)).

L’adaptateur PEFT a été rechargé puis converti en GGUF F16 de **4,5 Mo** avec llama.cpp au commit `0c1e57098`. La conversion couvre `q_proj` sur **42** couches et `v_proj` sur les couches **0 à 23** ; les **18** dernières partagent le cache KV et n’ont pas de `v_proj`. Source : même entrée du journal SCRUM-29 (en relecture, PR [#23](https://github.com/LindaBOUKHIT/TeamAI/pull/23)).

Le transfert de l’adaptation entraînée en NF4 vers la base d’inférence GGUF Q4_0 reste une réserve. L’inférence avec l’adaptateur sur la RTX 3050 n’est pas faite ; elle relève de SCRUM-61. Aucun gain LoRA sur la qualité n’est donc établi. Sources : journal SCRUM-29 (en relecture, PR [#23](https://github.com/LindaBOUKHIT/TeamAI/pull/23)) et fiche PEFT/QLoRA (en relecture, PR [#42](https://github.com/LindaBOUKHIT/TeamAI/pull/42)).

#### RAG à un agent — SCRUM-37

La chaîne de référence suit le parcours trace → requête → passages C6 → `generate()` → contrôle C5. Le retrieval combine un index FAISS dense, BM25 et une fusion par Reciprocal Rank Fusion. Les événements sont paraphrasés en anglais depuis les templates. Le corpus retient **51** passages découpés par section. Sources : [journal, entrée SCRUM-37](../projet/journal.md) et [corpus RAG](../volet_b/corpus_rag.md).

Sur **306** traces de validation de `data/sample`, avec **k = 3**, l’hybride atteint un rappel traces de **0,6644** et retrouve **6/10** templates de référence. BM25 seul atteint **0,6948** ; le dense avec paraphrases atteint **0,3481**. Ces résultats mesurent le retrieval, pas la fidélité des explications. Source : [retrieval de validation](../../eval/results/SCRUM-37/retrieval_val.json), variantes `hybrid`, `bm25` et `dense` avec `query: description`.

La référence et les paraphrases viennent de l’équipe. Les traces répètent peu de séquences distinctes. Les passages généraux, notamment « Safemode », peuvent remonter sans être utiles. Le seuil `min_score` n’a pas été activé, car les scores pertinents et non pertinents se chevauchent. L’agent complet est décrit comme vérifié en mode factice ; la qualité avec le SLM réel reste à mesurer. Source : [journal, entrée SCRUM-37](../projet/journal.md). Cette chaîne et la v16 sans RAG sont des configurations distinctes.

#### Agents spécialisés — SCRUM-42

L’organisation à **trois rôles**, recherche, rédaction et contrôle, est **en cours**. Elle n’est pas livrée à ce jour dans le périmètre de cette V1. Aucun gain ne peut lui être attribué. Source pour les rôles et la planification : [V0.1](TeamAI_Rapport_SCRUM33_V0.1.pdf), section 2.6, et [feuille de route](../projet/feuille_de_route.md), sprint « Agents & évaluation ». Au 09/11, le ticket SCRUM-42 est ouvert et aucune PR n’est déposée.

#### Défauts observés — SCRUM-46

Les comptes ci-dessous portent sur **40 nouveaux blocs de validation**, issus de `data/sample`, après exclusion des blocs déjà connus. Ils concernent la v16 sans RAG et sans adaptation LoRA évaluée. Les défauts peuvent se recouper ; leurs fréquences ne s’additionnent pas. Sources : défauts et feuille de route, sections 1 et 2 (en relecture, PR [#41](https://github.com/LindaBOUKHIT/TeamAI/pull/41)) et trace SCRUM-63, validation unique (en relecture, PR [#40](https://github.com/LindaBOUKHIT/TeamAI/pull/40)).

| Constat sur la validation | Fréquence | Source précise dans la synthèse SCRUM-46 |
|---|---:|---|
| Erreur de chronologie | 2/40 | Section 2.1, revue Q : `summary.other_chronology_error_cases` |
| Lien causal non démontré | 3/40 | Section 2.1, Q : `summary.unsupported_causal_link_cases` |
| Cause indéterminée non explicitée dans le résumé | 16/40, soit les 16 cas concernés | Section 2.1, Q : `summary.unknown_cause_statement_missing_in_summary_count` |
| Pseudo-référence | 3/40 | Section 2.1, Q : `summary.pseudo_reference_cases` |
| Résumé inutilisable par répétition | 1/40 | Section 2.2, Q : `summary.unusable_repetition_cases` |
| Référence inexistante | 1/40 avant correction ; 0/40 après | Section 2.2, V : `responses_with_unknown_references`, première réponse puis finale |
| Contrat JSON non respecté | 0/40 avant et après correction | Section 2.2, V : `contract_ok` |
| Réponse passant les contrôles factuels du runtime | 39/40 | Section 2.2, V : `runtime_factual_checks_ok` |

Source de toutes les lignes : synthèse SCRUM-46 (en relecture, PR [#41](https://github.com/LindaBOUKHIT/TeamAI/pull/41)). Les chemins Q et V y désignent respectivement `eval/results/SCRUM-63/revue_qualitative_validation.json` et `eval/results/SCRUM-63/comparaison_v16_validation.json`, livrés par la PR #40. Ces comptes sont repris de la synthèse, sans nouvelle inspection des réponses brutes.

Les **40/40** copies de faits exactes ne couvrent pas toute la prose. La revue distingue aussi **4** réponses avec hypothèse, parmi **21** blocs avec indice d’incident. Cela ne constitue pas un taux d’erreur. La précision des citations et l’utilité des questions ne sont pas mesurées exhaustivement. Source : SCRUM-46, sections 2.1 et 2.2 (en relecture, PR [#41](https://github.com/LindaBOUKHIT/TeamAI/pull/41)).

### 3.3 Données et évaluation

**À rédiger par Nassim.**

**Éléments attestés à reprendre**

- **HDFS_v1.** Présenter la provenance Loghub, les blocs, les labels, le parsing et les séquences d’événements. Distinguer anomalie annotée et cause de panne. Sources : [V0.1, section 2.4](TeamAI_Rapport_SCRUM33_V0.1.pdf) et [contrats C1/C2/C4](../contrats.md).
- **C4-bloc.** Le protocole de référence est stratifié par label, bloc par bloc : **70/15/15**, seed **42**. Un bloc appartient à un seul split. Les **575 061** blocs ne représentent que **18 373** séquences uniques ; des séquences identiques peuvent donc apparaître entre partitions. Source : [contrats, C4](../contrats.md).
- **Séquences inédites.** Le champ `unseen_seq` du fichier C4 indique, pour le test, une séquence absente du train ; il vaut faux par convention ailleurs. Les métriques finales doivent présenter le jeu global et ce sous-ensemble. Le champ `unseen` des métriques de validation SCRUM-25 est une analyse distincte à documenter explicitement. Sources : [contrats, C4](../contrats.md) et [métriques SCRUM-25](../../eval/results/SCRUM-25-bilstm-v1/metrics.json).
- **Réservation des données.** Aucun seuil, prompt, exemple de démonstration ou hyperparamètre ne doit être choisi sur le test. Le label et la réponse attendue ne sont transmis ni au SLM ni au retrieval lors de l’évaluation. Sources : [contrats, C4/C5](../contrats.md) et [guide d’annotation](../volet_b/grille_annotation.md).
- **Jeu réservé du volet B (SCRUM-35).** Blocs tirés du split test officiel, sans fuite vers le train ou la validation ; en relecture, PR [#36](https://github.com/LindaBOUKHIT/TeamAI/pull/36).
- **Traçabilité C7.** Présenter configuration, versions, empreintes, effectifs, erreurs, matériel et périmètre des mesures. Conserver les échecs au dénominateur ; une valeur non mesurée reste `null`. Source : [contrats, C7](../contrats.md).

## 4. Analyse comparative

Rédaction : Alain. Synthèse de comparaison_a_b.md, copie SCRUM-47 (en relecture, PR [#47](https://github.com/LindaBOUKHIT/TeamAI/pull/47)).

Le volet A réalise une détection binaire ; le volet B vise une explication de bloc.  
Leurs métriques de qualité ne sont donc pas directement interchangeables.  
A s’appuie sur un BiLSTM entraîné par l’équipe, exporté en ONNX et exécuté dans le navigateur.  
Ses résultats disponibles relèvent de la validation ; le choix du seuil arbitre entre anomalies manquées et fausses alertes.  
La présentation séparée des séquences inédites reste nécessaire pour décrire la généralisation.  
B utilise des poids préentraînés, un prompt, des règles de sortie et, selon la configuration, du retrieval.  
Un JSON conforme ou une citation existante ne garantit pas une explication juste.  
Le retrieval de validation mesure la récupération documentaire et ne remplace pas la lecture des réponses.  
Le contrôle de A porte notamment sur l’architecture et le seuil ; celui de B porte sur le prompt, les règles et l’adaptation.  
Les dépendances diffèrent : runtime ONNX et navigateur pour A ; poids amont, backend et embeddings pour B.  
Le coût financier, l’énergie, le temps humain, la mémoire et la latence des parcours finaux restent à mesurer.  
Les observations historiques SmolLM2 ne décrivent ni Gemma ni une chaîne complète avec LoRA et RAG.  
La reproductibilité exige de figer ensemble données, modèle, configuration, machine et méthode de mesure.  
**Chiffres de test à venir (SCRUM-44/45).**

La comparaison SCRUM-47 décrit l’état de dev et signale les PR encore ouvertes. Les éléments Gemma, LoRA et défauts repris en section 3.2 viennent de PR encore en relecture. Ils ne doivent pas être présentés comme déjà intégrés à dev. Sources : comparaison SCRUM-47 (en relecture, PR [#47](https://github.com/LindaBOUKHIT/TeamAI/pull/47)), trace SCRUM-63 (en relecture, PR [#40](https://github.com/LindaBOUKHIT/TeamAI/pull/40)), journal SCRUM-29 (en relecture, PR [#23](https://github.com/LindaBOUKHIT/TeamAI/pull/23)) et défauts SCRUM-46 (en relecture, PR [#41](https://github.com/LindaBOUKHIT/TeamAI/pull/41)).

## 5. Retour d’expérience

### 5.1 Retour collectif

Le jalon de mi-parcours du **01/10/2026** n’a pas été tenu. La feuille de route du **06/10/2026** prévoyait un sprint de rattrapage : données, premier site, inférence locale et préparation de J3. Le journal atteste ensuite une première inférence locale, un site statique, un modèle entraîné et un parcours de saisie et d’export. Ces réalisations ne suffisent pas à conclure que tous les objectifs du rattrapage sont clos. Sources : [feuille de route, situation et sprint de rattrapage](../projet/feuille_de_route.md) et [journal, entrées SCRUM-28/23/25/27](../projet/journal.md).

Jira, les branches et les PR donnent une structure au suivi. La règle associe un ticket, un responsable, un relecteur et un critère de fin à chaque travail. La séparation entre proposition, code disponible et relecture effective reste nécessaire. Le journal conserve des relectures attendues et ne contient pas de compte rendu de réunion attesté. Sources : [journal, décisions et réunions](../projet/journal.md) et [feuille de route, règles de travail](../projet/feuille_de_route.md).

Les nouveaux apports du volet B ne sont pas tous intégrés. Les entrées SCRUM-63, SCRUM-29 et SCRUM-46 indiquent une relecture d’Alain à faire. Les exemples LoRA régénérés demandent aussi une nouvelle relecture par Linda. Ces mentions constituent des attentes ; elles ne sont pas des avis attribués aux intéressés. Sources : journal de branche SCRUM-46 (en relecture, PR [#41](https://github.com/LindaBOUKHIT/TeamAI/pull/41)) et journal de branche SCRUM-29 (en relecture, PR [#23](https://github.com/LindaBOUKHIT/TeamAI/pull/23)).

Les assistants IA ont participé au cadrage, à l’organisation Jira, au code, à la documentation et aux relectures préparatoires. Le journal déclare les usages de Codex et de Claude Code par Alain, Linda et Bachar, avec des vérifications et des limites propres à chaque entrée. Cette déclaration ne remplace pas une relecture humaine et n’autorise pas à attribuer une validation collective. Source : [journal, usages des assistants IA et expériences](../projet/journal.md).

Les difficultés techniques ont conduit à revoir le matériel cible et la chaîne d’adaptation. Les erreurs mémoire et fp16 de l’essai LoRA ont été consignées avant les correctifs et l’essai T4 abouti. La baisse de loss sur le train reste séparée du gain de qualité à établir. Aucun écart chiffré entre estimation et temps réel de travail n’est établi dans les entrées utilisées ici ; le rapport n’en déduit pas de bilan de productivité. Source : journal SCRUM-29, entrées du 27/10 et du 08/11/2026 (en relecture, PR [#23](https://github.com/LindaBOUKHIT/TeamAI/pull/23)).

### 5.2 Retours individuels

#### À rédiger par Alain Evina (SCRUM-49)

#### À rédiger par Bachar Ben Slama (SCRUM-49)

#### À rédiger par Linda Boukhit (SCRUM-49)

#### À rédiger par Nassim Mezzai (SCRUM-49)

## 6. Cinq outils novateurs

Rédaction de la synthèse : Alain. Les fiches complètes sont dans `docs/rapport/outils/` (SCRUM-34, PR #42 à #46).

### 6.1 Codex CLI piloté par Claude Code

Le tandem sert à spécifier, écrire et relire le code et la documentation.  
Le découpage des rôles et les missions écrites ont structuré le travail d’Alain.  
L’échec principal est la production d’affirmations documentaires fausses sur les résultats, repérées en relecture.  
Le verdict de la fiche est de garder le tandem pour le code, avec vérification de chaque résultat avant son entrée dans le journal.  
Fiche : [outils/codex_claude.md](outils/codex_claude.md) (en relecture, PR [#46](https://github.com/LindaBOUKHIT/TeamAI/pull/46)).

### 6.2 Serveur MCP Kaggle

Le serveur sert à lancer et suivre les essais GPU, puis à récupérer adaptateur, métriques et journaux.  
Il a permis de diagnostiquer les erreurs et de récupérer les sorties de l’essai LoRA.  
La CLI refusait l’accès ; l’envoi d’une archive dans le contexte de l’agent était aussi trop volumineux.  
La solution décrite utilise des fichiers au commit figé avec empreintes ; les fins de ligne ont dû être maîtrisées.  
Le verdict est de garder cet outil pour les essais GPU courts, avec une limite liée à l’accès aux fichiers d’un dépôt privé.  
Fiche : [outils/kaggle_mcp.md](outils/kaggle_mcp.md) (en relecture, PR [#45](https://github.com/LindaBOUKHIT/TeamAI/pull/45)).

### 6.3 llama.cpp / GGUF

Le runtime sert à l’inférence quantifiée et à la conversion des adaptateurs.  
Les observations historiques montrent une réduction de mémoire ; le schéma JSON facilite les contrôles de format.  
L’échec principal reste sémantique : une réponse structurée peut inverser une chronologie, inventer un lien causal ou boucler.  
La sensibilité à l’ordre du prompt et à la charge de la machine limite aussi les conclusions de vitesse.  
Le verdict est de garder llama.cpp, avec vérification locale de l’inférence et de l’adaptateur encore attendue.  
Fiche : [outils/llama_cpp.md](outils/llama_cpp.md) (en relecture, PR [#43](https://github.com/LindaBOUKHIT/TeamAI/pull/43)).

### 6.4 Connecteur MCP Atlassian

Le connecteur sert à créer et suivre les tickets, les dépendances et les transitions Jira.  
La création du board et la préparation de relectures sont documentées pour Alain et Linda.  
La difficulté principale est la traçabilité : les actions de l’agent apparaissent sous le compte connecté, et un statut ne prouve pas le critère de fin.  
Le verdict est de garder le connecteur avec un site fixé, un commentaire par changement réel et une vérification avant clôture.  
Fiche : [outils/mcp_atlassian.md](outils/mcp_atlassian.md) (en relecture, PR [#44](https://github.com/LindaBOUKHIT/TeamAI/pull/44)).

### 6.5 PEFT / QLoRA — critique argumentée

Cette fiche constitue la **critique argumentée** : elle confronte l’adaptation économe en mémoire aux difficultés effectivement rencontrées.  
La chaîne T4 a permis un entraînement court et l’export de l’adaptateur.  
Les principaux échecs concernent la mémoire de la loss, les gradients fp16 et les incompatibilités de bibliothèques.  
La conversion révèle aussi des cibles d’adaptation différentes selon les couches à cache KV partagé.  
Le verdict est de garder QLoRA pour la faisabilité, avec une réserve explicite sur le transfert NF4 → Q4_0 et aucun gain de qualité établi avant comparaison locale.  
Fiche : [outils/peft_qlora.md](outils/peft_qlora.md) (en relecture, PR [#42](https://github.com/LindaBOUKHIT/TeamAI/pull/42)).

## 7. Conclusion et perspectives

**À rédiger après SCRUM-44/45.**

Les perspectives suivantes sont des propositions de la feuille de route des défauts, section 4 (en relecture, PR [#41](https://github.com/LindaBOUKHIT/TeamAI/pull/41)), et non des résultats acquis :

- **P0 : établir la référence et le coût local.** Figer la configuration avant les mesures réservées, conserver réponses et tentatives, relever l’environnement cible, puis mesurer chargement, latence, RAM et VRAM.
- **P1 : améliorer la fidélité et comparer les variantes.** Renforcer les contrôles des références, de l’incertitude et de la chronologie ; compléter les exemples relus ; vérifier l’adaptation complète et une variante v16+RAG identifiée avant d’en attribuer les gains.
- **P2–P3 : conditionner les extensions aux preuves.** N’envisager un modèle plus grand qu’après les améliorations et les mesures ; comparer les configurations sous protocole commun. Conserver Laya comme piste optionnelle reportée, avec rôle, budget et critère de gain à définir.

## Annexe — Sources internes

Les sources marquées « en relecture » viennent de PR non fusionnées dans `dev` au 09/11.

| Source | Usage dans le rapport | État documentaire |
|---|---|---|
| [Rapport V0.1](TeamAI_Rapport_SCRUM33_V0.1.pdf) | Reprise des chapitres 1 et 2 | PDF de Linda, SCRUM-33 |
| [docs/rapport/plan.md](plan.md) | Structure et attendus | Dev |
| [docs/projet/journal.md](../projet/journal.md) | Expériences, usages IA, relectures et organisation | Dev |
| [docs/contrats.md](../contrats.md) | Formats, C4-bloc, C5, C6 et C7 | Dev ; propositions et validations à distinguer |
| [docs/projet/environnements.md](../projet/environnements.md) | Relevé matériel ; contexte historique | Dev ; cible actualisée par SCRUM-63 |
| [docs/projet/feuille_de_route.md](../projet/feuille_de_route.md) | Jalons, rattrapage, responsabilités et dépendances | Dev ; objectifs planifiés |
| [docs/volet_b/corpus_rag.md](../volet_b/corpus_rag.md) | Corpus, couverture et limites documentaires | Dev |
| [docs/volet_b/grille_annotation.md](../volet_b/grille_annotation.md) | Annotation, relecture et séparation des données | Dev |
| [eval/results/SCRUM-25-bilstm-v1/metrics.json](../../eval/results/SCRUM-25-bilstm-v1/metrics.json) | Validation BiLSTM et référence baseline SCRUM-24 | Dev ; champs cités en 3.1 |
| [eval/results/SCRUM-28/README.md](../../eval/results/SCRUM-28/README.md) | Historique de première inférence SmolLM2 | Dev |
| [eval/results/SCRUM-37/retrieval_val.json](../../eval/results/SCRUM-37/retrieval_val.json) | Retrieval de validation | Dev |
| [eval/results/SCRUM-62_20261023T153242Z_690fcb/analysis.json](../../eval/results/SCRUM-62_20261023T153242Z_690fcb/analysis.json) | Choix de seuil sur validation | Dev |
| [eval/results/SCRUM-62_20261023T153242Z_690fcb/browser_check.json](../../eval/results/SCRUM-62_20261023T153242Z_690fcb/browser_check.json) | Vérification navigateur au seuil proposé | Dev |
| `docs/projet/journal.md` (branche SCRUM-46) | Gemma SCRUM-63, historique SCRUM-57 et défauts SCRUM-46 | En relecture, PR [#41](https://github.com/LindaBOUKHIT/TeamAI/pull/41) |
| `eval/results/SCRUM-63/README.md` | Modèle, prompt v16, schéma, contrôles et validation unique | En relecture, PR [#40](https://github.com/LindaBOUKHIT/TeamAI/pull/40) |
| `docs/projet/journal.md` (branche SCRUM-29) | Réglages LoRA, essai T4 et réserve SCRUM-61 | En relecture, PR [#23](https://github.com/LindaBOUKHIT/TeamAI/pull/23) |
| `docs/volet_b/defauts_feuille_de_route.md` | Comptes n/40 et perspectives P0–P3 | En relecture, PR [#41](https://github.com/LindaBOUKHIT/TeamAI/pull/41) |
| `eval/results/comparaison_a_b.md` | Synthèse comparative SCRUM-47 | En relecture, PR [#47](https://github.com/LindaBOUKHIT/TeamAI/pull/47) |
| `docs/rapport/outils/codex_claude.md` | Fiche d’outil SCRUM-34 | En relecture, PR [#46](https://github.com/LindaBOUKHIT/TeamAI/pull/46) |
| `docs/rapport/outils/kaggle_mcp.md` | Fiche d’outil SCRUM-34 | En relecture, PR [#45](https://github.com/LindaBOUKHIT/TeamAI/pull/45) |
| `docs/rapport/outils/llama_cpp.md` | Fiche d’outil SCRUM-34 | En relecture, PR [#43](https://github.com/LindaBOUKHIT/TeamAI/pull/43) |
| `docs/rapport/outils/mcp_atlassian.md` | Fiche d’outil SCRUM-34 | En relecture, PR [#44](https://github.com/LindaBOUKHIT/TeamAI/pull/44) |
| `docs/rapport/outils/peft_qlora.md` | Critique argumentée SCRUM-34 | En relecture, PR [#42](https://github.com/LindaBOUKHIT/TeamAI/pull/42) |
