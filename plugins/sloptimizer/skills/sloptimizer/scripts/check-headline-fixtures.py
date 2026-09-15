#!/usr/bin/env python3
"""Run Sloptimizer headline and slide fixture checks.

Fixture modes in tests/fixtures/headline-cases.json:
  headline          (default) one internal-document heading through audit_headline()
  slide-title       one title through audit_headline() with the container checks and external phrase lists
  shape             one standalone unit (slide shape, web label) through audit_shape()
  headings          a Markdown document through headline-audit.py (internal audience)
  headings-external the same with --audience external
  all-lines         a titles-only outline through headline-audit.py --all-lines
  slide             a deck file through headline-audit.py --slide
Then a .pptx built from raw XML goes through scripts/pptx-text.py and the slide audit.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "skills/sloptimizer/tests/fixtures/headline-cases.json"
HEADLINE_AUDIT = ROOT / "skills/sloptimizer/scripts/headline-audit.py"
PPTX_TEXT = ROOT / "skills/sloptimizer/scripts/pptx-text.py"


def load_audit():
    spec = importlib.util.spec_from_file_location("headline_audit", HEADLINE_AUDIT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_script(text: str, mode: str) -> set[str]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "case.md"
        path.write_text(text, encoding="utf-8")
        cmd = ["python3", str(HEADLINE_AUDIT), "--format", "json"]
        if mode == "all-lines":
            cmd.append("--all-lines")
        elif mode == "slide":
            cmd.append("--slide")
        elif mode == "headings-external":
            cmd += ["--audience", "external"]
        result = subprocess.run(cmd + [str(path)], check=False, text=True, capture_output=True)
    findings = json.loads(result.stdout or "[]")
    rules = {f["rule"].split(".", 1)[1] for f in findings}
    if bool(findings) != (result.returncode == 1):
        raise AssertionError(f"exit code {result.returncode} does not match {len(findings)} findings")
    return rules


SLIDE_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
<p:cSld><p:spTree>
<p:sp><p:nvSpPr><p:cNvPr id="2" name="Title 1"/><p:cNvSpPr/><p:nvPr><p:ph type="title"/></p:nvPr></p:nvSpPr>
<p:txBody><a:p><a:r><a:t>{title}</a:t></a:r></a:p></p:txBody></p:sp>
<p:sp><p:nvSpPr><p:cNvPr id="3" name="TextBox 2"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
<p:txBody><a:p><a:r><a:t>{line1}</a:t></a:r><a:br/><a:r><a:t>{line2}</a:t></a:r></a:p></p:txBody></p:sp>
</p:spTree></p:cSld></p:sld>"""
PRESENTATION_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
<p:sldIdLst><p:sldId id="256" r:id="rId3"/><p:sldId id="257" r:id="rId2"/></p:sldIdLst>
</p:presentation>"""
PRESENTATION_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide2.xml"/>
</Relationships>"""


def run_pptx_smoke() -> list[str]:
    """Build a two-slide .pptx from raw XML, extract it, and audit it as a slide target."""
    with tempfile.TemporaryDirectory() as tmp:
        deck = Path(tmp) / "deck.pptx"
        with zipfile.ZipFile(deck, "w") as archive:
            archive.writestr("ppt/presentation.xml", PRESENTATION_XML)
            archive.writestr("ppt/_rels/presentation.xml.rels", PRESENTATION_RELS)
            # rId3 -> slide2.xml is listed first, so slide2 must come out first.
            archive.writestr("ppt/slides/slide2.xml", SLIDE_XML.format(
                title="Firm capabilities",
                line1="WHAT EXISTS AND WHERE IT STANDS",
                line2="Verifies citations. Built as the worked example for moving a check between products."))
            archive.writestr("ppt/slides/slide1.xml", SLIDE_XML.format(
                title="Use cases", line1="Five checks built so far; one is in use.", line2="IN USE"))
        result = subprocess.run(["python3", str(PPTX_TEXT), str(deck)], check=False, text=True, capture_output=True)
        text = result.stdout
        expected_order = ["# Firm capabilities", "WHAT EXISTS AND WHERE IT STANDS", "---", "# Use cases", "IN USE"]
        positions = [text.find(marker) for marker in expected_order]
        if result.returncode != 0 or -1 in positions or positions != sorted(positions):
            return [f"pptx smoke: unexpected extraction output:\n{text}\n{result.stderr}"]
        if '<!-- slide 1: shape 3 "TextBox 2" -->' not in text:
            return ["pptx smoke: shape id comment missing"]
        md = Path(tmp) / "deck.md"
        md.write_text(text, encoding="utf-8")
        audit = subprocess.run(["python3", str(HEADLINE_AUDIT), "--slide", "--format", "json", str(md)],
                               check=False, text=True, capture_output=True)
        rules = {f["rule"] for f in json.loads(audit.stdout or "[]")}
    expected = {"SloptimizerHeadline.ContainerTitle", "SloptimizerShape.ShoutingLabel", "SloptimizerShape.TrailingCommentary"}
    if rules != expected:
        return [f"pptx smoke: slide audit expected {sorted(expected)}, got {sorted(rules)}"]
    return []


def main() -> int:
    audit = load_audit()
    cases = json.loads(FIXTURES.read_text(encoding="utf-8"))
    failures: list[str] = []
    for case in cases:
        expected = set(case["expected_rules"])
        mode = case.get("mode", "headline")
        if mode == "headline":
            actual = {rule for rule, _, _ in audit.audit_headline(case["headline"])}
        elif mode == "slide-title":
            actual = {rule for rule, _, _ in audit.audit_headline(case["headline"], label_rules=True, external=True)}
        elif mode == "shape":
            actual = {rule for rule, _, _ in audit.audit_shape(case["headline"])}
        else:
            try:
                actual = run_script(case["text"], mode)
            except AssertionError as exc:
                failures.append(f"{case['name']}: {exc}")
                continue
        if actual != expected:
            failures.append(f"{case['name']}: expected {sorted(expected)}, got {sorted(actual)}")
    failures.extend(run_pptx_smoke())
    if failures:
        print("Headline fixture validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(f"OK: {len(cases)} Sloptimizer headline fixtures passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
