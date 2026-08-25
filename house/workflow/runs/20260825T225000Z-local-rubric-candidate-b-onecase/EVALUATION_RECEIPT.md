# Local rubric candidate B: four-case inference receipt

## Scope

This run evaluates `local-rubric-candidate-b` only as a bounded local rubric
runtime/format smoke test. It is not a worker qualification, routing decision,
training result, provider call, task dispatch, or candidate promotion.

## Sealed inputs

- Execution manifest: `EXECUTION_MANIFEST_V2.json`
  (`541fc5327fabb84018ec2922fb59ee0bd4ac2e8cc26114c0f5fdb5ef8a28b56e`)
- Candidate prebinding: `../20260825T224000Z-local-rubric-candidate-b-prebinding/candidate_binding.json`
  (`b06ab02ddf7b237f358d425c416aa3a1824b1afd1167537830b3ca86c005aabf`)
- Frozen fixtures: four manifest-listed cases from
  `house/local_model_evaluation/rubric_fixtures_v1.json`.
- Adapter: `chat-json-score-v1`; the scorer received no model name or model
  path.

## Actual receipt

`INFERENCE_RECEIPT_V2.json` records all eight prebound artifact-file hashes as
matching before the model was loaded. With MLX `0.31.2`, mlx-lm `0.31.3`,
`fix_mistral_regex: true`, deterministic temperature `0.0`, seed `20260825`,
32 generated tokens maximum, and zero retries, all four cases produced a
closed JSON score.

| Metric | Result |
| --- | --- |
| Cases | 4 |
| Parse rate | 1.00 |
| Score agreement | 1.00 |

The specific outputs and expected-score sets are in the JSON receipt. They are
not a general quality claim: this corpus is deliberately too small and narrow
for that.

## Attempt ledger

1. The first ad-hoc four-case command printed streamed output but did not
   persist it. Its display was truncated, so it is **unrecoverable and not
   counted**.
2. The first sealed-runner invocation stopped before model loading because a
   direct-file invocation did not include the repository package on
   `sys.path`.
3. The second sealed-runner invocation reached generation but stopped before a
   receipt because installed mlx-lm expects a `sampler`, not a `temp` keyword.
4. The final invocation uses the explicit zero-temperature sampler and wrote
   `INFERENCE_RECEIPT_V2.json` atomically.

The two failed runner invocations yielded no scored cases or output receipt.
They are retained here as implementation diagnostics, not merged into the
candidate result.

## Disposition

`RUNTIME_AND_FORMAT_EVIDENCE_ONLY_NOT_A_WORKER_QUALIFICATION`.

Any later role qualification needs a separate, held-out evaluation plan with
task-appropriate metrics, runtime/resource evidence, and the existing Dream
House admission gates.
