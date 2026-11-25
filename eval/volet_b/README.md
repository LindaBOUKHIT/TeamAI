# Jeu de test réservé du volet B (SCRUM-35)

## Gel du 25/11/2026

`test.jsonl` est figé (80 cas, SHA-256 `658c3d0dd963e823a5af7764cbd8921dbf2e80a97a1af9e69cea9dc6eee2a38c`) avec `python -m eval.volet_b.figer_test --sans-relecture-croisee`. Les cas test-0001 à test-0020 ont été vérifiés par leur annotateur mais n'ont pas eu de relecture croisée : leur champ `reviewed_by` vaut « non relu (relecture croisée non faite) ». Les 60 autres cas sont vérifiés et relus.
