# Data Quality Rule Generation Reference

Use this reference when a task needs more than a small set of obvious
constraints.

## Evidence Ladder

Assign each rule one evidence level:

- `contract`: explicit schema, interface, or business requirement.
- `profile`: supported by data profile statistics across enough records.
- `sample`: observed in examples only; needs review before enforcement.
- `inference`: plausible from names or conventions; treat as exploratory.

Contract rules can be strict. Profile, sample, and inference rules should carry
confidence, rationale, and review notes.

## Rule Taxonomy

Structural rules:

- required column presence;
- type or parseability;
- column order only when consumers require it;
- row-level or compound uniqueness;
- minimum or maximum row count.

Completeness rules:

- non-null fields;
- conditional required fields;
- acceptable missing-rate thresholds;
- mutually exclusive or co-required field groups.

Validity rules:

- enum membership;
- numeric min, max, or between bounds;
- string length bounds;
- regex or parser-backed format checks;
- timestamp timezone, granularity, or allowed window checks.

Consistency rules:

- cross-column comparisons;
- derived field equality within tolerance;
- parent-child or foreign-key style membership;
- monotonic sequence checks inside ordered groups;
- duplicate detection beyond strict keys.

Distribution rules:

- approximate quantile bounds;
- mean, median, or standard deviation ranges;
- cardinality bounds;
- category proportion ranges;
- drift checks against a baseline profile.

Freshness rules:

- newest timestamp within an accepted delay;
- expected partitions present;
- load date matches processing window;
- append-only datasets have increasing row counts.

## Generation Process

1. Normalize input evidence into fields, types, sample values, profile metrics,
   and explicit constraints.
2. Generate contract-backed rules first.
3. Add profile-backed rules only when the observed metric is stable enough for
   the requested strictness.
4. Convert sample-only observations into recommendations, not hard failures,
   unless the user confirms they are contractual.
5. Add metadata that explains source evidence, rationale, severity, and review
   status when the output format permits it.
6. De-duplicate overlapping rules. Keep the rule with the clearer failure
   signal or lower maintenance burden.
7. Call out rules the target framework cannot express directly.

## Mapping To Great Expectations-Style JSON

Prefer a suite object:

```json
{
  "expectation_suite_name": "example_suite",
  "expectations": [
    {
      "expectation_type": "expect_column_values_to_not_be_null",
      "kwargs": {
        "column": "customer_id"
      },
      "meta": {
        "status": "required",
        "evidence": "contract",
        "rationale": "Field is part of the declared record key."
      }
    }
  ]
}
```

Common mappings:

- Required column: `expect_column_to_exist`
- Non-null column: `expect_column_values_to_not_be_null`
- Unique key: `expect_column_values_to_be_unique` or compound uniqueness
  equivalent when supported by the target runtime.
- Type or parseability: `expect_column_values_to_be_of_type` or parser-backed
  format expectation.
- Enum: `expect_column_values_to_be_in_set`
- Numeric range: `expect_column_values_to_be_between`
- Regex format: `expect_column_values_to_match_regex`
- Row count: `expect_table_row_count_to_be_between`
- Column set: `expect_table_columns_to_match_set`

When the exact expectation name varies by framework version, preserve the
portable intent in `meta.intent` and state the approximation in the response.

## Audit Rubric

Coverage:

- Are identifiers, required fields, ranges, enums, timestamps, and cross-field
  rules covered?
- Are dataset-level checks included, not only column checks?
- Are freshness and volume checks included where operationally relevant?

Reliability:

- Which rules are sample-only or inferred?
- Are thresholds tolerant enough for normal variation?
- Are null and empty-string semantics explicit?
- Are timezones and date boundaries explicit?

Maintainability:

- Are duplicate or redundant expectations removed?
- Are names and metadata understandable to future maintainers?
- Is every hard failure backed by a contract or high-confidence evidence?
- Are target-framework limitations documented?

Review flags:

- `needs-owner`: business meaning or acceptable threshold is unclear.
- `needs-baseline`: distribution or drift rule requires historical data.
- `needs-runtime-check`: rule shape is valid but target framework support is
  uncertain.
- `too-brittle`: rule is likely to fail on normal data variation.

## Response Shape

For a human-readable rule proposal:

```markdown
**Evidence Used**
- `<schema/profile/sample/business constraint summary>`

**Generated Rules**
- `<field or scope>`: `<rule>` (`<required|recommended|exploratory>`, evidence: `<level>`)

**Review Needed**
- `<thresholds, inferred semantics, missing baseline, framework limits>`
```

For JSON output, include only the requested machine-readable artifact unless
the user asks for explanation. Put assumptions in `meta` where possible.
