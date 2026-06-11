# Decision Matrix

Use this reference when comparing tools, designs, dependencies, standards, or
implementation approaches.

## Criteria Selection

Choose criteria from the user's goal and the evidence, not from generic
comparison templates. Common criteria:

- correctness or standards compliance;
- implementation complexity;
- operational risk;
- maintenance burden;
- performance or scalability;
- security, privacy, or data exposure;
- ecosystem maturity and support;
- migration cost and reversibility;
- testability and observability.

## Matrix Shape

```markdown
| Option | Evidence Fit | Advantages | Risks | Confidence |
|---|---|---|---|---|
| `<option>` | `<what sources support>` | `<why it helps>` | `<where it can fail>` | `<high|medium|low>` |
```

## Recommendation Rules

- Recommend one option only when evidence and constraints make it defensible.
- If two options are close, name the deciding question or experiment.
- Avoid "best" without scope. Say best for what workload, organization,
  version, time horizon, or failure mode.
- Include the cheapest validation step when the recommendation depends on a
  runtime or integration assumption.
