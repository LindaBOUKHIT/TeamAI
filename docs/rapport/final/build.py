"""Assemble le rapport (sections/*.html), calcule le sommaire paginé et produit le PDF.

Usage : python docs/rapport/final/build.py [--edge CHEMIN]
Deux passes : la première imprime le document pour repérer la page de chaque titre,
la seconde réimprime avec les numéros de page dans le sommaire.
"""
import argparse
import html
import re
import subprocess
from pathlib import Path

import fitz  # PyMuPDF

HERE = Path(__file__).resolve().parent
OUT_HTML = HERE / 'index.html'
OUT_PDF = HERE.parent / 'TeamAI_Rapport.pdf'
EDGE = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'

HEAD = """<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<title>TeamAI — Rapport de projet NLP 2</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Young+Serif&family=Figtree:ital,wght@0,400;0,500;0,700;1,400&family=Kalam:wght@400;700&family=Courier+Prime&display=block" rel="stylesheet">
<link rel="stylesheet" href="style.css">
</head><body>
"""
HEADING = re.compile(r'<(h1|h2)([^>]*)>(.*?)</\1>', re.S)


def plain(fragment: str) -> str:
    text = re.sub(r'<span class="(?:n|verdict[^"]*)">.*?</span>', '', fragment)
    text = re.sub(r'<br\s*/?>', ' ', text)
    return ' '.join(html.unescape(re.sub(r'<[^>]+>', '', text)).split())


def number_of(fragment: str) -> str:
    match = re.search(r'<span class="n">(.*?)</span>', fragment)
    return match.group(1) if match else ''


def collect(body: str) -> list[dict]:
    entries = []
    for tag, attrs, inner in HEADING.findall(body):
        if 'data-toc="no"' in attrs:
            continue
        entries.append({'level': 1 if tag == 'h1' else 2, 'title': plain(inner), 'num': number_of(inner),
                        'kicker': ''})
    return entries


def toc_html(entries: list[dict], pages: list[int] | None) -> str:
    rows = []
    for i, entry in enumerate(entries):
        page = str(pages[i]) if pages and pages[i] else ''
        num = html.escape(entry['num'])
        rows.append(f'<li class="l{entry["level"]}"><span class="n">{num}</span><span>{html.escape(entry["title"])}</span>'
                    f'<span class="dots"></span><span class="p">{page}</span></li>')
    return '<ol class="toc">' + '\n'.join(rows) + '</ol>'


def assemble(entries, pages) -> str:
    parts = [p.read_text(encoding='utf-8') for p in sorted((HERE / 'sections').glob('*.html'))]
    body = '\n'.join(parts).replace('<!--TOC-->', toc_html(entries, pages))
    return HEAD + body + '\n</body></html>\n'


def render(edge: str) -> None:
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([edge, '--headless=new', '--disable-gpu', '--no-pdf-header-footer', '--virtual-time-budget=20000',
                    f'--print-to-pdf={OUT_PDF}', OUT_HTML.as_uri()], check=True, capture_output=True)


def locate(entries: list[dict]) -> list[int]:
    doc = fitz.open(OUT_PDF)
    texts = [' '.join(page.get_text().split()) for page in doc]
    pages, start = [], 3  # la page de garde, le résumé et le sommaire précèdent le corps
    for entry in entries:
        needle = entry['title'][:40]
        found = next((i for i in range(start, len(texts)) if needle in texts[i]), None)
        if found is None:
            pages.append(0)
            continue
        pages.append(found + 1)
        start = found
    return pages


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--edge', default=EDGE)
    args = parser.parse_args()
    raw = '\n'.join(p.read_text(encoding='utf-8') for p in sorted((HERE / 'sections').glob('*.html')))
    entries = collect(raw)
    OUT_HTML.write_text(assemble(entries, None), encoding='utf-8')
    render(args.edge)
    pages = locate(entries)
    OUT_HTML.write_text(assemble(entries, pages), encoding='utf-8')
    render(args.edge)
    missing = [e['title'] for e, p in zip(entries, pages) if not p]
    print(f'{OUT_PDF.name} : {fitz.open(OUT_PDF).page_count} pages, {len(entries)} entrées de sommaire')
    if missing:
        print('Titres introuvables :', missing)


if __name__ == '__main__':
    main()
