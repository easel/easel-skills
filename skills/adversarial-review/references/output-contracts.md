# Output Contracts

Use these contracts when a review prompt needs exact, parseable output. Keep the
contract in the prompt instead of relying on prose expectations.

## Exact JSON Verdict Prompt

Use JSON when a harness, script, or follow-up agent will parse the review.

```text
Return only valid JSON. Do not wrap it in Markdown. Do not include comments,
trailing commas, explanatory prose, or fields not listed here.

Schema:
{
  "verdict": "APPROVE | REQUEST_CHANGES | BLOCK",
  "findings": [
    {
      "severity": "BLOCKING | WARNING | NOTE",
      "area": "short affected area",
      "evidence": "specific line, section, file, constraint, or explicit gap",
      "finding": "specific issue and why it matters",
      "recommendation": "minimal corrective action"
    }
  ],
  "disagreements_or_uncertainty": [
    {
      "topic": "short topic",
      "reason": "what is uncertain or what evidence is missing"
    }
  ],
  "summary": "2-4 sentences"
}

Severity rules:
- BLOCKING means execution should stop until resolved.
- WARNING means execution can continue only if the owner accepts the risk.
- NOTE means useful but non-blocking.

Evidence rules:
- Every finding must cite artifact evidence, governing constraint evidence, or
  reproducible reasoning.
- If no evidence supports a concern, omit it.
- If there are no findings, return "findings": [] and verdict "APPROVE".
```

## Exact Markdown Verdict Prompt

Use Markdown when a human will read and decide.

```text
Return exactly this Markdown structure and no other top-level sections.

### Findings

| Severity | Area | Evidence | Finding | Recommendation |
|---|---|---|---|---|
| BLOCKING | <area> | <line/section/file/constraint/gap> | <specific issue> | <minimal corrective action> |
| WARNING | <area> | <line/section/file/constraint/gap> | <specific issue> | <minimal corrective action> |
| NOTE | <area> | <line/section/file/constraint/gap> | <specific issue> | <minimal corrective action> |

If there are no findings, write one row:
| NOTE | none | reviewed artifact | No evidence-backed issues found. | none |

### Verdict

APPROVE | REQUEST_CHANGES | BLOCK

### Disagreements Or Uncertainty

<Only include uncertainty that affects the verdict. Write "None." if absent.>

### Summary

<2-4 sentences>
```

## Harness Notes

- Put the output contract at the end of the prompt so it is the last formatting
  instruction the model sees.
- For JSON, parse the output before trusting it. Invalid JSON is a harness
  failure, not a weak approval.
- For Markdown, reject extra top-level sections when exact verdict format
  matters.
- Do not let output formatting validation replace evidence review.
