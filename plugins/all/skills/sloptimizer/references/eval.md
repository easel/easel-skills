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
