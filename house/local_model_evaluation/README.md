# Shared local rubric evaluation contract

Status: `SOURCE_ONLY / NO_MODEL_EXECUTION / NO_PROMOTION`

This is the reusable shell around the four-case rubric smoke test first used
by an instructor-style local evaluator.  The fixture corpus, metrics, and
acceptance semantics are independent of a candidate model.  A model-specific
adapter declares only how to render the frozen prompt and parse a constrained
score result.

Model identity is deliberately absent from the scoring surface.  An actual
model/runtime binding, its artifact fingerprint, decoding settings, and an
availability receipt belong to a future sealed run record, not to this shared
contract.

## Current adapters

- `instructor-bracket-result-v1`: instructor-style single-user rendering with
  a bracketed integer result.
- `chat-json-score-v1`: system/user chat rendering with a closed JSON integer
  score.
- `chat-json-score-no-thinking-v1`: the same closed JSON score, with an
  explicitly documented chat-template no-thinking generation control.

Both are `DECLARED_UNQUALIFIED`: neither is a worker route or evidence that a
particular local model is suitable.

## Local check

```sh
python3 -m unittest discover -s house/local_model_evaluation/tests -v
```

The validator rejects every attempt to claim execution, model loading,
training, worker dispatch, or candidate promotion.  A future inference run
needs a separately sealed model-binding manifest and an explicit authorization.

## Sealed smoke-run driver

The execution driver is deliberately outside this source-only package:
`house/workflow/run_local_rubric_smoke.py`. It accepts only the closed
inference-only manifest surface, verifies the prebound artifact hashes, and
writes one receipt atomically. It never imports the Dream House control plane
and cannot promote or dispatch a candidate. The first completed four-case
example is recorded at
`house/workflow/runs/20260825T225000Z-local-rubric-candidate-b-onecase/`.
