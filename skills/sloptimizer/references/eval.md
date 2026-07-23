# Sloptimizer Eval

Run this after a rewrite (and after re-audit when files are available). Answer
each check pass or fail. If any check fails, fix the draft before returning it.

For `detect` requests, confirm the response names each pattern with a quoted
line and a short fix, without rewriting the draft or claiming AI authorship.

## Editing principles

1. Does the edit preserve the user's point without inventing claims, examples,
   stats, quotes, or opinions?
2. Does it preserve distinctive vocabulary, cadence, bluntness, humor,
   uncertainty, digressions, and polish when those are present?
3. Does it leave strong human sentences alone instead of rewriting them for
   consistency?
4. Is the amount of cutting proportional to the actual slop, with no aggressive
   compression that strips character the writer already had?
5. Do retained sentences earn their place with concrete facts, actors, or
   decisions?
6. Are genuinely tangled sentences fixed while clear spoken cadence remains?

## Patterns (prose targets only)

Skip this section when the target is a `work-item` or `plan`. Those use the
section below instead.

1. Are throat-clearing openers, faux-insight setups, binary contrasts, and
   negative listings removed or rewritten as direct claims?
2. Are colon reveals, superficial `-ing` analysis, importance puffery, and
   weasel attribution fixed or flagged?
3. Are synonym cycling, dramatic fragmentation, rhetorical setups, and robotic
   rhythm addressed?
4. Are fake-profound kickers and summary-recap endings cut so the piece ends on
   a concrete takeaway or next action?
5. Is chatbot residue ("I hope this helps!", "Great question!") removed from
   shipped prose?
6. Is formatting slop removed when it is decorative rather than structural?

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
