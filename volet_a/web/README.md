# volet_a/web — Site statique

**Responsable** : Bachar · **Prétraitement JS** : Linda (SCRUM-26) · Déployé automatiquement depuis `main` (GitHub Pages, `.github/workflows/deploy-volet-a.yml`).

```
web/
├── index.html
├── package.json            Vite + onnxruntime-web
├── src/
│   ├── main.js             Câblage de l'interface
│   ├── preprocess.js       Logs bruts → séquences (regex de public/vocab.json)   SCRUM-26
│   ├── model.js            Chargement + cache du modèle, inférence (Web Worker)   SCRUM-23 / SCRUM-40
│   ├── worker.js           Inférence par lot sans bloquer l'interface             SCRUM-40
│   └── ui/                 Saisie, dépôt de fichier, tableau, export CSV          SCRUM-27 / SCRUM-41
├── public/                 Copié tel quel dans le site publié
│   ├── model/detector.onnx + detector.meta.json      (contrat C3)
│   ├── vocab.json                                      (contrat C2)
│   └── examples/*.log                                  (SCRUM-21)
└── tests/
    ├── parity.test.js      JS == Event_traces.csv sur N blocs                     SCRUM-26
    └── parity_cases.json   Cas limites partagés avec tests/test_preprocess.py      SCRUM-26
```

## Prétraitement (SCRUM-26)

`src/preprocess.js` applique les regex de `public/vocab.json` (contrat C2), dans l'ordre des EventId : lignes brutes → séquence d'EventId par bloc → 50 indices (padding à droite, inconnu = 30). Il est le miroir de `teamai/data/preprocess.py`.

```js
import { compileVocab, preprocess } from "./preprocess.js";
const vocab = compileVocab(await (await fetch("./vocab.json")).json());
const { blocks, stats } = preprocess(texteCollé, vocab);   // lève une erreur si aucun bloc n'est reconnu
// blocks[i] = { blockId, events, ids (50 entiers), length, truncated, unknown }
```

L'interface affiche `truncated` (événements au-delà de 50) et `unknown` (lignes sans template), ainsi que `stats.invalid_header` et `stats.without_block` (lignes ignorées).

```bash
npm test                                   # parité JS : échantillon de 2 000 blocs + cas limites
python -m teamai.data.preprocess           # régénère public/vocab.json depuis les 29 templates
pytest tests/test_preprocess.py            # parité Python (même échantillon, mêmes cas limites)
```

Vérifié le 13/10 sur le corpus complet : 575 061 blocs sur 575 061 identiques à `Event_traces.csv`, aucune ligne ambiguë ni inconnue (`TEAMAI_FULL_PARITY=1 pytest tests/test_preprocess.py`).

## Règles

- Aucune requête vers un serveur d'inférence ou une API payante : tout s'exécute dans le navigateur.
- Le modèle est téléchargé une fois puis mis en cache (Cache API).
- Toute évolution de `preprocess.js` doit garder `tests/parity.test.js` au vert.
