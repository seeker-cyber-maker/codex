# User decision addendum: TERM notation preference

## Status

`CONTROLLING_POST_COUNCIL_DESIGN_DECISION / DOCUMENT_ONLY / NOT_IMPLEMENTED`

This addendum preserves the user's decision after the sealed peer review and
general council. It does not rewrite either run.

## Decision

When a formal review or experiment requires a reviewer to assess the proposed
shorthand, the request must explicitly ask whether that reviewer prefers it.
The response must state the preference rather than leaving the chair to infer
it from correct use, an acceptance verdict, silence, or surrounding prose.

The required question is:

```text
PREF? target=TERM_NOTATION/1
```

The permitted explicit responses are:

```text
PREF= target=TERM_NOTATION/1 | preferred
PREF= target=TERM_NOTATION/1 | not_preferred
PREF= target=TERM_NOTATION/1 | no_preference
PREF= target=TERM_NOTATION/1 | undetermined
```

If the required field is absent, the wrapper records `not_stated`. It never
turns missing output into a preference.

## Boundary

Preference is attributed advisory evidence, not a vote or correctness signal.
It cannot accept the notation, create a dialect, change task state, grant
authority, or override the empirical admission gate. A reviewer may agree on a
term's scoped meaning while preferring ordinary prose.

## Evidence-source disposition

The user's controlling disposition for YouTube video `6XrkGK9mqsE` is:

`VIDEO_INFERENCES_NOT_ADMISSIBLE / OFFICIAL_OPENAI_HUGGING_FACE_REPORTS_ONLY`

The video may help locate a claim but contributes no evidence weight and no
independent corroboration. Only separately bound official OpenAI or Hugging
Face material may support an incident claim in this branch.
