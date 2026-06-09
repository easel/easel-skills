# Sloptimizer Rule Matrix

Each phrase should have one Vale owner. When a phrase can be both an AI-writing
tell and an unsupported claim, choose the rule that gives the most actionable
message and do not duplicate it in another file.

| Pattern group | Current owner | Final owner | Profile | Level | Rationale |
|---|---|---|---|---|---|
| Phrase-level AI slop such as `unlock value`, `transform the way`, `sophisticated multi-agent` | `AISlop.yml` | `AISlop.yml` | yes | warning | Phrase forms are high-confidence generated or marketing filler that are not already owned by unsupported-claim checks. |
| Unsupported quality claims such as `robust`, `scalable`, `production-ready`, `seamless experience`, `powerful automation` | `UnsupportedClaim.yml` | `UnsupportedClaim.yml` | yes | warning | The fix is evidence or deletion, not synonym replacement. |
| Capability verbs such as `supports`, `provides`, `enables` | `MissingActorAction.yml` | `MissingActorAction.yml` | yes | warning | The fix is naming the actor and concrete operation. |
| Filler transitions such as `in conclusion`, `moreover`, `that said` | `FillerTransition.yml` | `FillerTransition.yml` | yes | suggestion | These usually carry structure poorly but can be intentional. |
| Reader-steering phrases such as `worth noting`, `what stands out`, `the real answer` | none | `ReaderSteeringPhrases.yml` | yes | suggestion | The fix is naming the concrete reason or consequence. |
| Token-cost phrases such as `in order to`, `due to the fact that` | `TokenCost.yml` | `TokenCost.yml` | yes | suggestion | Deterministic substitutions with low semantic risk. |
| Generic adverbs such as `simply`, `quickly`, `effectively` | `Vocabulary.yml` | `Vocabulary.yml` | yes | suggestion | Prefer specifics, but context can justify them. |
| Repeated sentence openings | `RepeatedOpening.yml` | `raw-profile-audit.py` | default, results, strict | suggestion | Heuristic rhythm check; use as review signal, not proof. |
| Comparative hype verbs such as `beats`, `dominates`, `crushes` | none | `SloptimizerResults/ComparativeHype.yml` | results, strict | suggestion | The fix is scoping the comparison to metric, dataset, run, or time window. |
| Em dashes | none | `raw-profile-audit.py` | strict | suggestion | Source-level house-style check; default prose audit does not enforce it. |
| Bold inline header bullets | none | `raw-profile-audit.py` | strict | suggestion | Source-level Markdown structure check; default prose audit does not enforce it. |
| Negation reversal such as `it is not X, it is Y` | none | `raw-profile-audit.py` | strict | suggestion | High false-positive risk, so it is available only in the explicit strict profile. |
