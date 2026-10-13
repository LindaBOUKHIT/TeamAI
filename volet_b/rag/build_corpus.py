"""Build a small, source-traceable HDFS documentation corpus in C6 format."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen


CORPUS_DIR = Path(__file__).resolve().parent / "corpus"
RAW_DIR = CORPUS_DIR / "raw"
OUTPUT_PATH = CORPUS_DIR / "chunks.jsonl"
COMPARISON_PATH = CORPUS_DIR / "chunking_comparison.json"
MAX_CHARS = 1600
OVERLAP_CHARS = 200

SOURCES = (
    {
        "id": "hdfs-architecture-1.2.1",
        "doc": "HDFS Architecture Guide",
        "url": "https://hadoop.apache.org/docs/stable1/hdfs_design.html",
        "version": "Hadoop 1.2.1 documentation; guide copyright 2008",
        "filename": "hdfs_design.html",
    },
    {
        "id": "hdfs-users-1.2.1",
        "doc": "HDFS Users Guide",
        "url": "https://hadoop.apache.org/docs/stable1/hdfs_user_guide.html",
        "version": "Hadoop 1.2.1 documentation; guide copyright 2008",
        "filename": "hdfs_user_guide.html",
    },
)


@dataclass(frozen=True)
class Section:
    """Text and heading extracted from one documentation section."""

    title: str
    text: str


class _SectionParser(HTMLParser):
    """Extract headings and body text while ignoring page navigation."""

    _SKIP_TAGS = {"nav", "header", "footer", "aside", "script", "style", "noscript"}
    _VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
    _BLOCK_TAGS = {
        "address", "article", "blockquote", "br", "dd", "div", "dl", "dt",
        "h1", "h2", "h3", "h4", "h5", "h6", "li", "ol", "p", "pre",
        "section", "table", "td", "th", "tr", "ul",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.sections: list[Section] = []
        self._title = "Introduction"
        self._body: list[str] = []
        self._heading: list[str] | None = None
        self._skip_depth = 0
        self._started_content = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_map = dict(attrs)
        classes = (attrs_map.get("class") or "").lower()
        if self._skip_depth:
            if tag not in self._VOID_TAGS:
                self._skip_depth += 1
            return
        element_id = (attrs_map.get("id") or "").lower()
        if tag in self._SKIP_TAGS or element_id in {"menu", "publishedstrip", "level2tabs"} or any(
            marker in classes for marker in ("sidebar", "sidenav", "navbar", "footer", "breadtrail", "minitoc")
        ):
            self._skip_depth = 1
            return
        heading_level = int(tag[1]) if re.fullmatch(r"h[1-6]", tag) else None
        if heading_level is not None:
            if heading_level == 1:
                if self._started_content:
                    self._finish_section()
            elif not self._started_content:
                # Drop the page title and print/PDF links before the first real section.
                self._body = []
                self._started_content = True
            else:
                self._finish_section()
            self._heading = []
        elif tag in self._BLOCK_TAGS:
            self._body.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if self._skip_depth:
            self._skip_depth -= 1
            return
        if re.fullmatch(r"h[1-6]", tag) and self._heading is not None:
            heading = _clean_text("".join(self._heading))
            if heading:
                self._title = heading
            self._heading = None
        elif tag in self._BLOCK_TAGS:
            self._body.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        if self._heading is not None:
            self._heading.append(data)
        else:
            self._body.append(data)

    def finish(self) -> list[Section]:
        self._finish_section()
        return self.sections

    def _finish_section(self) -> None:
        body = _clean_text("".join(self._body))
        if body:
            self.sections.append(Section(title=self._title, text=body))
        self._body = []


def _clean_text(value: str) -> str:
    """Normalize whitespace while retaining paragraph boundaries."""
    lines = [re.sub(r"\s+", " ", line).strip() for line in value.splitlines()]
    return "\n".join(line for line in lines if line)


def _slug(value: str) -> str:
    """Create a stable, URL-like identifier from a section title."""
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-") or "section"


def _download_sources(force: bool = False) -> None:
    """Download the pinned official documentation pages into the ignored raw directory."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for source in SOURCES:
        destination = RAW_DIR / source["filename"]
        if destination.exists() and not force:
            continue
        request = Request(
            source["url"],
            headers={"User-Agent": "TeamAI-HDFS-corpus-builder/1.0"},
        )
        with urlopen(request, timeout=30) as response:
            page = response.read()
        destination.write_bytes(page)


def _load_sections(source: dict[str, str]) -> list[Section]:
    """Parse one downloaded HTML page into titled text sections."""
    page_path = RAW_DIR / source["filename"]
    if not page_path.is_file():
        raise FileNotFoundError(
            f"Source absente : {page_path}. Relancez sans --no-download pour la télécharger."
        )
    parser = _SectionParser()
    parser.feed(page_path.read_text(encoding="utf-8", errors="replace"))
    sections = parser.finish()
    if not sections:
        raise ValueError(f"Aucun texte n’a été extrait de {page_path}.")
    return sections


def _split_at_boundary(text: str, max_chars: int) -> list[str]:
    """Split long text at paragraph or whitespace boundaries."""
    remaining = text.strip()
    pieces: list[str] = []
    while len(remaining) > max_chars:
        boundary = remaining.rfind("\n", 0, max_chars + 1)
        if boundary < max_chars // 2:
            boundary = remaining.rfind(" ", 0, max_chars + 1)
        if boundary < max_chars // 2:
            boundary = max_chars
        pieces.append(remaining[:boundary].strip())
        remaining = remaining[boundary:].strip()
    if remaining:
        pieces.append(remaining)
    return pieces


def _section_chunks(source: dict[str, str], sections: list[Section], max_chars: int) -> list[dict[str, str]]:
    """Build C6 passages without crossing documentation section boundaries."""
    chunks: list[dict[str, str]] = []
    section_counts: dict[str, int] = {}
    for section in sections:
        pieces = _split_at_boundary(section.text, max_chars)
        section_slug = _slug(section.title)
        for piece in pieces:
            section_counts[section_slug] = section_counts.get(section_slug, 0) + 1
            chunks.append(
                {
                    "id": f"{source['id']}#{section_slug}#{section_counts[section_slug]}",
                    "doc": source["doc"],
                    "section": section.title,
                    "text": piece,
                    "source_url": source["url"],
                    "version": source["version"],
                }
            )
    return chunks


def _window_chunks(
    source: dict[str, str], sections: list[Section], max_chars: int, overlap_chars: int
) -> list[dict[str, str]]:
    """Build fixed-size C6 passages across each document with overlap."""
    indexed: list[tuple[int, str]] = []
    offset = 0
    for section_index, section in enumerate(sections):
        text = f"{section.title}\n{section.text}"
        indexed.append((offset, text))
        offset += len(text) + 2
    document = "\n\n".join(text for _, text in indexed).strip()
    chunks: list[dict[str, str]] = []
    start = 0
    while start < len(document):
        end = min(start + max_chars, len(document))
        if end < len(document):
            boundary = document.rfind(" ", start + max_chars // 2, end)
            if boundary > start:
                end = boundary
        text = document[start:end].strip()
        section_titles = [
            sections[index].title
            for index, (section_start, section_text) in enumerate(indexed)
            if section_start <= end and section_start + len(section_text) >= start
        ]
        chunks.append(
            {
                "id": f"{source['id']}#document#{len(chunks) + 1}",
                "doc": source["doc"],
                "section": " / ".join(section_titles),
                "text": text,
                "source_url": source["url"],
                "version": source["version"],
            }
        )
        if end == len(document):
            break
        start = max(start + 1, end - overlap_chars)
    return chunks


def _summarize(chunks: list[dict[str, str]]) -> dict[str, int | float]:
    """Calculate comparable size and section-boundary statistics."""
    lengths = [len(chunk["text"]) for chunk in chunks]
    return {
        "chunk_count": len(chunks),
        "mean_chars": round(sum(lengths) / len(lengths), 1) if lengths else 0,
        "median_chars": sorted(lengths)[len(lengths) // 2] if lengths else 0,
        "max_chars": max(lengths, default=0),
        "chunks_spanning_multiple_sections": sum(" / " in chunk["section"] for chunk in chunks),
    }


def _write_jsonl(path: Path, chunks: list[dict[str, str]]) -> None:
    """Write UTF-8 C6 records as one JSON object per line."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as output:
        for chunk in chunks:
            output.write(json.dumps(chunk, ensure_ascii=False) + "\n")


def build(strategy: str, download: bool, force_download: bool, max_chars: int, overlap_chars: int) -> None:
    """Compare chunking strategies and write the requested strategy and metrics."""
    if max_chars < 200:
        raise ValueError("--max-chars doit être supérieur ou égal à 200.")
    if overlap_chars < 0 or overlap_chars >= max_chars:
        raise ValueError("--overlap doit être compris entre 0 et max-chars - 1.")
    if download:
        _download_sources(force=force_download)

    all_sections = [(source, _load_sections(source)) for source in SOURCES]
    section_chunks = [
        chunk
        for source, sections in all_sections
        for chunk in _section_chunks(source, sections, max_chars)
    ]
    window_chunks = [
        chunk
        for source, sections in all_sections
        for chunk in _window_chunks(source, sections, max_chars, overlap_chars)
    ]

    comparison = {
        "sources": [source["id"] for source in SOURCES],
        "max_chars": max_chars,
        "overlap_chars": overlap_chars,
        "section": _summarize(section_chunks),
        "sliding_window": _summarize(window_chunks),
        "recommended_strategy": "section",
        "written_strategy": strategy,
        "recommendation_reason": (
            "Les sections préservent le contexte documentaire et les frontières thématiques. "
            "Les sections trop longues sont découpées sans mélanger deux sections."
        ),
    }
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    COMPARISON_PATH.write_text(
        json.dumps(comparison, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    selected = window_chunks if strategy == "sliding-window" else section_chunks
    _write_jsonl(OUTPUT_PATH, selected)
    print(f"Stratégie écrite   : {strategy}")
    print(f"Découpage par section : {_summarize(section_chunks)}")
    print(f"Fenêtre glissante    : {_summarize(window_chunks)}")
    print(f"Passages C6 générés  : {len(selected)} ({OUTPUT_PATH})")
    print(f"Comparaison          : {COMPARISON_PATH}")


def main() -> None:
    """Parse command-line options and build the HDFS corpus."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strategy",
        choices=("section", "sliding-window"),
        default="section",
        help="Stratégie à écrire dans chunks.jsonl (les deux sont comparées à chaque exécution).",
    )
    parser.add_argument("--max-chars", type=int, default=MAX_CHARS)
    parser.add_argument("--overlap", type=int, default=OVERLAP_CHARS)
    parser.add_argument("--no-download", action="store_true", help="Utiliser les pages déjà présentes dans corpus/raw.")
    parser.add_argument("--force-download", action="store_true", help="Retélécharger les pages officielles.")
    args = parser.parse_args()
    build(
        strategy=args.strategy,
        download=not args.no_download,
        force_download=args.force_download,
        max_chars=args.max_chars,
        overlap_chars=args.overlap,
    )


if __name__ == "__main__":
    main()
