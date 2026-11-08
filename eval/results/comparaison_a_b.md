# Comparaison volet A / volet B — squelette SCRUM-47

## Objet et règles

Ce document prépare la comparaison technique prévue dans `docs/rapport/plan.md`.
Les chiffres proviennent uniquement des dossiers C7 ou de leurs résumés dans `eval/results/`, avec machine et méthode ; une information absente reste « à mesurer » ou « non relevé ».
Toute différence de machine, backend, tâche ou périmètre de chronométrage doit être déclarée avant comparaison.
Aucune métrique de test n'est encore disponible : A reste à mesurer dans SCRUM-44 et B dans SCRUM-45.
Le volet B est décrit d'après `dev` au 09/11 : le passage à Gemma 4 E4B QAT (SCRUM-63), l'essai LoRA (SCRUM-29) et les défauts v16 (SCRUM-46) sont encore en PR. La colonne B sera mise à jour après leur fusion.

## Tableau principal

| Axe | Volet A | Volet B | Source | Statut |
|---|---|---|---|---|
| Coût | Coût financier, énergie et temps humain : à mesurer. | Coût financier, énergie et temps humain de l'adaptation et de l'inférence : à mesurer. | `docs/contrats.md` (C7) ; `docs/rapport/plan.md` | à mesurer : SCRUM-44 / SCRUM-45 |
| Latence | Latence du détecteur final dans le navigateur : à mesurer. La durée d'entraînement ne constitue pas une latence d'inférence. | Latence de la chaîne Gemma + LoRA + RAG : à mesurer. Observation historique SmolLM2 détaillée ci-dessous, non transposable. | `eval/results/SCRUM-25-bilstm-v1/metrics.json` ; `eval/results/SCRUM-28/README.md` | à mesurer : SCRUM-44 / SCRUM-45 ; historique technique pour B |
| Qualité des résultats | Détection binaire. Métriques de validation globale et `unseen` ci-dessous ; qualité finale : à mesurer. | Explication d'un bloc. Retrieval évalué sur validation ; qualité des explications de la cible : à mesurer. Les tâches diffèrent. | `eval/results/SCRUM-25-bilstm-v1/metrics.json` ; `eval/results/SCRUM-62_20261023T153242Z_690fcb/analysis.json` ; `eval/results/SCRUM-37/retrieval_val.json` ; `docs/contrats.md` (C3/C5) | attesté (val) ; à mesurer : SCRUM-44 / SCRUM-45 |
| Degré de contrôle | Architecture BiLSTM entraînée par l'équipe, export ONNX, seuil choisi sur validation et hashes conservés. | Poids préentraînés empruntés ; contrôle du prompt, du retrieval et des règles de sortie. Adaptation LoRA de la cible : non attestée dans les sources lues. | `eval/results/SCRUM-25-bilstm-v1/config.json` ; `docs/projet/journal.md` ; `volet_b/slm/README.md` ; `docs/contrats.md` | qualitatif |
| Explicabilité | Classe et score ; le score n'est pas présenté comme une probabilité calibrée. Une anomalie ne donne pas une cause de panne. | Contrat d'explication : faits, hypothèses, informations manquantes, sources et abstention. Une structure valide ne prouve pas la justesse de l'explication. | `docs/contrats.md` (C3/C5/C6) | qualitatif ; qualité à mesurer : SCRUM-45 |
| Dépendance fournisseur | Poids entraînés par l'équipe ; dépendance au format ONNX et au runtime navigateur. | Dépendance aux poids et à leur révision amont, au backend et au modèle d'embeddings. Conditions de licence de la cible : non relevé dans les sources lues. | `docs/projet/journal.md` ; `volet_b/slm/configs/generation.yaml` ; `docs/contrats.md` | qualitatif |
| Effort de données | Traces, labels, parsing, vocabulaire et splits nécessaires à l'entraînement. Temps de préparation : non relevé. | Exemples annotés et relus pour LoRA ; corpus documentaire et références pour le RAG. Temps d'annotation et de maintenance : non relevé. | `docs/contrats.md` (C1/C2/C4/C5/C6) | qualitatif ; à mesurer : SCRUM-44 / SCRUM-45 |
| Reproductibilité | Configuration, hashes des données, splits et sources conservés. Le relevé d'entraînement indique des fichiers modifiés ou non suivis : le commit seul ne suffit pas. | Révision SmolLM2 figée et preuves historiques conservées. La configuration de la cible Gemma, de l'adaptateur et du RAG reste à consigner ensemble selon C7. | `eval/results/SCRUM-25-bilstm-v1/config.json` ; `eval/results/SCRUM-28/README.md` ; `volet_b/slm/configs/generation.yaml` ; `docs/contrats.md` | qualitatif ; à compléter : SCRUM-44 / SCRUM-45 |
| Empreinte mémoire | Mémoire du processus navigateur et pic pendant l'inférence : non relevé. Taille d'un fichier ONNX et mémoire vive ne sont pas interchangeables. | Mémoire de la cible complète : à mesurer. RSS historique SmolLM2 détaillée ci-dessous ; elle ne décrit pas Gemma ni le RAG. | `eval/results/SCRUM-62_20261023T153242Z_690fcb/browser_check.json` ; `eval/results/SCRUM-28/README.md` | à mesurer : SCRUM-44 / SCRUM-45 ; historique technique pour B |
| Déploiement | Site statique et exécution ONNX Runtime Web/WASM attestés ; qualification du modèle final : à compléter. | Cible de mission : Gemma 4 E4B QAT sous llama.cpp, LoRA et RAG. Les sources lues documentent encore SmolLM2 via Transformers et un banc GGUF séparé ; déploiement de la cible : non attesté. | `docs/projet/journal.md` ; `eval/results/SCRUM-62_20261023T153242Z_690fcb/browser_check.json` ; `volet_b/slm/README.md` ; `volet_b/slm/configs/generation.yaml` | qualitatif ; à mesurer : SCRUM-44 / SCRUM-45 |

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

**Emplacement SCRUM-44** : [à mesurer : version et seuil figés ; machine ; backend ; protocole ; qualité globale et inédite ; latence ; mémoire ; coût ; chemins des preuves C7].

## Volet B : portée des preuves disponibles

B explique un bloc ; il ne constitue pas le détecteur binaire de A. Le contrat de sortie porte sur le résumé, les faits, les hypothèses, les informations manquantes, les sources et l'abstention (`docs/contrats.md`, C5). Comparer directement une macro-F1 de détection à une qualité d'explication serait comparer des tâches différentes. Les anciens prompts demandant aussi un avis normal/anormal ne changent pas cette limite.

La cible Gemma 4 E4B QAT sous llama.cpp, adaptée par LoRA et associée au RAG, est le périmètre demandé pour cette mission. Elle n'est pas attestée comme configuration intégrée dans les fichiers lus. Le README SLM et le YAML décrivent encore SmolLM2, et le backend GGUF reste décrit comme un banc séparé (`volet_b/slm/README.md` ; `volet_b/slm/configs/generation.yaml`). Aucun résultat v16 sur blocs de validation n'est présent dans `docs/projet/journal.md` : non relevé.

### Historique SmolLM2 : aucune extrapolation à Gemma

SCRUM-28 décrit SmolLM2 en float32, Transformers/PyTorch CPU, sur la machine d'Alain : **i5-1240P, 32 Go, sans GPU NVIDIA** (`eval/results/SCRUM-28/README.md`). La mesure couvre un bloc de développement ; elle ne valide ni LoRA ni le RAG.

- Génération : **156 tokens en 952,03 s, soit 0,16 token/s** (`eval/results/SCRUM-28/README.md`). Le temps inclut le traitement du prompt dans `model.generate()`, hors tokenisation, décodage et fichiers.
- Chargement : **238,0 s** (`eval/results/SCRUM-28/README.md`), imports, tokenizer et poids en cache inclus.
- RSS après chargement : **6,77 GiB** ; pic au chargement : **9,84 GiB** ; pic en génération : **8,00 GiB** (`eval/results/SCRUM-28/README.md`). Le RSS du processus est échantillonné toutes les **0,2 s** (`eval/results/SCRUM-28/README.md`) ; les pics plus brefs peuvent être manqués. VRAM : non relevé.

La réponse historique omet les avertissements et invente des informations. Ce cas isolé ne permet pas une conclusion générale sur la qualité (`eval/results/SCRUM-28/README.md`). Les comparaisons entre anciennes exécutions ne sont pas contrôlées.

SCRUM-57 est décrit dans le journal comme une observation historique SmolLM2 GGUF sous llama.cpp face à Transformers, avec backend et quantification différents. Aucun chiffre de cette entrée n'est repris ici : aucun dossier C7 ou résumé dédié dans `eval/results/` n'a été identifié parmi les sources demandées. Ce banc n'atteste pas la cible Gemma (`docs/projet/journal.md` ; `volet_b/slm/README.md`).

### Retrieval : validation, pas qualité globale des explications

Le retrieval est évalué sur **306 traces** (`eval/results/SCRUM-37/retrieval_val.json`), split `val (data/sample)`. Pour la méthode hybride et les requêtes par description, **k = 3**, le rappel des traces vaut **0,6644**, et les templates trouvés **6/10** (`eval/results/SCRUM-37/retrieval_val.json`). Ces chiffres mesurent la récupération documentaire, pas la justesse des réponses générées. Le JSON ne relève pas la machine ; aucune mesure de performance matérielle n'en est déduite.

Le journal précise que références et paraphrases viennent de l'équipe et que les traces répètent peu de séquences distinctes. L'agent complet y est seulement vérifié en mode factice ; cela n'atteste pas la qualité du SLM réel (`docs/projet/journal.md`, entrée SCRUM-37).

**Emplacement SCRUM-45** : [à mesurer : modèle et révision ; adaptateur LoRA ; corpus et retrieval ; machine ; backend et quantification ; protocole ; qualité factuelle ; citations ; abstention ; erreurs de format ; latence complète ; mémoire ; coût ; chemins des preuves C7].

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
