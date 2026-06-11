# Source Quality

Use this reference when deciding what evidence is strong enough to support a
research review.

## Source Ladder

Prefer sources in this order:

1. Current local evidence: repository files, tests, logs, config, release
   manifests, and source code relevant to the question.
2. Primary external sources: official docs, standards, specifications, papers,
   source repositories, release notes, changelogs, and vendor engineering posts.
3. Independent evidence: benchmarks, issue threads, postmortems, published
   evaluations, and reproducible examples.
4. Secondary summaries: blogs, tutorials, news, or forum answers. Use these for
   orientation unless they cite primary evidence.

## Recency

Check dates or versions when the topic changes over time:

- APIs, SDKs, model behavior, prices, quotas, dependencies, security guidance,
  legal or policy requirements, standards drafts, and product capabilities.
- If no date is visible, say so and reduce confidence.
- Prefer newer evidence only when authority and applicability are comparable.

## Conflicts

When sources disagree:

- identify the exact conflicting claim;
- compare authority, date, scope, and version;
- prefer the source closest to the implementation or standard;
- preserve the disagreement if the decision still depends on it.

## Citation Discipline

- Cite the source that directly supports the claim.
- Use local paths for repository evidence and URLs for external evidence.
- Put citations near the relevant claim, not only in a bibliography.
- Do not cite search-result snippets, generated summaries, or sources you did
  not open.
- Avoid long quotations. Paraphrase and quote only short phrases when exact
  wording matters.
- For web evidence, prefer sources that expose a stable URL, date or version,
  author or publisher, and enough primary material to verify the claim.

## Research Boundaries

State the boundary when the review is intentionally limited:

- maximum source count or tool-call budget;
- source classes excluded, such as news, forums, or vendor marketing;
- date range or version range;
- local files or repositories inspected;
- whether browsing, package registry lookup, or paper search was unavailable.

## Confidence Labels

- `High`: multiple current primary sources agree, or one authoritative source
  directly controls the behavior.
- `Medium`: primary evidence exists but has scope limits, version ambiguity, or
  partial conflicts.
- `Low`: evidence is indirect, old, secondary, sample-only, or inferential.
