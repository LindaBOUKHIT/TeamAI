# SCRUM-43 — Mesures CPU de la démo du volet B, 24/11/2026

Trois lancements de `volet_b.app.app.analyze` avec le vrai modèle GGUF, sur CPU, faits pour vérifier la PR #54. Ce sont des **essais ponctuels** : un bloc par configuration, sans répétition. Ils ne mesurent pas la qualité du volet B. Seuls des blocs de **validation** sont utilisés ; le test n'est pas consulté.

## Machine et logiciels

- Portable de développement d'Alain : Intel Core i5-1240P (16 threads logiques), 31,7 Go de RAM, Windows 11, sans GPU utilisé.
- Python 3.12.10, `llama-cpp-python` 0.3.36 (roue CPU).
- Modèle : `google/gemma-4-E4B-it-qat-q4_0-gguf`, fichier `gemma-4-E4B_q4_0-it.gguf`, révision `4b4a2c1d584be7264f87aac328a1bc739ce81b6c`, contexte 4 096 tokens, réponse limitée à 800 tokens (`volet_b/slm/configs/generation.yaml`).
- Index RAG construit localement (51 passages), `HF_HUB_OFFLINE=1`.
- Splits : `data/splits/splits.csv`, SHA-256 `f504592cb7ac13b8b7e5d532a336b4e3641ec441a863c5efafd164faa2a43f22`.

## Blocs

| Bloc | Split | Label | Événements | Origine |
|---|---|---|---:|---|
| `blk_7956543127401791181` | val | Fail | 39 | Exemple d'anomalie choisi par `choose_examples()` avant le correctif |
| `blk_8490580439615020929` | val | Fail | 20 | Exemple choisi après le correctif (`DEMO_MAX_LINES = 20`) |

## Lancements

Commande commune, depuis la racine d'un worktree de la branche de la PR #54 :

```
PYTHONPATH=<worktree> HF_HUB_OFFLINE=1 python <script>
```

| Fichier de sortie | Script | Code | Configuration | Résultat |
|---|---|---|---|---|
| `run1_1agent_39lignes.txt` | `run1_demo_check.py.txt` | `f89f6c5` | 1 agent, bloc de 39 événements | Échec de contexte : **4 329** tokens demandés pour **4 096** ; 19,8 s |
| `run2_3agents_39lignes.txt` | `run2_demo_check3.py.txt` | `f89f6c5` | 3 agents, bloc de 39 événements | Refus : prompt au-delà du plafond v16 de **2 900** tokens ; 162,9 s, chargement compris |
| `run3_20lignes_1et3agents.txt` | `run3_demo_check_both.py.txt` | `981018c` | 1 agent puis 3 agents, bloc de 20 événements | 1 agent : sortie réduite à « ```json { », rejetée (`invalid_json`), **397,6 s**. 3 agents : **5** appels, réponse rejetée par le contrôleur, **1 519,7 s** |

Limites des sorties :

- Les sorties sont copiées telles quelles. Celle du run 3 a été filtrée au lancement : les lignes de journal de llama.cpp sont retirées.
- Le script du run 3 coupe chaque rendu à 2 500 caractères.
- Les durées comprennent le chargement du modèle au premier appel de chaque lancement.

## Longueur des blocs de validation

`longueurs_val.py.txt` compte, sur les seuls blocs `val`, ceux qui dépassent un nombre d'événements donné. Sa sortie est `longueurs_val.json`. Commande depuis la racine :

```
python - < eval/results/SCRUM-43/cpu_24-11/longueurs_val.py.txt
```

Au-delà de 39 événements : **124** blocs sur 86 259 (0,1 %), dont **105** anomalies sur 2 525 (4,2 %).

## Ce que ces essais établissent, et ce qu'ils n'établissent pas

- **Établi** : un bloc de 39 événements échoue dans les deux modes. Un bloc de 20 événements passe la vérification de contexte dans les deux modes.
- **Établi** : le mode 3 agents va jusqu'au bout sur CPU.
- **Non établi** : la longueur exacte à partir de laquelle le contexte est dépassé.
- **Non établi** : un taux d'échec du mode 1 agent, puisqu'un seul essai a été fait.
- **Non établi** : une latence représentative, puisqu'il n'y a qu'un passage par configuration sur une seule machine.
