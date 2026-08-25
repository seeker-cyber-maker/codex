# Chat/Work advisory capsule: TERM notation syntax v1

## Claim and ceiling

Review the proposed first machine-readable implementation boundary for Dream
House TERM notation. Return advisory design findings only. Do not claim that
code ran, tests passed, a dialect was adopted, or any task/authority effect is
authorized.

## Frozen design

Formal name: Scoped Terminology Repair notation. Ordinary name: TERM notation.
It is a scoped ambiguity-repair notation, not a language, native dialect,
protocol standard, command surface, or global lexicon.

Declared forms:

```text
TERM? <candidate>
MEAN <intended meaning>
NOT <nearest excluded meaning>
SCOPE <task, artifact, project, or context generation>

TERM= <candidate> | MEAN <meaning> | SCOPE <scope> | CTX <generation>
TERM~ <candidate> | SCOPE <scope> | WHY <reason>

PREF? target=TERM_NOTATION/1
PREF= target=TERM_NOTATION/1 | preferred
```

Preference may instead be `not_preferred`, `no_preference`, or
`undetermined`; a missing required response is recorded by the wrapper as
`not_stated`. Preference is advisory and independent from correctness.

## Candidate first-slice boundary

- A versioned JSON dictionary defines operators, field names, allowed
  preference values, limits, and human-readable semantics.
- A pure Python parser accepts one TERM or PREF record at a time and returns a
  typed dictionary.
- The delimiter `|`, newlines within values, duplicate fields, unknown fields,
  unknown operators, oversize values, and task/authority-like extensions fail
  closed.
- Casual `TERM? <candidate>` may omit MEAN/NOT/SCOPE; any included detail line
  must be from the closed set.
- `TERM=` requires MEAN, SCOPE, and CTX. `TERM~` requires SCOPE and WHY.
- `PREF?` requires the exact target `TERM_NOTATION/1`. `PREF=` requires that
  target and exactly one declared value; `ALT` is allowed only after
  `not_preferred`.
- The module performs no I/O and has no task, relay, prompt, execution,
  authority, or admission integrations.

## Context boundary

The current Codex fork and Dream House share the upstream Codex source base.
The user reports a current Codex CLI stop-hook issue. This first slice does not
use hooks; please identify any design coupling that would accidentally make
TERM correctness depend on stop-hook delivery or continuation behavior.

## Requested fixed response

1. Proven contradiction or ambiguity in the proposed grammar.
2. Smallest dictionary fields needed for safe cross-model use.
3. Negative fixtures that would catch control-plane leakage or silent parsing.
4. Stop-hook coupling risks, clearly separating direct dependency from future
   integration risk.
5. Explicitly non-blocking exclusions.
6. `PREF= target=TERM_NOTATION/1 | preferred|not_preferred|no_preference|undetermined`

Do not infer facts outside this capsule. Label all unproven claims as
hypotheses.
