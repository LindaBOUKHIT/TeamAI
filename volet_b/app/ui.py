"""Identité visuelle de la démo « Vigie » : thème, styles, pictogrammes et contenus statiques de l'interface.

Chaque chiffre affiché ici renvoie à une mesure ou à un fichier du dépôt ; aucune qualité non mesurée
n'est annoncée. Les pictogrammes sont des SVG au trait (couleur du texte), jamais des émojis.
Le texte reste lisible en thème clair comme en thème sombre ; la page occupe toute la largeur.
"""
from urllib.parse import quote

from teamai.paths import APP_ASSETS as ASSETS

AVATARS = (str(ASSETS / "utilisateur.svg"), str(ASSETS / "vigie.svg"))
FONT = ["Inter", "Segoe UI", "system-ui", "sans-serif"]
MONO = ["JetBrains Mono", "Cascadia Code", "Consolas", "monospace"]

# Tracés 24 × 24 au trait, dessinés pour l'interface.
ICONS = {
    "lock": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    "link": '<path d="M10 13a5 5 0 0 0 7.07 0l3-3a5 5 0 0 0-7.07-7.07l-1.5 1.5"/>'
            '<path d="M14 11a5 5 0 0 0-7.07 0l-3 3a5 5 0 0 0 7.07 7.07l1.5-1.5"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>',
    "message": '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/>',
    "flow": '<rect x="3" y="4" width="6" height="6" rx="1.5"/><rect x="15" y="14" width="6" height="6" rx="1.5"/>'
            '<path d="M9 7h4a2 2 0 0 1 2 2v5"/>',
    "book": '<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/><path d="M8 7h7"/>',
    "compass": '<circle cx="12" cy="12" r="9"/><path d="M15.5 8.5l-2 5-5 2 2-5z"/>',
    "alert": '<path d="M12 3l10 18H2z"/><path d="M12 10v4"/><path d="M12 17.5v.01"/>',
    "check": '<circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/>',
    "layers": '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/>',
    "sliders": '<path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12"/><circle cx="16" cy="6" r="2"/>'
               '<circle cx="10" cy="12" r="2"/><circle cx="18" cy="18" r="2"/>',
    "reset": '<path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v5h5"/>',
    "send": '<path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4z"/>',
}


def icon(name, cls="vg-ic"):
    """Pictogramme SVG en ligne, à la couleur du texte qui l'entoure."""
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


def mask(name):
    """URL de données du pictogramme, pour un masque CSS sur les composants Gradio sans HTML."""
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="black" '
           f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>')
    return f'url("data:image/svg+xml,{quote(svg)}")'


LOGO = """<svg class="vg-logo" viewBox="0 0 64 64" aria-hidden="true">
<defs><linearGradient id="vg-beam" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#F5A524" stop-opacity=".95"/>
<stop offset="1" stop-color="#F5A524" stop-opacity="0"/></linearGradient></defs>
<rect width="64" height="64" rx="16" fill="#0B1F33"/><path d="M30 22 L62 10 L62 34 Z" fill="url(#vg-beam)"/>
<path d="M10 32 C18 20 42 20 50 32 C42 44 18 44 10 32 Z" fill="none" stroke="#E2E8F0" stroke-width="3"/>
<circle cx="30" cy="32" r="7.5" fill="#F5A524"/><circle cx="30" cy="32" r="3" fill="#0B1F33"/>
<path d="M8 50 H56" stroke="#14B8A6" stroke-width="3" stroke-linecap="round" stroke-dasharray="2 5"/></svg>"""

# Mesures et faits du dépôt : SCRUM-61 (mémoire T4), corpus SCRUM-30 (51 passages), templates Loghub E1–E29.
HEADER = f"""
<header class="vg-hero">
  <div class="vg-hero-grid" aria-hidden="true"></div>
  <div class="vg-hero-main">
    <div class="vg-brand">{LOGO}<div><div class="vg-name">Vigie</div>
      <div class="vg-kicker">L'assistant qui lit vos logs HDFS</div></div></div>
    <h1 class="vg-title">Ce qui est arrivé à chaque bloc, <span>preuves à l'appui.</span></h1>
    <p class="vg-lead">Collez vos logs : Vigie reconstitue la vie de chaque bloc, signale ce qui sort de l'ordinaire
    et cite les lignes qui le prouvent. Quand les logs ne disent pas la cause, elle le dit au lieu de l'inventer.</p>
    <div class="vg-pills">
      <span class="vg-pill">{icon("lock")}100 % local, rien ne quitte la machine</span>
      <span class="vg-pill">{icon("link")}Chaque fait renvoie à une ligne de log</span>
      <span class="vg-pill">{icon("shield")}S'abstient plutôt que d'inventer</span>
    </div>
  </div>
  <div class="vg-stats">
    <div><b>Gemma 4 E4B</b><small>modèle ouvert, quantifié 4 bits</small></div>
    <div><b>≈ 4,3 Gio</b><small>mémoire GPU mesurée</small></div>
    <div><b>29</b><small>types d'événements HDFS reconnus</small></div>
    <div><b>51</b><small>passages de doc Apache indexés</small></div>
  </div>
</header>
"""

RESULT_EMPTY = """### Prêt à analyser

Collez des lignes de logs HDFS à gauche, ou chargez un exemple, puis lancez l'analyse.

Pour chaque bloc `blk_…` (5 au maximum), Vigie rend :
- un **résumé** de la vie du bloc ;
- les **faits observés**, chacun relié à ses lignes ;
- les **hypothèses**, seulement quand une ligne de log les appuie ;
- les **questions à vérifier** sur le cluster."""

CHAT_PLACEHOLDER = f"""<div class="vg-chat-empty">
{icon("message", "vg-ic vg-ic-xl")}
<h3>Demandez à la documentation HDFS</h3>
<p>Fonctionnement du NameNode, réplication, heartbeats, signification d'un événement Exx…<br>
Chaque réponse cite ses passages, ou dit honnêtement que la doc ne couvre pas la question.</p>
</div>"""

COVERAGE = f"""<div class="vg-side">
<h4>{icon("book")}Ce que Vigie a lu</h4>
<ul><li>HDFS Architecture Guide (Apache, 1.2.1)</li><li>HDFS Users Guide (Apache, 1.2.1)</li>
<li>Les 29 formats de messages Loghub (E1 à E29)</li></ul>
<h4>{icon("compass")}Ce que la doc ne dit pas</h4>
<p>Elle décrit le fonctionnement de HDFS, pas la cause de chaque exception : pour 19 types d'événements
sur 29, aucun passage ne s'applique. Vigie s'abstient alors.</p>
<p class="vg-note">Démonstration : la qualité de cet onglet n'a pas été mesurée.</p>
</div>"""

HOW_IT_WORKS = f"""
<section class="vg-how">
  <h2>Le code établit les faits, le modèle les raconte, le contrôle vérifie.</h2>
  <ol class="vg-steps">
    <li><span>1</span><b>Lecture</b><p>Chaque ligne est rattachée à son bloc et à l'un des 29 événements HDFS.</p></li>
    <li><span>2</span><b>Faits vérifiés</b><p>Le code compte, date et numérote les faits [Fxx] et les lignes [Lxx].</p></li>
    <li><span>3</span><b>Rédaction</b><p>Gemma 4, en local, rédige le rapport dans un schéma JSON fermé.</p></li>
    <li><span>4</span><b>Contrôle</b><p>Références, sources et hypothèses sont vérifiées ; une seule reprise permise.</p></li>
    <li><span>5</span><b>Rapport</b><p>Résumé, faits, hypothèses appuyées et questions à vérifier sur le cluster.</p></li>
  </ol>
  <div class="vg-cards">
    <div class="vg-card"><h3>{icon("shield")}Garde-fous</h3><ul>
      <li>Hypothèses permises seulement quand une ligne de log énonce la cause.</li>
      <li>Sources limitées aux passages réellement fournis au modèle.</li>
      <li>Les blocs du jeu de test sont refusés avant tout appel au modèle.</li></ul></div>
    <div class="vg-card"><h3>{icon("layers")}Deux architectures</h3><ul>
      <li><b>1 agent</b> : un seul appel rédige le rapport.</li>
      <li><b>3 agents</b> : recherche documentaire, rédaction, puis contrôle.</li>
      <li><b>Adapté</b> : le même modèle avec un adaptateur LoRA appris sur nos exemples annotés.</li></ul></div>
    <div class="vg-card vg-card-warn"><h3>{icon("alert")}Limites assumées</h3><ul>
      <li>Une explication générée peut être fausse : vérifiez les lignes citées.</li>
      <li>Le jeu HDFS_v1 dit si un bloc est anormal, jamais pourquoi : la cause racine reste à établir.</li>
      <li>L'onglet de questions est une démonstration : sa qualité n'est pas mesurée.</li></ul></div>
  </div>
</section>
"""

FOOTER = """<div class="vg-footer">Vigie · projet TeamAI, M2 IA · démonstration locale.
Les explications sont générées et peuvent être fausses : vérifiez les lignes citées.</div>"""

CSS = """
.gradio-container { max-width: none !important; width: 100% !important; padding: 18px 28px 8px !important; }
.vg-ic { width: 16px; height: 16px; flex: none; vertical-align: -3px; margin-right: 7px; }
.vg-ic-xl { width: 40px; height: 40px; margin: 0 auto; display: block; color: #F5A524; }

.vg-hero { position: relative; overflow: hidden; border-radius: 22px; padding: 26px 32px;
  display: grid; grid-template-columns: minmax(0, 1.55fr) minmax(320px, 1fr); gap: 28px; align-items: center;
  background: radial-gradient(1200px 420px at 80% -20%, rgba(245,165,36,.26), transparent 60%),
              linear-gradient(135deg, #0B1F33 0%, #12355B 60%, #0E4A5A 100%);
  color: #E2E8F0; box-shadow: 0 18px 50px -24px rgba(11,31,51,.75); }
.vg-hero-grid { position: absolute; inset: 0; opacity: .12; pointer-events: none;
  background-image: repeating-linear-gradient(0deg, #94A3B8 0 1px, transparent 1px 26px),
                    repeating-linear-gradient(90deg, #94A3B8 0 1px, transparent 1px 26px);
  mask-image: linear-gradient(90deg, transparent, #000 40%, #000); }
.vg-hero-main, .vg-stats { position: relative; }
.vg-brand { display: flex; align-items: center; gap: 12px; }
.vg-logo { width: 44px; height: 44px; filter: drop-shadow(0 6px 14px rgba(245,165,36,.35)); }
.vg-name { font-size: 22px; font-weight: 800; letter-spacing: .5px; color: #fff; }
.vg-kicker { font-size: 13px; color: #F5A524; font-weight: 600; letter-spacing: .3px; }
.vg-title { margin: 16px 0 8px !important; font-size: clamp(26px, 3vw, 40px) !important;
  line-height: 1.12 !important; font-weight: 800 !important; color: #fff !important; }
.vg-title span { background: linear-gradient(90deg, #F5A524, #FDE68A); -webkit-background-clip: text;
  background-clip: text; color: transparent; }
.vg-lead { max-width: 860px; font-size: 16px; line-height: 1.55; color: #CBD5E1; margin: 0; }
.vg-pills { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }
.vg-pill { display: inline-flex; align-items: center; font-size: 13px; padding: 6px 12px; border-radius: 999px;
  background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.16); color: #E2E8F0; }
.vg-pill .vg-ic { color: #F5A524; }
.vg-stats { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 10px; }
.vg-stats div { padding: 14px 16px; border-radius: 14px; background: rgba(2,6,23,.35);
  border: 1px solid rgba(148,163,184,.18); }
.vg-stats b { display: block; font-size: 22px; color: #fff; }
.vg-stats small { color: #94A3B8; font-size: 12.5px; }
@media (max-width: 980px) { .vg-hero { grid-template-columns: 1fr; padding: 22px 20px; } }

.vg-tabs button[role="tab"] { font-weight: 700 !important; font-size: 15px !important; display: inline-flex !important;
  align-items: center; }
.vg-tabs button[role="tab"]::before, .vg-mask::before, .vg-settings > button::before {
  content: ""; width: 16px; height: 16px; margin-right: 8px; flex: none; background-color: currentColor;
  -webkit-mask: var(--vg-icon) center / contain no-repeat; mask: var(--vg-icon) center / contain no-repeat; }
.vg-tabs button[role="tab"]:nth-of-type(1) { --vg-icon: ICON_search; }
.vg-tabs button[role="tab"]:nth-of-type(2) { --vg-icon: ICON_message; }
.vg-tabs button[role="tab"]:nth-of-type(3) { --vg-icon: ICON_flow; }
.vg-settings > button { display: flex !important; align-items: center; --vg-icon: ICON_sliders; }
.vg-settings > button > span:first-of-type { flex: 1; text-align: left; font-weight: 700; }
.vg-mask { display: inline-flex !important; align-items: center; justify-content: center; }
.vg-i-alert { --vg-icon: ICON_alert; } .vg-i-check { --vg-icon: ICON_check; }
.vg-i-reset { --vg-icon: ICON_reset; } .vg-i-send { --vg-icon: ICON_send; }
.vg-chip { border-radius: 999px !important; font-weight: 600 !important; }
.vg-cta { font-size: 16px !important; font-weight: 800 !important; min-height: 48px !important;
  box-shadow: 0 10px 24px -12px rgba(249,115,22,.8) !important; }
.vg-logs textarea { font-family: "JetBrains Mono", "Cascadia Code", Consolas, monospace !important;
  font-size: 12.5px !important; line-height: 1.5 !important; }

.vg-panel { border-radius: 18px !important; }
.vg-result { min-height: 560px; }
.vg-result h2 { margin-top: 6px !important; padding: 10px 14px; border-radius: 12px;
  border-left: 5px solid #F5A524; background: var(--block-background-fill); font-size: 18px !important; }
.vg-result h3 { text-transform: uppercase; letter-spacing: .08em; font-size: 12.5px !important;
  color: #0E9F8E !important; margin: 18px 0 6px !important; }
.vg-result table { font-size: 13px; }
.vg-result pre { max-height: 300px; overflow: auto; }

.vg-chat-empty { text-align: center; padding: 40px 18px; }
.vg-chat-empty h3 { margin: 12px 0 6px; font-size: 20px; font-weight: 800; }
.vg-chat-empty p { opacity: .8; line-height: 1.5; }
.vg-side { padding: 4px 6px; font-size: 14px; line-height: 1.5; }
.vg-side h4 { display: flex; align-items: center; margin: 12px 0 6px; font-size: 14px; font-weight: 800; }
.vg-side h4 .vg-ic { color: #0E9F8E; }
.vg-side ul { margin: 0 0 6px 18px; }
.vg-note { font-size: 12.5px; opacity: .7; }

.vg-how h2 { font-size: 22px; font-weight: 800; margin: 6px 0 18px; }
.vg-steps { list-style: none; padding: 0; margin: 0 0 18px; display: grid; gap: 12px;
  grid-template-columns: repeat(5, minmax(0,1fr)); }
.vg-steps li { padding: 16px 16px 14px; border-radius: 16px;
  border: 1px solid var(--border-color-primary); background: var(--block-background-fill); }
.vg-steps li span { display: inline-grid; place-items: center; width: 28px; height: 28px; border-radius: 50%;
  background: linear-gradient(135deg, #F5A524, #F97316); color: #0B1F33; font-weight: 800; margin-bottom: 8px; }
.vg-steps b { display: block; font-size: 15px; margin-bottom: 4px; }
.vg-steps p { margin: 0; font-size: 13.5px; opacity: .82; line-height: 1.45; }
.vg-cards { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 12px; }
.vg-card { padding: 16px 18px; border-radius: 16px; border: 1px solid var(--border-color-primary);
  background: var(--block-background-fill); }
.vg-card h3 { display: flex; align-items: center; margin: 0 0 8px; font-size: 16px; font-weight: 800; }
.vg-card h3 .vg-ic { color: #F5A524; }
.vg-card ul { margin: 0 0 0 18px; font-size: 13.5px; line-height: 1.5; }
.vg-card-warn { border-color: rgba(245,165,36,.55); }
@media (max-width: 900px) { .vg-steps { grid-template-columns: 1fr 1fr; } .vg-cards { grid-template-columns: 1fr; } }

.vg-footer { text-align: center; font-size: 12.5px; opacity: .7; padding: 18px 0 6px; }
footer { display: none !important; }
"""
for _name in ICONS:
    CSS = CSS.replace(f"ICON_{_name};", f"{mask(_name)};")


def theme():
    """Thème Gradio de la marque : marine profond, faisceau ambre, accent sarcelle."""
    import gradio as gr

    return gr.themes.Soft(primary_hue="amber", secondary_hue="teal", neutral_hue="slate",
                          radius_size="lg", font=[gr.themes.Font(f) for f in FONT],
                          font_mono=[gr.themes.Font(f) for f in MONO]).set(
        button_primary_background_fill="linear-gradient(90deg, #F5A524, #F97316)",
        button_primary_background_fill_hover="linear-gradient(90deg, #F7B84B, #FB8A3C)",
        button_primary_text_color="#0B1F33",
        button_primary_border_color="transparent",
        block_radius="18px",
    )
