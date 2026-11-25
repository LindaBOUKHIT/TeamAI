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
│   ├── figer_test.py           Contrôle C5 et validation humaine, puis écrit test.jsonl et test.sha256   SCRUM-35
│   ├── run_config.py           Mesure base via v16 (SCRUM-38) → runs/                            SCRUM-38 / SCRUM-45
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
- Toute exécution enregistre sa configuration (C7) ; le commit est à renseigner hors script, sans commande git dans SCRUM-38.
- Un résultat négatif (ex. pas de gain des agents) est un résultat : il va dans `results/`.

## Mesures avant adaptation du volet B (SCRUM-38)

SCRUM-38 mesure **base seulement**, avec Gemma 4 E4B QAT Q4_0 sous llama.cpp
et le pipeline v16 figé. À lancer sur le **portable de Nassim après fusion de #40**,
avec les poids déjà disponibles localement et le test C5 figé par SCRUM-35 :

```bash
python -m eval.volet_b.run_config --config base
```

`rag1` renvoie une erreur explicite : « rag1 reporté : pas de variante v16 + RAG
figée ; voir SCRUM-42/SCRUM-45 ». Le retrieval de Linda reste utilisable dans
`single_agent.retrieve_for_trace` ; aucune variante RAG n'est mesurée ici.

Pour chaque exemple, `facts.prepare_block` reconstruit les faits, la chronologie,
les preuves et les causes autorisées depuis `trace_lines`, puis `explain_block`
exécute le schéma fermé, les contrôles et l'éventuelle correction unique.
`expected`, `label`, `events` annotés et les autres annotations ne sont jamais
transmis au prompt. Les références de ligne sont locales à `trace_lines`, à partir
de 1 : C5 ne conserve pas les numéros du journal global. Les 29 templates sont lus
dans `data/raw/HDFS_v1/preprocessed/`, sinon dans leur copie versionnée de
`tests/fixtures/preprocessed/` ; le chemin et l'empreinte sont enregistrés.

Le script vérifie le SHA-256 du test officiel contre `test.sha256` s'il existe.
Une entrée absente ou une empreinte divergente arrête le lancement. `--data CHEMIN`
et `--limit N` servent aux essais sur des exemples fabriqués train/val. Un
`--adapter CHEMIN` est transmis à v16, mais exclut la publication avant adaptation.
Ne jamais ajuster un prompt ou un paramètre après lecture du test réservé.

Chaque lancement écrit un C7 neuf dans `eval/runs/` :

- `config.json` : empreintes de consigne et politique issues de
  `eval/results/SCRUM-63/prompt_freeze.json`, modèle, fichier et révision GGUF,
  contexte 4096, budget 800, paramètres figés, plateforme réelle et machine cible
  informative (portable de Nassim). Le commit reste `null`, à renseigner hors
  script : aucune commande git n'est exécutée.
- `predictions.jsonl` : toutes les tentatives, textes et prompts, erreurs de
  contrat et factuelles, alertes, `finish_reason`, tokens, temps et nombre réel
  d'appels, y compris une correction échouée. Les entrées invalides comptent aussi.
- `metrics.json` : conformité C5, sources valides et abstention ; contrat v16,
  faits exactement copiés, références inexistantes, causes réseau sans appui,
  enquêtes sans indice d'incident, hypothèses avec et sans incident, anti-boucle,
  corrections déclenchées, tentées et réussies ; latences et mémoire.

Tous les taux ont pour dénominateur **tous les exemples lus, échecs compris**.
Les hypothèses par bloc avec/sans incident sont rapportées au **nombre de blocs
du groupe**, échecs compris dès que `attention` est connu ; une réponse invalide
compte 0 hypothèse. Un groupe vide donne `None` (`null` en JSON). Les effectifs
et les sommes sont conservés. Ce calcul suit SCRUM-63 : 4 hypothèses / 21 blocs
avec incident = 0,19 après arrondi ; la métrique conserve la valeur non arrondie.
L'incident correspond à `attention` calculé par v16, jamais au label.
Les faits exactement copiés exigent une structure évaluable par les contrôles v16.
L'anti-boucle compte un exemple si une tentative est rejetée par `repetition_errors`
(répétition ou budget presque épuisé). Une correction réussie satisfait tous les
contrôles v16 ; les alertes lexicales ne certifient pas la fidélité sémantique.

Le temps mural inclut préparation, contrôles et chargement éventuel ; les temps
renvoyés par la génération sont conservés séparément et sommés. Les pics RSS et
VRAM du processus sont échantillonnés toutes les 0,2 s, chargement inclus. La VRAM
somme le PID courant sur les GPU NVIDIA : `pynvml` si disponible, sinon
`nvidia-smi --query-compute-apps`. Une mesure indisponible vaut `null` ; aucune
nouvelle dépendance GPU n'est obligatoire. Ce relevé peut manquer un pic bref.

`update_summary(metric_paths)` actualise seulement la ligne `base` de « Avant
adaptation » dans `eval/results/volet_b.md`. Il refuse `rag1`, les runs factices,
partiels, vides, hors test officiel ou avec adaptateur. Aucun résumé n'est publié
automatiquement. Les tests fabriqués de `tests/test_run_config.py` traversent v16
avec une génération simulée, dont une boucle et une correction, sans modèle ni
réseau. Les tests d'empreintes de `tests/test_v16.py` restent inchangés.

## SCRUM-35 : jeu de test réservé du volet B

### Contenu

`test.jsonl` contient 80 exemples C5 du split officiel `test` de SCRUM-20, un par ligne,
dans l'ordre de `test-0001` à `test-0080` (UTF-8, fins de ligne LF, accents non échappés).
Chaque ligne reprend `id`, `block_id`, `split`, `trace_lines`, `events` et `label` tels que
sélectionnés par `prepare_test.py`, puis `expected`, `annotator` et `reviewed_by`.

- 40 traces normales et 40 anomalies, toutes distinctes. L'échantillon est équilibré
  volontairement : il ne représente pas la prévalence réelle des anomalies dans HDFS.
- Les quatre blocs de test déjà exposés sont exclus.
- 10 abstentions, chacune expliquée par au moins une information manquante : `test-0011`
  (normale, quinze exceptions E4 sans détail) et 9 anomalies dont la trace s'arrête après
  l'allocation et un début de réception (`test-0050`, `0051`, `0055`, `0061`, `0063`,
  `0064`, `0071`, `0076`, `0077`).
- Aucune hypothèse ni source C6 : les explications décrivent la trace sans affirmation
  documentaire, et les listes vides sont conformes à C5.

### Vérification et relecture

| Cas | Vérification (`annotator`) | Relecture (`reviewed_by`) |
|---|---|---|
| `test-0001` à `test-0020` | Alain | à faire |
| `test-0021` à `test-0040` | Linda | Alain |
| `test-0041` à `test-0060` | Bachar | Alain |
| `test-0061` à `test-0080` | Alain | Bachar |

Chaque cas est contrôlé contre `trace_lines` : effectifs d'événements, heures, ordre,
destinataires et formulations qui affirment plus que la trace (achèvement, causalité,
chronologie). Une ligne `Deleting block` atteste une suppression journalisée, pas son
achèvement ; une ligne E23 inscrit le bloc dans un ensemble d'invalidation.

32 corrections sont reportées dans `annotations_travail.jsonl` avec `page_relecture.py --appliquer`
et journalisées dans `corrections_journal.csv` : 3 de Bachar (`corrections_Bachar.jsonl`) et
29 d'Alain (`corrections_Alain.jsonl`). Les verdicts, grilles et motifs figurent dans
`validation_humaine.csv`. Les champs `id`, `block_id`, `split`, `label`, `trace_lines` et
`events` sont identiques à ceux de la sélection initiale.

Les fichiers de double annotation (30 traces, `double_annotation.csv`) restent vierges.

### Gel et empreinte

`python -m eval.volet_b.figer_test` écrit `test.jsonl` et `test.sha256`
(`<sha256>  test.jsonl`) seulement si les 80 cas respectent C5 (`validate_example`) et sont
vérifiés puis relus par deux personnes distinctes dans `validation_humaine.csv`.
`--controler` fait le même contrôle sans rien écrire.

`run_config.py` lit le premier mot de `test.sha256`, recalcule le SHA-256 de `test.jsonl`
et refuse toute exécution ou publication en cas d'écart. `tests/test_fichiers_du_depot.py`
vérifie C5 sur le fichier figé et l'absence de ses blocs dans les annotations d'adaptation.
Toute modification après le gel change l'empreinte.

Le jeu de test ne sert jamais à l'entraînement, à l'adaptation LoRA, au réglage des prompts
ni à l'optimisation du RAG.

### État

La relecture croisée de `test-0001` à `test-0020` manque : C5 impose un relecteur distinct
d'Alain et aucun n'est désigné. `figer_test` refuse donc d'écrire `test.jsonl` et
`test.sha256`. Une fois la relecture faite, le relecteur est renseigné dans
`validation_humaine.csv` et `annotations_travail.jsonl`, puis la commande est relancée.
