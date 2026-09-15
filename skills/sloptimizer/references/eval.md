# Sloptimizer Eval

Run this after a rewrite, and after the re-audit when files are available.
Answer each check pass or fail. Fix any failure before returning the draft.

For `detect` requests, confirm the response names each pattern with a quoted
line and a short fix, without rewriting the draft or claiming AI authorship.

## Editing principles

1. Does the edit preserve the user's point without inventing claims, examples,
   stats, quotes, or opinions?
2. Does it leave strong human sentences alone, keeping distinctive vocabulary,
   cadence, bluntness, humor, uncertainty, and digressions?
3. Is the cutting proportional to the actual slop, rather than compression
   that strips character the writer already had?
4. Do the retained sentences earn their place with concrete facts, actors, or
   decisions?

## Patterns (prose targets only)

Skip this section for `work-item` and `plan` targets; use the next one.

1. Are the eight tells under "Highest-Yield Patterns" in
   `references/ai-writing.md` gone, and does a scan of the full catalog in
   that file turn up nothing still unaddressed?
2. Did the rewrite introduce fresh ones? A second pass often adds filler,
   broad claims, or reader-steering labels while fixing the first set.
3. Does every catalog pattern left in the draft survive the "When The Pattern
   Is Fine" test in the same file, and does the change summary say why it
   stayed?
4. Do headings and titles pass `references/headlines.md`? The sentence rules
   skip them, so a clean prose audit says nothing about them.
5. Is assistant chrome gone ("I hope this helps!"), and is every bullet, bold
   span, and heading structural rather than decorative?
6. Are example values obvious placeholders rather than real names, and is
   tool-specific behavior scoped to the tool it belongs to?

## Slides

When the target is a `slide` or deck, after the prose checks above:

1. Is every title a claim about what the slide shows, not a container label
   ("Firm capabilities") or a self-justification ("Why we control it")?
2. Are status labels plain states the reader already knows (in use, built,
   specified, idea, not adopted, retired; not built, not decided, no owner
   yet) rather than coined ones ("portability reference", "fit unproven")?
3. Are self-justifying sections, aphoristic closers, and shouting all-caps
   labels deleted rather than reworded, with no new aphorism in the old
   one's place?
4. Does each idea appear in one shape, with the subtitle, banner, and
   takeaway no longer restating each other, and each card down to its first
   sentence?
5. Are internal taxonomy codes (Zone 6, Plane 11, P3) and compound coinages
   gone from text the audience reads?
6. Are unsourced numbers and stale names flagged for the user rather than
   silently kept or silently cut?
7. Was the layout rebalanced (cards shrunk to content, lower sections moved
   up) without adding a section to fill space or shrinking the deck's font
   sizes?
8. Does the report say in three lines what was cut, what was renamed, and
   what was left for the user's call?

## Work items and plans

When the target is a work item or plan rather than prose:

1. Can a competent agent execute the item from the text alone?
2. Are actors, inputs, outputs, acceptance checks, and non-scope explicit?
3. Are unsupported implementation promises flagged rather than polished?
4. Prefer executability over prose pattern cleanup. Do not rewrite ticket text
   solely to remove stylistic AI tells unless they hide the task.

## Final read

1. Was the edit checked against this file without requiring a separate reviewer
   agent?
2. Does the final output include the edited text and a short **What changed**
   section (for rewrites)?
3. For detect requests, does each finding name a pattern, quote a line, and
   give a short fix?
