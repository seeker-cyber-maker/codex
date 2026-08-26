# Local rubric candidate C: template-control comparison

## Scope

This is inference-only runtime/format evidence for
`local-rubric-candidate-c`. It does not qualify a worker, authorize routing,
train weights, call a provider, dispatch work, or promote a candidate.

## Sealed comparison

Both runs used the same frozen four fixtures, rubric, closed JSON score parser,
temperature `0.0`, seed `20260825`, maximum 32 generated tokens, zero retries,
and verified eight prebound artifact-file hashes.

| Run | Adapter | Parse rate | Score agreement | Interpretation |
| --- | --- | ---: | ---: | --- |
| Default template | `chat-json-score-v1` | 0.00 | 0.00 | Template opened a reasoning block; the 32-token ceiling captured only its reasoning prelude, so no JSON score was emitted. |
| Explicit no-thinking control | `chat-json-score-no-thinking-v1` | 1.00 | 0.75 | The documented template control restored the closed JSON surface; one arithmetic case was scored `2` where the frozen expected set is `[1]`. |

The default evidence remains at
`../20260825T234500Z-local-rubric-candidate-c-fourcase/INFERENCE_RECEIPT.json`.
The controlled receipt is `INFERENCE_RECEIPT.json` in this directory. The
adapters differ only in the explicit template generation control; neither
changes the rubric, parser, fixtures, decoding settings, or acceptance ceiling.

## Disposition

`RUNTIME_AND_FORMAT_EVIDENCE_ONLY_NOT_A_WORKER_QUALIFICATION`.

The no-thinking template control is reusable for local chat templates that
document that control. It is not a silent model-specific exception. A future
held-out, role-specific evaluation would need to decide whether 0.75 on this
tiny smoke set is acceptable; it is not sufficient evidence to do so.
