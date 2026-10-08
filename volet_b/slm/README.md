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

Les fichiers publics `data/raw/HDFS_v1/HDFS.log` et `preprocessed/Event_traces.csv` sont requis. S'ils sont absents, utiliser `python data/download_hdfs.py` (téléchargement, MD5 et extraction). Aucun jeu de test réservé n'est utilisé pour cet essai technique. Le bloc inspecté sert au développement et doit être exclu du futur test réservé du volet B.

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

La [preuve du 08/10](../../eval/results/SCRUM-28/README.md) publie la synthèse, la réponse brute et les artefacts compacts pour permettre une relecture sans télécharger les poids. Linda vérifie la commande, les artefacts et les limites ; SCRUM-28 reste en revue jusqu'à son approbation et à la fusion de la PR #4. Le tableau complet des environnements (SCRUM-15) demeure une dépendance de clôture suivie dans Jira.
