# Mapping And Survivorship Spec

Use this reference when the task needs a detailed mapping artifact, reviewer
checklist, or machine-checkable JSON spec. Keep product and domain adapters in a
separate appendix supplied by the caller.

## Evidence Checklist

Capture enough evidence for another agent or engineer to reproduce the mapping:

- Source inventory: dataset, entity, field, type, nullable status, examples,
  unique keys, foreign keys, value ranges, and observed quality issues.
- Target inventory: entity, field, type, required status, allowed values,
  uniqueness, grain, and downstream contract.
- Name evidence: exact source names, exact target names, aliases, canonical
  name proposal, tokenization notes, and abbreviations.
- Example evidence: at least one representative row or value for inferred
  parses, casts, joins, and derived fields.
- Rule evidence: documented priority order, trusted source, freshness
  timestamp, tie-breaker, or manual-review rule.
- Gaps: unmapped required targets, unused source fields with likely meaning,
  ambiguous mappings, and lossy transforms.

## Recommended JSON Shape

The validation script checks this shape. Add fields as needed, but keep these
top-level arrays when producing a deterministic spec.

```json
{
  "version": "1",
  "sources": [
    {
      "name": "source_a",
      "kind": "table",
      "grain": "one row per source entity"
    }
  ],
  "targets": [
    {
      "name": "target_entity",
      "grain": "one row per target entity"
    }
  ],
  "canonical_names": [
    {
      "canonical": "entity.identifier",
      "aliases": ["entity_id", "id"]
    }
  ],
  "extraction_rules": [
    {
      "id": "extract_date_from_filename",
      "input": "filename",
      "pattern": "^(?P<batch_date>[0-9]{8})_.*[.]csv$",
      "outputs": ["batch_date"],
      "examples": [
        {
          "input": "20260131_entities.csv",
          "output": {"batch_date": "20260131"}
        }
      ]
    }
  ],
  "mappings": [
    {
      "id": "map_entity_identifier",
      "target": "target_entity.identifier",
      "sources": ["source_a.entity_id"],
      "transform": "trim and cast to string",
      "required": true,
      "confidence": "high",
      "evidence": "Name match and sample values align.",
      "assumptions": []
    }
  ],
  "survivorship": [
    {
      "id": "survive_entity_name",
      "target": "target_entity.name",
      "match_keys": ["target_entity.identifier"],
      "priority": ["source_a.name", "source_b.name"],
      "conflict_policy": "prefer_first_non_null",
      "tie_breaker": "latest updated_at",
      "manual_review": false
    }
  ],
  "open_questions": [
    {
      "id": "q_required_status",
      "question": "Which source owns status when all values are stale?",
      "blocks": ["target_entity.status"]
    }
  ]
}
```

## Mapping Rules

- Use target-first rows for coverage: every required target should be present,
  even when unmapped.
- Preserve source path exactly as `source.field`, `file.column`, or another
  stable identifier used by the project.
- Mark transform types clearly: `copy`, `rename`, `cast`, `parse`, `split`,
  `join`, `derive`, `default`, `lookup`, `aggregate`, or `manual_review`.
- Include lossy behavior, such as truncation, rounding, deduplication, timezone
  coercion, code collapsing, or discarded fields.
- Do not bury joins inside prose. State join keys, cardinality, expected
  unmatched behavior, and duplicate handling.

## Name Extraction Rules

For filenames, paths, partitions, and table names, specify:

- input surface: filename, full path, table name, partition key, or header;
- exact pattern, preferably a regular expression with named groups;
- examples that should match and at least one non-match when ambiguity matters;
- output field names and type conversions;
- collision handling when two names extract the same canonical value.

## Survivorship Rules

Define survivorship at the smallest useful scope:

- identity: match keys and whether they are exact, normalized, or probabilistic;
- precedence: ordered source list or scoring formula;
- freshness: timestamp field, timezone, clock-skew tolerance, and stale value
  behavior;
- null handling: ignore nulls, allow null overwrite, or preserve existing;
- conflicts: prefer source, prefer latest, prefer non-null, aggregate,
  concatenate, manual review, or reject row;
- ties: deterministic tie-breaker such as source order, timestamp, stable sort,
  or explicit error;
- audit columns: winning source, losing candidates, rule id, decision timestamp,
  and review reason.

## Review Checklist

Before finalizing, check:

- Required target fields are mapped or listed as blockers.
- Every inferred transform cites evidence or states an assumption.
- Source priority is explicit and field-level exceptions are documented.
- Conflicts and nulls have deterministic outcomes.
- Extraction rules include examples and named outputs.
- The spec can be implemented without reading private conversation history.
