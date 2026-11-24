"""SCRUM-48 : génère le PDF du rapport à partir de rapport_v1.md.

Usage, depuis la racine : python -m teamai.rapport_pdf [--out docs/rapport/TeamAI_Rapport_V1.pdf]

Le Markdown est converti en HTML (paquet `markdown`), puis imprimé en PDF par
Microsoft Edge ou Chrome sans interface. Les liens relatifs vers le dépôt sont
réécrits vers GitHub (branche dev) pour rester cliquables dans le PDF.
"""
import argparse
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import markdown

from teamai.paths import RAPPORT as HERE, ROOT, resolve_path

REPO_URL = "https://github.com/LindaBOUKHIT/TeamAI/blob/dev/"

BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "msedge", "google-chrome", "chromium", "chrome",
]

CSS = """
@page { size: A4; margin: 22mm 20mm 20mm 20mm;
  @bottom-center { content: counter(page) " / " counter(pages); font: 9pt system-ui, sans-serif; color: #667; } }
@page :first { @bottom-center { content: none; } }
html { font: 10.5pt/1.5 "Segoe UI", system-ui, sans-serif; color: #111827; }
body { margin: 0; }
.cover { height: 240mm; display: flex; flex-direction: column; justify-content: center; break-after: page; }
.cover h1 { font-size: 30pt; line-height: 1.1; margin: 0 0 8mm; color: #1e3a8a; letter-spacing: -0.02em; }
.cover .subtitle { font-size: 15pt; margin: 0 0 18mm; color: #374151; }
.cover p { margin: 2mm 0; font-size: 11pt; }
.cover .status { margin-top: 18mm; padding: 4mm 5mm; border-left: 3px solid #1e3a8a; background: #f1f5ff; font-size: 9.5pt; }
h2 { font-size: 17pt; color: #1e3a8a; margin: 0 0 4mm; padding-bottom: 2mm; border-bottom: 1.5px solid #c7d2fe; break-before: page; }
h3 { font-size: 13pt; color: #1f2937; margin: 7mm 0 2mm; break-after: avoid; }
h4 { font-size: 11pt; color: #1f2937; margin: 5mm 0 1.5mm; break-after: avoid; }
p, li { text-align: left; orphans: 3; widows: 3; }
a { color: #1d4ed8; text-decoration: none; }
code { font: 8.8pt Consolas, "Cascadia Mono", monospace; background: #f3f4f6; padding: 0 2px; border-radius: 3px; overflow-wrap: anywhere; }
table { width: 100%; border-collapse: collapse; margin: 3mm 0 4mm; font-size: 9pt; break-inside: auto; }
tr { break-inside: avoid; }
th, td { border: 0.6px solid #d1d5db; padding: 1.6mm 2mm; vertical-align: top; text-align: left; }
th { background: #eef2ff; }
td { overflow-wrap: anywhere; }
img { display: block; max-width: 95mm; margin: 4mm auto; }
blockquote { margin: 3mm 0; padding: 2mm 4mm; border-left: 3px solid #c7d2fe; color: #374151; background: #f8fafc; }
.toc { break-after: page; }
.toc h2 { break-before: auto; }
.toc ul { list-style: none; padding-left: 0; }
.toc ul ul { padding-left: 6mm; }
.toc li { text-align: left; margin: 1mm 0; }
"""


def find_browser():
    """Renvoie le premier navigateur Chromium disponible pour imprimer le PDF."""
    for candidate in BROWSERS:
        path = shutil.which(candidate) or (candidate if os.path.exists(candidate) else None)
        if path:
            return path
    raise SystemExit("Edge ou Chrome introuvable : impossible d'imprimer le PDF.")


def rewrite_links(html):
    """Liens relatifs vers le dépôt -> GitHub ; les images restent locales."""
    def repl(match):
        """Réécrit un lien relatif s'il désigne un fichier du dépôt."""
        href = match.group(1)
        if re.match(r"^(https?:|mailto:|#)", href):
            return match.group(0)
        target = (HERE / href.split("#", 1)[0]).resolve()
        try:
            rel = target.relative_to(ROOT).as_posix()
        except ValueError:
            return match.group(0)
        anchor = "#" + href.split("#", 1)[1] if "#" in href else ""
        return f'href="{REPO_URL}{rel}{anchor}"'
    return re.sub(r'href="([^"]+)"', repl, html)


def split_cover(text):
    """Les lignes avant le premier titre de niveau 2 forment la page de garde."""
    head, _, body = text.partition("\n## ")
    lines = [line.strip() for line in head.splitlines() if line.strip()]
    title = lines[0].lstrip("# ").strip()
    rest = lines[1:]
    # Espaces insécables : « NLP 2 » ne doit pas se couper.
    cover = [f"<h1>{title.replace(' 2', '&nbsp;2')}</h1>"]
    if rest:
        cover.append(f'<p class="subtitle">{rest[0]}</p>')
    status = []
    for line in rest[1:]:
        html = markdown.markdown(line)
        if line.startswith("**Version") or line.startswith("Master") or "·" in line:
            cover.append(html)
        else:
            status.append(html)
    if status:
        cover.append('<div class="status">' + "".join(status) + "</div>")
    return '<section class="cover">' + "".join(cover) + "</section>", "## " + body


def build(out):
    """Convertit rapport_v1.md en PDF à l'emplacement out."""
    text = (HERE / "rapport_v1.md").read_text(encoding="utf-8")
    cover, body = split_cover(text)
    md = markdown.Markdown(extensions=["tables", "toc", "sane_lists", "attr_list"],
                           extension_configs={"toc": {"toc_depth": "2-3"}})
    content = md.convert(body)
    toc = f'<section class="toc"><h2>Sommaire</h2>{md.toc}</section>'
    html = (
        '<!doctype html><html lang="fr"><head><meta charset="utf-8">'
        f"<title>TeamAI — Rapport V1</title><style>{CSS}</style></head><body>"
        f"{cover}{toc}{rewrite_links(content)}</body></html>"
    )
    # Le fichier HTML est écrit à côté du Markdown pour que les images relatives se chargent.
    with tempfile.NamedTemporaryFile("w", suffix=".html", dir=HERE, delete=False, encoding="utf-8") as tmp:
        tmp.write(html)
        source = Path(tmp.name)
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([find_browser(), "--headless", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={out.as_posix()}", source.as_uri()],
                       check=True, capture_output=True, timeout=120)
    finally:
        source.unlink(missing_ok=True)
    if not out.exists() or out.stat().st_size == 0:
        raise SystemExit("Le navigateur n'a pas produit de PDF.")
    print(f"PDF : {out} ({out.stat().st_size} octets)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=HERE / "TeamAI_Rapport_V1.pdf")
    build(resolve_path(parser.parse_args().out))
