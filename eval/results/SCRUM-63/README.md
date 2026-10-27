# SCRUM-63 — Gemma 4 E4B QAT et prompt v16 figé

Le modèle courant est `google/gemma-4-E4B-it-qat-q4_0-gguf`, fichier
`gemma-4-E4B_q4_0-it.gguf`, révision `4b4a2c1d584be7264f87aac328a1bc739ce81b6c`.
llama.cpp, réflexion désactivée, contexte 4096, réponse 800 tokens, température 0,
seed 42, repeat_penalty 1.0. Le fichier `model_v16.json` est la preuve de révision.
Ces résultats sont ceux de l’exploration existante ; aucune nouvelle inférence
n’a été effectuée pour ce port. La cible locale est le portable de Nassim,
Ryzen 5 8645HS, 32 Go, RTX 3050 Laptop 6 Go, environnement logiciel à relever.

## Choix du modèle : v6–v11

Source historique : `explorations/kaggle/README_v1-v11.md` et `v11/sortie_v11/`.
Les essais v6–v10 portent sur cinq blocs déjà réutilisés : ils orientent le choix,
mais ne mesurent pas une généralisation. Les chiffres manquants ne sont pas
reconstitués depuis une impression qualitative.

| Étape | Modèles et décision | Chiffres et limites |
|---|---|---|
| v6 | SmolLM3 3B, Granite 4.2 3B, Gemma 4 E2B/E4B ; E4B préféré pour le contenu | 5 blocs ; Granite nécessite repeat_penalty 1.0 et un schéma ; pas de score sémantique indépendant |
| v7 | Gemma QAT, flash attention, Qwen | Échec de montage de la sortie v6 ; aucun résultat comparatif exploitable |
| v8 | Gemma QAT E2B/E4B, avec/sans flash attention ; Qwen3-4B et Qwen3.5-2B/4B écartés pour boucles/erreurs | Gemma QAT 5/5 conformes ; flash attention environ 10 % plus rapide ; script v8 non conservé, sortie seule |
| v9 | Gemma E4B QAT préféré ; Granite invente une lecture ; SmolLM3 et E2B hallucinent depuis le glossaire | 5 blocs ; revue qualitative, sans taux de vérité établi |
| v10 | Glossaire réduit aux codes présents et durée calculée par le code | 5 blocs ; hallucinations depuis les codes absents non relevées dans cet essai, hypothèses parfois tautologiques |
| v11 | Gemma E4B QAT retenu, Granite écarté pour abstentions incohérentes | 40 blocs val (20 WARN/20 sans WARN, 13 Fail/27 Success) : Gemma 40/40 `ok`, moyenne 33,36 s ; Granite 22/40, 18 abstentions incohérentes, 16,36 s |

SmolLM2-1.7B reste une étape historique locale (SCRUM-28/SCRUM-57) : sur les cinq
blocs du banc SCRUM-57, 0/5 réponses conformes C5 pour les deux backends, avec ou
sans l’adaptateur d’essai. Les protocoles diffèrent : ces chiffres ne forment pas
une comparaison contrôlée SmolLM2/Gemma. Le choix de Gemma repose sur l’exploration,
la conformité relative et la lecture des réponses, pas sur une preuve de vérité.

## Réglage du prompt : v12–v16

- v12 : faits calculés avec références F/T/L, schéma contraignant et contrôles.
  Sur 20 blocs, 20 contrats conformes et faits copiés exacts ; 7 enquêtes sur
  blocs sans indice d’incident. Les demandes de suppression, fins de
  PacketResponder et chronologies étaient encore mal interprétées.
- v13 : définitions techniques précisées, demandes distinguées des opérations,
  prudence sur chronologie et causalité. Sur les mêmes 20 blocs : 20/20 contrats,
  20/20 faits copiés, enquêtes sans incident de 7 à 2 ; alertes d’ordre dans
  une même seconde de 4 à 1. Ce sont des alertes ciblées, pas un score sémantique.
- v14–v15 : travail sur les faits de même seconde, ancrages et correction unique.
  v15 emploie 40 nouveaux blocs val du sample, dont 21 avec indice d’incident.
  40/40 contrats et faits exacts, mais 2 réponses avec références inexistantes,
  16 hypothèses réseau sans appui, 18 enquêtes inutiles parmi les 19 blocs sans
  incident, 42 hypothèses sur les 21 blocs avec incident. Aucune correction
  déclenchée par le mécanisme de l’époque. La comparaison v13/v15 porte sur des
  cohortes distinctes ; aucun gain global ne peut lui être attribué.
- v16 : hypothèses facultatives, causes fermées issues des détails des messages,
  questions interdites sans indice reconnu, mentions factuelles E24/E27/E28,
  contrôle des références dans tous les champs et correction unique partagée.
  Sur les mêmes 40 blocs que v15 : 40/40 contrats et faits exacts, 0 référence
  inexistante finale après 2 corrections, 0 alerte réseau, 0 enquête sans incident,
  3 hypothèses au total pour 21 blocs avec incident. La moyenne avec corrections
  est de 30,46 s/bloc sur deux T4 ; elle ne prédit pas la latence sur le portable.

`prompt_freeze.json` contient les SHA-256 originaux du runtime Kaggle, de la
consigne, de la politique et des 40 prompts/schémas. `policy_v16.txt` est une copie
exacte du fichier Python de politique original : le test vérifie son hash puis
compare son AST au module porté après retrait des seules docstrings ajoutées.
Les contrôles v16 ne sont pas réinterprétés comme des preuves de fidélité.

## Validation unique sur 40 blocs inédits

Voir `comparaison_v16_validation.json` et `revue_qualitative_validation.json`.
Le prompt, schéma et règles sont ceux figés après v16, sans nouveau réglage.
Le tirage exclut les 85 blocs déjà connus, seed 42, 20 WARN/20 sans WARN ;
21 blocs ont un indice d’incident et 19 n’en ont pas. Aucun bloc test.

Résultats finaux : 40/40 contrats et copies de faits conformes, 0 référence
inexistante après une correction, 0 hypothèse réseau sans appui et 0 enquête
sans incident. Quatre hypothèses pour les 21 blocs avec incident, soit **0,19
hypothèse par bloc avec incident**. 39/40 passent les contrôles factuels du
runtime ; la moyenne avec correction est de 30,62 s/bloc.

La revue relève deux erreurs de chronologie (cas 10 et 13), trois liens causaux
non démontrés (13, 15, 33), trois pseudo-références (6, 24, 38) et un résumé
inutilisable (cas 7, `blk_3380500577009533140`) : F09 répété 130 fois,
783 tokens, malgré un arrêt `stop`. Aucun nouveau lancement n’a été fait pour
corriger ce résultat exploratoire. La mention « cause indéterminée » manque
encore dans les 16 résumés concernés. E24 et E27 sont absents de cette validation ;
E28 est présent une fois. Le schéma ne garantit donc pas une explication juste.

## Port et seul contrôle supplémentaire autorisé

Code : `volet_b/slm/v16/`. Les faits sont reconstruits avec `data.parse_hdfs` ;
seuls les codes présents entrent dans le glossaire du prompt. L’appel passe par
`generate()` avec le schéma v16 dans `response_format`. Aucun document RAG,
label attendu ou résultat de détection n’est injecté.

Après les contrôles v16, le port rejette six répétitions consécutives d’une même
référence ou d’un segment, ainsi qu’une réponse à au moins 95 % du budget
(760/800 tokens). L’erreur précise rejoint le déclencheur de correction unique
existant. Les deux réponses brutes sont conservées, même si la seconde échoue.
Ce contrôle ne modifie pas l’empreinte du prompt initial. Il n’a pas été appliqué
rétroactivement aux synthèses copiées ici ; il est testé avec le texte réel en
fixture et une réponse normale. La correction ne produit jamais un troisième appel.

## Périmètre et provenance

Les blocs sont des `val` de `data/sample`, pas un échantillon de tout HDFS.
Le prompt a été réglé sur une partie de ces blocs ; seule la dernière cohorte
est inédite. Les comparaisons non appariées ne prouvent pas de progrès causal.
La détection n’est pas faite par le SLM. Chronologies, causalités et citations
restent parfois fausses ; les règles et listes fermées expliquent une partie
des gains, sans démontrer un meilleur raisonnement général du modèle.
Aucune adaptation LoRA de Gemma ni chaîne RAG n’est évaluée dans cette trace.

Copies compactes : gel et politique, causes compatibles, règle de validation,
comparaisons et revues v13/v15/v16/validation, identité du modèle. Les fichiers
complets restent **hors dépôt** dans
`D:\scolaire\master\m2\26-27 Natural Language Processing 2_M2IA_S3\explorations\kaggle\`,
notamment `v16/` et `v16/validation_unique/`. Aucun journal Kaggle, roue, poids
ou résultat brut volumineux n’est ajouté au dépôt. Les seuls textes bruts copiés
en fixtures sont le cas en boucle et un cas normal ; les 40 entrées de mise au
point ne contiennent que l’identifiant, le split val et les lignes numérotées.

Vérification : Suite complète `python -m pytest -q` exécutée le 27/10 avec le Python du projet : 89 tests réussis, 5 ignorés, sans réseau ni GGUF.
