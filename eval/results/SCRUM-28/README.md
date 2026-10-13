# SCRUM-28 — Preuve de la première inférence locale

Alain, 08/10/2026. [PR #4](https://github.com/LindaBOUKHIT/TeamAI/pull/4), en revue vers `dev`.

L'exécution réelle utilise SmolLM2-1.7B-Instruct en float32 sur CPU, hors ligne, sur les 25 lignes du bloc `blk_8362325295506522506`. Le modèle, le prompt et les sources sont identifiés dans [config.json](config.json). Le prompt est identique à celui du 06/10 après normalisation des fins de ligne. Aucun label attendu n'est fourni au modèle.

## Mesures

| Mesure | 06/10, historique | 08/10, code corrigé |
|---|---:|---:|
| Chargement (s) | 37.4 | 238.0 |
| RSS après chargement (GiB) | 6.77 | 6.77 |
| Pic RSS au chargement (GiB) | Non mesuré | 9.84 |
| Pic RSS en génération (GiB) | 16.28 | 8.0 |
| Tokens produits | 156 | 156 |
| Génération (s) | 257.92 | 952.03 |
| Tokens/s | 0.6 | 0.16 |

Machine : i5-1240P, 32 Go, sans GPU NVIDIA ; Python 3.12.10, 12 threads PyTorch. Aucun GPU utilisé : VRAM non mesurée (`null`). Le pic est un échantillonnage RSS toutes les 0,2 s ; un pic plus bref peut être manqué. La génération inclut le traitement du prompt par le modèle, hors tokenisation, décodage et fichiers. Le chargement inclut les imports, le tokenizer et les poids déjà en cache.

Les deux exécutions ne constituent pas une comparaison contrôlée : cache système, charge et versions historiques ne sont pas entièrement documentés. Le correctif supprime un cas vérifié de double chargement, mais ces mesures seules ne quantifient pas son effet causal. Au contrôle de fin d'exécution, 2,2 GiB de RAM étaient disponibles sur la machine ; ce relevé ponctuel n'est pas une mesure de pic ni une explication causale de la latence. Les temps restent ceux observés, sans extrapolation à toutes les machines.

## Preuves et reproduction

Commande, depuis la racine du dépôt :

```powershell
python -m volet_b.slm.first_inference --offline --block-id blk_8362325295506522506 --torch-threads 12
```

- [config.json](config.json) : commit de mesure `4ee4034f30196caf3242632e1a0423a228b533b4`, code suivi propre, révision du modèle, versions exactes, hashes des sources, du prompt et du log brut.
- [metrics.json](metrics.json) : mesures de la nouvelle exécution.
- [output.txt](output.txt) et [predictions.jsonl](predictions.jsonl) : réponse brute, sans correction manuelle ; sortie non structurée explicitement signalée.
- [manifest.json](manifest.json) : dossier local `eval/runs/2026-10-08_033634_958183Z_816ba8d3_first_inference` et hashes physiques des cinq artefacts. Le hash du prompt dans `config.json` porte sur le texte UTF-8 avec LF ; le manifeste porte sur les octets des fichiers, avec CRLF sous Windows.
- [historical_2026-10-06](historical_2026-10-06/) : copie inchangée des mesures, paramètres et réponse historiques. Le commit `9085610` ancien ne suffit pas à reconstituer cette exécution ; aucune version précise actuelle ne lui est attribuée rétroactivement.

Le prompt complet, les logs bruts et les poids restent hors Git. Le [README du composant](../../../volet_b/slm/README.md) donne l'installation, les limites et les commandes de test. Les sept tests de régression passent sans charger de poids. La construction du paquet et son import hors du dépôt vérifient aussi que les modules SLM et la configuration YAML sont inclus.

## Portée de l'essai

Cet essai vérifie l'exécution locale et la collecte des preuves. Il ne valide pas la qualité sur un jeu de test, le schéma C5 du modèle réel, le RAG, les agents ou LoRA. Le mode factice renvoie C5 pour le développement, avec abstention ; il est exclu des mesures réelles.

Le bloc inspecté appartient au développement et doit être exclu du futur test réservé du volet B. La réponse du 08/10 est exactement celle du 06/10 : elle omet les trois `WARN`, ne répond pas à la question normal/anormal et invente des informations absentes (nom de domaine, ports spéciaux, envoi vers l'utilisateur). Les réponses sont conservées sans correction. Cet exemple seul ne permet pas de généraliser la qualité du modèle.

SCRUM-28 reste en revue jusqu'à l'approbation de Linda et à la fusion. SCRUM-15 reste une dépendance de clôture. Aucun remplacement du modèle n'est décidé ici : l'inférence aboutit sur cette machine ; la vitesse de la démo et la faisabilité LoRA demandent leurs propres essais.
