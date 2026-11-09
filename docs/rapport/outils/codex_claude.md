# Codex CLI piloté par Claude Code — agents de code

- **Utilisé par / pour** : Alain.
  - Rôles : Claude Code rédige les spécifications, relit, lance les tests et gère git, les PR et Jira ; Codex (`gpt-6.1-sol`, effort faible ou moyen) écrit le code et la documentation.
  - Exemples : passage à Gemma 4 E4B QAT (SCRUM-63), essai LoRA et ses correctifs (SCRUM-29), défauts du volet B (SCRUM-46).
  - Chaque usage est déclaré dans le [journal](../../projet/journal.md) (« Usage IA : Codex gpt-6.1-sol supervisé par Claude »).
- **Temps d'appropriation constaté** : non mesuré. Le mode de travail s'est stabilisé autour d'un script de lancement et de missions écrites.
- **Ce qui a marché** :
  - SCRUM-63 livré avec 89 tests réussis (27/10).
  - SCRUM-29 corrigé après l'essai de Nassim : 155 tests réussis, puis essai T4 réussi (08/11).
  - Le découpage des rôles réduit le contexte de chaque agent : l'un spécifie, l'autre code, et la relecture est séparée de l'écriture.
- **Ce qui a échoué ou déçu** :
  - Dans notre configuration, Codex n'a pas pu exécuter Python : c'est l'orchestrateur qui lance les tests. Ce point dépend du mode de bac à sable : avec `workspace-write` dans un worktree Git, Linda constate que Codex lance bien pytest, à condition d'ajouter `-p no:cacheprovider`, sinon il crée un `.pytest_cache` impossible à supprimer.
  - Codex a écrit des affirmations fausses dans la documentation : « Aucun pytest exécuté » dans le journal alors que les tests avaient tourné, et, pour SCRUM-46, un essai LoRA présenté comme non attesté alors qu'il était consigné. Les deux ont été repérées et corrigées en relecture.
  - Plusieurs paquets Codex installés en même temps ont cassé le script de lancement. Il choisit maintenant la version la plus récente qui contient l'exécutable.
  - Les connecteurs MCP non nécessaires doivent être désactivés au lancement, pour que Codex ne touche à aucune connexion externe.
- **Ce que la documentation omet** : un agent de code écrit volontiers des constats (tests, résultats) qu'il n'a pas vérifiés. Toute phrase sur un résultat doit être recoupée avec la commande et sa sortie.
- **Comparaison avec l'outil utilisé avant** : avant, Claude Code seul ou Codex seul (septembre-octobre). Le tandem ajoute une relecture systématique par un deuxième agent, mais aussi une étape de spécification. Pour une petite modification de documentation, c'est plus lent que d'écrire à la main.
- **Verdict** : on garde le tandem pour le code. Règle : aucun résultat écrit par un agent n'entre dans le journal sans avoir été vérifié par un humain ou par la commande correspondante. Les relectures d'Alain sur ces livraisons restent à faire.
