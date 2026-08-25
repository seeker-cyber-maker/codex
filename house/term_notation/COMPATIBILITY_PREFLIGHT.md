# TERM notation offline compatibility preflight v1

Status: `FROZEN_SOURCE_ONLY / NOT_READY_NO_DISPATCH`

This is the execution guard for the proposed offline TERM notation experiment.
It freezes a synthetic evaluator-only semantic corpus and checks that the
preflight cannot be mistaken for a live model evaluation.

## What is frozen

- Five comparison conditions: ordinary unmarked language, ordinary readable
  repair, marker-only TERM, full TERM form, and an overcompressed control.
- Eight semantic families, including scope, provenance, compaction, authority,
  and privacy boundaries.
- A canonical semantic hash of the fixture projection.
- An empty qualified-model roster and explicit missing prerequisites.

## What is deliberately absent

No model output, provider request, prompt injection, task state, relay message,
authority decision, or public claim exists here. `require_execution_authority`
always rejects: a later real experiment needs its own sealed manifest,
qualification receipts, evaluator, and human authorization.

## Local check

```bash
python3 -m unittest discover -s house/term_notation/tests -v
```

The canonical fixture hash binds semantic JSON content after parsing; the run
source seal separately binds the exact artifact bytes.
