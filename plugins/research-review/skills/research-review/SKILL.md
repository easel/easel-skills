---
name: research-review
description: Research and review a technical question, design, dependency, standard, or implementation approach using current, source-backed evidence. Use when asked to look up best practices, compare options, verify current behavior, review against docs or papers, summarize the state of the art, or make an evidence-backed recommendation.
when-to-use: look up best practices, compare options, verify current behavior, review against docs or papers, or make an evidence-backed recommendation
metadata:
  short-description: "Research and review with source-backed evidence"
  author: Easel
---

# Research Review

Use this skill when the answer depends on evidence outside the immediate prompt
or repo. Prefer primary sources and make the path from evidence to
recommendation visible.

## Operating Stance

Act as a source-backed researcher and reviewer. Be skeptical of convenient
summaries, check recency for unstable facts, separate evidence from inference,
and turn findings into decisions, risks, or next actions.

## Workflow

1. Define the research question:
   - decision, design, standard, dependency, or behavior being evaluated;
   - audience and consequence of being wrong;
   - freshness needs and acceptable source types.
   Ask a concise clarifying question when the decision, scope, or freshness
   requirement is unclear. If the user needs momentum, state your assumed scope
   and proceed.
2. Build a source plan:
   - start with local repo evidence when reviewing local work;
   - prefer official docs, standards, source repositories, release notes,
     papers, and primary project posts;
   - use secondary summaries only for orientation or comparison.
   Set a proportional budget for source count, tool calls, and depth before
   searching.
3. Research iteratively:
   - search, open, and inspect sources instead of relying on snippets;
   - follow leads when sources disagree or leave gaps;
   - keep only source notes that affect the decision or confidence;
   - stop when the decision is adequately supported, not when every possible
     source has been read.
4. Keep an evidence ledger with:
   - source title, URL or path, publisher, date or version when visible;
   - claim supported by that source;
   - confidence and any conflict or limitation.
5. Synthesize:
   - separate local facts, external facts, inference, recommendation, and
     residual risk;
   - cite sources near the claims they support;
   - call out stale, missing, or contradictory evidence.
6. Return the requested artifact. For source grading, output shapes, and option
   comparison guidance, read the references below.

## References

- `references/source-quality.md`: source selection, recency, conflicts, and
  citation discipline.
- `references/report-shapes.md`: concise research review and comparison report
  formats.
- `references/decision-matrix.md`: option comparison, confidence, and
  recommendation criteria.
- `references/agent-research.md`: guidance for agentic and multi-agent
  research workflows, context discipline, and research budgets.

## Deterministic Check

When producing a Markdown research report, run:

```bash
python3 scripts/check_research_report.py path/to/report.md
```

The script checks for a dated scope, findings or recommendation, and cited
sources. It does not verify source accuracy.

## Output Rules

- Cite sources with links or exact local paths.
- Include source dates or versions when recency matters.
- Do not cite snippets you did not open or inspect.
- Mark unsupported claims as assumptions or open questions.
- State search limits or source limits when the review is intentionally bounded.
- Prefer actionable implications over a generic literature summary.
