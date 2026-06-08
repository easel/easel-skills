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

## Slop Signals

- The item names an outcome but no files, commands, or interfaces.
- The description depends on a chat thread, temporary file, or memory.
- The test plan says "add tests" without naming what behavior must be tested.
- The proposed fix says "implement support" without naming the integration.
- The item mixes unrelated work that cannot be validated by one evidence set.

