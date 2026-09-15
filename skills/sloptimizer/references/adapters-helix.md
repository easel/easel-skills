# Optional HELIX Adapter

Use this when the project has HELIX artifacts such as feature, contract,
design, ADR, or migration documents. HELIX is read as methodology context, not
as a runtime dependency.

## Checks

- The implementation plan traces to the governing artifact.
- Acceptance criteria cover the contract or feature behavior.
- Migration work names source and destination artifacts.
- Risks and non-scope are explicit.
- Terminology matches the governing document.
- Claims stay inside the artifact's authority: PRDs state product scope, ADRs
  record decisions, test plans name verification strategy, and work items track
  execution.
- Rewrites preserve IDs, paths, artifact names, commands, metrics, statuses,
  acceptance criteria, trace links, non-scope, risks, assumptions, and open
  questions.
- Unsupported claims about tests, metrics, coverage, validation, or ratchets are
  flagged unless the text names the backing evidence.

## Rewrite Rule

Do not make a HELIX artifact sound more polished at the expense of authority.
Prefer precise traceability, file paths, commands, and acceptance checks over
smooth prose.

If a HELIX work item cannot be made measurable from the governing artifact,
return `NOT_EXECUTION_READY` rather than inventing missing acceptance detail.

## Deliverable Titles (`human-facing` profile)

HELIX's `present` mode projects governed artifacts into decks, one-pagers,
and briefs under the `human-facing` profile in `workflows/voice.yml`
(conciseness 5; audience: decision-makers, sponsors, clients, readers with no
HELIX vocabulary). The profile already requires that every title and heading
be a claim, not a label, and lists rhetorical reversals, rule-of-three
padding, and reader-steering tics under `avoid`. The headline rules in
`references/headlines.md` are the deterministic side of that profile; use
them so a rewrite lands inside the deck voice instead of fighting it.

Run on the script before the gate (`skills/helix/scripts/check-deliverable.py`
in HELIX, which carries its own port of these rules as `title.slop` and
`horizontal_logic` so the gate works without this skill installed):

```bash
scripts/slop-audit.sh <flow>/06-iterate/deliverables/DEL-<nnn>-<slug>.md
```

Unit titles are `### <n>. <title>` headings, so the default run audits every
one of them and the deck's H1. Then rewrite with `references/headlines.md`
and these profile-specific constraints:

- The subject is a noun the audience uses: the customer, the cost, the
  document, the team's own runtime. No artifact IDs, activity names,
  work-item terms, or acceptance-criterion codes; those live in the Sources
  appendix. `check-deliverable.py` blocks them in titles and bodies.
- A number in the title must appear in the unit's body and in the Sources
  table with its governing artifact section. Never derive a new figure by
  summing or rounding sourced ones; use the figure the source states.
- The title states what the reader gets, then the evidence, then the ask;
  the last content title is the ask itself, one or two imperatives, with the
  owner and date in the body.
- Read the `Titles-only read` list under `## Story` aloud as one paragraph.
  It must carry the chosen story spine (`story_spines` in
  `slide-patterns.yml`) on its own, and each title must share a word or idea
  with its neighbor. Keep that list identical to the unit headings under
  `## Content`.
- Keep `avoid` from the profile: no em dashes, no bold-label bullets, no
  hedges, no "the real X", no "the catalog" or "the flow" shorthand.
- No mannered prose in a title or body: the audience reads "the engine
  behind delivery" as decoration and "under the hood" as evasion. State the
  mechanism or the number; `SloptimizerHeadline.Mannered` and
  `Sloptimizer.ManneredProse` flag the stock phrases.

Rewrite the titles first and re-audit them before editing any body; a body
written under a slop title inherits its shape. Then run the unit bodies
through `references/slides.md`: a `present` deck carries the same tells in
its card labels (coined statuses), strips (principles served), and closers,
and `slop-audit.sh --target slide` on the deliverable checks both layers.

## Useful Project Gates

When present, use the project's own gates as evidence:

```bash
just lint-prose
just check-prose-redundancy
just validate-artifact-schemas
just test-website-generated
git diff --check
```

These commands are optional. Sloptimizer must still work when HELIX tooling is
not installed.
