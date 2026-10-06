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
    └── parity.test.js      JS == Event_traces.csv sur N blocs                     SCRUM-26
```

## Règles

- Aucune requête vers un serveur d'inférence ou une API payante : tout s'exécute dans le navigateur.
- Le modèle est téléchargé une fois puis mis en cache (Cache API).
- Toute évolution de `preprocess.js` doit garder `tests/parity.test.js` au vert.
