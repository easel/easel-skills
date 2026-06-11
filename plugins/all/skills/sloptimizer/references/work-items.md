# Work Item Rubric

A work item is ready when an agent can execute it without extra chat context.

## Required Fields

- Problem: what is wrong or missing.
- Root cause or current gap: file, module, behavior, or artifact that explains
  why work is needed.
- Proposed fix: concrete implementation direction.
- Non-scope: what the worker must not expand into.
- Acceptance criteria: numbered, observable outcomes.
- Evidence commands: exact checks to run.

## Acceptance Criteria

Good acceptance criteria name observable behavior:

```text
1. `queue status --json` includes each worker's project, node, task, and state.
2. `TestWorkerStatusIncludesProject` covers the serialized project field.
3. `go test ./internal/server/...` passes.
```

Weak acceptance criteria use vague outcomes:

```text
1. The interface is better.
2. The feature works.
3. Tests are added.
```

## Not Execution-Ready

If the source material does not contain enough authority to make acceptance
criteria measurable, do not fill the gap from chat memory or guesswork. Return a
`NOT_EXECUTION_READY` finding and name what authority is missing.

Use this outcome when:

- The worker would need unstated product behavior, file paths, commands, or test
  names to know when to stop.
- The acceptance criteria can only say "works", "better", "complete",
  "correct", or "aligned".
- The proposed fix depends on a decision missing from the governing artifact,
  issue, or source file.

Finding shape:

```text
NOT_EXECUTION_READY: <short reason>
Missing authority: <decision, artifact, command, file, or acceptance detail>
Suggested next step: <ask for guidance | create/update governing artifact | split task>
```

## Slop Signals

<!-- vale off -->
- The item names an outcome but no files, commands, or interfaces.
- The description depends on a chat thread, temporary file, or memory.
- The test plan says "add tests" without naming what behavior must be tested.
- The proposed fix says "implement support" without naming the integration.
- The item mixes unrelated work that cannot be validated by one evidence set.
<!-- vale on -->
