# Volet B — Explication sourcée d'une trace HDFS en local

**Epics** : SCRUM-8 (SLM, LoRA — Alain, binôme Linda) · SCRUM-9 (RAG, agents, interface — Linda, binôme Alain)
Modèle actuel : Gemma 4 E4B QAT, GGUF Q4_0, backend llama.cpp, prompt v16 figé.

Gemma est retenu pour la qualité relative des explications exploratoires (v11 : 40/40 contrats contre 22/40 pour Granite), avec des erreurs sémantiques persistantes : [trace SCRUM-63](../eval/results/SCRUM-63/README.md). `slm/v16/` extrait les faits avec `data.parse_hdfs`, applique les causes fermées, contrôle les réponses et autorise une seule correction. Cette référence n’utilise pas le RAG ; les chaînes RAG existantes gardent leurs propres prompts et ne sont pas couvertes par la validation v16. SmolLM2 et les essais LoRA associés sont historiques.

```
volet_b/
├── slm/                                                         Alain
│   ├── first_inference.py      1re inférence + mesures mémoire/latence          SCRUM-28
│   ├── generate.py             Interface unique : generate(prompt ou messages, adapter=None)
│   ├── train_lora.py           Entraînement LoRA / QLoRA                        SCRUM-29 / SCRUM-39
│   ├── configs/                lora_essai.yaml, lora_final.yaml, generation.yaml
│   ├── adapters/               — non versionné
│   └── models/                 — non versionné (cache des poids)
├── rag/                                                         Linda
│   ├── corpus/raw/             Pages de documentation HDFS téléchargées — non versionné
│   ├── corpus/sources.md       URL, version, licence de chaque document         SCRUM-30
│   ├── build_corpus.py         Nettoyage + découpage → corpus/chunks.jsonl (C6)  SCRUM-30
│   ├── build_index.py          Embeddings + index FAISS → index/                SCRUM-37
│   ├── retriever.py            search(query, k) → passages C6 + score (hybride) SCRUM-37
│   ├── event_descriptions.json Paraphrase anglaise des 29 événements (requête)   SCRUM-37
│   ├── evaluate_retrieval.py   Rappel@k sur la validation                       SCRUM-37
│   └── index/                  — non versionné
├── agents/                                                      Linda
│   ├── single_agent.py         Référence : résumé → retrieval → réponse C5      SCRUM-37
│   ├── orchestrator.py         3 agents, 1 reprise max, ≤ 5 appels              SCRUM-42
│   ├── roles/                  search.py, writer.py, checker.py
│   ├── prompts/                Un fichier .txt par rôle (versionnés, jamais réglés sur le test)
│   └── validate.py             Contrôle par code : JSON valide, sources existantes
├── app/                                                         Linda
│   └── app.py                  Interface Gradio                                 SCRUM-43
└── annotations/                                                 tous
    ├── seed_alain.jsonl        ~20 exemples provisoires pour l'essai LoRA        SCRUM-29
    ├── train.jsonl, val.jsonl  Jeu d'adaptation relu (C5)                        SCRUM-36
    └── README.md               Qui annote quoi, taux de correction humaine
```

## Ce qui découple le travail

- `slm/generate.py` est la **seule** porte d'entrée vers le modèle : RAG et agents l'appellent sans savoir s'il s'agit du modèle de base ou adapté.
- En attendant le vrai modèle, `generate.py` peut renvoyer une réponse factice au format C5 : Linda développe le RAG et les agents sans attendre la machine d'Alain.
- Les tests du RAG (`tests/test_rag.py`) utilisent un encodeur haché et le mode factice : ils tournent sans modèle.

## Les 4 configurations évaluées (eval/volet_b)

1. Base sans RAG · 2. Base + RAG 1 agent · 3. Adapté + RAG 1 agent · 4. Adapté + RAG 3 agents.

## Commandes

```bash
pip install -e ".[data,volet_b]"
python -m volet_b.slm.first_inference
python -m volet_b.app.app          # interface locale
```

## Lancer la démo

```bash
# 1. Dépendances (llama-cpp-python épinglé en 0.3.36, version de toutes nos mesures)
pip install -e ".[volet_b,volet_b_gguf]" --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

# 2. Découpage officiel C4 (data/splits/splits.csv, non versionné) : obligatoire pour que la démo
#    puisse refuser tout bloc du split test ; sans lui, seuls les blocs de data/sample/ sont acceptés
python -m data.download_hdfs        # ~180 Mo → data/raw/HDFS_v1/
python -m data.make_splits          # → data/splits/splits.csv (seed 42, vérifié par splits_meta.json)

# 3. Modèle GGUF (≈ 5,2 Go), OBLIGATOIRE avant la première analyse réelle, révision figée
python -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='google/gemma-4-E4B-it-qat-q4_0-gguf', filename='gemma-4-E4B_q4_0-it.gguf', revision='4b4a2c1d584be7264f87aac328a1bc739ce81b6c', local_files_only=False)"

# 4. Index RAG, puis lancement
python -m volet_b.rag.build_index
python -m volet_b.app.app
```

Ouvrir http://127.0.0.1:7860 ; `--port 7861` change le port. L'interface écoute uniquement
sur `127.0.0.1`, sans partage public. Détails du modèle (cache, accès Hugging Face, GPU) :
[README du SLM](slm/README.md).

Pour essayer sans modèle ni index : `python -m volet_b.app.app --mock`. La case « Mode factice »
permet aussi de changer de mode dans l'interface ; les réponses factices sont signalées.
Coller des logs ou importer un fichier `.log`/`.txt`, puis choisir 1 ou 3 agents et le modèle
de base ou adapté (chemin d'adaptateur vide = base). Les deux exemples sont choisis uniquement
dans la validation officielle de `data/sample`. Tout bloc du split test fait refuser l'entrée
entière avant appel au modèle ; chaque analyse traite au maximum cinq blocs.

Le CPU est lent ; compter environ 30 s par appel sur T4, et jusqu'à 5 appels par bloc avec
3 agents. Les ressources sont chargées à la première utilisation puis réutilisées. Les explications
peuvent être fausses : vérifier les lignes citées. Les réponses invalides ou rejetées restent
affichées en sortie brute avec leurs erreurs, sans réparation.

### RAG à un agent (SCRUM-37)

```bash
python -m volet_b.rag.build_index                                   # index FAISS des 51 passages (une fois)
python -m volet_b.rag.evaluate_retrieval                            # rappel@3 sur la validation → eval/results/SCRUM-37/
python -m volet_b.agents.single_agent --split val --n 5 --mock      # chaîne complète sans modèle
python -m volet_b.agents.single_agent --block blk_4971154345890344  # un bloc de data/sample/, avec le SLM
```

La requête paraphrase en anglais les événements distincts de la trace (`rag/event_descriptions.json`) ; le retriever fusionne embeddings (BGE small, FAISS) et BM25 (`--method dense|bm25|hybrid`). Le prompt (`agents/prompts/single_agent.txt`) donne la consigne avant la trace et les passages ; `agents/validate.py` vérifie le JSON, le format C5 et que chaque source citée fait partie des passages fournis. Chaque exécution écrit un dossier C7 dans `eval/runs/` (étapes, scores, erreurs). Le split `test` est refusé.

Pour SCRUM-28, suivre le [README du SLM](slm/README.md) : installation minimale, mode factice, exécution réelle et preuves d'inférence. Les autres composants de l'arborescence restent des livraisons prévues par leurs tickets.
