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




## SCRUM-23 — Site v0

Prérequis : Node.js 24 et npm.

Depuis la racine du dépôt, dans PowerShell :

    cd volet_a/web
    npm.cmd ci
    npm.cmd test
    npm.cmd run dev

Ouvrir l’adresse affichée par Vite suivie de /TeamAI/.
Cliquer sur « Tester une inférence ».

### Vérifier la version compilée

    npm.cmd run build
    npm.cmd run preview

Ouvrir l’adresse de preview suivie de /TeamAI/.

### Modèle et cache

Le site charge public/vocab.json, public/model/detector.meta.json
et public/model/detector.onnx.

Les empreintes SHA-256 du modèle et du vocabulaire sont vérifiées
lorsqu’elles sont présentes dans les métadonnées.
Le modèle est stocké avec la Cache API ; son hash identifie la version.
Après un premier chargement, actualiser la page :
« source : cache navigateur » confirme sa réutilisation.

Le modèle actuel est un spike à poids aléatoires.
Un avertissement explicite est affiché et aucune classe
normal/anomalie n’est interprétée pour ce modèle factice.

### Publication

Le workflow deploy-volet-a.yml installe les dépendances,
exécute les tests et compile le site avec Node.js 24.
Le dossier dist est généré automatiquement et ignoré par Git.

Publication après fusion vers main via SCRUM-17.
Dans GitHub : Settings > Pages > Source = GitHub Actions.

URL prévue : https://lindaboukhit.github.io/TeamAI/
Statut : publication publique à vérifier après déploiement.

## SCRUM-27 — Parcours fonctionnel

### Utilisation

- Coller des logs dans la zone de saisie ou importer un fichier
  texte .log / .txt, limité à 10 Mo.
- Cliquer sur « Analyser les logs ».
- Consulter les résultats par bloc : classe, score, longueur,
  événements tronqués, inconnus encodés et avertissements.
- Cocher « Anomalies seulement » pour filtrer le tableau.
- Exporter les résultats affichés en CSV.

Le seuil est lu dans detector.meta.json :
p_anomaly >= threshold donne la classe anomalie.
Le score n’est pas une probabilité calibrée.

Les exemples sont chargés depuis public/examples/.
Ils permettent de vérifier les blocs normaux, les anomalies,
les fichiers contenant plusieurs blocs et les entrées dégradées.

### Entrées incomplètes et invalides

Une entrée sans bloc reconnu est rejetée.
Les lignes invalides ou sans identifiant de bloc sont comptées
et ignorées. Les événements inconnus sont signalés.

Le prétraitement conserve les 50 premiers événements par bloc,
complète avec le padding et signale les événements tronqués.

La complétude d’un bloc ne peut pas être garantie à partir
des seules lignes fournies. L’exemple volontairement incomplet
est identifié lorsqu’il est chargé par le sélecteur d’exemples.
Un fichier importé affiche « Complétude non vérifiée ».

Modifier la saisie ou charger une autre source efface les anciens
résultats. Une erreur ne produit aucune prédiction de remplacement.

### Export CSV

L’export respecte le filtre actif et contient :
BlockId, label, p_anomaly, length, truncated, unknown,
warnings, threshold et model_sha256.

Les valeurs sont échappées pour le CSV ; les cellules textuelles
pouvant être interprétées comme des formules sont neutralisées.

### Vérifications

Depuis volet_a/web :

    npm ci
    npm test
    npm run build
    npm run preview

Ouvrir l’adresse affichée suivie de /TeamAI/.

Vérifications réalisées :
- 16 tests JavaScript réussis.
- Compilation de production réussie.
- Exemple multi-blocs : trois blocs dont une anomalie.
- Import du même fichier : résultats identiques.
- Filtre et export : une seule anomalie exportée.
- Entrée invalide rejetée.
- Lignes ignorées et événement inconnu signalés.
- Exemple incomplet signalé.

L’inférence utilise des lots de 64 blocs.
Le déplacement du traitement vers un Web Worker relève de SCRUM-40.
Publication publique à vérifier après fusion et déploiement.