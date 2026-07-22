---
name: data-quality
description: Generate, audit, and refine portable data quality validation rules from schemas, sample rows, profile statistics, business constraints, and target validation frameworks. Use when drafting expectation suites, mapping constraints to checks, reviewing rule coverage, producing Great Expectations-style JSON, or improving data validation rules without assuming a product-specific domain.
when-to-use: drafting expectation suites, mapping constraints to checks, reviewing rule coverage, or producing Great Expectations-style validation rules
metadata:
  short-description: "Generate and audit data validation rules"
  author: Easel
---

# Data Quality

Use this skill to turn evidence about a dataset into practical validation
rules. Keep the core workflow portable across domains and validation tools.

## Operating Stance

Act as a data quality validator. Be skeptical of sample-only patterns, separate
contractual constraints from inferred checks, and tune rule strictness to the
evidence. Prefer checks that fail with actionable signals over broad rules that
create noisy failures.

## Workflow

1. Collect evidence:
   - schema, field descriptions, data types, keys, and relationships;
   - sample rows, profile statistics, null rates, ranges, and distinct counts;
   - business constraints, freshness needs, accepted failure thresholds, and
     target validation framework.
   Ask for the target validation framework, failure tolerance, or enforcement
   mode when unclear. If absent, state assumptions before generating rules.
2. Classify candidate rules:
   - structural: required columns, types, uniqueness, primary keys;
   - completeness: nullability, conditional required fields, row counts;
   - validity: ranges, enums, formats, parseability;
   - consistency: cross-field logic, referential checks, derived values;
   - distribution: drift, quantiles, cardinality, outlier bounds;
   - freshness: timestamps, load windows, partition coverage.
3. Separate facts from inferences. Rules backed by explicit constraints should
   be required; rules inferred from samples or profiles should be proposed with
   rationale, confidence, and review notes.
4. Choose strictness deliberately. Prefer exact checks for contractual schema
   and tolerant checks for observed distributions unless the user asks for hard
   enforcement.
5. Generate output in the requested target format. For Great Expectations-style
   JSON, produce an expectation suite with `expectation_type`, `kwargs`, and
   optional `meta` fields.
6. Audit the suite for coverage, duplicates, brittle sample-only assumptions,
   missing severity or threshold decisions, and framework-specific limitations.

## References

- `references/rule-generation.md`: detailed rule taxonomy, mapping guidance,
  audit rubric, and JSON output examples.

## Deterministic Check

When producing Great Expectations-style JSON, validate its basic structure:

```bash
python3 scripts/validate_expectations.py path/to/suite.json
```

The script checks JSON syntax and expectation object shape only. It does not
execute rules against data or require any validation framework.

## Output Rules

- State evidence used and assumptions made.
- Mark each generated rule as `required`, `recommended`, or `exploratory` when
  the target format allows metadata.
- Keep source notes that affect severity, threshold, confidence, or framework
  mapping; omit incidental profile details.
- Do not hard-code domain, product, or organization vocabulary unless the user
  provides it.
- Prefer portable rule names and explain any target-framework approximation.
