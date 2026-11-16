# SCRUM-40 — Optimisation du volet A

Le site sert le modèle FP32. Le Web Worker charge le modèle WASM et exécute
les prédictions par lots de 64. La page affiche la progression et applique
le seuil de SCRUM-62 aux scores retournés.

## Comparaison sur la validation

Même seuil (0.40814146399497986) et mêmes 86 259 blocs. ONNX Runtime Python
sur CPU, quatre threads. Les deux variantes ont produit les mêmes décisions,
avec 59 faux positifs et un faux négatif. L'écart maximal des scores est de 0,0337.

| Mesure | FP32 | Candidat INT8 |
| --- | ---: | ---: |
| Taille (octets) | 56 806 | 21 564 |
| Macro-F1 | 0,993948 | 0,993948 |
| Latence médiane sur une trace (ms) | 0,189 | 0,214 |
| Validation en lots de 512 (s) | 3,45 | 3,74 |

## Opera, WASM, localhost

Médianes de trois passages. La récupération sans cache inclut l'écriture
dans Cache Storage. Le tout premier démarrage du moteur WASM est exclu
des comparaisons de latence d'inférence.

| Mesure (ms) | FP32 | Candidat INT8 |
| --- | ---: | ---: |
| Récupération sans cache | 23,7 | 20,7 |
| Lecture du cache | 8,1 | 6,8 |
| Inférence sur une trace synthétique | 0,20 | 0,30 |
| Inférence par trace en lot de 64 | 0,124 | 0,113 |

Les deux variantes échouent à créer une session WebGPU avec le repli CPU
désactivé. La présence d'un adaptateur GPU ne suffit pas à exécuter tout le graphe.

Le candidat INT8 réduit la taille de 62 %, avec un léger gain par lot sous
Opera et une latence supérieure sur une trace isolée. Il diffère du fichier
de 22 570 octets évalué dans SCRUM-44. Compte tenu de ces mesures et de cette
différence d'artefact, le site conserve le FP32.

Pour produire un candidat INT8 dans un nouveau dossier :

```powershell
python -m volet_a.training.export_onnx --int8-from volet_a/web/public/model/detector.onnx --output-dir eval/runs/scrum40-int8
```
