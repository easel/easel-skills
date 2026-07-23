---
name: data-mapping
description: Derive portable source-to-target data mappings, filename and table-name extraction rules, merge and survivorship logic, canonical names, priority order, conflict policies, and auditable transformation specs from schemas, samples, and examples.
when-to-use: source-to-target mappings, extraction rules, canonical names, conflict policies, merge logic, or survivorship specs
metadata:
  short-description: "Derive auditable mappings and survivorship rules"
  author: Easel
---

# Data Mapping

Use this skill when turning schemas, sample records, filenames, table names, or
business rules into an auditable mapping and survivorship specification. Keep
the core workflow portable. Put system-specific or domain-specific assumptions
in a clearly marked adapter or appendix instead of the base spec.

## Operating Stance

Act as a data architect. Work target-first, make identity and grain explicit,
record evidence for every inferred mapping, and treat ambiguity, lossy
transforms, and conflict handling as design decisions that need names.

## Workflow

1. Inventory evidence:
   - source files, tables, columns, types, keys, examples, null patterns, and
     filename or table-name conventions;
   - target entities, required fields, constraints, enumerations, and expected
     grain;
   - known precedence rules, freshness fields, trusted sources, and manual
     review requirements.
   Ask for the target contract or grain when it is missing. If the user needs a
   draft immediately, state the assumed target and mark affected mappings as
   provisional.
2. Normalize names before matching:
   - split tokens, expand obvious abbreviations, remove formatting noise, and
     record aliases;
   - preserve original names beside proposed canonical names.
3. Draft mappings:
   - map each target field to one or more source fields;
   - mark direct copies, renames, casts, parses, derivations, defaults, and
     unmapped fields;
   - include confidence, evidence, assumptions, and open questions.
4. Define extraction rules for filenames, paths, table names, partitions, or
   encoded metadata. Prefer exact patterns with named outputs.
5. Define merge and survivorship:
   - entity identity and match keys;
   - source priority order;
   - field-level precedence, freshness rules, null handling, tie-breakers, and
     conflict policies;
   - review queues for ambiguous or lossy cases.
6. Produce an auditable spec. For the recommended checklist and JSON shape,
   read `references/mapping-spec.md`.
7. Validate deterministic spec files when useful:

```bash
python3 <skill-dir>/scripts/validate_mapping_spec.py path/to/spec.json
```

## Output Rules

- Separate evidence from inference.
- Use stable identifiers for every source, target, mapping, and rule.
- State grain, key assumptions, and lossiness explicitly.
- Preserve only source evidence that affects matching, transforms,
  survivorship, confidence, or open questions.
- Prefer field-level survivorship rules over vague global precedence.
- Keep unresolved decisions as named open questions, not hidden assumptions.
