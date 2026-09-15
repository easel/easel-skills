#!/usr/bin/env python3
"""Extract the text of a .pptx deck as Markdown for slop-audit.sh --target slide.

Standard library only: a .pptx is a zip of XML parts, so no python-pptx is
needed. Output is one Markdown document in deck order:

    <!-- slide 1: shape 2 "Title 1" -->
    # The title placeholder becomes a heading
    <!-- slide 1: shape 3 "TextBox 4" -->
    Every other paragraph is one line.
    Line breaks inside a shape are separate lines.
    ---
    <!-- slide 2: ... -->

`---` separates slides, the title placeholder (`type="title"` or
`type="ctrTitle"`) is the slide's heading, table cells are lines, and the
comment before each shape names the slide index, shape id, and shape name so
a finding can be traced back to the shape it came from. `--no-ids` drops the
comments; `--notes` appends speaker notes under a `<!-- notes -->` marker.

Usage:
    pptx-text.py [--no-ids] [--notes] DECK.pptx [OUT.md]
"""
from __future__ import annotations

import argparse
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}
TITLE_TYPES = {"title", "ctrTitle"}


def slide_parts(archive: zipfile.ZipFile) -> list[str]:
    """Return slide part names in presentation order."""
    try:
        pres = ET.fromstring(archive.read("ppt/presentation.xml"))
        rels = ET.fromstring(archive.read("ppt/_rels/presentation.xml.rels"))
    except KeyError:
        pres = rels = None
    if pres is not None and rels is not None:
        targets = {
            rel.get("Id"): rel.get("Target", "")
            for rel in rels.findall("rel:Relationship", NS)
        }
        ordered = []
        for sld in pres.findall(".//p:sldIdLst/p:sldId", NS):
            target = targets.get(sld.get(f"{{{NS['r']}}}id"), "")
            if target:
                ordered.append(target if target.startswith("ppt/") else f"ppt/{target.lstrip('/')}")
        if ordered:
            return ordered
    names = [n for n in archive.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)]
    return sorted(names, key=lambda n: int(re.search(r"(\d+)\.xml$", n).group(1)))


def paragraph_lines(container: ET.Element) -> list[str]:
    """One line per <a:p>, splitting on <a:br/>."""
    lines: list[str] = []
    for para in container.iter(f"{{{NS['a']}}}p"):
        current: list[str] = []
        for node in para.iter():
            if node.tag == f"{{{NS['a']}}}t" and node.text:
                current.append(node.text)
            elif node.tag == f"{{{NS['a']}}}br":
                lines.append("".join(current))
                current = []
        lines.append("".join(current))
    return [re.sub(r"\s+", " ", line).strip() for line in lines if line.strip()]


def shape_kind(sp: ET.Element) -> str:
    ph = sp.find("./p:nvSpPr/p:nvPr/p:ph", NS)
    if ph is not None and ph.get("type") in TITLE_TYPES:
        return "title"
    return "body"


def shape_label(sp: ET.Element) -> tuple[str, str]:
    cnv = sp.find("./*/p:cNvPr", NS)
    if cnv is None:
        return "?", ""
    return cnv.get("id", "?"), cnv.get("name", "")


def slide_markdown(root: ET.Element, index: int, with_ids: bool) -> list[str]:
    out: list[str] = []
    title_done = False
    spTree = root.find("./p:cSld/p:spTree", NS)
    if spTree is None:
        return out
    for node in spTree.iter():
        if node.tag == f"{{{NS['p']}}}sp":
            lines = paragraph_lines(node)
            if not lines:
                continue
            shape_id, name = shape_label(node)
            if with_ids:
                out.append(f'<!-- slide {index}: shape {shape_id} "{name}" -->')
            if shape_kind(node) == "title" and not title_done:
                out.append(f"# {' '.join(lines)}")
                title_done = True
            else:
                out.extend(lines)
            out.append("")
        elif node.tag == f"{{{NS['a']}}}tbl":
            if with_ids:
                out.append(f"<!-- slide {index}: table -->")
            for cell in node.iter(f"{{{NS['a']}}}tc"):
                out.extend(paragraph_lines(cell))
            out.append("")
    return out


def notes_markdown(archive: zipfile.ZipFile, slide_part: str) -> list[str]:
    rels_name = slide_part.replace("ppt/slides/", "ppt/slides/_rels/") + ".rels"
    try:
        rels = ET.fromstring(archive.read(rels_name))
    except KeyError:
        return []
    for rel in rels.findall("rel:Relationship", NS):
        if rel.get("Type", "").endswith("/notesSlide"):
            target = rel.get("Target", "")
            part = "ppt/" + target.replace("../", "") if target.startswith("..") else target
            try:
                root = ET.fromstring(archive.read(part))
            except KeyError:
                return []
            lines: list[str] = []
            for sp in root.iter(f"{{{NS['p']}}}sp"):
                ph = sp.find("./p:nvSpPr/p:nvPr/p:ph", NS)
                if ph is not None and ph.get("type") == "body":
                    lines.extend(paragraph_lines(sp))
            return lines
    return []


def convert(path: Path, with_ids: bool = True, notes: bool = False) -> str:
    out: list[str] = []
    with zipfile.ZipFile(path) as archive:
        for index, part in enumerate(slide_parts(archive), 1):
            try:
                root = ET.fromstring(archive.read(part))
            except KeyError:
                continue
            if index > 1:
                out.append("---")
                out.append("")
            out.extend(slide_markdown(root, index, with_ids))
            if notes:
                note_lines = notes_markdown(archive, part)
                if note_lines:
                    out.append("<!-- notes -->")
                    out.extend(note_lines)
                    out.append("")
    text = "\n".join(out).rstrip() + "\n"
    return re.sub(r"\n{3,}", "\n\n", text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--no-ids", action="store_true", help="omit the slide/shape comments")
    parser.add_argument("--notes", action="store_true", help="append speaker notes per slide")
    parser.add_argument("deck")
    parser.add_argument("out", nargs="?")
    args = parser.parse_args()

    deck = Path(args.deck)
    if not deck.is_file() or not zipfile.is_zipfile(deck):
        print(f"pptx-text: {deck} is not a .pptx file", file=sys.stderr)
        return 2
    text = convert(deck, with_ids=not args.no_ids, notes=args.notes)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
