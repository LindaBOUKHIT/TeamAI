# Laya (encodeur ModernBERT de décision calibrée) — modèle ouvert, essayé puis abandonné

- **Utilisé par / pour** : Alain, SCRUM-58. Essai de Laya (`convaiinnovations/laya`, Apache 2.0, révision `85cc74dd`, paquet `laya` 0.4.31) comme « Système 1 » à côté du SLM : forcer l'abstention quand l'anomalie est ambiguë et écarter les hypothèses peu appuyées. Détails : [`eval/results/SCRUM-58/README.md`](../../../eval/results/SCRUM-58/README.md).
- **Temps d'appropriation constaté** : une journée (13/11), installation, quatre runs et décision comprises.
- **Ce qui a marché** :
  - Installation simple (`pip install laya`) et API courte (`Router.predict`), révision du modèle transmise au routeur.
  - Protocole propre : question choisie sur une cohorte de mise au point de 40 blocs `val`, puis appliquée une seule fois à 40 autres blocs `val`, sans ajustement après lecture.
  - Coût mesuré sur CPU : environ 2,3 s par bloc et 2,7 GiB de RSS.
- **Ce qui a échoué ou déçu** :
  - En zéro-shot, la probabilité d'anomalie ne sépare pas les blocs en échec des blocs normaux : AUC 0,47 sur la validation unique, soit le niveau du hasard.
  - Les abstentions ajoutées (8 sur 40) ne suivent donc pas le label.
  - La vérification des hypothèses conserve les deux hypothèses que la relecture de SCRUM-63 juge douteuses.
  - La révision effectivement chargée n'est pas vérifiable depuis l'API (`loaded_revision_verified: false`).
- **Ce que la documentation omet** : le comportement sur des entrées techniques non rédigées, comme une suite de templates HDFS ; les exemples portent sur des décisions en langue naturelle.
- **Comparaison avec l'outil utilisé avant** : sans Laya, l'abstention et le tri des hypothèses reposent sur les contrôles déterministes du pipeline v16. Laya ajoutait un coût sans apporter de signal.
- **Verdict** : abandonné. Une adaptation supervisée par les labels d'anomalie en ferait un second détecteur binaire, rôle déjà tenu par le volet A ; une adaptation sur les annotations du volet B demanderait un jeu relu. Le code reste testé (`tests/test_laya_gate.py`) pour une reprise éventuelle.
