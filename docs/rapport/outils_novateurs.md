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

## Fiches

### PEFT / QLoRA sur T4 Kaggle — bibliothèque d'adaptation (fiche critique)

- **Utilisé par / pour** : Alain, essai LoRA court du SLM (SCRUM-29, SCRUM-61) : r=8 sur `q_proj`/`v_proj` de Gemma 4 E4B QAT, base NF4 et calcul fp16, 20 exemples train, 30 pas. Détails et chiffres dans le journal (entrées SCRUM-29 du 14/10, 27/10 et 08/11) et la PR [#23](https://github.com/LindaBOUKHIT/TeamAI/pull/23).
- **Temps d'appropriation constaté** : environ quatre semaines calendaires entre le premier essai CPU (14/10) et le premier essai T4 complet (08/11), dont trois exécutions Kaggle le 08/11 avant la bonne. Le temps passé en heures n'a pas été relevé.
- **Ce qui a marché** : chaîne complète sur T4 (14,56 Gio) — 30 pas appliqués, aucun sauté, loss moyenne de 0,586 (5 premiers pas) à 0,052 (5 derniers), 4,9 s par pas, pic VRAM 10,24 Gio, 2 269 184 paramètres entraînables ; adaptateur rechargé puis converti en GGUF F16 de 4,5 Mo par llama.cpp. Ces pertes portent sur les exemples d'entraînement : elles montrent la faisabilité, pas la qualité.
- **Ce qui a échoué ou déçu** :
  1. OOM sur T4 (essai de Nassim) : `model(**batch).loss` calcule les logits de toutes les positions sur un vocabulaire de 262 144 tokens, puis les passe en float32 (environ 2 Gio pour 2 000 tokens). Correction : loss calculée sur le seul suffixe supervisé (`logits_to_keep`).
  2. « Gradient non fini » en fp16 : la T4 n'a pas de bf16, et l'échelle initiale de GradScaler (65 536) provoque des débordements. Notre script arrêtait l'essai au lieu de laisser le pas être sauté. Correction : échelle initiale 1024, écrêtage à 1.0, échec explicite après 8 sauts consécutifs.
  3. Image Kaggle : installer `torch==2.9.1` sans figer `torchvision==0.24.1` et `torchaudio==2.9.1` fait échouer l'import de PEFT (`torchvision::nms does not exist`).
  4. Premier essai sur CPU (SmolLM2 1,7 B, float32) : 784 s pour un pas de 2 056 tokens ; 30 pas auraient pris 4 à 6 h.
- **Ce que la documentation omet** :
  - le coût mémoire de la loss intégrée quand le vocabulaire est grand : il dépasse le gain de QLoRA sur une carte de 15 Gio ;
  - le comportement de GradScaler en fp16 pur sur une carte sans bf16 : un pas sauté est normal, ce n'est pas une erreur à lever ;
  - les architectures à cache KV partagé : sur Gemma 4 E4B (`num_kv_shared_layers: 18`), les couches 24 à 41 n'ont pas de `v_proj`, donc `v_proj` n'est adapté que sur 24 couches sur 42, sans avertissement. Nous l'avons constaté à la conversion GGUF.
- **Comparaison avec l'outil utilisé avant** : avant, LoRA en float32 sur CPU (i5-1240P, SmolLM2 1,7 B) : 150 à 784 s par pas. Après, QLoRA sur T4 : 4,9 s par pas. Modèle, longueur et matériel diffèrent : ce n'est pas une comparaison contrôlée, seulement un ordre de grandeur qui rend l'essai faisable.
- **Verdict** : on garde QLoRA pour l'essai court, avec une réserve. On entraîne sur une base NF4, puis l'inférence se fait sur un GGUF Q4_0 (RTX 3050) : deux quantifications différentes. Rien ne garantit que l'adaptateur transfère bien de l'une à l'autre. Tant que la comparaison `lora_scale` 0 / 1 sur la RTX 3050 (SCRUM-61) n'est pas faite, le gain apporté par LoRA reste non démontré : on ne le présentera pas comme un résultat.

## Candidats

| Outil | Nature | Qui | Statut |
|---|---|---|---|
| Connecteur MCP Atlassian (Jira) via Claude Code | MCP | Alain | En cours — board, sprints, liens de dépendance créés le 06/10 |
| ONNX Runtime Web | Bibliothèque | Bachar | À démarrer (SCRUM-22) |
| PEFT / QLoRA | Bibliothèque | Alain | Fiche rédigée (critique) — transfert vers GGUF à vérifier (SCRUM-61) |
| Ollama ou llama.cpp | Runtime local | Alain | À évaluer |
| Gradio | Bibliothèque UI | Linda | À démarrer |
