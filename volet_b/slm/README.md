# SLM actuel — Gemma 4 E4B QAT, prompt v16 figé (SCRUM-63)

`generation.yaml` sélectionne `google/gemma-4-E4B-it-qat-q4_0-gguf`, fichier
`gemma-4-E4B_q4_0-it.gguf`, révision `4b4a2c1d584be7264f87aac328a1bc739ce81b6c`.
Contexte 4096, réponse 800 tokens, température 0, seed 42, repeat_penalty 1.0,
réflexion désactivée. Le cache local est imposé par défaut (`local_files_only: true`).
Une version de llama-cpp-python compatible Gemma 4 est nécessaire ; l’exploration
utilisait 0.3.36. Aucun modèle n’a été chargé ou téléchargé pour ce port.

Gemma a été retenu après comparaison exploratoire (v11 : 40/40 contrats contre
22/40 pour Granite). Les erreurs de causalité et de chronologie persistent :
[trace et limites SCRUM-63](../../eval/results/SCRUM-63/README.md).
La machine cible est le portable de Nassim ; son environnement CUDA/Python et
ses performances restent à relever. Le chargeur local existant reste sur CPU ;
le passage GPU sur ce portable n’est pas validé par ce port.

```python
from data.parse_hdfs import compile_templates
from teamai.paths import resolve_path
from volet_b.slm.v16.facts import prepare_block
from volet_b.slm.v16.explain import explain_block

templates = compile_templates(resolve_path("tests/fixtures/preprocessed/HDFS.log_templates.csv"))
# lines : couples (numéro de ligne dans le journal source, texte brut), dans l’ordre.
# Le numéro d’origine est nécessaire à l’identité des références Txx.
block = prepare_block(block_id, lines, templates)
result = explain_block(block)
# À conserver par l’appelant : result["first_response"], result["second_response"].
```

`prepare_block` ne reçoit aucun label. Le glossaire est restreint aux codes présents
lors de la construction des faits. `explain_block` envoie le prompt et le schéma
JSON fermés à `generate()`, vérifie le contexte avant chaque appel et contrôle les
réponses. Comme le worker v16, le template par défaut doit être identique à celui
produit avec `enable_thinking=False`, sans marqueur de réflexion. Le budget des
prompts est 2900 tokens bruts et une marge de 32 tokens après formatage.

Les contrôles v16 et leur déclencheur de correction sont conservés. Seul ajout :
une référence ou un segment de tokens lexicaux répété six fois de suite,
ou une réponse utilisant au moins 95 % des 800 tokens (760), est rejeté après
les contrôles v16. Cette erreur précise déclenche la correction unique partagée.
La seconde réponse reste conservée même invalide, sans troisième appel.
Si le contexte interdit la correction, la première réponse et la raison restent
conservées. Les alertes de revue sémantique ne certifient pas la vérité du résumé.

`generate(messages, adapter=None)` conserve son retour habituel `text`, `new_tokens`,
`seconds` et le mode `TEAMAI_SLM_MOCK=1`. Les options `response_format` (schéma JSON)
et `return_metadata=True` (ajout de `finish_reason`, `prompt_tokens`) servent au
contrôle v16. Un adaptateur SmolLM2 historique n’est pas compatible avec Gemma.
Les chaînes RAG/agents existantes utilisent encore leurs propres prompts ; leurs
résultats ne sont pas une exécution v16. La référence v16 fonctionne sans RAG,
sans LoRA et ne détecte pas les anomalies : elle explique les preuves reçues.

Vérification sans GGUF ni réseau : `python -m pytest -q`.
`tests/test_v16.py` reconstruit les 40 prompts à partir de lignes `val` uniquement,
vérifie leurs SHA-256 et ceux des schémas et de la consigne contre le gel original.
La politique originale est conservée byte pour byte dans la trace ; son SHA-256
est vérifié et son AST est comparé à celui de la politique exécutée après retrait
des seules docstrings ajoutées pour SCRUM-59. Les empreintes de référence ne
sont jamais régénérées. Le SHA du runtime Kaggle est une provenance historique :
le module porté exclut l’orchestration Kaggle et ajoute le contrôle autorisé.

## Historique SmolLM2 — SCRUM-28 et SCRUM-57

Les sections ci-dessous décrivent les anciens essais SmolLM2 et leurs commandes.
Elles ne décrivent pas le modèle actuel. Les configurations C7 archivées restent
la référence pour leur reproduction ; le YAML actuel ne reproduit pas ces essais.

# Première inférence locale — SCRUM-28

Responsable : Alain. Relectrice : Linda. [PR #4](https://github.com/LindaBOUKHIT/TeamAI/pull/4) vers `dev`.

Ce composant fournit `generate()` et une commande de vérification technique sur une trace HDFS. Il ne fournit pas encore le RAG, les agents, l'adaptation LoRA ou une réponse structurée fiable du modèle réel.

## Installation

Depuis la racine du dépôt, avec Python 3.12 :

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[data,slm]"
```

`slm` contient seulement les dépendances de la première inférence. L'extra `volet_b` ajoute les composants des futurs tickets, dont PEFT pour utiliser un adaptateur. La configuration YAML est incluse dans le paquet Python.

Versions relevées sur la machine d'Alain le 08/10 : Python 3.12.10, torch 2.12.0 (CPU), transformers 4.57.6, pandas 3.0.3, PyYAML 6.0.3, psutil 7.2.2, hf-xet 1.6.0. Pour reproduire cet environnement, installer ces versions après les extras ; le fichier `config.json` de chaque exécution conserve les versions effectivement utilisées. Les exigences du paquet sont des plages de compatibilité, pas un verrou complet des dépendances transitives.

Le modèle est `HuggingFaceTB/SmolLM2-1.7B-Instruct`, en float32 sur CPU. Sa révision est fixée dans `configs/generation.yaml`. `revision` et `local_files_only` sont transmis aux chargeurs selon la [documentation Transformers](https://huggingface.co/docs/transformers/v4.57.1/en/main_classes/model#from_pretrained).

## Mode factice pour Linda

Cette commande n'importe pas PyTorch et ne charge aucun poids :

```powershell
$env:TEAMAI_SLM_MOCK = "1"
python -c "from volet_b.slm.generate import generate; print(generate('Explique cette trace factice.'))"
Remove-Item Env:TEAMAI_SLM_MOCK
```

`generate()` accepte un prompt texte ou une liste de messages `{"role": "user", "content": "..."}`. Il retourne `text`, `new_tokens` et `seconds`. Dans le mode factice, `text` contient le JSON C5, avec abstention et listes vides ; les compteurs valent zéro. Ces résultats ne participent jamais aux mesures de qualité ou de vitesse du modèle.

La sortie réelle est du texte brut. C'est au consommateur de l'analyser et de contrôler son format et ses sources. Le simple essai de résumé historique ne sollicite pas les six champs C5 et ne valide donc pas leur génération par le modèle.

## Exécution réelle

Les fichiers publics `data/raw/HDFS_v1/HDFS.log` et `preprocessed/Event_traces.csv` sont requis. S'ils sont absents, utiliser `python -m data.download_hdfs` (téléchargement, MD5 et extraction). Aucun jeu de test réservé n'est utilisé pour cet essai technique. Le bloc inspecté sert au développement et doit être exclu du futur test réservé du volet B.

Avec les poids déjà en cache :

```powershell
python -m volet_b.slm.first_inference --offline --block-id blk_8362325295506522506 --torch-threads 12
```

Pour un premier téléchargement, retirer `--offline`. Vérifier le disque du cache avant de charger le modèle. Sur la machine d'Alain, le cache existant est défini par l'environnement Hugging Face sur `D:` ; ne pas le déplacer pour cette relecture.

Le script refuse `TEAMAI_SLM_MOCK=1` afin de ne pas enregistrer une réponse factice comme inférence réelle. `--block-id` fixe le bloc ; sans cet argument, le premier bloc anormal de longueur moyenne du corpus est choisi. Le prompt historique du 06/10 est conservé, avec les logs avant la consigne. Aucun label attendu n'est fourni au modèle.

## Sorties et mesures

Chaque exécution crée un dossier distinct `eval/runs/<date_heure_UTC>_first_inference/`, non versionné :

- `config.json` : paramètres, révision du modèle, versions, machine, commit complet, état du code, hashes des sources, du prompt et du log.
- `metrics.json` : chargement, génération, tokens/s et mémoire du processus.
- `prompt.txt`, `output.txt` : entrée et réponse exactes.
- `predictions.jsonl` : réponse brute identifiée par bloc ; la sortie de cet essai est marquée non structurée, sans réparation silencieuse.

Les champs mémoire finissant par `_gb` gardent leur nom historique, mais leur unité est **GiB** (`1024**3`). Le pic RSS est échantillonné toutes les 0,2 s, séparément au chargement et en génération ; il peut manquer un pic plus bref. C'est la mémoire du processus, pas toute la RAM de la machine. Aucun GPU n'est utilisé ; la VRAM reste `null`, elle n'est pas mesurée.

Le temps de chargement inclut les imports nécessaires au modèle, le tokenizer et les poids, mais pas un premier téléchargement effectué séparément. Le temps de génération couvre `model.generate()` (traitement du prompt inclus), hors tokenisation, décodage, extraction de la trace et écriture des fichiers. Les chronométrages varient selon la machine, le cache et sa charge ; une seed et un décodage glouton ne garantissent pas une identité entre versions et matériels.

## Relecture

```powershell
python -m unittest discover -s tests -p test_scrum28_inference.py -v
```

Les tests utilisent des lignes factices et des dossiers temporaires : ils vérifient que le mode factice ne charge pas les poids, qu'une vraie mesure refuse ce mode, que l'extraction ne mélange pas les blocs, et qu'une relance conserve les preuves antérieures.

La [preuve du 08/10](../../eval/results/SCRUM-28/README.md) publie la synthèse, la réponse brute et les artefacts compacts pour permettre une relecture sans télécharger les poids. La PR #4 a été fusionnée dans `dev`. Le tableau complet des environnements (SCRUM-15) reste à compléter par Bachar et Nassim.

## Version 4 bits (SCRUM-57, expérimental)

`python -m volet_b.slm.bench_gguf --backend llamacpp|transformers --offline` conserve le banc historique sur un bloc. Installation : `pip install -e ".[volet_b_gguf]" --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu`. Résultats et limites dans `docs/projet/journal.md`.

## Backend llama.cpp et conversion LoRA → GGUF

Dans SCRUM-57, Transformers était le défaut et SmolLM2 la base. Depuis SCRUM-63, le YAML sélectionne Gemma sous llama.cpp ; ces commandes historiques exigent de reprendre les configurations archivées dans les résultats SCRUM-28/SCRUM-57 pour reproduire leurs mesures. L'interface et le retour (`text`, `new_tokens`, `seconds`) sont inchangés. `TEAMAI_SLM_MOCK=1` fonctionne avec les deux backends sans charger de poids.

La base GGUF officielle est retrouvée par `hf_hub_download` avec `gguf_repo`, `gguf_file`, `gguf_revision` figés dans le YAML (valeurs du banc historique). `local_files_only=True` impose le cache local. Le cache d'instances llama.cpp comprend la base, la révision, le contexte, la seed et l'adaptateur. Le backend utilise le CPU, 4 096 tokens de contexte, la pénalité sur tout le contexte et le décodage glouton ; `do_sample=true` est refusé.

Avec ce backend, `adapter` est **un fichier GGUF d'adaptateur**, transmis à `Llama(lora_path=...)` au-dessus de la base Q4_K_M. Un modèle fusionné est une base complète : passer `gguf_path` sans `adapter`.

```python
from volet_b.slm.generate import generate
out = generate("Consigne puis logs", backend="llamacpp", local_files_only=True,
               adapter="volet_b/slm/adapters/essai-adapter/adapter.gguf")
# Route fusionnée, une fois convertie :
out = generate("Consigne puis logs", backend="llamacpp", local_files_only=True,
               gguf_path="volet_b/slm/adapters/essai-merged/model-q4_k_m.gguf")
```

Les commandes suivantes sont à lancer manuellement depuis la racine. Elles exigent les dépendances SLM/PEFT/GGUF et le clone local llama.cpp. Elles ne téléchargent rien. `--llama-cpp` remplace la variable `TEAMAI_LLAMA_CPP` si souhaité.

```powershell
$py = 'D:\scolaire\master\m2\26-27 Natural Language Processing 2_M2IA_S3\projet\.venv\Scripts\python.exe'
$adapter = 'D:\scolaire\master\m2\26-27 Natural Language Processing 2_M2IA_S3\projet\volet_b\slm\adapters\essai'
$env:HF_HOME = 'D:\IA_Caches\HuggingFace'
$env:TEAMAI_LLAMA_CPP = 'D:\IA_Caches\llama.cpp'

# Inspection uniquement : aucun chargement ni conversion.
& $py -m volet_b.slm.convert_gguf adapter $adapter --name essai-adapter --dry-run
& $py -m volet_b.slm.convert_gguf merged $adapter --name essai-merged --dry-run

# Route b : adaptateur f16 à charger sur la base Q4_K_M officielle.
& $py -m volet_b.slm.convert_gguf adapter $adapter --name essai-adapter

# Route a : fusion float32 CPU, HF temporaire, GGUF f16 puis Q4_K_M.
& $py -m volet_b.slm.convert_gguf merged $adapter --name essai-merged

# Base seule : Transformers float32 contre GGUF Q4_K_M officiel.
& $py -m volet_b.slm.compare_backends --n 5

# Même adaptateur source côté PEFT et côté GGUF (route b).
& $py -m volet_b.slm.compare_backends --n 5 --adapter-hf $adapter --adapter-gguf volet_b/slm/adapters/essai-adapter/adapter.gguf

# Un seul backend pour fractionner les calculs.
& $py -m volet_b.slm.compare_backends --n 5 --backends llamacpp

# Tests sans modèle ni conversion.
& $py -m pytest -q
```

Chaque conversion occupe un **nouveau** sous-dossier de `volet_b/slm/adapters/` (déjà ignoré par Git) ; un nom existant est refusé. `meta.json` conserve la route, l'empreinte source (noms relatifs, tailles et contenus), la révision de base, le commit llama.cpp et la taille produite. Les intermédiaires HF/f16 sont supprimés, y compris sur erreur. Si l'adaptateur ne déclare aucune révision, sa révision d'entraînement reste à confirmer par son producteur. Une conversion réussie n'atteste pas une inférence correcte (`inference_validated: false`).

Les deux routes ont été exécutées le 26/10 sur l'adaptateur `essai` (deux pas d'entraînement) : elles servent à vérifier le chemin, pas à conclure sur la qualité. La route a demande `sentencepiece` (inclus dans l'extra `volet_b_gguf`). En cas d'incompatibilité PEFT/architecture sur un autre adaptateur, la conserver comme preuve, essayer l'autre route puis évaluer PEFT sur GPU si les deux échouent.

Le fichier C4 `data/splits/splits.csv` doit déjà exister dans ce checkout : le sample seul n'indique pas les splits. S'il manque, le banc s'arrête sans générer de split. Il tire cinq blocs `val` du sample avec la seed du YAML (42) ; `--n` permet de modifier l'effectif. Tout split différent de `val` est refusé. Ni labels ni annotations ne sont transmis au modèle. Le prompt exact, identique des deux côtés, demande C5 et place la consigne avant les logs. Un appel par bloc, sans réparation ni relance sur erreur.

Chaque comparaison crée un dossier C7 neuf : `config.json`, `predictions.jsonl`, `metrics.json`, `comparison.md` et résultats intermédiaires des workers. Les backends tournent dans des processus CPU distincts pour séparer la RSS (pic échantillonné à 0,2 s, chargement inclus). Le débit est la moyenne des tokens/s mesurés ; les échecs restent au dénominateur de conformité et d'abstention. Les valeurs non mesurées sont `null`. La conformité C5 et l'abstention ne mesurent pas la justesse : relire les sorties brutes. Le temps de génération inclut le prompt ; Transformers exclut tokenisation/décodage, llama.cpp mesure l'appel chat complet.

Ce diagnostic change à la fois le backend et la quantification. Pour les évaluations comparant base, LoRA, RAG et agents, conserver un unique couple backend/quantification et le consigner au journal. Mesures du 26/10 et lecture : `eval/results/SCRUM-57/README.md` et journal.

## Essai LoRA (SCRUM-29, faisabilité matérielle)

`python -m volet_b.slm.make_seed` régénère les 20 exemples C5 provisoires (`volet_b/annotations/seed_alain.jsonl`, blocs du split train de `data/sample/`, réponses calculées par règles, `sources: []`). `python -m volet_b.slm.train_lora` entraîne un adaptateur LoRA (r 8 sur `q_proj`/`v_proj`, configuration dans `configs/lora_essai.yaml`), puis vérifie qu'il se recharge via `generate(…, adapter=…)`. Mesures dans un dossier `eval/runs/<horodatage>_lora_essai/` (`metrics.json`, `train_log.jsonl`, `config.json`) ; adaptateur dans `volet_b/slm/adapters/essai/` (non versionné).

Sur CPU (i5-1240P, 14/10) la chaîne fonctionne mais un pas prend de 2,5 à 13 min selon la longueur de la trace : l'essai complet se fait sur GPU NVIDIA.

```powershell
pip install torch --index-url https://download.pytorch.org/whl/cu124   # PyTorch CUDA
pip install -e ".[lora]" bitsandbytes
python -m volet_b.slm.train_lora --device cuda --qlora                   # 6 Go de VRAM : 4 bits d'abord
python -m volet_b.slm.train_lora --device cuda                           # bfloat16, si la VRAM suffit
```

Le premier lancement télécharge le modèle (3,4 Go, révision figée) ; ensuite `--offline` suffit. Le rechargement de l'adaptateur se fait sur CPU comme toutes les inférences de `generate()` (quelques minutes).
