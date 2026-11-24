# Questions probables du jury et réponses courtes (SCRUM-53)

Support de répétition. Chaque membre doit pouvoir répondre à toutes les questions, y compris sur la partie d'un autre. Les réponses tiennent en deux ou trois phrases ; la source permet de vérifier un chiffre avant la soutenance. **À relire par l'équipe** : ce fichier ne vaut pas validation collective.

Règle pour toutes les réponses : distinguer **validation** et **test**, et dire « non mesuré » plutôt qu'avancer un chiffre absent des sources.

## 1. Projet et données

**1. Quel problème traitez-vous ?**
Repérer les blocs HDFS anormaux dans des journaux, puis aider un opérateur à comprendre ce qui s'est passé. Le volet A classe chaque bloc ; le volet B produit une explication structurée des événements d'un bloc. Source : [rapport, §1](../rapport/rapport_v1.md).

**2. Quelles données, et comment les avez-vous découpées ?**
HDFS_v1 de Loghub : 575 061 blocs, chacun étiqueté normal ou anomalie. Découpage `C4-bloc` : tirage stratifié par label, bloc par bloc, 70/15/15, graine 42, soit 402 542 blocs en entraînement, 86 259 en validation et 86 260 en test. Source : [contrats, C4](../contrats.md).

**3. Des séquences identiques en entraînement et en test, ce n'est pas une fuite ?**
Ce n'est pas une fuite d'identifiant : un bloc n'appartient qu'à un seul split. Mais HDFS ne compte que 18 373 séquences distinctes, donc beaucoup de séquences du test ont déjà été vues. C'est pourquoi nous publions toujours un second chiffre sur les **1 962** blocs du test à séquence inédite. Source : [contrats, C4](../contrats.md).

**4. Avez-vous touché au test pendant le développement ?**
Non pour les choix : seuil, prompt, exemples et hyperparamètres sont fixés sur la validation. Le test du volet A a été ouvert une seule fois (SCRUM-44). Un précédent est déclaré : un fichier de la baseline contenait déjà des mesures sur le test le 12/10, sans servir au réglage. Source : [évaluation du volet A](../../eval/results/volet_a.md).

## 2. Volet A — détection

**5. Pourquoi un BiLSTM plutôt qu'un modèle plus gros ?**
Il doit tourner dans le navigateur, sur un site statique et gratuit. Le modèle FP32 pèse 56 806 octets et lit 50 événements par bloc. Il bat la baseline par régression logistique sur le test, avec deux fois moins de fausses alertes (58 contre 116). Source : [rapport, §3.1](../rapport/rapport_v1.md).

**6. Décrivez l'architecture.**
Embedding de dimension 16 sur 31 indices (29 événements, remplissage, inconnu), LSTM bidirectionnel de 32 unités par sens, moyenne sur les positions réelles, couche linéaire puis sigmoïde. Cinq époques, lots de 512, taux d'apprentissage 0,001. Source : `volet_a/training/bilstm.py`, `volet_a/training/train.py`.

**7. Pourquoi un seuil de 0,41 et pas 0,5 ?**
Le seuil a été choisi sur la validation pour ne manquer presque aucune anomalie : 1 anomalie manquée au lieu de 21 avec le seuil initial de 0,99, au prix de 59 fausses alertes au lieu de 23. Les poids n'ont pas changé. Source : [analyse SCRUM-62](../../eval/results/SCRUM-62_20261023T153242Z_690fcb/analysis.json).

**8. Quels sont les résultats sur le test ?**
BiLSTM FP32 : macro-F1 **0,9938**, 58 fausses alertes et 3 anomalies manquées sur 86 260 blocs. Sur les séquences inédites : macro-F1 **0,9714**, 43 fausses alertes contre 67 pour la baseline. Source : [évaluation du volet A](../../eval/results/volet_a.md).

**9. Quelles erreurs fait le modèle ?**
Les 3 anomalies manquées ont toutes une séquence inédite. L'analyse de 10 erreurs repose sur les 50 premiers événements ; les logs bruts n'ont pas encore été examinés, donc nous ne connaissons pas la cause. Source : [évaluation du volet A](../../eval/results/volet_a.md), analyse des erreurs.

**10. Le navigateur donne-t-il les mêmes résultats que Python ?**
Oui : sur les 86 260 blocs du test, **0** décision divergente, écart maximal de 2,4 × 10⁻⁷ en FP32. Les scores Python sauvegardés ont servi de référence, sans rouvrir le test. Source : [évaluation du volet A](../../eval/results/volet_a.md), parité navigateur.

**11. Pourquoi servir le FP32 et pas l'INT8 ?**
L'INT8 prend les mêmes décisions et réduit la taille de 62 %, mais le gain de vitesse est faible et le fichier candidat n'est pas celui que le test a évalué. Comme le FP32 ne pèse que 57 Ko, la taille ne pose pas de problème. Source : [optimisation](../volet_a/optimisation.md).

**12. Les logs de l'utilisateur partent-ils sur un serveur ?**
Non. ONNX Runtime Web exécute le modèle en WASM dans un Web Worker ; la page n'envoie pas les logs. Source : `volet_a/web/src/worker.js`, [optimisation](../volet_a/optimisation.md).

**13. Le score est-il une probabilité ?**
Non, il n'est pas calibré, et le site l'affiche. Il sert à comparer au seuil, pas à dire « 99 % de chances ». Le site prévient aussi qu'un extrait peut ne pas contenir tout le bloc.

## 3. Volet B — explication

**14. Quel modèle, et pourquoi ?**
Gemma 4 E4B QAT en GGUF 4 bits, exécuté par llama.cpp, contexte de 4 096 tokens. Il a été retenu après comparaison de plusieurs modèles et versions de prompt (v6 à v16) sur la validation, pour tenir sur une machine locale. Source : [trace SCRUM-63](../../eval/results/SCRUM-63/README.md).

**15. Comment limitez-vous les hallucinations ?**
Le prompt v16 fournit des faits calculés (événements, chronologie, lignes) et impose une réponse JSON à six champs. Chaque affirmation doit citer un fait, une étape de chronologie ou une ligne. Un contrôle refuse les références inexistantes. Cela réduit les inventions sans les supprimer. Source : [défauts et feuille de route](../volet_b/defauts_feuille_de_route.md).

**16. Quels défauts avez-vous mesurés ?**
Sur 40 nouveaux blocs de validation : 2 erreurs de chronologie, 3 liens de causalité non étayés, 3 pseudo-références, 1 réponse en boucle. Dans les 16 cas où la cause reste inconnue, aucun résumé ne le dit. Les blocs de plus de 39 événements dépassent la fenêtre de contexte ; ils représentent 4,2 % des anomalies de la validation. Source : [défauts et feuille de route](../volet_b/defauts_feuille_de_route.md).

**17. À quoi sert le RAG ?**
Il ajoute des passages de la documentation HDFS pour éclairer les événements. Dans les runs à 3 agents, aucune réponse acceptée ne cite de passage : l'apport du RAG n'est pas démontré. Source : [SCRUM-42](../../eval/results/SCRUM-42/kaggle_val5_v2/README.md).

**18. Pourquoi trois agents ?**
Pour séparer la recherche des passages, la rédaction et le contrôle. Sur 5 blocs de validation, 1 réponse est acceptée sur 5, avec environ 86 s de génération par bloc sur un T4. C'est un essai de fonctionnement, pas une mesure de qualité. Source : [SCRUM-42](../../eval/results/SCRUM-42/kaggle_val5_v2/README.md).

**19. Et le LoRA ?**
La faisabilité est établie : un essai QLoRA de 30 pas sur un T4 Kaggle, puis la conversion de l'adaptateur en GGUF. L'inférence avec l'adaptateur et l'entraînement complet ne sont pas faits ; aucun gain n'est donc établi. Source : [rapport, §3.2](../rapport/rapport_v1.md).

**20. Avez-vous évalué le volet B sur le test ?**
Pas encore : il faut d'abord un jeu de référence relu et une double annotation (SCRUM-35, SCRUM-45). Tous les chiffres du volet B présentés viennent de la validation. *Mettre à jour cette réponse si SCRUM-45 aboutit avant la soutenance.*

## 4. Comparaison et perspectives

**21. Lequel des deux volets est le meilleur ?**
Ils ne font pas la même chose : A décide si un bloc est anormal, B aide à le comprendre. A est mesuré sur le test ; B seulement sur la validation. Les comparer sur une seule métrique n'aurait pas de sens. Source : [comparaison A/B](../../eval/results/comparaison_a_b.md).

**22. Pourquoi ne pas les enchaîner ?**
C'est la suite naturelle : A trie tout, B n'explique que les blocs signalés. Sur le test, A signale 2 581 blocs (3,0 %). Au rythme mesuré pour B, il faudrait environ 22 heures de GPU au lieu de 734 heures pour tout expliquer. Ces durées sont calculées, pas mesurées. Il ne faudrait pas transmettre le verdict de A à B, et la chaîne devrait être évaluée comme un troisième système. Source : [rapport, §4.3](../rapport/rapport_v1.md).

**23. Que feriez-vous avec un mois de plus ?**
Mesurer le volet B sur le test avec double annotation, gérer les traces longues (résumé ou découpage), puis évaluer la chaîne A puis B. Un modèle plus grand ne viendrait qu'après. Source : [feuille de route](../volet_b/defauts_feuille_de_route.md), §4.

## 5. Organisation et outils

**24. Comment vous êtes-vous organisés ?**
Jira pour les tickets, avec un responsable, un relecteur et un critère de fin par tâche. Une branche par ticket, des PR relues vers `dev`, puis `dev` publié sur `main`. Les décisions et les usages de l'IA sont tracés dans le journal. Source : [journal](../projet/journal.md).

**25. Comment avez-vous utilisé l'IA générative ?**
Pour le code, la documentation, l'organisation Jira et des relectures préparatoires, avec des outils déclarés dans le journal. Les validations humaines restent faites par l'équipe. Une erreur notable : des affirmations fausses sur des résultats, repérées en relecture. Source : [rapport, §6](../rapport/rapport_v1.md).

**26. Comment avez-vous eu accès à un GPU ?**
Le BiLSTM s'entraîne en 6 minutes sur CPU. Pour Gemma et le LoRA, nous avons utilisé des GPU T4 sur Kaggle, pilotés par un serveur MCP. Seules les données d'entraînement et de validation y sont envoyées, jamais le test. Source : [fiche outil Kaggle MCP](../rapport/outils/kaggle_mcp.md).

## Démonstrations à savoir refaire

- **Volet A** : ouvrir le site, charger « Plusieurs blocs », analyser, filtrer les anomalies, déplier une séquence, exporter le CSV. Montrer le repère du seuil sur la barre de score.
- **Volet B** : `python -m volet_b.app.app`, exemple d'anomalie, mode 3 agents. Prévoir plusieurs minutes sur CPU ; garder la vidéo de secours (SCRUM-51) et le mode `--mock` si le modèle ne charge pas.
