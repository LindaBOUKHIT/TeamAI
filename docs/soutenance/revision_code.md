# Révision du code pour la soutenance (SCRUM-53)

Le jury choisit qui répond, sur n'importe quelle partie du code. Cette fiche donne, module par module, ce qu'il faut savoir expliquer sans aide : rôle, point d'entrée, mécanisme clé, chiffres du dépôt avec leur fichier source, questions probables. Elle complète [questions_jury.md](questions_jury.md), sans la remplacer.

Règles de lecture :

- chaque chiffre renvoie au fichier qui l'atteste ; « validation » et « test » ne se mélangent jamais ;
- les mesures automatiques du volet B sur le test (SCRUM-45, 25/11) sont dans `eval/results/volet_b.md` et reprises aux § 5 et 8 ; la justesse des explications attend la double annotation à l'aveugle ;
- toutes les commandes se lancent depuis la racine du dépôt (`python -m paquet.module`) ;
- la suite de tests passe sur `dev` le 25/11/2026 : `python -m pytest -q` donne 302 tests réussis et 6 ignorés, sans modèle ni réseau.

## 1. Parcours de bout en bout : une trace, un verdict, une explication

Exemple réel : `volet_a/web/public/examples/02_anomalie.log`, bloc `blk_-1013481023655112960`. Ce fichier est produit par `data/generate_web_examples.py` à partir de la **validation** officielle (le test reste réservé). Dans `Event_traces.csv`, ce bloc est `Fail`, type 31 ; dans `splits.csv`, il est `val`. Les valeurs ci-dessous ont été recalculées le 25/11 avec le code de `dev`.

1. **Quatre lignes brutes.** La dernière : `081110 010454 5105 INFO dfs.DataNode$DataXceiver: writeBlock blk_-1013481023655112960 received exception java.io.IOException: Could not read from stream`.
2. **En-tête et bloc** (`teamai/data/preprocess.py`, miroir JS `volet_a/web/src/preprocess.js`). `HEADER_REGEX` sépare date, heure, PID, niveau, composant et message ; `BLOCK_REGEX` (`blk_-?\d+`) trouve le bloc. Statistiques : 4 lignes, 4 reconnues, 0 inconnue, 0 en-tête invalide.
3. **EventId.** Chaque message est testé contre les 29 regex de `vocab.json`, dans l'ordre numérique ; la première qui correspond gagne. Séquence obtenue : `E22, E5, E5, E7` (allocation par le NameNode, deux débuts de réception, une exception d'écriture).
4. **Encodage C2** (`encode`). Indices `[22, 5, 5, 7]`, puis 46 zéros de padding à droite : tenseur `event_ids` int64 de forme `[1, 50]`.
5. **Verdict du volet A.** `detector.onnx` (entrée `event_ids`, sortie `p_anomaly`) donne **0,99999** ; le fichier INT8 donne la même décision. Le seuil figé de `detector.meta.json` est **0,40814146399497986** ; comme `score >= seuil`, le site affiche « anomalie ». Dans le navigateur, le même calcul tourne dans un Web Worker, avec ONNX Runtime Web en WASM.
6. **Faits du volet B** (`volet_b/slm/v16/facts.py`, `prepare_block`). Le parseur strict `data/parse_hdfs.py` reconnaît les 4 lignes, puis le code calcule les faits : `[F01]` 4 lignes, durée 3 s ; `[F02]` 0 WARN ; `[F03]` à `[F05]` comptes de E5, E7, E22 avec leur définition ; `[F06]` E5, E5 et E22 dans la même seconde, « ordre non déterminable ». La chronologie partielle compte 4 entrées `[T01]` à `[T04]`. Une seule preuve `[L01]` est retenue, la ligne E7, car E7 est un code atypique (`ATTENTION_CODES`).
7. **Hypothèse autorisée** (`policy.make_cause_catalog`). Le message E7 contient « Could not read from stream ». Le catalogue fermé autorise alors une seule phrase : « L'exception d'écriture pourrait être liée à l'impossibilité de lire le flux [L01]. »
8. **Prompt et schéma** (`runtime.build_prompt`, `runtime.schema`). Consigne, faits, chronologie et preuve forment un prompt de 4 331 caractères. Le schéma JSON impose les six champs C5 : `faits_observes` doit recopier 2 à 5 phrases `[Fxx]`, `hypotheses` ne peut contenir que la phrase autorisée, et `sources` reste vide. Aucun label ni score du volet A n'entre dans le prompt.
9. **Génération et contrôle** (`explain.explain_block`). `generate()` appelle Gemma 4 E4B QAT sous llama.cpp, à température 0, avec ce schéma. Le code contrôle ensuite les références, les ancrages, les alertes réseau et les boucles. S'il trouve une erreur, il autorise **une seule** correction.
10. **Variantes RAG et 3 agents.** La requête RAG paraphrase en anglais les événements distincts : « NameNode allocates a new block for a file being written. DataNode starts receiving a block from a client or another DataNode. Exception in DataNode writeBlock while receiving a block ». La suite dépend de l'index local, non versionné et non reconstruit ici : passages, rédaction, puis contrôle (§ 8).

À retenir : A et B lisent les **mêmes lignes**, mais **indépendamment**. A donne un score de détection ; B explique les preuves sans connaître ce score.

## 2. `teamai/` : socle partagé

- **Rôle** : code importé par tous, pour ne jamais écrire deux fois la même chose. `paths.py` centralise les chemins, `data/loader.py` charge les traces et le vocabulaire, `data/preprocess.py` publie le vocabulaire C2, `data/splits.py` lit les splits C4, `contracts.py` vérifie le format C5.
- **Entrées** : `python -m teamai.data.loader` affiche les statistiques du corpus ; `python -m teamai.data.preprocess` écrit `volet_a/web/public/vocab.json`.
- **Mécanisme** : `template_to_regex` échappe les caractères spéciaux d'un template Loghub et remplace `[*]` par `.*?`, entre `^` et `$`. La regex est ainsi lue de la même façon par Python et par JavaScript. `encode` garde les 50 premiers événements et complète à droite par 0 ; un événement inconnu vaut 30.
- **Contrôles** : `load_split` refuse un `splits.csv` dont le SHA-256 diffère de `splits_meta.json`. `validate_answer` vérifie les six champs C5 : avec `abstention: true`, `hypotheses` doit être vide et `infos_manquantes` non vide. `validate_example` exige un relecteur différent de l'annotateur ; `leaked_blocks` détecte un bloc commun entre adaptation et test.
- **Chiffres** : 29 événements, `PAD_ID = 0`, `UNK_ID = 30`, `MAX_LEN = 50` (`teamai/data/loader.py`).

**Questions probables**

- *Pourquoi 31 entrées d'embedding ?* 0 pour le padding, 1 à 29 pour E1 à E29, 30 pour un événement inconnu (contrat C2).
- *Que se passe-t-il si une ligne correspond à deux templates ?* Dans `preprocess.py` et `preprocess.js`, le premier EventId dans l'ordre numérique l'emporte. Le parseur strict `data/parse_hdfs.py` compte la ligne comme « ambiguë » et l'écarte.
- *Pourquoi les fonctions de contrôle renvoient-elles une liste d'erreurs au lieu de lever une exception ?* Pour compter les sorties non conformes, critère d'évaluation du volet B, sans jamais réparer la réponse.

## 3. `data/` : corpus, échantillon, splits

- **Rôle** : télécharger HDFS_v1 (`download_hdfs.py`, MD5 et reprise), tirer un échantillon partagé (`make_sample.py`), parser les lignes brutes (`parse_hdfs.py`), découper les splits (`make_splits.py`), produire les exemples du site (`generate_web_examples.py`).
- **Entrées** : `python -m data.download_hdfs`, puis `python -m data.make_splits` (seed 42, 70/15/15).
- **Mécanisme** : les blocs sont triés par `BlockId`, puis découpés deux fois par `train_test_split`, stratifié sur le label. Le drapeau `unseen_seq` marque les blocs du test dont la séquence complète est absente du train. `parse_hdfs.py` exige qu'un seul template corresponde (`fullmatch`) ; c'est ce parseur qu'utilise la v16.
- **Chiffres** : 575 061 blocs ; train 402 542 (11 787 anomalies), validation 86 259 (2 525), test 86 260 (2 526), soit 2,93 % partout ; 1 962 blocs de test à séquence inédite, 2,27 % (`data/splits/splits_meta.json`). 98,09 % des blocs appartiennent à des séquences répétées ; 10 séquences portent des labels contradictoires, sur 46 blocs (`docs/data/audit_hdfs_scrum18.md`). L'échantillon `data/sample/` compte 2 000 blocs, dont 25 % d'anomalies, extraits du C4 sans nouveau découpage (`data/sample/splits_provenance.json`).

**Questions probables**

- *Où est la fuite de données ?* Le découpage se fait par bloc, mais des séquences identiques se retrouvent de part et d'autre. D'où le sous-ensemble `unseen_seq`, toujours rapporté à côté du test complet.
- *Pourquoi stratifier ?* Pour garder 2,93 % d'anomalies dans chaque split ; aucun sous-échantillonnage des normaux (`normal_undersampling: false`).
- *L'échantillon à 25 % d'anomalies sert-il à l'évaluation ?* Non. Il sert au développement et au volet B ; les métriques du volet A portent sur la distribution naturelle.

## 4. `volet_a/` : détecteur BiLSTM dans le navigateur

**Entraînement (`volet_a/training/`)**

- **Entrées** : `python -m volet_a.training.train`, puis `python -m volet_a.training.export_onnx --run <dossier du run>`, puis `check_parity.py`. `baseline.py` sert de référence ; `analyze_threshold.py` révise le seuil (SCRUM-62).
- **Baseline** : comptages d'événements (`Event_occurrence_matrix.csv`), `StandardScaler` puis régression logistique avec `class_weight="balanced"`.
- **BiLSTM** (`bilstm.py`) : embedding 31 × 16 avec `padding_idx=0`, BiLSTM de 32 unités par direction, moyenne des sorties sur les seules positions non nulles, couche linéaire puis sigmoïde. Le modèle compte 13 361 paramètres.
- **Entraînement** (`train.py`) : 5 époques, lots de 512, Adam à 0,001, `BCEWithLogitsLoss` pondérée par `pos_weight` (normaux / anomalies), écrêtage du gradient à 1. Le seuil est d'abord choisi sur la macro-F1 de validation, avec une grille de 0,01 à 0,99 : il tombe sur la borne, 0,99.
- **Seuil SCRUM-62** : on maximise le F1 anomalie avec au plus deux anomalies manquées en validation. Seuil **0,40814146399497986** : 59 fausses alertes et 1 anomalie manquée, contre 23 et 21 au seuil 0,99 (`volet_a/training/README.md`, `eval/results/SCRUM-62_20261023T153242Z_690fcb/analysis.json`).
- **Export** : ONNX opset 17, lot dynamique. L'INT8 vient de `quantize_dynamic` (poids `QInt8`). `detector.meta.json` garde le seuil et les SHA-256 du modèle, du vocabulaire et des splits.

**Site (`volet_a/web/`)**

- **Entrées** : `cd volet_a/web`, `npm ci`, `npm run dev` ; `npm test` lance la parité JS. Le site est publié sur GitHub Pages depuis `main`, avec la base `/TeamAI/` (`vite.config.js`, `.github/workflows/deploy-volet-a.yml`).
- **Mécanisme** : `model.js` télécharge `detector.onnx`, vérifie son SHA-256 contre les métadonnées et le garde dans Cache Storage. Il crée ensuite une session ONNX Runtime Web en WASM, sur un seul thread. `worker.js` exécute l'inférence hors du fil de l'interface, par lots de 64 (`docs/volet_a/optimisation.md`). `main.js` applique `score >= seuil`. Le tableau, les filtres et l'export CSV sont dans `ui/results.js`.

**Chiffres du test officiel** (`eval/results/volet_a.md`, campagne unique SCRUM-44)

| Modèle | Population | Macro-F1 | Fausses alertes | Anomalies manquées |
|---|---|---:|---:|---:|
| Baseline | test complet (86 260) | 0,988227 | 116 | 2 |
| Baseline | séquences inédites (1 962) | 0,957585 | 67 | 2 |
| BiLSTM FP32 | test complet | 0,993846 | 58 | 3 |
| BiLSTM FP32 | séquences inédites | 0,971354 | 43 | 3 |

L'INT8 donne des métriques identiques. Parité Python / Chrome sur les 86 260 blocs : 0 décision divergente ; écart maximal 2,38 × 10⁻⁷ en FP32 et 0,00414 en INT8. Taille : 56 806 octets en FP32, 22 570 en INT8. Débit Chrome WASM, boucle JavaScript comprise : 6 198,58 blocs/s en FP32 et 3 004,27 en INT8 (`eval/results/volet_a.md`).

**Questions probables**

- *Pourquoi un BiLSTM ?* Il lit l'ordre des événements, que la baseline à comptages ignore. Il reste assez petit pour le navigateur (56 806 octets). Sur le test, il divise par deux les fausses alertes de la baseline (58 contre 116), pour une anomalie manquée de plus (3 contre 2).
- *Pourquoi HDFS est-il « facile » ?* Une régression logistique sur des comptages atteint déjà 0,988 de macro-F1, et 98,09 % des blocs ont une séquence répétée. La vraie difficulté est sur les séquences inédites : 0,958 pour la baseline, 0,971 pour le BiLSTM.
- *Pourquoi 0,408 et pas 0,5 ? Le score est-il une probabilité ?* Le seuil a été choisi sur la validation pour privilégier le rappel. Le score n'est pas calibré, car la perte est pondérée. Le test n'a servi à aucun choix.
- *Pourquoi le site sert-il le FP32 ?* Le candidat INT8 réduit la taille de 62 %, mais il est plus lent sur une trace isolée et ce n'est pas le fichier évalué dans SCRUM-44 (`docs/volet_a/optimisation.md`).

## 5. `volet_b/slm/` : modèle, interface unique et LoRA

- **Rôle** : `generate.py` est la seule porte vers le modèle. Le RAG et les agents l'appellent sans savoir si le modèle est de base ou adapté. `train_lora.py` entraîne l'adaptateur, `make_seed.py` produit des brouillons d'exemples, `convert_gguf.py` convertit l'adaptateur en GGUF, `kaggle_bundle.py` et `kaggle_lora_essai.py` préparent l'essai de 30 pas, `kaggle_lora_final.py` mène l'entraînement complet, l'export et la sélection sur val (SCRUM-39), et `verif_machine.py` contrôle l'adaptateur sur une machine donnée (SCRUM-61).
- **Entrées** : `generate(messages, adapter=None)` ; `python -m volet_b.slm.kaggle_lora_essai --bundle sortie.zip`, puis, sur Kaggle, `--steps 3` et `--steps 30` ; pour le LoRA final, `python -m volet_b.slm.kaggle_lora_final --train` puis `--select`. `TEAMAI_SLM_MOCK=1` renvoie une réponse C5 factice sans charger de poids.
- **Configuration** (`configs/generation.yaml`) : `google/gemma-4-E4B-it-qat-q4_0-gguf`, révision `4b4a2c1d…`, backend llama.cpp, contexte 4 096, 800 tokens, température 0, seed 42, réflexion désactivée, `local_files_only: true`, `n_gpu_layers: -1`. L'instance llama.cpp est gardée en cache (`lru_cache`).
- **LoRA final** (`configs/lora_final.yaml`, SCRUM-39) : même base et même QLoRA que l'essai, 400 pas (2 époques), contexte d'entraînement de 4 096 tokens, un exemple trop long écarté entier et listé, jamais tronqué. Deux réglages : `r8_qv` (r = 8, `q_proj` et `v_proj`, lr 2 × 10⁻⁴) et `r16_qkvo` (r = 16, q/k/v/o, lr 1 × 10⁻⁴). La règle de sélection sur val (acceptation, hypothèses par bloc avec incident, erreurs d'appui) est fixée avant l'entraînement.
- **LoRA de l'essai** (`configs/lora_essai.yaml`) : base HF `gemma-4-E4B-it-qat-q4_0-unquantized` (révision `476025a…`), QLoRA NF4 avec calcul en fp16, r = 8, alpha = 16, `q_proj` et `v_proj`, lot de 1, 30 pas, lr 2 × 10⁻⁴, 3 072 tokens au plus sans troncature. La perte ne porte que sur le JSON de la réponse et le marqueur de fin de tour : `logits_to_keep` évite de calculer les logits du prompt sur un vocabulaire de 262 144 tokens.
- **Données** : pour le LoRA final, la [version de SCRUM-36 utilisée au commit `faabb47`](https://github.com/LindaBOUKHIT/TeamAI/tree/faabb47f454b1b47bfc138de840d83ce957cb187/volet_b/annotations) comptait 200 exemples train et 40 val, dont 60 avec une relecture croisée consignée. Pour l'essai, 20 brouillons tirés des blocs **train** du sample avec les fonctions v16 (`make_seed.py`). `lora_data.prepare_examples` vérifie le split C4 de chaque bloc et réserve les blocs train à l’entraînement et les blocs val à la validation.
- **Chiffres** du LoRA final, T4 Kaggle du 25/11 (`eval/results/SCRUM-39/kaggle_final/README.md`) : 199 exemples sur 200 (`bachar-049`, 5 778 tokens, écarté), 400 pas sans pas sauté pour chaque réglage. `r8_qv` : perte 0,880 → 0,151, pic VRAM 11,1 Go, 6,5 s par pas. `r16_qkvo` : perte 0,827 → 0,140. Sur val, égalité parfaite (39/40 acceptées, 12 hypothèses chacun, 11 pour la base) : l'ordre de la configuration retient `r8_qv`, le plus petit, ce départage étant constaté et non décidé à l'avance. Adaptateur GGUF de 4 547 904 octets, SHA-256 `52ff1ba7…59db7b`, versionné dans le dépôt.
- **Chiffres** de l'essai T4 Kaggle du 08/11 (`docs/projet/journal.md`, entrée SCRUM-29) : 30 pas appliqués, 0 sauté, perte moyenne de 0,586 sur les 5 premiers pas à 0,052 sur les 5 derniers, 4,9 s par pas, pic VRAM 10,24 Gio, 2 269 184 paramètres entraînables. Adaptateur GGUF F16 de 4 547 904 octets, `inference_validated: false` (`eval/results/SCRUM-29/kaggle_t4_gguf_meta.json`).

**Questions probables**

- *Pourquoi QLoRA ?* Les poids BF16 de la base pèsent environ 15,9 Go, autant que la T4 de 16 Go. En NF4, l'entraînement tient, avec un pic à 10,24 Gio.
- *La perte qui baisse prouve-t-elle que LoRA aide ?* Non : elle porte sur les exemples d'entraînement. Sur val, l'effet est faible (une hypothèse de plus). Sur le test (SCRUM-45, `eval/results/volet_b.md`), à 1 agent, les acceptations ne changent pas (79/80) mais les résumés qui affirment un ordre entre événements passent de 35/80 à 1/80. À 3 agents, le contrôleur accepte 25 réponses sur 80 au lieu de 9. Ces mesures portent sur la forme et l'appui ; la justesse relève de la double annotation à l'aveugle. L'inférence sur la RTX 3050 reste à faire (`verif_machine.py`, SCRUM-61).
- *Pourquoi deux bases différentes ?* On entraîne sur les poids HF non quantifiés de la version QAT et on infère sur le GGUF Q4_0 officiel, l'adaptateur étant chargé par `lora_path`. Sur T4, l'adaptateur appliqué au GGUF à l'échelle 0 redonne exactement la sortie de la base, et l'échelle 1 la modifie ; sur le test, il ajoute moins de 10 Mio de mémoire GPU. La fusion puis requantification n'est pas retenue : elle ne reproduit pas le GGUF QAT officiel.

## 6. `volet_b/slm/v16/` : explication contrôlée, sans RAG

- **Rôle** : la référence du volet B. Elle explique les preuves d'un bloc ; elle ne détecte rien.
- **Entrée** : `prepare_block(block_id, lignes numérotées, templates)` puis `explain_block(block)` ; voir l'exemple du § 1.
- **Mécanisme** : le code calcule les faits (`[Fxx]`), une chronologie partielle (`[Txx]`, première et dernière occurrence de chaque code) et les messages à examiner (`[Lxx]` : codes atypiques ou niveaux WARN, ERROR, FATAL). Le glossaire est réduit aux codes présents. Le schéma JSON transforme les faits et les hypothèses autorisées en listes fermées (`enum`). Le catalogue de causes ne connaît que deux cas lisibles dans le message (E7 « Could not read from stream » et E20 « BlockInfo not found in volumeMap ») ; tout autre code atypique donne « cause indéterminée ».
- **Garde-fous** : une seule correction (`runtime.run_block`). Ajout du port : `explain.repetition_errors` rejette une référence ou un segment répété 6 fois de suite, ou une réponse d'au moins 760 tokens sur 800.
- **Chiffres** de la validation unique sur 40 nouveaux blocs `val`, deux T4 Kaggle : 40/40 contrats conformes et faits recopiés exactement ; 39/40 contrôles factuels passés ; références inexistantes de 1/40 au premier essai à 0/40 après correction ; 30,624 s par bloc (`eval/results/SCRUM-63/comparaison_v16_validation.json`). La revue humaine relève 2/40 chronologies fausses, 3/40 causalités non démontrées et 1/40 résumé en boucle (`eval/results/SCRUM-63/revue_qualitative_validation.json`). Choix du modèle en v11 : Gemma 40/40 conformes, Granite 22/40 (`eval/results/SCRUM-63/README.md`).

**Questions probables**

- *Pourquoi faire calculer les faits par le code ?* Un petit modèle invente des nombres et des événements. Ici, il ne peut que recopier des phrases calculées, imposées par le schéma.
- *Le modèle peut-il inventer une cause ?* Pas dans le champ `hypotheses`, limité aux formulations du catalogue. Le résumé reste du texte libre : c'est là que la revue trouve encore des erreurs de chronologie et de causalité.
- *40/40 conformes, est-ce 40/40 justes ?* Non. La conformité porte sur la forme ; la justesse se mesure par la grille humaine (SCRUM-45).

## 7. `volet_b/rag/` : corpus documentaire et recherche

- **Rôle** : retrouver des passages de documentation HDFS officielle pour les variantes avec RAG.
- **Entrées** : `python -m volet_b.rag.build_corpus` écrit `corpus/chunks.jsonl` (C6) ; `python -m volet_b.rag.build_index` construit l'index FAISS, non versionné ; `python -m volet_b.rag.evaluate_retrieval` écrit le rappel@3 dans `eval/results/SCRUM-37/`.
- **Mécanisme** : deux guides Hadoop 1.2.1, Architecture et Users (`corpus/sources.md`), découpés par section, 1 600 caractères au plus, coupés sur une fin de ligne ou une espace. Embeddings `BAAI/bge-small-en-v1.5`, `IndexFlatIP` sur vecteurs normalisés, soit une similarité cosinus exacte. La requête paraphrase en anglais les événements distincts (`event_descriptions.json`), sans label. Le mode `hybrid`, par défaut, fusionne les classements dense et BM25 par Reciprocal Rank Fusion (`RRF_K = 60`) ; `k = 3` par défaut.
- **Chiffres** : 51 passages par section, contre 28 en fenêtre glissante, dont 26 à cheval sur deux sections (`corpus/chunking_comparison.json`). Rappel@3 sur 306 traces `val` du sample : dense sur template brut 0,3233 ; dense sur paraphrase 0,3481 ; BM25 0,6948 ; hybride 0,6644 (`eval/results/SCRUM-37/retrieval_val.json`).

**Questions probables**

- *Pourquoi l'hybride si BM25 fait mieux ?* L'écart est faible, et l'hybride garde les embeddings, plus robustes aux reformulations libres des agents (décision SCRUM-37, `docs/projet/journal.md`).
- *Pourquoi aucun seuil de score ?* Les passages non pertinents ont des scores denses aussi élevés que les pertinents (`score_separation`) : un seuil en retirerait autant des uns que des autres.
- *Pourquoi la référence v16 n'utilise-t-elle pas le RAG ?* Elle a été validée sans. La variante v16 + RAG n'est pas figée : `run_config.py` refuse `rag1` avec un message explicite.

## 8. `volet_b/agents/` : un agent ou trois agents

- **Un agent** (`single_agent.py`, SCRUM-37) : trace (60 lignes au plus), 3 passages, un appel à `generate()`, puis `validate.check_answer` (JSON, C5, sources limitées aux passages fournis). Ce prompt (`prompts/single_agent.txt`) n'est pas celui de la v16.
- **Trois agents** (`orchestrator.py`, SCRUM-42) : une seule instance du modèle, au plus 5 appels par bloc et une reprise. Les rôles s'enchaînent :
  - **recherche** (`roles/search.py`) : le modèle choisit au plus 2 passages parmi 5 candidats, par `enum`, avec un budget de 3 000 caractères ;
  - **rédaction** (`roles/writer.py`) : sans passage, c'est le prompt v16 à l'identique ; sinon deux phrases fixes sont remplacées et une section DOCUMENTATION est ajoutée ;
  - **contrôle** (`roles/checker.py`) : le code vérifie d'abord C5, v16, les boucles et l'arrêt normal ; le modèle ne rend son verdict (`accepte`, `corriger`, `abstention`) que si ces contrôles passent.
  Un ordre affirmé entre événements de la même seconde déclenche la reprise par le code, sans appel au contrôleur. La réponse finale n'est jamais réparée. Statuts possibles : `accepte`, `rejete`, `abstention_demandee`, `non_controle`.
- **Entrées** : `python -m volet_b.agents.single_agent --split val --n 5 --mock` ; `python -m volet_b.agents.orchestrator`. Le split `test` est refusé dans les deux cas.
- **Chiffres** du test réservé, T4 Kaggle du 25/11 (SCRUM-45, `eval/results/volet_b.md`), 80 cas, échecs au dénominateur : à 1 agent, 79/80 acceptées avec ou sans LoRA ; à 3 agents, 9/80 pour la base et 25/80 avec le LoRA. Latence moyenne : 27,8 s et 24,6 s à 1 agent, 84,3 s et 73,8 s à 3 agents. Aucune hypothèse sur un bloc sans incident. La recherche ne renvoie que 4 passages distincts sur les 80 cas.
- **Chiffres** de la validation, T4 Kaggle : runs 1 et 2, 1 bloc accepté sur 5, 5/5 conformes C5 ; run 3, 0 accepté sur 10, 10/10 conformes C5, passages cités dans 3 réponses finales sur 10 (`eval/results/SCRUM-42/kaggle_val5*/`). Porte Laya (SCRUM-58) abandonnée : AUC de 0,47 entre `Fail` et `Success` sur la validation unique (`eval/results/SCRUM-58/README.md`, `laya_gate.py`).

**Questions probables**

- *Quel est le gain réel des agents ?* Sur le test, aucun gain d'acceptation : 9/80 à 3 agents contre 79/80 à 1 agent pour la base, pour une latence trois fois plus élevée. Avec le LoRA, 25/80, dont 12 blocs avec incident et 5 réponses qui citent la documentation. À la relecture, environ un rejet sur trois est justifié (un ordre inventé entre des événements de la même seconde). Sur 10 blocs de validation, le contrôleur rejetait déjà tout. Il rejette aussi des réponses sans erreur visible et manque des ordres affirmés (`eval/results/SCRUM-42/kaggle_val5_v3/README.md`).
- *Pourquoi 5 appels au plus ?* Chaque appel coûte de l'ordre de 30 s sur T4 (`volet_b/README.md`). La limite borne le coût : 1 recherche, puis 2 rédactions et 2 contrôles au plus.
- *Que se passe-t-il si le contexte de 4 096 tokens déborde ?* Le code retire des passages avant l'appel. Si le contrôle ne tient pas, aucun appel n'est fait et la réponse prend le statut `non_controle`.

## 9. `volet_b/app/` : démonstration locale

- **Rôle** : interface Gradio. On colle des logs ou on importe un fichier, on choisit 1 ou 3 agents, base ou adapté, et on lit le résumé, les faits, les hypothèses, les sources et le journal des étapes.
- **Entrées** : `python -m volet_b.app.app` (http://127.0.0.1:7860), ou `--mock` pour la démo sans modèle.
- **Mécanisme** : `analyze` regroupe les lignes par bloc et refuse **toute** l'entrée si un bloc est dans le test. Sans `splits.csv` complet, il refuse aussi les blocs absents du sample. Il traite au plus 5 blocs et échappe tout texte issu des données (`safe`). Avec 3 agents, il appelle `prepare_block` puis l'orchestrateur ; avec 1 agent, `single_agent`. Les exemples proposés sont des blocs de validation de 20 lignes au plus (`DEMO_MAX_LINES`). Le serveur écoute sur `127.0.0.1`, sans partage public.
- **Chiffres** des essais CPU du 24/11 sur le portable d'Alain (i5-1240P, sans GPU) : un bloc de 39 événements demande 4 329 tokens pour 4 096 ; sur un bloc de 20 événements, 1 agent rend un JSON invalide en 397,6 s et 3 agents font 5 appels en 1 519,7 s, réponse rejetée (`eval/results/SCRUM-43/cpu_24-11/README.md`). Ce sont des essais de fonctionnement, pas une mesure de qualité.

**Questions probables**

- *Pourquoi refuser les blocs du test dans la démo ?* Pour ne jamais exposer le jeu réservé au modèle ni à l'équipe avant l'évaluation finale.
- *Pourquoi limiter les exemples à 20 lignes ?* Un bloc de 39 lignes dépassait le contexte de 4 096 tokens.
- *La démo marche-t-elle sur CPU ?* Oui, mais lentement, de l'ordre de plusieurs minutes par bloc. La cible est le GPU de la RTX 3050.

## 10. `eval/` : protocoles et résultats

- **Rôle** : évaluer sans tricher. `metrics.py` calcule précision, rappel, macro-F1 et matrice de confusion ; `volet_a/evaluate.py` porte la campagne SCRUM-44 ; `volet_b/run_config.py` mesure la configuration de base v16 (SCRUM-38/45) ; `volet_b/gpu_memory.py` échantillonne la VRAM du processus toutes les 0,2 s. Les résultats sont dans `results/`, les sorties brutes C7 dans `runs/` (non versionné).
- **Entrées** : `python -m eval.volet_a.evaluate --preflight` ne lit jamais le test. `--run-final --confirm-test-once SCRUM-44-TEST-UNIQUE` crée un marqueur irrévocable **avant** d'ouvrir le test. `python -m eval.volet_b.run_config --config base` vérifie le SHA-256 du test C5 contre `test.sha256` et refuse `rag1`.
- **Mécanisme** : le seuil, l'empreinte du modèle FP32 et celle des splits sont figés dans le code (`EXPECTED_THRESHOLD`, `EXPECTED_FP32_SHA`, `EXPECTED_SPLITS_SHA`). Trois populations : test complet, séquences inédites, et test sans les 3 blocs exposés auparavant.
- **Chiffres** : volet A au § 4 (`eval/results/volet_a.md`) ; comparaison A/B dans `eval/results/comparaison_a_b.md` ; volet B dans `eval/results/volet_b.md` (SCRUM-45 : 4 configurations sur les 80 cas du test, le 25/11).

**Questions probables**

- *Pourquoi la macro-F1 et pas l'accuracy ?* Avec 2,93 % d'anomalies, un modèle qui répond toujours « normal » obtient 97,07 % d'accuracy sans rien détecter.
- *Comment prouver que le test n'a été ouvert qu'une fois ?* Par le marqueur créé avant l'ouverture, les empreintes figées et le dossier C7 de chaque modèle. Un précédent est déclaré dans `volet_a.md` : un fichier SCRUM-24 contenait déjà des résultats de test (commit `b77b1a2`), sans usage pour le réglage.
- *Peut-on comparer la macro-F1 de A à la qualité de B ?* Non. A détecte, B explique : ce sont deux tâches différentes, comparées axe par axe dans `comparaison_a_b.md` (coût, latence, contrôle, déploiement).

## 11. Questions croisées : qui s'entraîne sur quoi

Chacun explique une partie qu'il n'a pas codée, d'après les responsables indiqués dans les README.

| Bloc | Codé surtout par | À faire expliquer par |
|---|---|---|
| Parsing, splits (`data/`, `teamai/data/`) | Nassim, Linda (prétraitement C2, SCRUM-26) | Alain, Bachar |
| BiLSTM, ONNX, site (`volet_a/`) | Bachar, Nassim, Linda (prétraitement JS) | Alain |
| LoRA, v16 (`volet_b/slm/`) | Alain | Bachar, Nassim |
| RAG, agents, app (`volet_b/rag/`, `agents/`, `app/`) | Linda | Bachar, Nassim |
| Évaluation (`eval/`) | Nassim, tous | Linda, Bachar |

Critère de fin du ticket : chaque membre répond sans aide sur chaque bloc.
