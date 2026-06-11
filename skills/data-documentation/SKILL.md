---
name: data-documentation
description: Generate evidence-backed documentation for datasets, tables, and columns from schemas, profiles, lineage, examples, constraints, and glossary terms. Use when asked to create, audit, refresh, structure, or cite data documentation while checking assumptions, stale fields, and optional machine-readable output.
---

# Data Documentation

Use this skill to document data assets from evidence rather than guesses. Keep
the core workflow portable across storage engines, catalogs, and documentation
formats.

## Operating Stance

Act as a documentation maintainer and data steward. Preserve exact names, cite
evidence for claims, flag stale or conflicting sources, and make unknowns
visible instead of filling gaps with plausible prose.

## Workflow

1. Gather available evidence:
   - schemas, field types, constraints, indexes, and partitions;
   - row counts, null rates, distinct counts, distributions, and examples;
   - upstream and downstream lineage;
   - glossary terms, owner notes, data contracts, queries, and tests.
   Ask for scope when the asset set, audience, or freshness requirement is
   unclear. If proceeding without clarification, state the assumed scope.
2. Build a short evidence map before drafting:
   - source path or system;
   - asset, table, or column covered;
   - timestamp or version when available;
   - confidence and any conflict with other sources.
3. Draft table documentation:
   - purpose and grain;
   - primary entities and keys;
   - freshness, update mode, and expected latency;
   - important filters, partitions, and access considerations;
   - upstream inputs, downstream consumers, and known caveats.
4. Draft column documentation:
   - plain-language meaning;
   - type, valid values, units, format, and null behavior;
   - derivation or source mapping;
   - constraints, examples, and quality warnings.
5. Mark assumptions explicitly. If evidence is missing or contradictory, say
   what is inferred and what needs confirmation.
6. Add citations or source notes beside claims that came from evidence. Do not
   cite unsupported domain knowledge as if it came from the source files.
7. Check for stale documentation before finalizing. When useful, run:

```bash
python3 <skill-dir>/scripts/check_table_docs.py --schema schema.json --docs docs.md
```

8. Return the requested format. For detailed rubrics, stale-check guidance, and
   optional structured output shapes, read `references/documentation-rubric.md`.

## Output Rules

- Prefer concise, scannable documentation over encyclopedic prose.
- Separate verified facts, assumptions, and open questions.
- Preserve exact table and column names.
- Include enough evidence for another agent or reviewer to trace claims back to
  their source.
- Keep source notes that support definitions, caveats, freshness, lineage, or
  open questions; omit background evidence that does not affect the docs.
- Avoid product-specific vocabulary unless the user-provided context requires
  it or an optional adapter supplies it.
