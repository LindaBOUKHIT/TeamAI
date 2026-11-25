"""Interface locale : traces HDFS, explications contrôlées, journal des agents et questions sur la documentation."""
import argparse
import csv
import html
import os
import re
import threading
import time
from functools import lru_cache

import pandas as pd

from data.parse_hdfs import compile_templates
from teamai.contracts import validate_answer
from teamai.paths import SAMPLE, SPLITS, resolve_path
from volet_b.agents import doc_chat, orchestrator, single_agent
from volet_b.app import ui
from volet_b.slm.v16.facts import prepare_block

BANNER = "Démo locale. Les explications sont générées et peuvent être fausses ; vérifiez les lignes citées."
LOCK = threading.Lock()
DEMO_MAX_LINES = 20  # exemple de 39 lignes mesuré le 24/11 : 4329 tokens demandés pour 4096


def safe(text):
    """Échappe le HTML et la syntaxe Markdown provenant des données.

    quote=False : html.escape changerait l'apostrophe en &#x27;, dont le « # » serait échappé
    une seconde fois et s'afficherait tel quel (« l&&#35;x27;enregistrement »).
    """
    return re.sub(r"[\\`*_{}\[\]()#+.!|>~-]", lambda m: f"&#{ord(m[0])};",
                  html.escape(str(text), quote=False)).replace("\n", " ")


STATUS_ICONS = {"accepte": "✅", "abstention_demandee": "⏸️", "rejete": "⛔", "erreur": "⚠️"}


def render_block(record):
    """Rend un enregistrement sans réparer sa réponse ni exécuter son contenu."""
    passages = record.get("passages", [])
    answer = record.get("parsed_response")
    errors = list(record.get("errors", [])) + validate_answer(
        answer, allowed_sources=[p["id"] for p in passages])
    status = record.get("statut", "rejete" if errors else "accepte")
    if status not in ("accepte", "abstention_demandee"):
        errors.append(f"statut de l'enregistrement : {status}")
    icon = STATUS_ICONS.get(status, "⚠️")
    parts = [f"## {icon} Bloc {safe(record['id'])}",
             f"Statut : {safe(status)} · Nombre d'appels : {record.get('n_calls', 1)}",
             f"Temps total : {record.get('total_seconds', record.get('seconds', 0)):.2f} s"]
    if errors:
        raw = record.get("raw_text", "")
        fence = "`" * max(3, max((len(m[0]) + 1 for m in re.finditer(r"`+", raw)), default=3))
        parts += ["### Sortie brute", f"{fence}text\n{html.escape(raw, quote=False)}\n{fence}",
                  "### Erreurs", *[f"- {safe(e)}" for e in dict.fromkeys(errors)]]
    else:
        for title, key in (("Résumé", "resume_evenements"), ("Faits observés", "faits_observes"),
                           ("Hypothèses", "hypotheses"), ("Infos manquantes", "infos_manquantes")):
            value = answer[key]
            parts += [f"### {title}", safe(value) if isinstance(value, str) else
                      "\n".join(f"- {safe(v)}" for v in value) or "Aucune."]
        parts += ["### Abstention", "Oui" if answer["abstention"] else "Non", "### Passages sources"]
        parts += [f"- **{safe(p['id'])}** : {safe(p['text'][:300])} — {safe(p['source_url'])}"
                  for p in passages] or ["Aucun passage fourni."]
    parts.append("### Journal des étapes")
    table = ["| Agent | Tentative | Verdict | Erreurs | Secondes |",
             "| --- | --- | --- | --- | --- |"]
    for step in record.get("steps", []):
        table.append("| " + " | ".join(safe(step.get(k) if step.get(k) is not None else "—")
                     for k in ("agent", "tentative", "verdict", "errors", "seconds")) + " |")
    return "\n\n".join(parts + ["\n".join(table)])


@lru_cache(maxsize=1)
def demo_split():
    """Lit le split officiel, ou son sous-ensemble livré avec l'échantillon."""
    if official_splits_available():
        return single_agent.official_split()
    return pd.read_csv(SAMPLE / "splits.csv").set_index("BlockId")["split"]


def official_splits_available():
    """Vrai si data/splits/splits.csv (C4 complet, non versionné) est présent."""
    return (SPLITS / "splits.csv").exists()


def refuse_unknown_blocks(block_ids, split):
    """Sans le C4 complet, refuse tout bloc absent de l'échantillon : il pourrait appartenir au test."""
    unknown = sorted(b for b in block_ids if b not in split)
    if unknown:
        shown = ", ".join(unknown[:3]) + (" …" if len(unknown) > 3 else "")
        raise SystemExit(f"{len(unknown)} bloc(s) absent(s) de data/sample/splits.csv ({shown}) : sans "
                         "data/splits/splits.csv, impossible de vérifier qu'ils ne sont pas dans le split test. "
                         "Créer ce fichier (voir « Lancer la démo » dans volet_b/README.md).")


def choose_examples():
    """Choisit deux blocs de validation uniquement, selon leur label d'échantillon.

    Pour chaque label, le bloc retenu est le plus long qui tient en DEMO_MAX_LINES lignes
    (le premier rencontré en cas d'égalité) : au-delà, le prompt v16 dépasse son plafond.
    """
    if not (SAMPLE / "HDFS_sample.log").exists():
        return "", ""
    split = demo_split()
    blocks = single_agent.lines_by_block((SAMPLE / "HDFS_sample.log").read_text(encoding="utf-8").splitlines())
    chosen = {}
    with (SAMPLE / "Event_traces.csv").open(encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            bid, label = row["BlockId"], row["Label"]
            if split.get(bid) != "val" or bid not in blocks or len(blocks[bid]) > DEMO_MAX_LINES:
                continue
            if label in chosen and len(chosen[label]) >= len(blocks[bid]):
                continue
            # Une ligne partagée ne doit pas introduire un autre bloc réservé.
            referenced = single_agent.lines_by_block(blocks[bid])
            if all(split.get(b) == "val" for b in referenced):
                chosen[label] = blocks[bid]
    return "\n".join(chosen.get("Fail", [])), "\n".join(chosen.get("Success", []))


@lru_cache(maxsize=2)
def get_retriever(mock):
    """Charge paresseusement une seule instance par mode."""
    return orchestrator.MockRetriever() if mock else orchestrator.load_retriever()


@lru_cache(maxsize=None)
def get_caller(adapter):
    """Conserve l'appelant et le modèle chargés pour chaque adaptateur demandé."""
    return orchestrator.make_call_slm(adapter)


@lru_cache(maxsize=1)
def get_templates():
    """Compile une seule fois les templates livrés dans l'échantillon."""
    return compile_templates(SAMPLE / "HDFS.log_templates.csv")


class PassageRecorder:
    """Retient les passages réellement fournis à la chaîne à un agent."""

    def __init__(self, retriever):
        """Associe le retriever partagé à un journal propre au bloc."""
        self.retriever, self.passages = retriever, []

    def search(self, query, k):
        """Recherche et conserve les passages sans modifier leurs identifiants."""
        self.passages = self.retriever.search(query, k)
        return self.passages


def analyze(text, configuration="3 agents", model="base", adapter="", mock=False):
    """Contrôle toute l'entrée puis explique au plus cinq blocs, sans accès au test."""
    banner = BANNER + (" **Mode factice actif (sans modèle).**" if mock else "")
    blocks = single_agent.lines_by_block(text.splitlines())
    if not blocks:
        return banner + "\n\nAucun bloc HDFS trouvé (identifiant blk_ attendu)."
    try:
        split = demo_split()
        single_agent.refuse_test_blocks(blocks, split)
        if not official_splits_available():
            refuse_unknown_blocks(blocks, split)
    except SystemExit as exc:
        return banner + "\n\nAnalyse refusée : " + safe(exc) + " Aucun appel au modèle."
    except (OSError, ValueError) as exc:
        return banner + "\n\nVérification des splits impossible : " + safe(exc)
    output = [banner]
    if len(blocks) > 5:
        output.append(f"Limite de 5 blocs par analyse : seuls les 5 premiers des {len(blocks)} blocs sont traités.")
    adapter = str(resolve_path(adapter.strip())) if model == "adapté" and adapter.strip() else None
    # Le verrou protège aussi la variable d'environnement utilisée par la chaîne historique.
    with LOCK:
        previous = os.environ.get("TEAMAI_SLM_MOCK")
        os.environ["TEAMAI_SLM_MOCK"] = "1" if mock else "0"
        try:
            retriever = get_retriever(mock)
            for bid, lines in list(blocks.items())[:5]:
                start = time.perf_counter()
                try:
                    if configuration == "3 agents":
                        numbered = [(n, line) for n, line in enumerate(text.splitlines(), 1) if line in lines]
                        block = prepare_block(bid, numbered, get_templates(), split=split.get(bid))
                        caller = orchestrator.mock_call_slm if mock else get_caller(adapter)
                        record = orchestrator.explain_block_three_agents(block, retriever, caller)
                    else:
                        recorder = PassageRecorder(retriever)
                        record = single_agent.explain_block(bid, lines, recorder, adapter=adapter)
                        record.update(passages=recorder.passages, n_calls=1, steps=[dict(
                            agent="single_agent", tentative=1, verdict="rejete" if record['errors'] else "accepte",
                            errors=record['errors'], seconds=record['seconds'])])
                    record["total_seconds"] = time.perf_counter() - start
                    output.append(render_block(record))
                except Exception as exc:
                    output.append(render_block(dict(
                        id=bid, statut="erreur", n_calls=None, steps=[], raw_text="",
                        errors=[f"Analyse impossible : {exc}", "Nombre d'appels non mesuré en cas d'exception."],
                        total_seconds=time.perf_counter() - start)))
        except Exception as exc:
            output.append("Chargement impossible : " + safe(exc))
        finally:
            if previous is None:
                os.environ.pop("TEAMAI_SLM_MOCK", None)
            else:
                os.environ["TEAMAI_SLM_MOCK"] = previous
    return "\n\n".join(output)


CHAT_EXAMPLES = ("Que signifie l'événement E23 ?", "Comment HDFS détecte-t-il qu'un DataNode est en panne ?",
                 "Que se passe-t-il quand une réplique d'un bloc est perdue ?",
                 "Que faut-il vérifier pour le dernier bloc analysé ?")


def source_line(passage):
    """Une source citée : document, section et lien officiel quand il est sûr."""
    label = f"{safe(passage['doc'])}, {safe(passage['section'])}"
    url = str(passage.get("source_url") or "")
    if re.fullmatch(r"https://[\w./#%-]+", url):
        return f"- [{label}]({url})"
    return f"- {label}"


def render_reply(record):
    """Rend la réponse contrôlée, ses sources, la requête lancée et les passages consultés."""
    if record["status"] == "vide":
        return ""
    by_id = {p["id"]: p for p in record["passages"]}
    consulted = ", ".join(safe(p["id"]) for p in record["passages"]) or "aucun"
    trace = f"_Requête : {safe(record['query'])} · passages consultés : {consulted}_"
    if record["status"] == "refusée":
        return "Réponse refusée par le contrôle : " + safe(" ; ".join(record["errors"])) + ".\n\n" + trace
    answer = record["answer"]
    if answer["abstention"]:
        return "**Abstention.** " + safe(answer["reponse"]) + "\n\n" + trace
    return "\n".join([safe(answer["reponse"]), "", "**Sources**",
                      *[source_line(by_id[s]) for s in answer["sources"]], "", trace])


def chat(question, history, analysis="", model="base", adapter="", mock=False):
    """Ajoute au fil la question et sa réponse sourcée ; vide la zone de saisie."""
    history = list(history or [])
    question = (question or "").strip()
    if not question:
        return history, ""
    adapter = str(resolve_path(adapter.strip())) if model == "adapté" and adapter.strip() else None
    previous_turns = [{**m, "content": html.unescape(str(m.get("content") or ""))} for m in history]
    with LOCK:
        previous = os.environ.get("TEAMAI_SLM_MOCK")
        os.environ["TEAMAI_SLM_MOCK"] = "1" if mock else "0"
        try:
            caller = doc_chat.mock_call_slm if mock else get_caller(adapter)
            # Seule une sortie d'analyse (qui commence par le bandeau) sert de contexte, pas l'accueil.
            context = html.unescape(analysis) if (analysis or "").startswith(BANNER) else ""
            record = doc_chat.ask(question, previous_turns, get_retriever(mock), caller, analysis=context)
            reply = render_reply(record)
        except Exception as exc:
            reply = "Réponse impossible : " + safe(exc)
        finally:
            if previous is None:
                os.environ.pop("TEAMAI_SLM_MOCK", None)
            else:
                os.environ["TEAMAI_SLM_MOCK"] = previous
    if mock:
        reply += "\n\n**Mode factice actif (sans modèle).**"
    return history + [{"role": "user", "content": question}, {"role": "assistant", "content": reply}], ""


def import_logs(path):
    """Lit un fichier de logs importé depuis le composant local."""
    return resolve_path(path).read_text(encoding="utf-8", errors="replace") if path else ""


def build_app(mock=False):
    """Construit l'interface « Vigie » en important Gradio uniquement à la demande."""
    import gradio as gr

    anomaly, normal = choose_examples()
    with gr.Blocks(title="Vigie · l'assistant qui lit vos logs HDFS", theme=ui.theme(), css=ui.CSS) as app:
        gr.HTML(ui.HEADER)
        with gr.Accordion("⚙️ Réglages du moteur", open=False):
            with gr.Row():
                configuration = gr.Radio(["1 agent", "3 agents"], value="3 agents", label="Architecture",
                                         info="3 agents : recherche documentaire, rédaction puis contrôle.")
                model = gr.Radio(["base", "adapté"], value="base", label="Modèle",
                                 info="Adapté : Gemma 4 avec l'adaptateur LoRA de l'équipe.")
            with gr.Row():
                adapter = gr.Textbox(label="Chemin de l'adaptateur GGUF", placeholder="vide = modèle de base")
                mock_mode = gr.Checkbox(value=mock, label="Mode factice (sans modèle)",
                                        info="Pour découvrir l'interface sans charger le modèle.")
            mock_notice = gr.Markdown("Mode factice actif (sans modèle)." if mock else "")
            mock_mode.change(mock_message, mock_mode, mock_notice)
        with gr.Tabs(elem_classes="vg-tabs"):
            with gr.Tab("🔎 Analyser une trace"):
                with gr.Row(equal_height=False):
                    with gr.Column(scale=5, min_width=320):
                        text = gr.Textbox(label="Logs HDFS bruts", lines=16, max_lines=24, elem_classes="vg-logs",
                                          placeholder="081109 203615 148 INFO dfs.DataNode$PacketResponder: "
                                                      "PacketResponder 1 for block blk_… terminating")
                        with gr.Row():
                            gr.Button("⚠️ Exemple : bloc anormal", size="sm", elem_classes="vg-chip").click(
                                example_anomaly, gr.State(anomaly), text)
                            gr.Button("✅ Exemple : bloc normal", size="sm", elem_classes="vg-chip").click(
                                example_normal, gr.State(normal), text)
                        file = gr.File(label="… ou importer un fichier .log / .txt", file_types=[".log", ".txt"],
                                       type="filepath")
                        file.change(import_logs, file, text)
                        run = gr.Button("Analyser la trace", variant="primary", elem_classes="vg-cta")
                    with gr.Column(scale=7, min_width=360):
                        with gr.Group(elem_classes="vg-panel"):
                            result = gr.Markdown(ui.RESULT_EMPTY, sanitize_html=True, elem_classes="vg-result",
                                                 padding=True)
                run.click(analyze, [text, configuration, model, adapter, mock_mode], result, concurrency_limit=1)
            with gr.Tab("💬 Demander à la doc"):
                with gr.Row(equal_height=False):
                    with gr.Column(scale=8, min_width=360):
                        thread = gr.Chatbot(type="messages", height=470, allow_tags=False, sanitize_html=True,
                                            show_label=False, avatar_images=ui.AVATARS,
                                            placeholder=ui.CHAT_PLACEHOLDER, show_copy_button=True)
                        with gr.Row(equal_height=True):
                            question = gr.Textbox(show_label=False, placeholder="Posez votre question sur HDFS…",
                                                  scale=6, container=False, autofocus=False)
                            send = gr.Button("Envoyer ➤", variant="primary", scale=1, min_width=110)
                    with gr.Column(scale=4, min_width=260):
                        gr.Markdown("**Essayez**")
                        for example in CHAT_EXAMPLES:
                            gr.Button(example, size="sm", elem_classes="vg-chip").click(
                                lambda e=example: e, None, question)
                        gr.ClearButton([thread, question], value="🧹 Nouvelle conversation", size="sm")
                        gr.HTML(ui.COVERAGE)
                inputs = [question, thread, result, model, adapter, mock_mode]
                send.click(chat, inputs, [thread, question], concurrency_limit=1)
                question.submit(chat, inputs, [thread, question], concurrency_limit=1)
            with gr.Tab("🧭 Comment ça marche"):
                gr.HTML(ui.HOW_IT_WORKS)
        gr.HTML(ui.FOOTER)
    return app


def mock_message(active):
    """Indique immédiatement si les prochaines réponses seront factices."""
    return "Mode factice actif (sans modèle)." if active else ""


def example_anomaly(text):
    """Remplit la zone avec l'exemple de validation présentant une anomalie."""
    return text


def example_normal(text):
    """Remplit la zone avec l'exemple normal de validation."""
    return text


def main(argv=None):
    """Lance exclusivement sur l'interface de boucle locale, sans partage public."""
    parser = argparse.ArgumentParser(description="Démo locale TeamAI")
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--port", type=int, default=7860)
    args = parser.parse_args(argv)
    build_app(args.mock).launch(server_name="127.0.0.1", server_port=args.port, share=False)


if __name__ == "__main__":
    main()
