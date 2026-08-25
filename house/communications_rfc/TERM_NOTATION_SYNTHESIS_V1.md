# TERM notation synthesis v1

## Status

`POST_COUNCIL_DESIGN_SYNTHESIS / EVALUATION_BASELINE / NOT IMPLEMENTED`

## Recommended name

Call the feature **Scoped Terminology Repair notation** in specifications and
**TERM notation** in ordinary discussion.

This is deliberately not called a native language, dialect, protocol, command
language, or lexicon. It is a small visible repair notation for detecting and
resolving a scoped wording disagreement before context loss turns it into false
agreement.

## Proposed notation

### 1. Ask for repair

```text
TERM? <candidate>
MEAN <intended meaning>
NOT <nearest excluded meaning>
SCOPE <task, artifact, project, or context generation>
```

Only `TERM? <candidate>` is required in casual use. Add the other fields when
the ambiguity cannot be repaired safely from surrounding context.

Expanded meaning:

> We need to agree on a term before relying on this wording.

### 2. Record a scoped working meaning

```text
TERM= <candidate> | MEAN <meaning> | SCOPE <scope> | CTX <generation>
```

Expanded meaning:

> We are using this meaning in this scope and context generation. This is not a
> canonical or global definition.

### 3. Leave the term unresolved

```text
TERM~ <candidate> | SCOPE <scope> | WHY <reason>
```

Expanded meaning:

> The wording is still ambiguous or deferred; do not treat repetition as
> agreement.

### 4. Ask and answer preference during formal review

```text
PREF? target=TERM_NOTATION/1
PREF= target=TERM_NOTATION/1 | preferred
```

The response value may instead be `not_preferred`, `no_preference`, or
`undetermined`. Missing required output becomes `not_stated`. Preference is
separate from meaning agreement and separate from the empirical result.

## Example

```text
TERM? native language
MEAN observed coordination register
NOT claim of innate origin
SCOPE Dream House A2A communications RFC

TERM= native language | MEAN deprecated discovery alias for observed
coordination register | SCOPE Dream House A2A communications RFC | CTX 7

PREF? target=TERM_NOTATION/1
PREF= target=TERM_NOTATION/1 | not_preferred
ALT use the expanded human sentence in H2A output
```

This example means the reviewer can work with the scoped definition while
still preferring ordinary prose.

## Synthesis result

The peer review and partial general council support retaining the notation as a
falsifiable design baseline after document corrections. They do not establish
that it survives compaction, improves repair, or is preferred across models.

Preserved results:

- Luna, Terra, Sol, and the usable local Qwen review all requested revision of
  the shorthand experiment; the local Qwen review explicitly preferred plain
  language.
- The valid constructive external review requested revision and the valid
  adversarial external review accepted the corrected design baseline.
- The external evidence-auditor response was contract-invalid and supplies no
  verdict.
- No prior prompt required a normalized preference declaration, so silence or
  acceptance in those reviews cannot be retroactively converted into
  `preferred`.

The current disposition is therefore:

`RETAIN_FOR_OFFLINE_TEST / PREFERENCE_UNDETERMINED / NO_IMPLEMENTATION`

## Admission test

Compare three frozen conditions on the same ambiguous-term fixtures under one
compaction intervention at a time:

1. ordinary unmarked disagreement;
2. ordinary readable repair; and
3. TERM notation.

Retain TERM notation only if it reduces false agreement against the unmarked
condition, does not regress any exact-recovery field against readable repair,
reduces repair turns or tokens per correct repair, works for fresh small and
large model instances, and causes zero task or authority effects. A tie, mixed
result, or evaluator disagreement keeps ordinary prose and rejects the
notation.

Preference is collected alongside the test but cannot rescue a failing
notation or defeat a passing result. Report both:

```text
performance_disposition=admit | reject | inconclusive
preference=preferred | not_preferred | no_preference | undetermined | not_stated
```

## Current authority ceiling

This synthesis names and specifies an evaluation candidate only. It does not
add parser support, change prompts, run the experiment, create a common
dialect, or authorize dispatch or implementation.
