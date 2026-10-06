# Volet A — Détecteur d'anomalies dans le navigateur

**Responsable** : Bachar · **Binôme** : Nassim · **Epic** : SCRUM-7
Contrainte : site **statique et gratuit**, inférence **côté client** (ONNX Runtime Web), modèle **entraîné par l'équipe**.

```
volet_a/
├── training/                       Python
│   ├── spike_onnx.py               BiLSTM jouet → ONNX → parité navigateur          SCRUM-22
│   ├── baseline.py                 Comptages + régression logistique                  SCRUM-24 (Nassim)
│   ├── dataset.py                  Encodage des séquences (teamai.data.loader)        SCRUM-25
│   ├── bilstm.py                   Architecture du modèle                             SCRUM-25
│   ├── train.py                    Entraînement + choix du seuil sur val              SCRUM-25
│   ├── export_onnx.py              Export C3 + quantification int8                    SCRUM-25 / SCRUM-39
│   ├── check_parity.py             Python vs onnxruntime sur les mêmes entrées        SCRUM-25
│   └── checkpoints/                — non versionné
└── web/                            Site statique (voir web/README.md)
    ├── index.html
    ├── src/                        preprocess.js, model.js, ui/…
    ├── public/
    │   ├── model/detector.onnx     Modèle servi (versionné, quelques Mo)
    │   ├── model/detector.meta.json
    │   ├── vocab.json              Contrat C2 (produit par data/parse_hdfs.py)
    │   └── examples/               Extraits de logs pour « Essayer un exemple »         SCRUM-21
    └── tests/                      Parité JS ↔ Python                                  SCRUM-26
```

## Flux

```
logs bruts collés ─► preprocess.js (regex C2) ─► séquences par blk_ ─► event_ids [n,50]
                                                                            │
                     tableau, filtres, export CSV ◄── p_anomaly ◄── detector.onnx (ORT Web, Web Worker)
```

## Commandes

```bash
pip install -e ".[data,volet_a]"
python volet_a/training/train.py --split provisoire   # tant que SCRUM-20 n'est pas livré
python volet_a/training/export_onnx.py                # → web/public/model/
cd volet_a/web && npm install && npm run dev          # site en local
```

## Ordre de travail sans attendre personne

1. Spike ONNX avec poids aléatoires (aucune dépendance).
2. Site v0 + déploiement GitHub Pages avec le modèle du spike.
3. BiLSTM sur `Event_traces.csv` avec un split provisoire, puis réentraînement sur les splits officiels (même script).
