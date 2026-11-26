"""SCRUM-36 : fiche HTML de correction d'un lot, ouverte localement dans un navigateur.

L'annotateur ou l'annotatrice corrige chaque brouillon (résumé, faits, hypothèses,
questions), marque l'exemple validé et télécharge `corrections_<lot>.jsonl`.
Les faits et hypothèses ne peuvent être choisis que parmi les valeurs du prompt v16.
"""
import argparse
import html
import json
import re

from volet_b.slm.check_lots import load
from volet_b.slm.make_lots import DRAFTS
from volet_b.slm.v16.runtime import INSTRUCTION


def section(prompt, title):
    """Texte d'une section du prompt v16, jusqu'à la suivante."""
    start = prompt.find(title)
    if start < 0:
        return ""
    body = prompt[start:].split("\n", 1)[1]
    end = re.search(r"\n\n[A-Z][A-Z ’'/]+[^\n]*:\n", body)
    return (body[:end.start()] if end else body).strip()


def allowed(prompt):
    """Formulations d'hypothèses autorisées par la section des causes."""
    return re.findall(r"autorise seulement : (.+)$", section(prompt, "CAUSES COMPATIBLES"), re.M)


def card(ex):
    """Carte HTML d'un exemple : preuves à gauche, réponse modifiable à droite."""
    p, e, i = ex["prompt"], ex["expected"], ex["id"]
    facts = re.findall(r"^\[F\d{2}\] .*$", p, re.M)
    esc = html.escape
    fact_boxes = "".join(
        f'<label class="opt"><input type="checkbox" data-f="{i}" value="{esc(f)}"{" checked" if f in e["faits_observes"] else ""}> {esc(f)}</label>'
        for f in facts)
    hyps = allowed(p)
    hyp_boxes = "".join(
        f'<label class="opt"><input type="checkbox" data-h="{i}" value="{esc(h)}"{" checked" if h in e["hypotheses"] else ""}> {esc(h)}</label>'
        for h in hyps) or '<p class="muted">Aucune hypothèse autorisée pour ce bloc : la liste reste vide.</p>'
    return f"""
<section class="card" id="{i}" data-id="{i}">
 <header><h2>{i}</h2><span class="meta">{ex['block_id']} · {ex['split']} · strate « {esc(ex['strate'])} » · {len(ex['trace_lines'])} lignes</span></header>
 <div class="grid">
  <div class="proofs">
   <h3>Preuves données au modèle</h3>
   <pre>{esc(section(p, 'COMPTEURS'))}</pre>
   <h4>Messages [Lxx]</h4><pre>{esc(section(p, 'MESSAGES A EXAMINER'))}</pre>
   <h4>Causes autorisées</h4><pre>{esc(section(p, 'CAUSES COMPATIBLES'))}</pre>
   <details><summary>Chronologie [Txx]</summary><pre>{esc(section(p, 'CHRONOLOGIE'))}</pre></details>
   <details><summary>Logs bruts</summary><pre>{esc(chr(10).join(ex['trace_lines']))}</pre></details>
  </div>
  <div class="answer">
   <h3>Réponse (modifiable)</h3>
   <label class="lab" for="r-{i}">Résumé (2–3 phrases, une référence par phrase)</label>
   <textarea id="r-{i}" data-r="{i}" rows="6">{esc(e['resume_evenements'])}</textarea>
   <h4>Faits observés (2 à 5)</h4><div class="opts">{fact_boxes}</div>
   <h4>Hypothèses (0 à 2, seulement si le message les justifie)</h4><div class="opts">{hyp_boxes}</div>
   <label class="lab" for="q-{i}">Infos manquantes (une question par ligne, 0 à 3)</label>
   <textarea id="q-{i}" data-q="{i}" rows="3">{esc(chr(10).join(e['infos_manquantes']))}</textarea>
   <p class="warn" id="w-{i}"></p>
   <div class="verdict">
    <label><input type="radio" name="v-{i}" value="ok" data-v="{i}"> Validé sans changement</label>
    <label><input type="radio" name="v-{i}" value="corrige" data-v="{i}"> Validé après correction</label>
    <label><input type="radio" name="v-{i}" value="rejet" data-v="{i}"> À retirer (exemple mauvais)</label>
   </div>
  </div>
 </div>
</section>"""


def main(argv=None):
    """Écrit fiche_<lot>.html à côté des brouillons."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lot", required=True)
    parser.add_argument("--annotateur", required=True, help="prénom en minuscules, ex. linda")
    args = parser.parse_args(argv)
    _, examples = load(args.lot)
    if any(not isinstance(ex.get("expected"), dict) for ex in examples):
        raise SystemExit("Lot incomplet : rédiger et contrôler les brouillons d'abord.")
    keys = ("resume_evenements", "faits_observes", "hypotheses", "infos_manquantes", "sources", "abstention")
    original = {ex["id"]: {k: ex["expected"][k] for k in keys} for ex in examples}
    nav = "".join(f'<a href="#{ex["id"]}" data-n="{ex["id"]}">{ex["id"].split("-")[1]}</a>' for ex in examples)
    rules = html.escape(INSTRUCTION)
    page = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Correction lot {args.lot}</title><style>
:root{{--bg:#f6f7f9;--card:#fff;--ink:#14181f;--muted:#5b6472;--line:#e2e5ea;--accent:#1f4fb8;--ok:#1f6f43;--fix:#9a3412;--code:#f3f4f6}}
@media (prefers-color-scheme:dark){{:root{{--bg:#141619;--card:#1d2024;--ink:#e8eaed;--muted:#a4abb6;--line:#30353c;--accent:#8fb3f5;--ok:#6cc392;--fix:#f0a37a;--code:#262a30}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,"Segoe UI",sans-serif}}
.top{{position:sticky;top:0;z-index:2;background:var(--bg);border-bottom:1px solid var(--line);padding:10px 16px;display:flex;flex-wrap:wrap;gap:12px;align-items:center}}
.top h1{{font-size:17px;margin:0;flex:1 1 240px}}button{{font:inherit;min-height:40px;padding:0 14px;border-radius:8px;border:1px solid var(--line);background:var(--card);color:var(--ink);cursor:pointer}}
button.primary{{background:var(--accent);border-color:var(--accent);color:#fff}}
main{{max-width:1300px;margin:0 auto;padding:16px}}.intro,.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 18px;margin-bottom:16px}}
.card{{scroll-margin-top:64px}}.card header{{display:flex;flex-wrap:wrap;gap:12px;align-items:baseline;border-bottom:1px solid var(--line);padding-bottom:6px}}
h2{{margin:0;font-size:18px}}h3{{font-size:15px;margin:12px 0 6px;color:var(--accent)}}h4{{font-size:13px;margin:10px 0 4px;color:var(--muted)}}
.meta,.muted{{color:var(--muted)}}.grid{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:20px}}@media (max-width:860px){{.grid{{grid-template-columns:1fr}}}}
pre{{background:var(--code);padding:8px;border-radius:6px;font-size:12px;white-space:pre-wrap;word-break:break-word;margin:0}}
textarea{{width:100%;font:inherit;font-size:14px;background:var(--bg);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:8px}}
.lab{{display:block;font-size:13px;font-weight:600;margin:10px 0 4px}}.opts{{display:flex;flex-direction:column;gap:4px}}
.opt{{font-size:13px;display:flex;gap:6px;align-items:flex-start}}.verdict{{display:flex;flex-wrap:wrap;gap:16px;margin-top:10px;font-size:14px}}
.warn{{color:var(--fix);font-size:13px;font-weight:600;margin:6px 0 0}}.nav{{display:flex;flex-wrap:wrap;gap:4px;margin-top:8px}}
.nav a{{text-decoration:none;color:var(--ink);background:var(--code);border-radius:4px;padding:1px 6px;font-size:12px}}.nav a.ok{{background:var(--ok);color:#fff}}.nav a.corrige{{background:var(--accent);color:#fff}}.nav a.rejet{{background:var(--fix);color:#fff}}
details summary{{cursor:pointer;color:var(--accent)}}
</style></head><body>
<div class="top"><h1>Correction du lot « {args.lot} » — annotation : {args.annotateur}</h1><span id="prog" class="muted"></span><button class="primary" id="dl">Télécharger mes corrections</button></div>
<main><div class="intro"><strong>Comment faire (≈ 2 min par exemple)</strong><ol>
<li>Lis les preuves à gauche, puis le brouillon à droite (préparé par IA).</li>
<li>Corrige ce qui est faux ou imprécis : rien d'inventé, pas d'ordre ni de cause non prouvés (« puis », « avant », « provoque »…), une référence [Fxx]/[Txx]/[Lxx] par phrase.</li>
<li>Choisis le verdict. « À retirer » si l'exemple ne peut pas être sauvé.</li>
<li>À la fin, « Télécharger mes corrections » et envoie le fichier à Claude, qui le contrôle automatiquement.</li></ol>
<p class="muted">Tes saisies restent dans ce navigateur (même ordinateur, même navigateur) : tu peux t'arrêter et reprendre.</p>
<details><summary>Règles complètes du format v16</summary><pre>{rules}</pre></details>
<div class="nav">{nav}</div></div>
{''.join(card(ex) for ex in examples)}
</main><script>
const LOT={json.dumps(args.lot)},WHO={json.dumps(args.annotateur)},ORIG={json.dumps(original, ensure_ascii=False)},KEY='scrum36-'+LOT;
let st={{}};try{{st=JSON.parse(localStorage.getItem(KEY)||'{{}}')}}catch(e){{}}
const save=()=>{{try{{localStorage.setItem(KEY,JSON.stringify(st))}}catch(e){{}}}};
const ids=Object.keys(ORIG);
function read(id){{
 const r=document.querySelector('[data-r="'+id+'"]').value.trim();
 const f=[...document.querySelectorAll('[data-f="'+id+'"]:checked')].map(x=>x.value);
 const h=[...document.querySelectorAll('[data-h="'+id+'"]:checked')].map(x=>x.value);
 const q=document.querySelector('[data-q="'+id+'"]').value.split('\\n').map(s=>s.trim()).filter(Boolean);
 return {{resume_evenements:r,faits_observes:f,hypotheses:h,infos_manquantes:q,sources:[],abstention:false}};
}}
const norm=a=>JSON.stringify([a.resume_evenements.trim(),[...a.faits_observes].sort(),[...a.hypotheses].sort(),a.infos_manquantes.map(x=>x.trim())]);
function warn(id){{const a=read(id),w=[];
 if(a.faits_observes.length<2||a.faits_observes.length>5)w.push('2 à 5 faits');
 if(a.hypotheses.length>2)w.push('2 hypothèses max');if(a.infos_manquantes.length>3)w.push('3 questions max');
 if(/\\b(puis|après|avant|ensuite|finalement|provoqu|génèr|entraîn|à cause)/i.test(a.resume_evenements+' '+a.infos_manquantes.join(' ')))w.push('mot de chronologie ou de cause');
 document.getElementById('w-'+id).textContent=w.length?'⚠ '+w.join(' · '):'';}}
function restore(){{ids.forEach(id=>{{const s=st[id];if(!s)return;
 if(s.a){{document.querySelector('[data-r="'+id+'"]').value=s.a.resume_evenements;document.querySelector('[data-q="'+id+'"]').value=s.a.infos_manquantes.join('\\n');
  document.querySelectorAll('[data-f="'+id+'"]').forEach(x=>x.checked=s.a.faits_observes.includes(x.value));
  document.querySelectorAll('[data-h="'+id+'"]').forEach(x=>x.checked=s.a.hypotheses.includes(x.value));}}
 if(s.v){{const r=document.querySelector('input[name="v-'+id+'"][value="'+s.v+'"]');if(r)r.checked=true;}}}});}}
function upd(){{let n=0;ids.forEach(id=>{{const v=(st[id]||{{}}).v;const a=document.querySelector('.nav a[data-n="'+id+'"]');a.className=v||'';if(v)n++;warn(id)}});
 document.getElementById('prog').textContent=n+' / '+ids.length+' traités';}}
document.querySelectorAll('.card').forEach(c=>{{const id=c.dataset.id;c.addEventListener('input',()=>{{st[id]=st[id]||{{}};st[id].a=read(id);
 const v=c.querySelector('input[name="v-'+id+'"]:checked');if(v)st[id].v=v.value;save();upd();}});}});
restore();upd();
document.getElementById('dl').onclick=()=>{{const lines=ids.map(id=>{{const a=read(id),v=(st[id]||{{}}).v||'';
 return JSON.stringify({{id,expected:a,verdict:v,modifie:norm(a)!==norm(ORIG[id]),annotator:WHO}});}});
 const b=new Blob([lines.join('\\n')+'\\n'],{{type:'application/json'}});const u=URL.createObjectURL(b);
 const l=document.createElement('a');l.href=u;l.download='corrections_'+LOT+'.jsonl';l.click();setTimeout(()=>URL.revokeObjectURL(u),2000);}};
</script></body></html>"""
    out = DRAFTS / f"fiche_{args.lot}.html"
    out.write_text(page, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
