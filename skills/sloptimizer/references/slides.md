# Slides

Use this reference when the target is a `slide`: one slide or a whole deck,
in PowerPoint, a `.pptx` file, a Marp or Markdown deck, or pasted shape
text. A slide is a title plus a handful of text shapes (subtitle, card
labels, banners, section labels, a closer), each read in a second or two by
someone who does not have the author's map. The title is a `headline` and
follows `references/headlines.md`. Every other text shape goes through the
checklist below. Each hit is a required edit, not a suggestion.

## Detect

Run every text shape against this list. Deterministic owners are in the
last column: `SloptimizerHeadline.*` and `SloptimizerSlide.*` come from
`scripts/headline-audit.py --slide`, and the `SloptimizerSlide` Vale style
runs on body shapes under `slop-audit.sh --target slide`. Name the pattern in
detect findings.

<!-- vale off -->
| Pattern | Tell | Fix | Owner |
|---|---|---|---|
| Container title | The title names a category or grouping box ("Firm capabilities", "Foundations", "Platform layer") instead of a thing. | Title the slide with what it shows. If it shows nothing concrete, the slide should not exist; say so. | `SloptimizerHeadline.ContainerTitle` (slide titles and titles-only outlines; document headings such as `## Overview` are a convention and are not flagged) |
| Invented status vocabulary | Labels the author coined for a state: "portability reference", "representative workload", "working hypothesis", "proposed contract", "candidate, scope open". | A state the reader already knows: `In use / Built / Specified / Idea / Not adopted / Retired`. | `SloptimizerSlide.StatusJargon` (Vale, body); `SloptimizerHeadline.StatusJargon` (titles, same token list) |
| Dressed-up hedge | "fit unproven", "scope open", "not committed", "directionally correct", "in flight". | "not built", "not decided", "no owner yet". | `SloptimizerSlide.StatusJargon` |
| Self-justifying section | "Why we control it", "What stays fixed", "Design principles served P3 P4 P7", "How to read this slide". The slide argues for itself. | Delete the section. If one fact in it is load-bearing, move it into the subtitle. | `SelfJustifying` (title or shape) |
| Aphoristic closer | A bottom line that sounds like a quote: "X is a request, not a capability", "That is what makes it portable". | Delete. Do not replace it with a different aphorism. | `SloptimizerSlide.Aphorism`, `SloptimizerSlide.ContrastiveReversal` |
| Restatement stack | Subtitle, banner, and takeaway say the same idea in different words. | Keep one shape; delete the other two. | `SloptimizerSlide.Restatement` catches lexical overlap on one slide; paraphrase is editorial |
| Compound coinage and marketing register | Modifier-noun coinages the reader must decode ("matter-aware", "governed conversational access") and marketing adjectives (leverage, differentiated, seamless, robust, universal experience). | The plain noun or verb: "firm-owned", "checked on every call", "the interface the firm controls". | `SloptimizerSlide.MarketingRegister` (Vale, body); `Sloptimizer.UnsupportedClaim`, `Sloptimizer.AISlop`; coinages are editorial |
| Trailing commentary | The second sentence explains why the first is there: "Verifies citations. Built as the worked example for moving a check between products." | Keep the first sentence. If the second carries a status, move it into the status label. | `SloptimizerSlide.TrailingCommentary` |
| Unsourced number | A count the audience cannot trace ("102 use cases, 183 demos"). | Cut unless the user confirms the source and wants it kept. | Editorial; the user's call |
| Stale name | Retired brands, old product names, "naming TBD". | Use the current name; flag to the user if unsure. | Editorial; `tbd` is in `StatusJargon` |
| Shouting label | A letterspaced all-caps section label that tells the reader what to think: "WHAT EXISTS AND WHERE IT STANDS", "WHY THE FIRM OWNS IT". | Shorten to a plain noun ("Current list", "To add one") or delete. A two-word status label in caps (`IN USE`) is fine. | `SloptimizerSlide.ShoutingLabel` |
| Internal taxonomy code | Zone, plane, pillar, and principle codes in body text ("Zone 6", "Plane 11", "P3 P4 P7"). The reader does not have the map. | Drop the code and name the thing. | `SloptimizerSlide.InternalTaxonomy` (Vale, body); `SloptimizerHeadline.Taxonomy` (titles) |
<!-- vale on -->

The title also gets every rule in `references/headlines.md`; the shape rules
above are the ones a title cannot carry (a title is never a closer or a
restatement of itself).

## Rewrite

Tool-specific steps (Office.js, `.pptx` on disk, Markdown decks) are in
`references/adapters-powerpoint.md`. The order is the same everywhere:

1. **Look first.** Render or screenshot the slide, list its text shapes,
   and read only the shapes you will change (one representative card is
   enough to copy formatting from). *Done when* every checklist hit has a
   shape id or line number.
2. **Title first.** Rewrite the title with `references/headlines.md` before
   touching a shape; a body written under a container title inherits its
   shape. If the slide shows nothing concrete, stop and tell the user the
   slide should not exist.
3. **Rewrite in one pass.** Change every flagged shape at once: rewrite the
   text, delete the shapes for cut sections, keep the deck's own paragraph
   and run formatting. Plain state labels replace coined ones; one sentence
   per card; no new aphorism where the old one was.
4. **Rebalance geometry.** Less text leaves holes. Shrink cards to their
   content and move lower sections up. Do not add a section to fill space
   and do not shrink text to fit; keep the deck's font sizes. *Done when*
   no card is more than about 40% empty and nothing overlaps.
5. **Verify.** Re-audit the slide text (`slop-audit.sh --target slide`) or
   run the host's visual check with the list of edits as expected changes.
   Fix everything flagged except deck-convention font sizes. *Done when*
   the checklist is clean.
6. **Report in three lines:** what was cut, what was renamed, and what you
   left because it needs the user's call (stale names, unsourced numbers,
   whether the slide should exist).

## Example

```text
Before
  title:   Firm capabilities
  banner:  THE PORTABILITY TEST — a capability passes when its contract
           survives a change of caller, protocol and model
  cards:   LIVE / PORTABILITY REFERENCE / REPRESENTATIVE WORKLOAD /
           PROPOSED CONTRACT / WORKING HYPOTHESIS
  strip:   DESIGN PRINCIPLES SERVED P3 P4 P7
  closer:  Known rules move out of prompts into versioned, testable components.

After
  title:    Use cases
  subtitle: Checks the firm has built as its own components. Five so far;
            one is in use.
  cards:    IN USE / BUILT / BUILT / SPECIFIED / IDEA, one plain sentence each
  deleted:  banner, principles strip, closer
  layout:   cards shortened, lower section moved up
```

## Validate

```bash
scripts/slop-audit.sh --target slide deck.md      # Marp or Markdown deck, --- between slides
scripts/slop-audit.sh deck.pptx                   # .pptx: extracted with scripts/pptx-text.py, audited as slides
scripts/pptx-text.py deck.pptx > deck.md          # the extraction alone, shape ids as comments
```

Exit 1 means at least one title or shape has a finding. Without Vale on the
path the body-text phrase rules are skipped and the title and shape rules
still run.
