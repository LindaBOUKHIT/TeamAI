# Outils novateurs (bonus, jusqu'à +3)

À remplir **pendant** l'usage, pas à la fin. Ce qui compte : les conditions d'échec, ce que la doc omet, le temps d'appropriation, la comparaison avec l'outil d'avant, un abandon argumenté. Recopier la doc ou lister des fonctionnalités ne rapporte rien.

## Modèle de fiche

### <Nom de l'outil> — <nature : MCP, agent, bibliothèque, IDE…>

- **Utilisé par / pour** :
- **Temps d'appropriation constaté** :
- **Ce qui a marché** (résultat concret, lien vers commit/ticket) :
- **Ce qui a échoué ou déçu** (conditions précises) :
- **Ce que la documentation omet** :
- **Comparaison avec l'outil utilisé avant** :
- **Verdict** (on garde / on abandonne, pourquoi) :

## Fiches rédigées

| Fiche | Nature | Auteur |
|---|---|---|
| [PEFT / QLoRA sur T4 Kaggle](outils/peft_qlora.md) — **fiche critique** | Bibliothèque | Alain |
| [llama.cpp / GGUF](outils/llama_cpp.md) | Runtime local | Alain |
| [Connecteur MCP Atlassian](outils/mcp_atlassian.md) | MCP | Alain (avec les automatisations de Linda) |
| [Serveur MCP Kaggle](outils/kaggle_mcp.md) | MCP | Alain |
| [Codex CLI piloté par Claude Code](outils/codex_claude.md) | Agents de code | Alain |

## Candidats

| Outil | Nature | Qui | Statut |
|---|---|---|---|
| Connecteur MCP Atlassian (Jira) via Claude Code | MCP | Alain | Fiche rédigée |
| ONNX Runtime Web | Bibliothèque | Bachar | À démarrer (SCRUM-22) |
| PEFT / QLoRA | Bibliothèque | Alain | Fiche rédigée (critique) |
| Ollama ou llama.cpp | Runtime local | Alain | llama.cpp retenu, fiche rédigée ; Ollama non évalué |
| Gradio | Bibliothèque UI | Linda | À démarrer |
| Serveur MCP Kaggle | MCP | Alain | Fiche rédigée |
| Codex CLI piloté par Claude Code | Agents de code | Alain | Fiche rédigée |
| Laya (modèle de décision calibré, ModernBERT) | Modèle ouvert | Alain | Essayé (SCRUM-58), non retenu |

## Laya : essai court (SCRUM-58)

Laya (`convaiinnovations/laya`, Apache 2.0) est un encodeur ModernBERT. Il répond en une passe à des questions typées, avec des probabilités qu'il présente comme calibrées. Nous l'avons essayé comme « Système 1 » à côté du SLM : il devait forcer l'abstention quand l'anomalie est ambiguë et écarter les hypothèses peu appuyées. L'installation (`pip install laya`) et l'API `Router.predict` sont simples, et la révision du modèle se fige. Sur CPU, chaque bloc coûte environ 2,3 s et 2,7 GiB de RSS.

En zéro-shot, sur une séquence de templates HDFS, la probabilité d'anomalie ne sépare pas les blocs en échec des blocs normaux. L'AUC vaut 0,47 sur 40 blocs de validation, après choix de la question sur 40 autres blocs. La vérification des hypothèses ne retient pas les deux hypothèses que la relecture humaine juge douteuses. Verdict : intéressant pour des décisions génériques, inadapté sans adaptation à des journaux techniques. Nous ne l'avons pas intégré. Source : `eval/results/SCRUM-58/README.md`.
