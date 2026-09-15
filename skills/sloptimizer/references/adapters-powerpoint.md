# Optional PowerPoint Adapter

Use this when the slide target lives in PowerPoint or a `.pptx` file. The
checklist and rewrite order are in `references/slides.md`; this file maps
them onto the tools each host gives you. Nothing here is required to run
the core skill.

## PowerPoint with Office.js tools

In a session that exposes the Office.js slide tools (`execute_office_js`,
`list_slide_shapes`, `read_slide_text`, `edit_slide_xml`,
`verify_slide_visual`):

1. **Look first.** `execute_office_js` with `getImageAsBase64` and
   `attachImage` to see the slide, then `list_slide_shapes`. Read only the
   text shapes you will change with `read_slide_text`; one representative
   card is enough to copy its formatting. Name every checklist hit by shape
   id before editing.
2. **Rewrite in one pass.** One `edit_slide_xml` call: rewrite each flagged
   shape's paragraphs, copying the existing `<a:pPr>` and `<a:rPr>` from
   the read; delete cut sections with `removeChild` on their `<p:sp>`; keep
   `bodyPr` and `lstStyle`; run all text through `escapeXml`.
3. **Rebalance geometry.** In `execute_office_js`, shrink card heights to
   their content and move lower sections up. Keep the deck's font sizes.
4. **Verify.** `verify_slide_visual` with the list of edits as
   `expected_changes`. Fix anything flagged except deck-convention font
   sizes. Done when the verdict is `done`.
5. **Report** in the three lines from `references/slides.md`.

## A `.pptx` file on disk

```bash
scripts/slop-audit.sh deck.pptx
```

`slop-audit.sh` extracts the deck with `scripts/pptx-text.py` (standard
library only: the file is a zip of XML parts), switches the target to
`slide`, and audits the text. Each shape is preceded by a comment naming
its slide index, shape id, and shape name, so a finding at a line maps back
to a shape. To edit, use whatever the session offers for the file
(python-pptx, LibreOffice, or the Office.js tools above after opening it);
this skill does not write `.pptx`.

`scripts/pptx-text.py --notes deck.pptx` appends speaker notes per slide
when the notes are part of what will be read aloud.

## Markdown decks (Marp, Slidev, reveal-md)

The deck source is already the slide layout the audit expects: a heading per
slide, `---` between slides, one line per shape.

```bash
scripts/slop-audit.sh --target slide slides.md
```

Frontmatter is skipped; `![bg](...)` and HTML lines are ignored.

## Other hosts

Google Slides and Keynote: export to `.pptx` and use the file path above.
Pasted shape text with no file: write it one shape per line with `---`
between slides and run the Markdown command, or apply the checklist by hand
and report the pattern names.
