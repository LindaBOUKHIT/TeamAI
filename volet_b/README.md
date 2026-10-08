# Volet B — Explication sourcée d'une trace HDFS en local

**Epics** : SCRUM-8 (SLM, LoRA — Alain, binôme Linda) · SCRUM-9 (RAG, agents, interface — Linda, binôme Alain)
Modèle : SmolLM2-1.7B-Instruct (repli : plus petit si la machine l'impose, décision tracée).

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
│   ├── retriever.py            retrieve(query, k) → passages C6                 SCRUM-37
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
- En attendant l'index, `retriever.py` peut renvoyer 3 passages fixes au format C6.

## Les 4 configurations évaluées (eval/volet_b)

1. Base sans RAG · 2. Base + RAG 1 agent · 3. Adapté + RAG 1 agent · 4. Adapté + RAG 3 agents.

## Commandes

```bash
pip install -e ".[data,volet_b]"
python -m volet_b.slm.first_inference
python volet_b/app/app.py          # interface locale
```

Pour SCRUM-28, suivre le [README du SLM](slm/README.md) : installation minimale, mode factice, exécution réelle et preuves d'inférence. Les autres composants de l'arborescence restent des livraisons prévues par leurs tickets.
