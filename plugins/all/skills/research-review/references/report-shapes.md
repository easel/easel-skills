# Research Review Report Shapes

Use these shapes when the user has not requested a specific format.

## Quick Review

```markdown
**Question**
`<decision or claim being evaluated>`

**Scope**
- As of: `<date>`
- Sources inspected: `<count and source classes>`
- Non-scope: `<what was not checked>`

**Findings**
- `<claim>` Source: `<link or path>`. Confidence: `<high|medium|low>`.

**Recommendation**
`<actionable recommendation and why>`

**Open Questions**
- `<unknown, missing source, conflict, or validation needed>`
```

## Design Against Best Practices

```markdown
**Verdict**
`<fit | partial fit | mismatch | insufficient evidence>`

**Evidence**
- Local: `<repo evidence>`
- External: `<primary sources and dates>`

**Gaps**
- `<where the design diverges from evidence or needs a decision>`

**Implications**
- `<implementation, testing, migration, operational, or documentation impact>`
```

## Source Ledger

```markdown
| Source | Date/Version | Claim Used | Confidence | Notes |
|---|---:|---|---|---|
| `<title/link/path>` | `<date>` | `<claim>` | `<level>` | `<limits/conflicts>` |
```

## Final Answer Rules

- Lead with the answer or verdict when the decision is clear.
- Keep source summaries short; spend detail on implications and conflicts.
- Do not hide uncertainty in neutral prose. Use open questions or risk bullets.
