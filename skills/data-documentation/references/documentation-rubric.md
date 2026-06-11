# Documentation Rubric

Use this reference when producing detailed table or column documentation,
reviewing existing docs, or returning structured output.

## Evidence Quality

Strong evidence usually includes:

- schema definitions for names, types, constraints, and relationships;
- data profiles for nulls, cardinality, ranges, distributions, and examples;
- lineage for upstream sources, transformations, and downstream use;
- glossary entries or contracts for business meaning;
- tests, queries, dashboards, or notebooks that show how the asset is used;
- recent timestamps, versions, commits, or catalog update times.

Weak evidence includes names alone, one-off sample rows, unversioned notes, or
claims copied from old docs without source support. Use weak evidence only with
a clear confidence note.

## Table Documentation Checklist

Cover these fields when evidence exists:

- Name: exact table or dataset identifier.
- Summary: one or two sentences describing what the asset represents.
- Grain: one row per what, including time, entity, or event boundaries.
- Keys: primary, natural, foreign, or uniqueness constraints.
- Freshness: update cadence, latency, backfill behavior, and retention.
- Scope: filters, partitions, regions, tenants, or excluded records.
- Lineage: upstream inputs, transformation notes, and downstream consumers.
- Quality: tests, known gaps, duplication risks, nullable areas, and caveats.
- Ownership: steward, team, contact, or escalation path when available.
- Evidence: source paths, catalog links, query names, or timestamps.

## Column Documentation Checklist

For each important column, document:

- Meaning: plain-language definition tied to the table grain.
- Type: physical type and any semantic type or format.
- Allowed values: enum values, ranges, units, codes, or reference tables.
- Null behavior: whether null is expected, exceptional, or unknown.
- Derivation: source field, transformation, defaulting, or calculation.
- Examples: representative values that do not expose sensitive data.
- Constraints: uniqueness, not-null, foreign key, regex, or test coverage.
- Quality notes: drift, outliers, imputation, deprecated values, or caveats.
- Evidence: which source supports the definition.

## Assumptions And Confidence

Use direct labels:

- `Verified`: supported by current evidence.
- `Inferred`: likely from names, lineage, examples, or query usage.
- `Unclear`: evidence is missing, stale, or contradictory.

When evidence conflicts, state the conflict instead of choosing silently. Prefer
the newest versioned source only when recency and authority are clear.

## Citation Patterns

Keep citations compact and local to the claim:

- Markdown: `Definition text. Source: schema.sql, profile.json.`
- Table cell: `Customer identifier (Source: schema.sql)`
- Structured output: include an `evidence` array with `source`, `field`, and
  optional `observed_at` keys.

Do not over-cite repeated schema facts. A table-level evidence note can cover a
group of column types or constraints when all claims came from the same source.

## Stale-Doc Checks

Before finalizing, compare docs against the latest available evidence:

- documented tables absent from schema or lineage;
- documented columns absent from the current schema;
- schema columns missing from documentation;
- renamed columns where old and new names both appear;
- type, enum, or nullability changes not reflected in docs;
- freshness or row-count claims older than the latest profile;
- lineage claims that disagree with current transformations or jobs.

Use `scripts/check_table_docs.py` for a lightweight Markdown/schema coverage
check when schema evidence is available as JSON. Treat script results as hints;
review ambiguous identifier matches manually.

## Optional Structured Output

Use this shape when the user asks for JSON/YAML or when docs need to feed a
catalog API:

```yaml
tables:
  - name: table_name
    summary: ""
    grain: ""
    freshness: ""
    keys: []
    lineage:
      upstream: []
      downstream: []
    assumptions: []
    evidence:
      - source: ""
        observed_at: ""
        notes: ""
    columns:
      - name: column_name
        type: ""
        meaning: ""
        null_behavior: ""
        allowed_values: []
        derivation: ""
        examples: []
        quality_notes: []
        confidence: verified
        evidence:
          - source: ""
            field: ""
```

Keep empty or unknown fields only when the receiving system requires them.
