# TeamAI — Feuille de route

Mise à jour du 6 octobre 2026. La source de vérité est le [board Jira SCRUM](https://lindaboukhit04.atlassian.net/jira/software/projects/SCRUM/boards/1) ; ce document en donne la vue d'ensemble.

Sujet : détection et interprétation d'anomalies dans les logs HDFS (Loghub HDFS_v1). Validation de l'enseignant toujours en attente ; l'équipe a démarré pour ne pas perdre de temps (relance : SCRUM-12).

## Situation au 6 octobre

- Jalon de mi-parcours du 1er octobre **non tenu** : rien n'est encore déployé ni poussé (le dépôt ne contient que le README). Rattrapage prévu dans le sprint 1 (SCRUM-17).
- Prochain jalon noté : **J3 le 16 octobre** (volet A fonctionnel, adaptation engagée, supports préparés, rapport commencé).

## Jalons

| Date | Jalon | Ce qui doit exister |
|---|---|---|
| 01/10 (manqué) | Mi-parcours | Volet A v0 en ligne, 1re inférence locale, tag Git, capture du board |
| **16/10** | J3 | Volet A fonctionnel, LoRA engagé, supports J3, rapport commencé |
| 28/11 (interne) | Rapport V1 | PDF remis, site figé en v1.0 |
| **07/12** | J4 — soutenance | Site en ligne **avant** ce jour, pitch + présentation envoyés, vidéos de secours |

## Sprints

| Sprint | Dates | Objectif |
|---|---|---|
| 1 — Rattrapage & J3 | 06/10 → 16/10 | Données auditées et splits figés ; spike ONNX ; site v0 puis fonctionnel avec BiLSTM v1 ; 1re inférence SLM ; essai LoRA ; corpus doc ; grille d'annotation ; supports J3 ; rapport démarré |
| 2 — Adaptation & RAG | 19/10 → 01/11 | Jeu de test B réservé ; annotation du jeu d'adaptation ; RAG à 1 agent ; mesures « avant » ; LoRA complet ; volet A optimisé (int8) et UX soignée |
| 3 — Agents & évaluation | 02/11 → 15/11 | 3 agents ; interface locale ; évaluation finale A ; évaluation B (4 configurations, double annotation) ; défauts + feuille de route B |
| 4 — Rapport & gel site | 16/11 → 29/11 | Comparaison A/B ; rapport V1 PDF ; retours d'expérience individuels ; site v1.0 vérifié ; vidéos de démo |
| 5 — Soutenance | 30/11 → 07/12 | Pitch et présentation ; répétitions et questions croisées ; remise des livrables |

## Epics et responsables

| Epic | Responsable | Binôme / relecture |
|---|---|---|
| SCRUM-5 Pilotage, traçabilité et jalons | Linda | Alain |
| SCRUM-6 Corpus HDFS_v1 | Nassim | Bachar |
| SCRUM-7 Volet A — BiLSTM dans le navigateur | Bachar | Nassim |
| SCRUM-8 Volet B — SLM et LoRA | Alain | Linda |
| SCRUM-9 Volet B — RAG, agents, interface | Linda | Alain |
| SCRUM-10 Évaluation et comparaison | Nassim | toute l'équipe |
| SCRUM-11 Rapport, outils, démos, soutenance | Alain | toute l'équipe |

## Chemin critique (dépendances minimisées le 6 octobre)

Les données Loghub sont déjà prétraitées (`Event_traces.csv`, 29 templates) et les formats d'échange sont proposés dans `docs/contrats.md`. Chacun démarre donc sans attendre les autres : les vraies dépendances restantes sont visibles sur le board (liens « bloque »).

1. Réunion de lancement (SCRUM-55, 07/10) → débloque BiLSTM (25), parité JS (26), essai LoRA (29).
2. Volet A : spike ONNX (22) → site v0 (23) → parcours (27) → **J3**. Le BiLSTM (25) tourne d'abord sur un split provisoire ; les splits officiels (20) ne bloquent que l'évaluation finale (44).
3. Volet B : machine cible (15) → 1re inférence + `generate.py` (28) → essai LoRA (29) → **J3**. RAG et agents avancent avec le mode factice de `generate.py`.
4. Après J3 : grille (31) → test B (35) + annotation (36) ; corpus (30) → RAG (37) → mesures « avant » (38) → LoRA (39) → agents (42) → évaluation B (45) → défauts (46) → comparaison (47) → rapport (48).

Points à surveiller à chaque réunion : la machine cible du SLM (15) et l'annotation (36), seules étapes longues sans solution de contournement.

## Règles de travail

- Ticket créé **avant** de commencer ; un responsable, un relecteur, un critère de fin.
- Git : `main` = production (le site se déploie depuis `main`), `dev` = travail en cours. Branche `feat/SCRUM-<n>-<slug>` depuis `dev` → PR relue vers `dev` → PR `dev` → `main` + tag à chaque mise en production.
- Commits `SCRUM-<n>: message`, sans mention d'assistant IA ; l'usage de l'IA est consigné dans le journal dédié.
- Le jeu de test (A et B) n'est ouvert qu'à l'évaluation finale.
- Tout abandon de fonctionnalité est consigné comme décision (valorisé par l'enseignant).

## Risques suivis

| Risque | Parade |
|---|---|
| Sujet refusé tardivement par l'enseignant | Relance immédiate (SCRUM-12) ; architecture réutilisable sur un autre corpus |
| HDFS trop « facile » (baseline quasi parfaite) | Le présenter comme un résultat ; analyser les erreurs ; valoriser l'UX et l'optimisation |
| Machine insuffisante pour LoRA | QLoRA, modèle plus petit, ou GPU gratuit (Colab/Kaggle) ; jamais de remplacement silencieux par du prompting |
| Explications de référence coûteuses à produire | Pré-génération assistée + relecture humaine systématique, tracée |
| Agents sans gain mesurable | Résultat négatif documenté, comparaison à 1 agent conservée |
| Site non livré à temps | Déployé dès le sprint 1, gel v1.0 le 27/11 |
