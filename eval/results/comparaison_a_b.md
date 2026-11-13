# Comparaison volet A / volet B — squelette SCRUM-47

## Objet et règles

Ce document prépare la comparaison technique prévue dans `docs/rapport/plan.md`.
Les chiffres proviennent uniquement des dossiers C7 ou de leurs résumés dans `eval/results/`, avec machine et méthode ; une information absente reste « à mesurer » ou « non relevé ».
Le relevé T4 de SCRUM-29 est cité séparément comme observation de faisabilité issue de `docs/projet/journal.md`, hors comparaison de qualité. Ses métriques d’entraînement ne figurent pas dans le JSON d’export de `eval/results/SCRUM-29/` ; elles restent à consolider dans C7.
Toute différence de machine, backend, tâche ou périmètre de chronométrage doit être déclarée avant comparaison.
Les métriques de test de A existent dans SCRUM-44, encore en relecture (PR #50, non fusionnée dans `dev`) : elles sont reprises avec cette mention. B reste à mesurer sur le test dans SCRUM-45.
État documentaire au 13/11/2026, après fusion de `dev` : les sources de SCRUM-63, SCRUM-29 et SCRUM-46 sont intégrées. La validation Gemma, la faisabilité LoRA et les défauts relevés restent des preuves distinctes. La chaîne complète reste à mesurer : SCRUM-45.

## Tableau principal

| Axe | Volet A | Volet B | Source | Statut |
|---|---|---|---|---|
| Coût | Coût financier, énergie et temps humain : à mesurer. | Coût financier, énergie et temps humain de l'adaptation et de l'inférence : à mesurer. | `docs/contrats.md` (C7) ; `docs/rapport/plan.md` | à mesurer : SCRUM-44 / SCRUM-45 |
| Latence | Débit sur le test : **6 198,58 blocs/s** (FP32) et **3 004,27 blocs/s** (INT8) sous Chrome WASM, boucle JavaScript comprise ; **45 149,83** et **48 329,83 blocs/s** sous ONNX Runtime Python CPU, lots de 512 (`eval/results/volet_a.md` (PR #50, en relecture)). Machine non relevée dans ce résumé. La durée d'entraînement ne constitue pas une latence d'inférence. | Gemma v16 sans LoRA ni RAG : **30,624 s/bloc**, correction incluse, sur deux T4 Kaggle sous llama.cpp (`eval/results/SCRUM-63/comparaison_v16_validation.json` ; `eval/results/SCRUM-63/README.md`). Validation, pas test. Chaîne complète sur la cible : à mesurer : SCRUM-45. | `eval/results/SCRUM-25-bilstm-v1/metrics.json` ; `eval/results/SCRUM-63/comparaison_v16_validation.json` ; `eval/results/SCRUM-63/README.md` | A : test en relecture (PR #50) ; B : validation exploratoire, à mesurer : SCRUM-45 |
| Qualité des résultats | Détection binaire. Test officiel, BiLSTM FP32 au seuil SCRUM-62 : macro-F1 **0,9938**, **58 fausses alertes et 3 anomalies manquées** sur 86 260 blocs ; macro-F1 **0,9714** sur les 1 962 séquences inédites ; INT8 identique (`eval/results/volet_a.md` (PR #50, en relecture)). Validation détaillée ci-dessous. | Explication, sans verdict binaire. Validation v16 : **40/40** contrats et copies de faits conformes, **39/40** contrôles factuels du runtime (`eval/results/SCRUM-63/comparaison_v16_validation.json`). Revue : **2/40** chronologies fausses, **3/40** causalités non démontrées, **1/40** résumé en boucle (`eval/results/SCRUM-63/revue_qualitative_validation.json`). Retrieval évalué séparément ; qualité finale : à mesurer : SCRUM-45. | `eval/results/SCRUM-25-bilstm-v1/metrics.json` ; `eval/results/SCRUM-62_20261023T153242Z_690fcb/analysis.json` ; `eval/results/SCRUM-63/comparaison_v16_validation.json` ; `eval/results/SCRUM-63/revue_qualitative_validation.json` ; `eval/results/SCRUM-37/retrieval_val.json` ; `docs/contrats.md` (C3/C5) | A : test en relecture (PR #50) ; B : validation, à mesurer : SCRUM-45 |
| Degré de contrôle | Architecture BiLSTM entraînée par l'équipe, export ONNX, seuil choisi sur validation et hashes conservés. | Poids préentraînés empruntés. Prompt v16 figé, schéma fermé, faits calculés, causes conditionnelles autorisées et correction unique. Le port ajoute un garde anti-boucle. Essai QLoRA NF4 entraîné puis exporté en GGUF F16 ; transfert vers Q4_0 et gain non validés. RAG absent de la validation v16. | `eval/results/SCRUM-25-bilstm-v1/config.json` ; `eval/results/SCRUM-63/prompt_freeze.json` ; `eval/results/SCRUM-63/causes_compatibles.json` ; `eval/results/SCRUM-63/README.md` ; `eval/results/SCRUM-29/kaggle_t4_gguf_meta.json` ; `docs/projet/journal.md` ; `docs/contrats.md` | contrôles et faisabilité attestés ; gain LoRA à mesurer : SCRUM-45 |
| Explicabilité | Classe et score ; le score n'est pas présenté comme une probabilité calibrée. Une anomalie ne donne pas une cause de panne. | Contrat d'explication : faits, hypothèses, informations manquantes, sources et abstention. Une structure valide ne prouve pas la justesse de l'explication. | `docs/contrats.md` (C3/C5/C6) | qualitatif ; qualité à mesurer : SCRUM-45 |
| Dépendance fournisseur | Poids entraînés par l'équipe ; dépendance au format ONNX et au runtime navigateur. | Gemma 4 E4B QAT : dépôt `google/gemma-4-E4B-it-qat-q4_0-gguf`, révision `4b4a2c1d584be7264f87aac328a1bc739ce81b6c` (`eval/results/SCRUM-63/model_v16.json`). Base HF d’entraînement distincte, révision consignée dans le JSON d’export. Dépendances à llama.cpp et au modèle d’embeddings du RAG. Licence : non relevée dans les sources lues. | `eval/results/SCRUM-63/model_v16.json` ; `eval/results/SCRUM-29/kaggle_t4_gguf_meta.json` ; `docs/projet/journal.md` ; `volet_b/slm/configs/generation.yaml` ; `docs/contrats.md` | identités attestées ; licence non relevée |
| Effort de données | Traces, labels, parsing, vocabulaire et splits nécessaires à l'entraînement. Temps de préparation : non relevé. | Brouillons LoRA issus du train, encore à relire ; un jeu relu reste nécessaire pour l’adaptation complète. Corpus documentaire et références pour le RAG. Temps d’annotation et de maintenance : non relevé. | `docs/contrats.md` (C1/C2/C4/C5/C6) ; `volet_b/slm/README.md` | brouillons attestés ; relecture à compléter ; à mesurer : SCRUM-44 / SCRUM-45 |
| Reproductibilité | Configuration, hashes des données, splits et sources conservés. Le relevé d'entraînement indique des fichiers modifiés ou non suivis : le commit seul ne suffit pas. | Révision GGUF et paramètres figés. SHA-256 du runtime Kaggle, de la consigne, de la politique, des prompts et schémas conservés. Export LoRA : révision HF, hash source et commit du convertisseur conservés. Le port avec garde anti-boucle diffère du runtime mesuré. Configuration intégrée LoRA/RAG et environnement cible à consigner ensemble selon C7. | `eval/results/SCRUM-25-bilstm-v1/config.json` ; `eval/results/SCRUM-63/model_v16.json` ; `eval/results/SCRUM-63/prompt_freeze.json` ; `eval/results/SCRUM-63/validation_rule.json` ; `eval/results/SCRUM-29/kaggle_t4_gguf_meta.json` ; `volet_b/slm/configs/generation.yaml` ; `docs/contrats.md` | gel et provenance attestés ; à compléter : SCRUM-44 / SCRUM-45 |
| Empreinte mémoire | Taille du modèle : **56 806 octets** (FP32) et **22 570 octets** (INT8) (`eval/results/volet_a.md` (PR #50, en relecture)). Mémoire du processus navigateur et pic pendant l'inférence : non relevés. Taille d'un fichier ONNX et mémoire vive ne sont pas interchangeables. | RAM/VRAM d’inférence Gemma v16 : non relevées dans la trace de validation. Le pic VRAM T4 LoRA concerne l’entraînement. Historique RSS SmolLM2 ci-dessous, non transposable. Chaîne complète sur la cible : à mesurer : SCRUM-45. | `eval/results/SCRUM-62_20261023T153242Z_690fcb/browser_check.json` ; `eval/results/SCRUM-63/README.md` ; `docs/projet/journal.md` ; `docs/volet_b/defauts_feuille_de_route.md` | A : taille en relecture (PR #50), RAM non relevée ; B à mesurer : SCRUM-45 ; entraînement et inférence distincts |
| Déploiement | Site statique et exécution ONNX Runtime Web/WASM attestés. Parité Python/Chrome sur les 86 260 blocs du test : **0 décision divergente** en FP32 comme en INT8 ; écart maximal des scores **0,00414** en INT8 (`eval/results/volet_a.md` (PR #50, en relecture)). | Base actuelle : Gemma 4 E4B QAT GGUF Q4_0 sous llama.cpp. Cible : portable de Nassim, Ryzen 5 8645HS, **32 Go**, RTX 3050 Laptop **6 Go** (`docs/projet/environnements.md`). Offload GPU configuré ; inférence avec adaptateur sur cette cible non faite (SCRUM-61). Chaîne v16 + LoRA + RAG non évaluée. | `eval/results/SCRUM-62_20261023T153242Z_690fcb/browser_check.json` ; `eval/results/SCRUM-63/README.md` ; `volet_b/slm/README.md` ; `volet_b/slm/configs/generation.yaml` ; `docs/projet/environnements.md` ; `docs/projet/journal.md` | A : parité test en relecture (PR #50) ; B : configuration attestée, inférence cible à valider, à mesurer : SCRUM-45 |

## Volet A : validation, pas test

Les métriques suivantes concernent le BiLSTM entraîné sur CPU sous Windows, avec PyTorch CPU. Le modèle et les splits sont identifiés par hashes. Le processeur exact de cette exécution est non relevé dans `eval/results/SCRUM-25-bilstm-v1/config.json` ; les autres postes de `docs/projet/environnements.md` ne lui sont pas attribués par déduction.

Le seuil initial est **0,99** (`eval/results/SCRUM-25-bilstm-v1/metrics.json`). La méthode de sélection maximise la macro-F1 sur une grille de validation (`eval/results/SCRUM-25-bilstm-v1/config.json`). Il s'agit de **validation, pas test**.

| Périmètre | Effectif | Macro-F1 | Précision anomalie | Rappel anomalie |
|---|---|---|---|---|
| Validation globale | 86 259 (`eval/results/SCRUM-25-bilstm-v1/metrics.json`) | 0,9955 (`eval/results/SCRUM-25-bilstm-v1/metrics.json`) | 0,9909 (`eval/results/SCRUM-25-bilstm-v1/metrics.json`) | 0,9917 (`eval/results/SCRUM-25-bilstm-v1/metrics.json`) |
| Validation, séquences inédites `unseen` | 1 929 (`eval/results/SCRUM-25-bilstm-v1/metrics.json`) | 0,9767 (`eval/results/SCRUM-25-bilstm-v1/metrics.json`) | 0,9646 (`eval/results/SCRUM-25-bilstm-v1/metrics.json`) | 0,9682 (`eval/results/SCRUM-25-bilstm-v1/metrics.json`) |

Le protocole de référence sépare les blocs, mais autorise des séquences identiques entre splits. Le sous-ensemble inédit doit donc rester visible ; la validation globale seule ne suffit pas à décrire la généralisation (`docs/contrats.md`, C4).

### Révision du seuil : SCRUM-62

L'analyse conserve les poids et cherche le maximum de F1 anomalie sous contrainte d'anomalies manquées. Au seuil initial, elle relève **21 anomalies manquées et 23 fausses alertes** (`eval/results/SCRUM-62_20261023T153242Z_690fcb/analysis.json`, `candidates.current.all_validation`).

Le candidat **0,4081** (`eval/results/SCRUM-62_20261023T153242Z_690fcb/analysis.json`, `candidates.max_fn_1`) donne **1 anomalie manquée et 59 fausses alertes** (`eval/results/SCRUM-62_20261023T153242Z_690fcb/analysis.json`). Le rappel devient **0,9996** et la macro-F1 **0,9939** (`eval/results/SCRUM-62_20261023T153242Z_690fcb/analysis.json`). C'est un compromis de validation qui privilégie le rappel, sans conclusion sur le test.

Le relevé navigateur atteste WASM, un modèle issu du cache et **10 cas distincts sans désaccord de classe** (`eval/results/SCRUM-62_20261023T153242Z_690fcb/browser_check.json`). Il ne mesure pas la latence ni la mémoire. L'analyse indique `metadata_updated: false`, tandis que le journal annonce des métadonnées actualisées : la version finale et son seuil devront être identifiés dans le dossier C7 de SCRUM-44 (`eval/results/SCRUM-62_20261023T153242Z_690fcb/analysis.json` ; `docs/projet/journal.md`).

### Test officiel : SCRUM-44 (en relecture, PR #50)

Ces chiffres viennent de `eval/results/volet_a.md`, ajouté par la PR #50 et encore relu par Bachar. Ils ne sont pas fusionnés dans `dev`. Le protocole est C4-bloc, test officiel ouvert une seule fois, seuil figé SCRUM-62 **0,40814146399497986** (`eval/results/volet_a.md`). Le résumé déclare un précédent : un fichier SCRUM-24 contenait déjà des résultats de test (commit `b77b1a2`, 12/10/2026), sans usage pour le réglage actuel (`eval/results/volet_a.md`).

| Modèle | Population | N | Précision anomalie | Rappel anomalie | Macro-F1 | FP | FN |
|---|---|---|---|---|---|---|---|
| Baseline | test complet | 86 260 | 0,9561 | 0,9992 | 0,9882 | 116 | 2 |
| Baseline | séquences inédites | 1 962 | 0,8898 | 0,9963 | 0,9576 | 67 | 2 |
| BiLSTM FP32 | test complet | 86 260 | 0,9775 | 0,9988 | 0,9938 | 58 | 3 |
| BiLSTM FP32 | séquences inédites | 1 962 | 0,9262 | 0,9945 | 0,9714 | 43 | 3 |
| BiLSTM INT8 | test complet | 86 260 | 0,9775 | 0,9988 | 0,9938 | 58 | 3 |

Source de chaque ligne : `eval/results/volet_a.md`, section « Metriques ». Les résultats INT8 sur les séquences inédites sont identiques à ceux du FP32. Les dossiers C7 cités dans ce résumé (`eval/runs/…SCRUM-44_*`) ne sont pas versionnés dans la PR.

Par rapport à la baseline, le BiLSTM divise par deux les fausses alertes (58 contre 116) au prix d'une anomalie manquée de plus (3 contre 2). L'écart se creuse sur les séquences inédites : 43 fausses alertes contre 67. Le relevé navigateur ne mesure ni la création de session ONNX Runtime ni la mémoire. Les débits Chrome et Node.js relèvent de protocoles distincts (`eval/results/volet_a.md`). Ces chiffres seront figés à la fusion de la PR #50.

## Volet B : portée des preuves disponibles

B explique un bloc ; il ne constitue pas le détecteur binaire de A. Le contrat de sortie porte sur le résumé, les faits, les hypothèses, les informations manquantes, les sources et l'abstention (`docs/contrats.md`, C5). Comparer directement une macro-F1 de détection à une qualité d'explication serait comparer des tâches différentes. Les anciens prompts demandant aussi un avis normal/anormal ne changent pas cette limite.

### Gemma 4 E4B QAT, prompt v16 (SCRUM-63)

La base est `google/gemma-4-E4B-it-qat-q4_0-gguf`, fichier `gemma-4-E4B_q4_0-it.gguf`, révision `4b4a2c1d584be7264f87aac328a1bc739ce81b6c` (`eval/results/SCRUM-63/model_v16.json`). Le backend est llama.cpp ; l’exploration utilisait llama-cpp-python **0.3.36** (`volet_b/slm/README.md`). Quantification Q4_0, réflexion désactivée, contexte **4096**, budget **800 tokens**, température **0**, seed **42**, pénalité de répétition **1,0** (`eval/results/SCRUM-63/README.md` ; `volet_b/slm/configs/generation.yaml`). La licence n’est pas précisée dans les sources lues.

Le prompt, le schéma, le catalogue de causes et les contrôles sont figés après v16 (`eval/results/SCRUM-63/validation_rule.json`). Les SHA-256 du runtime Kaggle, de la consigne, de la politique, des **40 prompts et schémas** sont conservés (`eval/results/SCRUM-63/prompt_freeze.json`). Les faits sont calculés ; le glossaire n’inclut que les codes présents. Les hypothèses sont facultatives et limitées à des formulations conditionnelles ancrées dans les messages (`eval/results/SCRUM-63/causes_compatibles.json`). Aucun label attendu, résultat de détection, document RAG ou adaptateur LoRA n’est injecté (`eval/results/SCRUM-63/README.md`).

La validation unique porte sur **40 nouveaux blocs `val` de `data/sample`**, après exclusion de **85 blocs connus**, sans réglage après lecture (`eval/results/SCRUM-63/comparaison_v16_validation.json`, `selection`). Elle comprend **20 blocs avec WARN et 20 sans WARN**, dont **21 avec indice d’incident et 19 sans** (`eval/results/SCRUM-63/comparaison_v16_validation.json`). Il s’agit de **validation, pas test**. Ce sample ne représente pas tout HDFS.

- Résultats finaux : **40/40** contrats et copies exactes des faits sélectionnés ; **39/40** réponses passent les contrôles factuels du runtime (`eval/results/SCRUM-63/comparaison_v16_validation.json`, `automatic_metrics.v16_validation_final`). La copie exacte ne garantit pas la fidélité de la prose.
- Références inexistantes : **1/40 au premier essai, 0/40 en final**, après **une correction** (`eval/results/SCRUM-63/comparaison_v16_validation.json`, `automatic_metrics` et `retry_metrics.v16_validation`). **0/40** hypothèse réseau sans appui et **0/40** enquête sans incident ; **4 hypothèses pour 21 blocs avec incident**, soit **0,19 par bloc avec incident** (`eval/results/SCRUM-63/comparaison_v16_validation.json`). Ces alertes ciblées ne sont pas un score de vérité.
- Machine : **deux T4 Kaggle**, avec répartition des blocs par worker (`eval/results/SCRUM-63/README.md` ; `eval/results/SCRUM-63/comparaison_v16_validation.json`, `selection`). Moyenne de génération avec correction : **30,624 s/bloc** ; cumul des workers : **1 224,948 s** ; durée murale d’inférence parallèle : **629,360 s** (`eval/results/SCRUM-63/comparaison_v16_validation.json`, `automatic_metrics.v16_validation_final` et `execution.v16_validation`). Ces périmètres diffèrent. Ils ne mesurent ni la chaîne complète ni la latence sur le portable. CPU, RAM hôte et pics RAM/VRAM d’inférence : non relevés dans cette trace.

Le port ajoute un rejet des répétitions et des sorties proches du budget à la correction unique existante. Ce garde-fou est postérieur à la mesure ; son efficacité n’est pas mesurée rétroactivement (`eval/results/SCRUM-63/README.md`). La cible locale est le portable de Nassim : Ryzen 5 8645HS, **32 Go**, RTX 3050 Laptop **6 Go** (`docs/projet/environnements.md`). L’offload GPU est configuré, mais les versions locales et les performances restent à relever. L’inférence avec adaptateur sur cette cible n’est pas faite (SCRUM-61 ; `docs/projet/journal.md`, entrée SCRUM-29 du 08/11). La variante v16 + RAG reste à figer ; `rag1` est explicitement reporté (`docs/projet/journal.md`, entrée SCRUM-38 du 27/10).

### Essai LoRA (SCRUM-29)

La base d’entraînement est distincte du GGUF d’inférence : `google/gemma-4-E4B-it-qat-q4_0-unquantized`, révision `476025a01dbf99361c062bbeca3d6a76bb4c4566` (`eval/results/SCRUM-29/kaggle_t4_gguf_meta.json`). Chargement texte seul, QLoRA NF4 avec calcul FP16, `q_proj`/`v_proj`, rang **8**, alpha **16**, dropout **0,05**, lot **1**, taux d’apprentissage **2e-4**, checkpointing, plafond de **3072 tokens** sans troncature (`volet_b/slm/configs/lora_essai.yaml` ; `volet_b/slm/README.md`). La perte porte sur la réponse et le marqueur de fin de tour ; les logits du prompt ne sont plus matérialisés (`volet_b/slm/README.md`).

L’essai T4 du **08/11/2026** utilise **20 exemples train**, encore sans relecture humaine attestée (`docs/projet/journal.md`, entrée SCRUM-29 du 08/11 ; `volet_b/slm/README.md`). Les chiffres suivants viennent du journal, pas de métriques d’entraînement présentes dans le JSON d’export :

- **30 pas appliqués, 0 sauté**, échelle **1024** stable ; loss moyenne **0,586 sur les 5 premiers pas**, puis **0,052 sur les 5 derniers** (`docs/projet/journal.md`, entrée SCRUM-29 du 08/11). Ce sont des pertes sur le train, pas des résultats de validation ni une qualité d’explication.
- **4,9 s/pas**, pic VRAM **10,24 Gio**, dont **8,63 Gio au chargement**, et **2 269 184 paramètres entraînables** (`docs/projet/journal.md`, entrée SCRUM-29 du 08/11). Machine : T4 Kaggle de **14,56 Gio** (`docs/projet/journal.md`). Réglages et versions de départ dans `volet_b/slm/README.md` et `volet_b/slm/configs/lora_essai.yaml`. Ce pic concerne l’entraînement, pas l’inférence.
- Adaptateur PEFT rechargé puis converti en GGUF F16. Le JSON atteste **4 547 904 octets**, le commit llama.cpp `0c1e57098`, le SHA-256 source `38652e34d50c641dbd41faf91d57b2ee201bfc6075a7ab27628531a1faa32194` et `inference_validated: false` (`eval/results/SCRUM-29/kaggle_t4_gguf_meta.json`). La couverture est `q_proj` sur **42 couches**, `v_proj` sur les couches **0 à 23**, les autres partageant le cache KV (`docs/projet/journal.md`, entrée SCRUM-29 du 08/11 ; `eval/results/SCRUM-29/kaggle_t4_gguf_meta.json`).

Cet essai atteste la faisabilité d’entraînement et de conversion. Il ne valide ni le transfert NF4 → Q4_0, ni l’inférence RTX 3050, ni un gain de fidélité. La fusion puis requantification n’est pas la route retenue pour la base QAT officielle. Une comparaison base/adapté à prompts identiques reste nécessaire (`volet_b/slm/README.md` ; `eval/results/SCRUM-29/kaggle_t4_gguf_meta.json` ; `docs/projet/journal.md`).

**Incohérences documentaires.** Le README SLM dit encore que la faisabilité T4 reste à mesurer et que les correctifs ne sont pas revalidés sur GPU. Le journal décrit ensuite l’essai abouti du 08/11 ; ces formulations ne sont plus alignées (`volet_b/slm/README.md` ; `docs/projet/journal.md`). L’entrée SCRUM-29 du 27/10 annonce l’inclusion du token de fin de tour, puis dit que ses marqueurs sont masqués. Le README inclut ce marqueur dans la perte (`docs/projet/journal.md` ; `volet_b/slm/README.md`). Le tableau historique des environnements qualifie aussi l’entraînement CPU SmolLM2 de non testé, alors que le journal décrit un essai CPU antérieur (`docs/projet/environnements.md` ; `docs/projet/journal.md`, entrée SCRUM-29 du 14/10). Ces écarts ne sont pas résolus par déduction.

### Défauts v16 (SCRUM-46)

La revue qualitative des réponses finales relève les défauts suivants. Les cas se recoupent ; les comptes ne s’additionnent pas (`eval/results/SCRUM-63/revue_qualitative_validation.json`).

| Constat sur la validation | Compte et source |
|---|---|
| Chronologie fausse | **2/40** (`eval/results/SCRUM-63/revue_qualitative_validation.json`, `summary.other_chronology_error_cases`) |
| Causalité non démontrée | **3/40** (`eval/results/SCRUM-63/revue_qualitative_validation.json`, `summary.unsupported_causal_link_cases`) |
| Pseudo-références | **3/40** (`eval/results/SCRUM-63/revue_qualitative_validation.json`, `summary.pseudo_reference_cases`) |
| Résumé en boucle, inutilisable | **1/40**, avec **130 occurrences de F09**, malgré un arrêt `stop` (`eval/results/SCRUM-63/revue_qualitative_validation.json` ; `eval/results/SCRUM-63/README.md`) |
| Cause indéterminée non explicitée | **16/40**, soit **16/16 cas concernés** (`eval/results/SCRUM-63/revue_qualitative_validation.json`, `summary.unknown_cause_statement_missing_in_summary_count` et `unknown_cause_incident_blocks`) |

Les **4/40 alertes causales** automatiques ne sont pas les **3/40 erreurs confirmées** en revue (`eval/results/SCRUM-63/comparaison_v16_validation.json` ; `eval/results/SCRUM-63/revue_qualitative_validation.json`). Les exemples de citations mal attribuées et de questions peu utiles ne constituent pas des taux exhaustifs. E24 et E27 sont absents de cette cohorte ; aucune réussite sur ces codes n’en découle (`eval/results/SCRUM-63/revue_qualitative_validation.json`). Voir `docs/volet_b/defauts_feuille_de_route.md` pour la typologie, les limites et les actions proposées avant SCRUM-38/45. Le contrat conforme ne garantit pas une explication juste.

### Historique SmolLM2 : aucune extrapolation à Gemma

SCRUM-28 décrit SmolLM2 en float32, Transformers/PyTorch CPU, sur la machine d'Alain : **i5-1240P, 32 Go, sans GPU NVIDIA** (`eval/results/SCRUM-28/README.md`). La mesure couvre un bloc de développement ; elle ne valide ni LoRA ni le RAG.

- Génération : **156 tokens en 952,03 s, soit 0,16 token/s** (`eval/results/SCRUM-28/README.md`). Le temps inclut le traitement du prompt dans `model.generate()`, hors tokenisation, décodage et fichiers.
- Chargement : **238,0 s** (`eval/results/SCRUM-28/README.md`), imports, tokenizer et poids en cache inclus.
- RSS après chargement : **6,77 GiB** ; pic au chargement : **9,84 GiB** ; pic en génération : **8,00 GiB** (`eval/results/SCRUM-28/README.md`). Le RSS du processus est échantillonné toutes les **0,2 s** (`eval/results/SCRUM-28/README.md`) ; les pics plus brefs peuvent être manqués. VRAM : non relevé.

La réponse historique omet les avertissements et invente des informations. Ce cas isolé ne permet pas une conclusion générale sur la qualité (`eval/results/SCRUM-28/README.md`). Les comparaisons entre anciennes exécutions ne sont pas contrôlées.

SCRUM-57 dispose désormais d’un dossier dédié (`eval/results/SCRUM-57/README.md`). Le banc historique SmolLM2 porte sur les mêmes **5 blocs de validation**, seed **42**, même prompt, décodage glouton, budget **300 tokens**, sur le CPU du portable d’Alain (`eval/results/SCRUM-57/README.md` ; `eval/results/SCRUM-57/base/config.json`). Il ne mesure pas Gemma.

| Exécution historique | Conformité C5 | Débit moyen | Pic RSS | Chargement |
|---|---|---|---|---|
| Base, Transformers float32 | 0/5 (`eval/results/SCRUM-57/base/metrics.json`) | 1,49 token/s (`eval/results/SCRUM-57/base/metrics.json`) | 9,94 GiB (`eval/results/SCRUM-57/README.md`) | 11,4 s (`eval/results/SCRUM-57/README.md`) |
| Base, llama.cpp Q4_K_M | 0/5 (`eval/results/SCRUM-57/base/metrics.json`) | 2,44 tokens/s (`eval/results/SCRUM-57/base/metrics.json`) | 2,83 GiB (`eval/results/SCRUM-57/README.md`) | 1,7 s (`eval/results/SCRUM-57/README.md`) |
| Adaptateur d’essai, Transformers float32 + PEFT | 0/5 (`eval/results/SCRUM-57/essai-adapter/metrics.json`) | 1,52 token/s (`eval/results/SCRUM-57/essai-adapter/metrics.json`) | 9,29 GiB (`eval/results/SCRUM-57/README.md`) | 11,7 s (`eval/results/SCRUM-57/README.md`) |
| Adaptateur d’essai, llama.cpp Q4_K_M + LoRA GGUF | 0/5 (`eval/results/SCRUM-57/essai-adapter/metrics.json`) | 2,37 tokens/s (`eval/results/SCRUM-57/essai-adapter/metrics.json`) | 2,12 GiB (`eval/results/SCRUM-57/README.md`) | 1,7 s (`eval/results/SCRUM-57/README.md`) |

L’adaptateur ne vérifie que le chemin de chargement. Les champs vides et le JSON invalide empêchent de conclure à un gain de qualité (`eval/results/SCRUM-57/README.md`). Le pic RSS inclut le chargement et est échantillonné toutes les **0,2 s** (`eval/results/SCRUM-57/base/metrics.json`). La génération inclut le prompt ; Transformers exclut tokenisation/décodage, llama.cpp chronomètre le chat complet (`eval/results/SCRUM-57/base/config.json` ; `eval/results/SCRUM-57/essai-adapter/config.json`). Backend et quantification changent ensemble. Ces mesures restent historiques, non transposables à Gemma et non comparables directement à la validation v16.

### Retrieval : validation, pas qualité globale des explications

Le retrieval est évalué sur **306 traces** (`eval/results/SCRUM-37/retrieval_val.json`), split `val (data/sample)`. Pour la méthode hybride et les requêtes par description, **k = 3**, le rappel des traces vaut **0,6644**, et les templates trouvés **6/10** (`eval/results/SCRUM-37/retrieval_val.json`). Ces chiffres mesurent la récupération documentaire, pas la justesse des réponses générées. Le JSON ne relève pas la machine ; aucune mesure de performance matérielle n'en est déduite.

Le journal précise que références et paraphrases viennent de l'équipe et que les traces répètent peu de séquences distinctes. L'agent complet y est seulement vérifié en mode factice ; cela n'atteste pas la qualité du SLM réel (`docs/projet/journal.md`, entrée SCRUM-37).

**Emplacement SCRUM-45** : [à mesurer : SCRUM-45, sur le test réservé, après gel et sans réglage sur ses réponses : effectif prévu/traité/échoué ; modèle et révision ; adaptateur LoRA ; variante du prompt et garde anti-boucle ; corpus et retrieval ; machine ; backend et quantification ; protocole ; qualité factuelle et utilité relues ; chronologie et causalité ; citations existantes et probantes ; incertitude ; abstention ; erreurs de format ; boucles ; corrections avant/après et échecs finaux ; gain base/LoRA/RAG à protocole commun ; chargement et latence complète ; pics RAM/VRAM ; coût ; chemins des preuves C7].

## Discussion (à compléter après SCRUM-44/45)

- Quel compromis entre anomalies manquées et fausses alertes retenir pour A, sur les séquences globales et inédites ?
- Quelle qualité factuelle, quelle pertinence des citations et quelle abstention B apporte-t-il sur sa tâche d'explication ?
- Comment présenter ensemble détection et explication sans confondre leurs métriques ni leur utilité ?
- À machine et méthode documentées, quels coûts, latences et pics mémoire observe-t-on pour chaque parcours complet ?
- Quel effort de préparation, d'annotation et de maintenance faut-il pour reproduire chaque solution avec ses versions figées ?

## Sources

Fichiers lus, chemins relatifs à la racine du dépôt :

- `eval/results/SCRUM-25-bilstm-v1/config.json`
- `eval/results/SCRUM-25-bilstm-v1/history.json`
- `eval/results/SCRUM-25-bilstm-v1/metrics.json`
- `eval/results/SCRUM-25-bilstm-v1/parity.json`
- `eval/results/SCRUM-62_20261023T153242Z_690fcb/analysis.json`
- `eval/results/SCRUM-62_20261023T153242Z_690fcb/browser_check.json`
- `eval/results/SCRUM-28/README.md`
- `eval/results/SCRUM-37/retrieval_val.json`
- `docs/projet/journal.md`
- `docs/contrats.md` (chemin disponible ; `docs/projet/contrats.md` absent)
- `docs/projet/environnements.md`
- `volet_b/slm/README.md`
- `volet_b/slm/configs/generation.yaml`
- `docs/rapport/plan.md`
- `eval/results/SCRUM-63/README.md`
- `eval/results/SCRUM-63/model_v16.json`
- `eval/results/SCRUM-63/prompt_freeze.json`
- `eval/results/SCRUM-63/comparaison_v16_validation.json`
- `eval/results/SCRUM-63/revue_qualitative_validation.json`
- `eval/results/SCRUM-63/validation_rule.json`
- `eval/results/SCRUM-63/causes_compatibles.json`
- `eval/results/SCRUM-57/README.md`
- `eval/results/SCRUM-57/base/comparison.md`
- `eval/results/SCRUM-57/base/config.json`
- `eval/results/SCRUM-57/base/metrics.json`
- `eval/results/SCRUM-57/base/llamacpp.json`
- `eval/results/SCRUM-57/base/transformers.json`
- `eval/results/SCRUM-57/essai-adapter/comparison.md`
- `eval/results/SCRUM-57/essai-adapter/config.json`
- `eval/results/SCRUM-57/essai-adapter/metrics.json`
- `eval/results/SCRUM-57/essai-adapter/llamacpp.json`
- `eval/results/SCRUM-57/essai-adapter/transformers.json`
- `eval/results/SCRUM-29/kaggle_t4_gguf_meta.json`
- `docs/volet_b/defauts_feuille_de_route.md`
- `volet_b/slm/configs/lora_essai.yaml`
- `docs/rapport/outils/peft_qlora.md` (cohérence uniquement)
- `docs/rapport/outils/llama_cpp.md` (cohérence uniquement)
