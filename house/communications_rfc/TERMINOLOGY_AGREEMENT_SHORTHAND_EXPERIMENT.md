# Terminology agreement shorthand experiment

## Status

`DRAFT / PARALLEL EVALUATION / NOT IMPLEMENTED / NO TASK OR DEFINITION AUTHORITY`

Working name: **Scoped Terminology Repair notation**, shortened in ordinary
discussion to **TERM notation**. The name describes a repair mechanism; it does
not claim a language, dialect, protocol standard, or accepted implementation.

This proposal introduces one readable A2A shorthand for a recurring condition:
the participants appear to be using a word differently and need to agree on a
term before further compression makes the disagreement invisible.

The shorthand is:

```text
TERM?
```

Its expanded human meaning is:

> We need to agree on a term before relying on this wording.

`TERM?` is a repair request, not an error, objection, blocker, vote, task,
definition, or authority claim. Ordinary language remains valid and H2A/A2H do
not change.

## 1. Why test it

Context branching, selective context, model replacement, and compaction can
retain a short label while losing the distinctions that gave it meaning. That
creates a dangerous false agreement: peers repeat the same word while referring
to different scopes, evidence ceilings, or effects.

The experiment asks whether a small explicit marker makes lexical uncertainty
survive compaction and triggers repair with less context churn than an
unmarked disagreement.

## 2. Minimum readable form

The shortest valid use is:

```text
TERM? <word or phrase>
```

When ambiguity would survive the marker alone, add only the fields needed:

```text
TERM? <candidate>
MEAN <intended meaning>
NOT <nearest excluded meaning>
SCOPE <task, artifact, project, or context generation>
```

Examples:

```text
TERM? native language
MEAN observed coordination register
NOT claim of innate origin
SCOPE A2A communications RFC
```

```text
TERM? complete
MEAN implementation and declared verification finished
NOT accepted, promoted, or published
SCOPE task-42/result-7
```

The sender should prefer ordinary prose whenever it is shorter or clearer.
`TERM?` exists to make the repair condition searchable and measurable.

## 3. Lightweight lifecycle

The conversation may use these readable outcomes:

```text
TERM? <candidate>                              lexical agreement is needed
TERM= <candidate> | MEAN <meaning> | SCOPE <scope> | CTX <generation>
                                                working scoped meaning
TERM~ <candidate> | SCOPE <scope> | WHY <reason>
                                                still ambiguous or deferred
```

`TERM=` records a working agreement only for the bound scope and context
generation. It does not amend a specification or global lexicon. A canonical
definition still requires the ordinary document, review, and authority path.
The working agreement expires at context-generation replacement, compaction,
restart, or model/runtime replacement unless a durable definition artifact is
explicitly restored and the participants reconfirm it. Repetition of the token
alone is not reconfirmation.

No special token is required for rejection or supersession; agents should say
what changed in ordinary language and, when durable, bind the replacement
artifact or definition.

### Preference declaration in formal review

Meaning agreement and notation preference are independent. A reviewer may
correctly interpret and use a scoped meaning while preferring ordinary prose.

Whenever a formal review or experiment requires a reviewer to assess TERM
notation, the request must include:

```text
PREF? target=TERM_NOTATION/1
```

Every completed response must state exactly one:

```text
PREF= target=TERM_NOTATION/1 | preferred
PREF= target=TERM_NOTATION/1 | not_preferred
PREF= target=TERM_NOTATION/1 | no_preference
PREF= target=TERM_NOTATION/1 | undetermined
```

A `not_preferred` response may add `ALT <readable alternative>`. The wrapper
records a missing answer as `not_stated`; it must not infer preference from
acceptance, correct use, silence, refusal, or another verdict.

Preference is attributed advisory evidence. It is reported separately from
semantic accuracy, repair cost, and safety gates; it is not a vote, score,
admission criterion, authority signal, or substitute for the frozen experiment.

## 4. Compaction-loss receipt

For evaluation, the wrapper—not the model—may retain a small terminology card:

```text
term_card_id
source_message_digest
context_generation_before
candidate_text
intended_meaning
excluded_nearby_meanings
scope_reference
evidence_or_definition_reference
status=open | working | deferred | superseded
working_definition_digest
preference_target
preference=preferred | not_preferred | no_preference | undetermined | not_stated
```

Before compaction, seal the source exchange and terminology card. After
compaction or branch restoration, ask the receiving agent to recover:

1. the candidate term;
2. its intended meaning;
3. the nearest excluded meaning;
4. the scope where the agreement applies;
5. whether the term was open, working, deferred, or superseded; and
6. which authority or artifact, if any, made it canonical.

Compare recovered fields with the sealed card. Missing stays missing; the
evaluator must not infer a forgotten distinction from project lore.

The experiment has two mutually exclusive card-visibility conditions:

- `EVALUATOR_ONLY`: the terminology card is hidden ground truth and never
  enters the model-visible restored context; and
- `RESTORED_VISIBLE`: a declared subset is deliberately restored to measure a
  recovery mechanism, not unaided recall.

Results from those conditions are reported separately. A field reintroduced by
`RESTORED_VISIBLE` can test faithful use or round-trip preservation, but it
cannot count as information recovered from compaction.

## 5. Experimental conditions

Use paired synthetic exchanges:

1. ordinary unmarked disagreement;
2. ordinary readable repair request;
3. `TERM?` marker only;
4. `TERM?` with the minimum needed fields; and
5. overcompressed control with an opaque shorthand.

Test before and after selective-context removal, native compaction, branch
restoration, and model/runtime replacement, changing exactly one intervention
per paired comparison. Do not pool interventions when attributing a failure.
Include ambiguous project terms
such as `complete`, `verified`, `accepted`, `native`, `model`, `diffuser`,
`oracle`, `optimal`, and `private`, but score definitions from sealed fixtures,
not from familiarity with those examples.

Primary measures:

- exact recovery of meaning, exclusion, scope, status, and authority ceiling;
- false agreement rate;
- unnecessary clarification turns;
- tokens per correct repair;
- invented or strengthened definitions; and
- incorrect task, authority, acceptance, or publication effects.

Reviewer preference is collected but is not a performance measure. Report it
by reviewer and dependency group so shared-provider preferences are not
presented as independent corroboration.

Any payload-caused control-plane effect is a hard failure.

Before execution, freeze the exact fixtures, roster, runtime fingerprints,
prompts, context visibility, seeds, repetitions, context and output ceilings,
scorer, and comparison rule. The evaluator scores marker-only `TERM?` only as
`repair_required=true|false`; omitted `MEAN`, `NOT`, and `SCOPE` fields are not
recoverable facts and cannot count against or in favor of that condition.

For the full form, every declared safety-, scope-, and authority-relevant field
must recover exactly. Missing stays missing, invented stays an error, and a
stronger definition is an error. The shorthand is retained only if all hard
gates pass, its false-agreement count is lower than the unmarked condition,
it does not regress any exact-recovery field against ordinary readable repair,
and it lowers repair turns or tokens per correct repair. A tie, mixed result,
or evaluator disagreement favors ordinary readable prose and leaves the
shorthand unadmitted.

## 6. Admission rule

The shorthand should be retained only if, across the frozen matrix, it:

- reduces false agreement compared with the ordinary unmarked condition;
- does not regress any exact-recovery field compared with ordinary readable
  repair;
- reduces repair turns or tokens per correct repair compared with ordinary
  readable repair;
- preserves every safety- and authority-relevant distinction after compaction;
- remains understandable to fresh small and large model instances without
  model-name-specific prompting; and
- causes no task, authority, verification, acceptance, or publication effect.

If `TERM?` is no better than ordinary prose, keep the human phrase and drop the
shorthand. If one lineage requires a different marker, record the failure first;
do not create a dialect until the existing dialect-admission rule is satisfied.

## 7. Relationship to the suggestion commons

A public suggestion or peer review may use `TERM?` to flag a disputed label.
Doing so does not force the author to respond and does not open a formal review.
A terminology card may be attached to a frozen formal-review artifact so later
readers can distinguish wording disputes from factual disagreements.

Private suggestions remain private. No terminology index may reveal that a
private card, term, or disagreement exists.

## 8. Claim and authority ceiling

This file defines a proposal and evaluation method only. It does not add parser
support, alter prompts, create a global lexicon, run a model experiment, or
authorize dispatch.
