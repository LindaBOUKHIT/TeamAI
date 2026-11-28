"""SCRUM-69 : assemble le rapport final (docs/rapport/final/sections/*.html), calcule le sommaire paginé
et produit docs/rapport/TeamAI_Rapport.pdf.

Usage, depuis la racine : python -m teamai.rapport_final [--edge CHEMIN]

Deux passes : la première imprime le document pour repérer la page de chaque titre, la seconde
réimprime avec les numéros de page dans le sommaire. Un commentaire <!--SVG:fichier.svg--> dans une
section est remplacé par le contenu du fichier SVG du même dossier. Nécessite PyMuPDF et Microsoft Edge.
"""
import argparse
import html
import re
import subprocess

import fitz  # PyMuPDF

from teamai.paths import RAPPORT, RAPPORT_FINAL

OUT_HTML = RAPPORT_FINAL / "index.html"
OUT_PDF = RAPPORT / "TeamAI_Rapport.pdf"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

HEAD = """<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<title>TeamAI — Rapport de projet NLP 2</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Young+Serif&family=Figtree:ital,wght@0,400;0,500;0,700;1,400&family=Kalam:wght@400;700&family=Courier+Prime&display=block" rel="stylesheet">
<link rel="stylesheet" href="style.css">
</head><body>
"""
HEADING = re.compile(r"<(h1|h2)([^>]*)>(.*?)</\1>", re.S)


def plain(fragment: str) -> str:
    """Texte brut d'un titre, sans son numéro ni ses badges."""
    text = re.sub(r'<span class="(?:n|verdict[^"]*)">.*?</span>', "", fragment)
    text = re.sub(r"<br\s*/?>", " ", text)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", "", text)).split())


def number_of(fragment: str) -> str:
    """Numéro de section porté par le titre, ou chaîne vide."""
    match = re.search(r'<span class="n">(.*?)</span>', fragment)
    return match.group(1) if match else ""


def sections() -> str:
    """Contenu des sections, concaténées dans l'ordre de leur nom de fichier."""
    files = sorted((RAPPORT_FINAL / "sections").glob("*.html"))
    return "\n".join(p.read_text(encoding="utf-8") for p in files)


def collect(body: str) -> list[dict]:
    """Entrées du sommaire : titres h1 et h2, sauf ceux marqués data-toc="no"."""
    entries = []
    for tag, attrs, inner in HEADING.findall(body):
        if 'data-toc="no"' in attrs:
            continue
        entries.append({"level": 1 if tag == "h1" else 2, "title": plain(inner), "num": number_of(inner)})
    return entries


def toc_html(entries: list[dict], pages: list[int] | None) -> str:
    """Liste HTML du sommaire, avec les numéros de page s'ils sont connus."""
    rows = []
    for i, entry in enumerate(entries):
        page = str(pages[i]) if pages and pages[i] else ""
        num = html.escape(entry["num"])
        rows.append(f'<li class="l{entry["level"]}"><span class="n">{num}</span><span>{html.escape(entry["title"])}</span>'
                    f'<span class="dots"></span><span class="p">{page}</span></li>')
    return '<ol class="toc">' + "\n".join(rows) + "</ol>"


def assemble(entries: list[dict], pages: list[int] | None) -> str:
    """Document HTML complet : sections, sommaire et schémas SVG insérés."""
    body = sections().replace("<!--TOC-->", toc_html(entries, pages))
    body = re.sub(r"<!--SVG:([\w.-]+)-->", lambda m: (RAPPORT_FINAL / m.group(1)).read_text(encoding="utf-8"), body)
    return HEAD + body + "\n</body></html>\n"


def render(edge: str) -> None:
    """Imprime index.html en PDF avec Edge sans interface."""
    subprocess.run([edge, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=20000",
                    f"--print-to-pdf={OUT_PDF}", OUT_HTML.as_uri()], check=True, capture_output=True)


def locate(entries: list[dict]) -> list[int]:
    """Page (base 1) de chaque titre dans le PDF imprimé, 0 si introuvable."""
    with fitz.open(OUT_PDF) as doc:
        texts = [" ".join(page.get_text().split()) for page in doc]
    pages, start = [], 3  # la page de garde, le résumé et le sommaire précèdent le corps
    for entry in entries:
        needle = entry["title"][:40]
        found = next((i for i in range(start, len(texts)) if needle in texts[i]), None)
        if found is None:
            pages.append(0)
            continue
        pages.append(found + 1)
        start = found
    return pages


def main() -> None:
    """Construit le rapport en deux passes et signale les titres introuvables."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--edge", default=EDGE, help="chemin de msedge.exe")
    args = parser.parse_args()
    entries = collect(sections())
    OUT_HTML.write_text(assemble(entries, None), encoding="utf-8")
    render(args.edge)
    pages = locate(entries)
    OUT_HTML.write_text(assemble(entries, pages), encoding="utf-8")
    render(args.edge)
    with fitz.open(OUT_PDF) as doc:
        print(f"{OUT_PDF.name} : {doc.page_count} pages, {len(entries)} entrées de sommaire")
    missing = [e["title"] for e, p in zip(entries, pages) if not p]
    if missing:
        print("Titres introuvables :", missing)


if __name__ == "__main__":
    main()
