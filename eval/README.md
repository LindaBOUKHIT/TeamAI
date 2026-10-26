# eval/ — Protocoles et résultats

**Pilotage** : Nassim · **Contributeurs** : tous (on n'évalue jamais seul son propre composant) · **Epic** : SCRUM-10

```
eval/
├── metrics.py                  Métriques communes (macro-F1, rappel anomalie, matrice de confusion…)
├── volet_a/
│   └── evaluate.py             Baseline vs BiLSTM fp32/int8, test standard + séquences inédites   SCRUM-44
├── volet_b/
│   ├── test.jsonl              Jeu de test RÉSERVÉ (C5), figé et hashé avant tout réglage           SCRUM-35
│   ├── test.sha256
│   ├── run_config.py           Exécute une des 4 configurations → runs/                            SCRUM-38 / SCRUM-45
│   ├── grille.md               Grille d'évaluation humaine (lien vers docs/volet_b/grille_annotation.md)
│   └── double_annotation.csv   Notes des 2 annotateurs + arbitrage                                SCRUM-45
├── runs/                       Sorties brutes par exécution (C7) — non versionné
└── results/                    Tableaux et figures pour le rapport — versionné
    ├── volet_a.md
    ├── volet_b.md
    └── comparaison_a_b.md                                                                       SCRUM-47
```

## Règles

- Le test n'est ouvert qu'une fois, modèles et prompts figés.
- Toute exécution enregistre sa configuration et le commit Git (C7) ; un résultat sans configuration n'existe pas.
- Un résultat négatif (ex. pas de gain des agents) est un résultat : il va dans `results/`.

## Mesures avant adaptation du volet B (SCRUM-38)

Depuis la racine, avec les poids déjà disponibles et les prompts figés :

```bash
python -m eval.volet_b.run_config --config base
python -m eval.volet_b.run_config --config rag1
```

L'entrée par défaut est `eval/volet_b/test.jsonl` (C5, SCRUM-35). Son absence arrête
le script avec un message explicite. Le SHA-256 du fichier entier est enregistré,
même avec `--limit N` ; pour le test officiel, une divergence avec `test.sha256`
refuse l'exécution. `--data CHEMIN` permet un essai sur des exemples fabriqués
train/val ; `--adapter DOSSIER` transmet un adaptateur à `generate()`.
Les paramètres de `generation.yaml` sont conservés sans surcharge.

`base` emploie la consigne de `single_agent.txt` sans passage ; la place des passages
indique « aucune documentation fournie dans cette configuration » (et non « aucun passage
trouvé », qui laisserait croire à une recherche). La consigne autorise déjà `sources: []`. `rag1` réutilise le parsing des lignes,
la requête, le retrieval hybride (top 3) et la construction du prompt de SCRUM-37.
L'index et l'encodeur RAG doivent être présents localement (chargement hors ligne).
Ni les annotations, ni `events` annotés, ni `label` ou `expected` ne sont transmis
au modèle ou au retrieval.

Chaque lancement crée un dossier C7 neuf sous `eval/runs/` avec `config.json`,
`predictions.jsonl` et `metrics.json`. Les sorties brutes, erreurs, passages fournis,
tokens et mesures sont conservés pour chaque exemple, y compris en cas d'échec.
La sortie est analysée exactement comme dans l'agent (`volet_b.agents.validate.check_answer` :
objet JSON du premier « { » au dernier « } », sans réparation) ; les réponses analysables
mais non conformes restent visibles. La conformité utilise `validate_answer()` et
les IDs des passages fournis (`[]` sans RAG). Le taux de sources valides accepte
une liste vide ; le taux d'abstention compte les abstentions C5 conformes.
Tous les taux ont pour dénominateur tous les exemples lus, erreurs comprises.
La latence murale inclut le retrieval et le chargement éventuel ; le temps renvoyé
par `generate()` est conservé séparément. Le maximum RSS du processus est
échantillonné toutes les 0,2 s, chargement inclus (ni GPU ni processus enfants).
Une mesure indisponible vaut `null`.

La fonction `eval.volet_b.run_config.update_summary(metric_paths)` ajoute ou
actualise « Avant adaptation » dans `eval/results/volet_b.md`, avec une ligne par
configuration (la dernière fournie remplace la précédente). `metric_paths` est une
liste de chemins vers les `metrics.json` retenus. Elle exige des exécutions réelles
sur le test officiel complet, sans adaptateur ; les essais factices et partiels
ne sont pas publiés comme résultats. Aucun résumé n'est modifié automatiquement.
Ne jamais ajuster une consigne ou un paramètre après lecture des résultats du test.

Les tests `tests/test_run_config.py` utilisent `TEAMAI_SLM_MOCK=1` et un bloc
`train` de `data/sample/`, avec un retriever simulé ; aucun modèle n'est chargé.
