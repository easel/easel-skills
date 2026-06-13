# Density And Voice

Use this reference when the user asks for tight, compact, dense,
"unsummarizable", or voice-preserving prose. The default target is compressed,
not stripped.

## Verbosity Scale

Use this calibration unless the user gives another one:

- `10`: padded, explanatory, repetitive.
- `8`: default assistant prose: clear but over-signposted.
- `5`: concise professional prose.
- `3`: highly compressed, optimized, still readable, with some flow and voice.
- `1`: mechanical telegraph style.

Default to `3` for Sloptimizer rewrites. Do not drift to `1` unless the user
asks for notes, labels, command output, or deliberately brutal compression.
In this skill, "as tight as possible" means as tight as possible without
discarding meaning, evidence, or useful voice.

At `3`, keep connective tissue, sentence rhythm, and one memorable detail,
contrast, or image when it carries meaning. Cut restatement, hedging, preface,
throat-clearing, generic summary, and decorative transitions.

## Density Targets

- Idea density: each sentence adds a distinct claim, distinction, mechanism,
  example, or implication.
- Evidence density: important claims carry a fact, source, command, metric,
  example, or observable condition.
- Decision density: the prose helps the reader choose, rank, reject, or act.
- Contrast density: the rewrite preserves differences a summary would flatten.
- Mechanism density: it says how something works, fails, changes, or causes
  another thing.
- Texture density: details carry specificity, voice, or memory, not decoration.
- Handoff density: for plans, specs, and tasks, each line helps execution,
  review, testing, or decision-making.

## Voice Guardrail

Cut filler, not fingerprint. Preserve voice when phrasing carries judgment,
cadence, emphasis, tension, surprise, humor, image, or a memorable distinction.
Cut voice-like ornament when it is generic cleverness, throat-clearing,
performative emphasis, or rhythm without information.

## Compression Pass

1. Remove throat-clearing, signposting, duplicate abstraction, and generic
   transitions.
2. Replace broad nouns and verbs with the specific artifact, action, mechanism,
   or consequence.
3. Keep one strong phrasing choice when it preserves the author's cadence or
   point of view.
4. Read the rewrite aloud or scan for meter. If it sounds clipped, restore the
   smallest phrase that brings flow back.
5. Stop when further cuts would remove distinction, evidence, rhythm, or
   useful texture.

## Output Calibration

When summarizing changes, use compact labels:

- `cut`: filler, repetition, signposting, unsupported claim.
- `kept`: voice, evidence, contrast, mechanism, texture.
- `risk`: meaning or cadence may have shifted.
