"""Identité visuelle de la démo « Vigie » : thème, styles et contenus statiques de l'interface.

Chaque chiffre affiché ici renvoie à une mesure ou à un fichier du dépôt ; aucune qualité non mesurée
n'est annoncée. Le texte reste lisible en thème clair comme en thème sombre.
"""
from teamai.paths import APP_ASSETS as ASSETS

AVATARS = (str(ASSETS / "utilisateur.svg"), str(ASSETS / "vigie.svg"))
FONT = ["Inter", "Segoe UI", "system-ui", "sans-serif"]
MONO = ["JetBrains Mono", "Cascadia Code", "Consolas", "monospace"]

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
  <div class="vg-brand">{LOGO}<div><div class="vg-name">Vigie</div>
    <div class="vg-kicker">L'assistant qui lit vos logs HDFS</div></div></div>
  <h1 class="vg-title">Ce qui est arrivé à chaque bloc,<br><span>preuves à l'appui.</span></h1>
  <p class="vg-lead">Collez vos logs : Vigie reconstitue la vie de chaque bloc, signale ce qui sort de l'ordinaire
  et cite les lignes qui le prouvent. Quand les logs ne disent pas la cause, elle le dit au lieu de l'inventer.</p>
  <div class="vg-pills">
    <span class="vg-pill">🔒 100 % local, rien ne quitte la machine</span>
    <span class="vg-pill">📎 Chaque fait renvoie à une ligne de log</span>
    <span class="vg-pill">🛑 S'abstient plutôt que d'inventer</span>
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

CHAT_PLACEHOLDER = """<div class="vg-chat-empty">
<div class="vg-chat-icon">💬</div>
<h3>Demandez à la documentation HDFS</h3>
<p>Fonctionnement du NameNode, réplication, heartbeats, signification d'un événement Exx…<br>
Chaque réponse cite ses passages, ou dit honnêtement que la doc ne couvre pas la question.</p>
</div>"""

COVERAGE = """<div class="vg-side">
<h4>📚 Ce que Vigie a lu</h4>
<ul><li>HDFS Architecture Guide (Apache, 1.2.1)</li><li>HDFS Users Guide (Apache, 1.2.1)</li>
<li>Les 29 formats de messages Loghub (E1 à E29)</li></ul>
<h4>🧭 Ce que la doc ne dit pas</h4>
<p>Elle décrit le fonctionnement de HDFS, pas la cause de chaque exception : pour 19 types d'événements
sur 29, aucun passage ne s'applique. Vigie s'abstient alors.</p>
<p class="vg-note">Démonstration : la qualité de cet onglet n'a pas été mesurée.</p>
</div>"""

HOW_IT_WORKS = """
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
    <div class="vg-card"><h3>🧱 Garde-fous</h3><ul>
      <li>Hypothèses permises seulement quand une ligne de log énonce la cause.</li>
      <li>Sources limitées aux passages réellement fournis au modèle.</li>
      <li>Les blocs du jeu de test sont refusés avant tout appel au modèle.</li></ul></div>
    <div class="vg-card"><h3>🤝 Deux modes</h3><ul>
      <li><b>1 agent</b> : un seul appel rédige le rapport.</li>
      <li><b>3 agents</b> : recherche documentaire, rédaction, puis contrôle.</li>
      <li><b>Adapté</b> : le même modèle avec un adaptateur LoRA appris sur nos exemples annotés.</li></ul></div>
    <div class="vg-card vg-card-warn"><h3>⚠️ Limites assumées</h3><ul>
      <li>Une explication générée peut être fausse : vérifiez les lignes citées.</li>
      <li>Le jeu HDFS_v1 dit si un bloc est anormal, jamais pourquoi : la cause racine reste à établir.</li>
      <li>L'onglet de questions est une démonstration : sa qualité n'est pas mesurée.</li></ul></div>
  </div>
</section>
"""

FOOTER = """<div class="vg-footer">Vigie · projet TeamAI, M2 IA · démonstration locale.
Les explications sont générées et peuvent être fausses : vérifiez les lignes citées.</div>"""

CSS = """
.gradio-container { max-width: 1180px !important; margin: 0 auto !important; }
.vg-hero { position: relative; overflow: hidden; border-radius: 22px; padding: 34px 36px 26px;
  background: radial-gradient(1200px 400px at 85% -10%, rgba(245,165,36,.28), transparent 60%),
              linear-gradient(135deg, #0B1F33 0%, #12355B 60%, #0E4A5A 100%);
  color: #E2E8F0; box-shadow: 0 18px 50px -24px rgba(11,31,51,.75); }
.vg-hero-grid { position: absolute; inset: 0; opacity: .12; pointer-events: none;
  background-image: repeating-linear-gradient(0deg, #94A3B8 0 1px, transparent 1px 26px),
                    repeating-linear-gradient(90deg, #94A3B8 0 1px, transparent 1px 26px);
  mask-image: linear-gradient(90deg, transparent, #000 40%, #000); }
.vg-brand { display: flex; align-items: center; gap: 12px; position: relative; }
.vg-logo { width: 46px; height: 46px; filter: drop-shadow(0 6px 14px rgba(245,165,36,.35)); }
.vg-name { font-size: 22px; font-weight: 800; letter-spacing: .5px; color: #fff; }
.vg-kicker { font-size: 13px; color: #F5A524; font-weight: 600; letter-spacing: .3px; }
.vg-title { position: relative; margin: 20px 0 8px !important; font-size: clamp(26px, 4vw, 40px) !important;
  line-height: 1.12 !important; font-weight: 800 !important; color: #fff !important; }
.vg-title span { background: linear-gradient(90deg, #F5A524, #FDE68A); -webkit-background-clip: text;
  background-clip: text; color: transparent; }
.vg-lead { position: relative; max-width: 720px; font-size: 16px; line-height: 1.55; color: #CBD5E1; margin: 0; }
.vg-pills { position: relative; display: flex; flex-wrap: wrap; gap: 8px; margin: 18px 0 22px; }
.vg-pill { font-size: 13px; padding: 6px 12px; border-radius: 999px; background: rgba(255,255,255,.08);
  border: 1px solid rgba(255,255,255,.16); color: #E2E8F0; backdrop-filter: blur(4px); }
.vg-stats { position: relative; display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 10px; }
.vg-stats div { padding: 12px 14px; border-radius: 14px; background: rgba(2,6,23,.35);
  border: 1px solid rgba(148,163,184,.18); }
.vg-stats b { display: block; font-size: 20px; color: #fff; }
.vg-stats small { color: #94A3B8; font-size: 12px; }
@media (max-width: 760px) { .vg-hero { padding: 24px 20px; } .vg-stats { grid-template-columns: repeat(2, minmax(0,1fr)); } }

.vg-tabs > .tab-wrapper button, .vg-tabs button[role="tab"] { font-weight: 700 !important; font-size: 15px !important; }
.vg-panel { border-radius: 18px !important; }
.vg-logs textarea { font-family: "JetBrains Mono", "Cascadia Code", Consolas, monospace !important;
  font-size: 12.5px !important; line-height: 1.5 !important; }
.vg-chip { border-radius: 999px !important; font-weight: 600 !important; }
.vg-cta { font-size: 16px !important; font-weight: 800 !important; min-height: 48px !important;
  box-shadow: 0 10px 24px -12px rgba(249,115,22,.8) !important; }

.vg-result { min-height: 420px; }
.vg-result h2 { margin-top: 6px !important; padding: 10px 14px; border-radius: 12px;
  border-left: 5px solid #F5A524; background: var(--block-background-fill); font-size: 18px !important; }
.vg-result h3 { text-transform: uppercase; letter-spacing: .08em; font-size: 12.5px !important;
  color: #0E9F8E !important; margin: 18px 0 6px !important; }
.vg-result table { font-size: 13px; }
.vg-result pre { max-height: 260px; overflow: auto; }

.vg-chat-empty { text-align: center; padding: 36px 18px; }
.vg-chat-icon { font-size: 38px; }
.vg-chat-empty h3 { margin: 8px 0 6px; font-size: 20px; font-weight: 800; }
.vg-chat-empty p { opacity: .8; line-height: 1.5; }
.vg-side { padding: 4px 6px; font-size: 14px; line-height: 1.5; }
.vg-side h4 { margin: 10px 0 6px; font-size: 14px; font-weight: 800; }
.vg-side ul { margin: 0 0 6px 18px; }
.vg-note { font-size: 12.5px; opacity: .7; }

.vg-how h2 { font-size: 22px; font-weight: 800; margin: 6px 0 18px; }
.vg-steps { list-style: none; padding: 0; margin: 0 0 18px; display: grid; gap: 10px;
  grid-template-columns: repeat(5, minmax(0,1fr)); counter-reset: none; }
.vg-steps li { position: relative; padding: 16px 14px 14px; border-radius: 16px;
  border: 1px solid var(--border-color-primary); background: var(--block-background-fill); }
.vg-steps li span { display: inline-grid; place-items: center; width: 28px; height: 28px; border-radius: 50%;
  background: linear-gradient(135deg, #F5A524, #F97316); color: #0B1F33; font-weight: 800; margin-bottom: 8px; }
.vg-steps b { display: block; font-size: 15px; margin-bottom: 4px; }
.vg-steps p { margin: 0; font-size: 13px; opacity: .82; line-height: 1.45; }
.vg-cards { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 12px; }
.vg-card { padding: 16px 18px; border-radius: 16px; border: 1px solid var(--border-color-primary);
  background: var(--block-background-fill); }
.vg-card h3 { margin: 0 0 8px; font-size: 16px; font-weight: 800; }
.vg-card ul { margin: 0 0 0 18px; font-size: 13.5px; line-height: 1.5; }
.vg-card-warn { border-color: rgba(245,165,36,.55); }
@media (max-width: 900px) { .vg-steps { grid-template-columns: 1fr 1fr; } .vg-cards { grid-template-columns: 1fr; } }

.vg-footer { text-align: center; font-size: 12.5px; opacity: .7; padding: 18px 0 6px; }
footer { display: none !important; }
"""


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
