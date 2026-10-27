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

Les sections SCRUM-28 et SCRUM-57 ci-dessous décrivent les anciens essais SmolLM2 et leurs commandes.
Elles ne décrivent pas le modèle actuel. Les configurations C7 archivées restent
la référence pour leur reproduction ; le YAML actuel ne reproduit pas ces essais.
La section « Essai LoRA » décrit l'adaptation Gemma actuelle de SCRUM-29.

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

## Essai LoRA (SCRUM-29, Gemma 4 E4B QAT)

Cette section remplace l'ancien essai SmolLM2. Entraînement par Nassim sur **une T4
Kaggle 16 Go** (SCRUM-61), puis inférence sur RTX 3050 6 Go. Les embeddings seuls
occupent environ 6,5 Gio en BF16 : l'entraînement E4B n'est pas prévu sur 6 Go.
La faisabilité T4 à 3072 tokens reste à mesurer, sans promesse de tenir en VRAM.

Base d'entraînement : `google/gemma-4-E4B-it-qat-q4_0-unquantized`, poids BF16
(environ 15,9 Go), révision **`476025a01dbf99361c062bbeca3d6a76bb4c4566`**,
relevée par Alain sur l'API Hugging Face le 27/10 et conservée dans C7 et dans
`base-config/teamai-base.json`. La base d'inférence reste le GGUF Q4_0 officiel
figé dans `configs/generation.yaml` ; ces deux identifiants sont distincts.

`train_lora.py` charge `Gemma4ForCausalLM` avec `Gemma4TextConfig` (Transformers
5.6.2), sans tours vision/audio. Le chargement refuse des poids texte manquants,
des dimensions incompatibles ou des clés inattendues hors tours multimodales.
Sur T4 : FP16, NF4 avec calcul float16, lot 1, checkpointing, r=8 et q_proj/v_proj.
La préparation gèle la base sans promouvoir temporairement ses embeddings en FP32
(ce qui doublerait leur occupation). DoRA, `modules_to_save`, embeddings,
`lm_head`, `per_layer_model_projection` et `all-linear` sont refusés.

`python -m volet_b.slm.make_seed` régénère vingt brouillons depuis les blocs train
du sample, avec les fonctions v16 inchangées : même consigne, faits, glossaire,
chronologie et catalogue de causes. Les réponses copient les faits exacts et ne
prennent leurs hypothèses que dans les formulations compatibles et référencées.
Sans indice, les listes d'hypothèses et d'informations manquantes restent vides.
Le JSON suit `runtime.schema(block)` ; ce schéma reste un paramètre de décodage
v16, il n'est pas ajouté au texte du prompt. Le dialogue est rendu par le template
Gemma avec `enable_thinking=False`. La perte porte seulement sur le JSON, sans
les tokens du prompt ni les marqueurs de fin de tour. Aucun exemple n'est tronqué.

Couverture régénérée : **E27 : 2 blocs ; E28 : 2 blocs ; E24 : absent** du train
du sample (20 blocs E27 et 24 blocs E28 disponibles). Les quatre blocs auparavant
exclus le restent. Tous les `reviewed_by` sont vides : la relecture antérieure de
Linda ne vaut plus. `validate_example()` continue à exiger un relecteur pour une
annotation validée ; la seule erreur tolérée pour ces brouillons est explicitement
`reviewed_by : texte non vide attendu`. Les contrôles v16 doivent tous passer.

Le manifeste `data/sample/splits.csv` est extrait du C4 officiel, sans nouveau
découpage. Sa provenance est décrite dans `data/sample/splits_provenance.json`.
`prepare_examples()` recoupe chaque bloc avec C4 et les lignes originales du
sample : déclarer artificiellement `split=train` pour un bloc val/test est refusé.
Si `data/splits/splits.csv` est présent, il prévaut sur ce sous-ensemble.

### Lancement Kaggle par Nassim

Construire localement l'archive minimale, puis envoyer uniquement `sortie.zip`
sur Kaggle (jamais le dépôt complet) :

```bash
python -m volet_b.slm.kaggle_lora_essai --bundle sortie.zip
```

La liste fermée `CODE_PATHS` de `kaggle_bundle.py` contient le code nécessaire de
`teamai/` et `volet_b/slm/`, `volet_b/__init__.py`, `pyproject.toml` et la config
`lora_essai.yaml`. S'y ajoutent uniquement `seed_alain.jsonl` et
`train_allowlist.json` : identifiants des seuls blocs train utilisés, empreinte
SHA-256 de `data/splits/splits.csv` source et empreintes des fichiers du bundle.
La préparation recoupe C4 et reconstruit v16 localement. Si le CSV complet est
absent, elle utilise le sous-ensemble local avec sa provenance et l'empreinte
source recoupée avec `splits_meta.json`. Aucun fichier de `data/sample/`, CSV de
split, log brut séparé ou identifiant val/test n'est empaqueté. Les extraits train
déjà inclus dans les annotations C5 sont conservés.

Extraire l'archive dans un dossier dédié, par exemple
`/kaggle/working/teamai-bundle/`, choisir **GPU T4** et activer Internet pour
la préparation. Depuis cette racine extraite, dans des cellules de commande :

```bash
python -m volet_b.slm.kaggle_lora_essai --dry-run
python -m volet_b.slm.kaggle_lora_essai --install
# Redémarrer le kernel si des bibliothèques avaient déjà été importées.
python -m volet_b.slm.kaggle_lora_essai --steps 30
```

Le mode `--install` installe puis quitte ; il ne télécharge aucun modèle.
Les versions de départ sont figées dans `PACKAGES` : torch 2.9.1, Transformers
5.6.2, PEFT 0.18.1, Accelerate 1.12.0, bitsandbytes 0.49.2, safetensors 0.7.0,
gguf 0.19.0, sentencepiece 0.2.1, PyYAML 6.0.3, psutil 7.2.2 et pandas 3.0.3.
Il ne s'agit pas d'un verrou de toutes les dépendances transitives. La résolution
de cette pile et sa compatibilité avec le pilote Kaggle restent à vérifier ;
aucune installation n'a été effectuée pour cette adaptation.

Le lancement vérifie les fichiers extraits et leurs empreintes avant toute
installation ou téléchargement. Il refuse `data/sample/`, les fichiers hors
liste blanche et les autorisations non-train. Kaggle ne relit aucun corpus :
les preuves v16 ont été reconstruites localement avant empaquetage.
Il télécharge ensuite la base à la révision fixée,
entraîne avec `--device cuda --qlora --offline`, libère le processus GPU puis
exporte immédiatement l'adaptateur seul. Aucun bloc val/test ne sert à la perte.
Pour un lancement direct avec poids déjà en cache :

```bash
python -m volet_b.slm.train_lora --device cuda --qlora --offline --steps 30
```

Sorties Kaggle dans `/kaggle/working/` : `adapter/` (PEFT),
`gguf/adapter.gguf`, `gguf/meta.json`, `gguf/conversion.log`, `base-config/`,
`lora_essai.yaml` et `runs/<horodatage>_lora_essai/` (C7 : configuration, versions,
VRAM maximale chargement/entraînement, durée par pas, pertes et paramètres).
Une sortie existante est refusée. La vérification finale recharge seulement les
tenseurs PEFT sauvegardés dans le modèle courant ; elle n'appelle plus `generate()`
et ne démontre pas une inférence correcte. La perte mesurée sur le train ne mesure
pas la qualité des explications.

### Conversion et comparaison sur RTX 3050

Convertisseur **`convert_lora_to_gguf.py` au commit `0c1e57098`**, correspondant à
llama-cpp-python **0.3.36**. Le script Kaggle télécharge une archive de ce commit,
sans commande Git, et conserve les empreintes des sources. La conversion locale
accepte aussi un checkout à ce commit, contrôlé par lecture de HEAD uniquement.
`--base-config` désigne la configuration de la base HF exacte, accompagnée de sa
provenance et de son empreinte, sans ses poids. Pour convertir un adaptateur déjà
produit, avec les outils et configurations locaux :

```bash
python -m volet_b.slm.convert_gguf adapter /chemin/adapter --llama-cpp /chemin/llama.cpp --base-config /chemin/base-config --name essai-gemma --dry-run
python -m volet_b.slm.convert_gguf adapter /chemin/adapter --llama-cpp /chemin/llama.cpp --base-config /chemin/base-config --name essai-gemma
```

Tout tenseur source inconnu, paire A/B incomplète, cible ignorée ou tenseur GGUF
supplémentaire provoque un échec explicite. `meta.json` consigne la couverture
exacte ; une conversion réussie reste `inference_validated=false`. Le contrôle
lit uniquement l'adaptateur, jamais les poids de base. La route `merged` reste
disponible pour les usages historiques mais **n'est pas retenue** : fusion puis
requantification ne reproduisent pas le GGUF QAT officiel.

Sur le portable, installer llama-cpp-python 0.3.36 avec la roue CUDA adaptée au
pilote. Comparer les mêmes prompts v16, seed et paramètres, aux échelles 0 et 1 :

```python
from llama_cpp import Llama
llm = Llama(model_path="gemma-4-E4B_q4_0-it.gguf", n_ctx=4096,
            n_gpu_layers=-1, n_batch=128, n_ubatch=128,
            lora_path="adapter.gguf", lora_scale=1.0, seed=42)
# Recréer l'instance avec lora_scale=0.0 pour la référence sans effet LoRA.
# Conserver le template sans thinking et le schéma runtime.schema(block).
```

L'interface existante `generate()` est conservée. Cette mission ne modifie pas
son backend. Mesurer VRAM, débits et sorties brutes ; réduire `n_gpu_layers` si
nécessaire. La résidence complète dans 6 Go, l'effet réel de l'adaptateur et le
transfert NF4 vers Q4_0 restent à vérifier avec les poids. Le test de qualité
ultérieur doit utiliser des blocs réservés et conserver les contrôles v16.

Commande de vérification locale sans poids ni réseau : `python -m pytest -q`.

Usage IA : Codex gpt-6.1-sol supervisé par Claude ; relecture d'Alain à faire ;
relecture des exemples par Linda à refaire.
