# Worked Examples

Full passages, before and after. The catalog in `references/ai-writing.md`
names each tell in isolation; these show a whole passage at the target
density, and they mark the sentences an edit must leave alone.

Read one example before a first rewrite. A rewrite that removes the slop and
also sands off the author's good sentences fails the "leave strong human
sentences alone" principle in `references/eval.md`, so every example below
lists what stayed and why.

## Prose, Minimum Effective Edit

The default for "make this sound less like AI". Fix the tells; keep what
already works.

```text
Here's the thing: our ingestion pipeline has become a real pain point. At its
core, the system was designed to handle a modest volume of events, but it now
processes significantly more. This is not a capacity problem. It's an
architecture problem.

The retry logic is the part most people miss. When a batch fails, the worker
re-reads the entire partition from offset zero, which means a single poison
message can burn forty minutes of CPU before anyone notices. We found this the
hard way during the March incident.

In conclusion, we should prioritize a robust fix that will seamlessly improve
reliability going forward.
```

```text
Our ingestion pipeline was built for a modest event rate and now runs well
above it. The failure is in the retry path.

When a batch fails, the worker re-reads the entire partition from offset zero,
so a single poison message can burn forty minutes of CPU before anyone
notices. We found this the hard way during the March incident.

The fix is per-message checkpointing. No estimate yet.
```

Fixed: the throat-clearing opener, three filler transitions
(`At its core`, `In conclusion`, `going forward`), the faux-insight setup
(`the part most people miss`), the binary contrast about capacity versus
architecture, and two unsupported claims (`robust fix`,
`seamlessly improve reliability`) that named no mechanism.

Kept untouched: the poison-message sentence, because it carries the mechanism
and a number, and `We found this the hard way during the March incident`,
because it carries evidence and the writer's cadence. Neither is a candidate
for compression.

Added nothing. `No estimate yet` replaces the invented promise with the true
state, which is the honest move when the draft has no schedule in it.

## The Same Passage On A Tight Request

Only when the user asks for tight, compact, dense, or unsummarizable prose.
The source above, compressed toward 3 on the scale in
`references/density-voice.md`:

```text
The pipeline was built for a modest event rate and now runs well above it.
The retry path is the failure: a failed batch re-reads its partition from
offset zero, so one poison message burns forty minutes of CPU before anyone
notices. We found this the hard way in the March incident. Per-message
checkpointing is the fix, with no estimate yet.
```

Using the labels from `references/density-voice.md`:

`cut`: paragraph breaks that carried no turn in the argument, and the standalone
sentence `The failure is in the retry path`, which the next clause proves.

`kept`: the number, the mechanism, the March incident, and the admission that
no estimate exists.

`risk`: the three-sentence version reads faster and lands harder; the
four-paragraph version is easier to skim in a long document. Ask which one the
target medium wants before compressing a draft this far.

## PR Description

```text
## Summary

This PR introduces a comprehensive refactor of the authentication module that
significantly improves security and provides a robust foundation for future
work. The changes are fully tested and production-ready.

## Changes

- **Refactored auth:** Streamlined the token validation flow
- **Improved errors:** Better error handling throughout
```

```text
## Summary

Token validation moves from `AuthMiddleware` to `TokenVerifier` so the refresh
path and the API-key path share one expiry check. Fixes the bug where an
expired refresh token was accepted for 60 seconds past expiry (#41).

## Changes

Expiry is checked once, in `TokenVerifier.verify`, against `time.Now()` at call
time rather than at middleware construction.

Failed verification returns `ErrTokenExpired` rather than a generic 401, so a
client can tell expiry from a bad signature.

## Verification

`go test ./internal/auth/...` passes, including the new
`TestExpiredRefreshTokenRejected`.
```

Fixed: four unsupported claims (`comprehensive`, `robust foundation`,
`fully tested`, `production-ready`), the security improvement asserted with no
mechanism, and two bold inline-header bullets carrying one vague clause each.

The evidence in the rewrite came from the diff and the test name, not from the
draft. When a PR has no test to cite, write what was checked by hand and leave
the gap visible. Do not promote `fully tested` into a named test that does not
exist.

## Work Item Without Enough Authority

```text
Improve the export feature so it handles large datasets better. Add tests.
```

Returning a polished version of this item would hide the problem. The shape
comes from `references/work-items.md`:

```text
NOT_EXECUTION_READY: "better" names no measurable target, and no failing case
is given.

Missing authority: the dataset size that fails today, the observed failure
(timeout, out-of-memory, truncated file), the export command or endpoint, and
the threshold the fix must meet.

Suggested next step: ask for one failing export (row count, command, error
output) and the target it must hit.
```

Rewriting the item into `Export completes reliably for large datasets` would
read better and execute no better. The test for a work item is whether an
agent can finish it from the text alone.
