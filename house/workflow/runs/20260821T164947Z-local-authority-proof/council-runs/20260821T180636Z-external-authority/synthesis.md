# Outside authority-boundary council synthesis

## Outcome

**ACCEPT progression to a separately authorized ceremony-design operation.**
Keep implementation, real-key enrollment, YubiKey access, production authority,
service changes, and live Codex/worker integration blocked.

The outside run attempted three independent provider roles over transport
SHA-256 `0fc395cee0c76271e405624dc32ae02ae663e12f3150a18d3285c7bf0d2283fa`:

- ClinePass / `cline-pass/deepseek-v4-flash`: initial response was substantive
  but truncated at 4,096 completion tokens; a preserved same-model 8,192-token
  retry completed and accepted the design stage.
- OpenRouter explicit-free: `google/gemma-4-31b-it:free` returned 429, then the
  declared `nvidia/nemotron-3-super-120b-a12b:free` fallback completed and
  requested one journal-corruption test.
- OpenCode Go: `deepseek-v4-flash` returned HTTP 200 with no visible content;
  declared fallback `qwen3.8-max` returned HTTP 500. This role remains failed.

The denominator is therefore three attempted outside roles, two substantive
completed reviews after the bounded retry, and one failed role. It is not a
three-reviewer external consensus.

## Confirmed observations

- DeepSeek independently found the strict signature, time, action, binding,
  permission, revocation, and replay checks sufficient for the offline
  candidate's narrow design-stage claim.
- DeepSeek independently preserved the same promotion blockers: hostile local
  writes, multi-process races, crash recovery, rejection retention, key
  custody/recovery, hardware behavior, and portable interoperability.
- Nemotron distinguished the sealed validation reports from independently
  reproduced execution and refused production or hardware claims.
- Nemotron's requested decisive test directly mutate-and-verify the journal is
  substantively present in the sealed suite:
  `test_second_bootstrap_and_corrupted_journal_fail_closed` changes an existing
  event's `payload_json`, commits it, and requires `verify_journal()` to fail.
  Flipping `event_sha256` instead exercises the same recomputed-hash mismatch
  and would not address coherent rewrite or truncation.

## Disagreements and resolution

Nemotron selected `schedule exactly one decisive local test`, while DeepSeek
selected `accept`. This is not a decision-bearing disagreement because the
named corruption behavior is already an explicit source fixture and reported
passing gate. No new execution is claimed from the outside review itself.

The external reviews did not challenge the local council's terminology finding
that the generated signature fixture is a same-library round trip rather than
an independent fixed known-answer vector. Silence is not contrary evidence;
the fixed-vector requirement remains a design input.

## Claims rejected or narrowed

- The outside review is not three-of-three: one OpenCode role failed.
- Journal integrity remains internal consistency, not tamper-proof history.
- The external reviewers did not reproduce the 51-test run.
- Provider cost is not literally zero in the receipts. OpenRouter reported
  zero; ClinePass reported accounting values of `0.0114576` and `0.011484`,
  totaling `0.0229416`, across the truncated attempt and its completion retry.
  The lane was configured as an existing subscription rather than a direct
  paid API, but the manifests do not prove zero economic cost.

## Decision and confidence

Decision: **accept design-only progression; retain every implementation and
operation gate.**

Confidence is moderate-to-high for that narrow decision. The useful external
responses came from distinct DeepSeek and Nemotron model families and matched
the source-level local findings. Confidence is reduced by one failed provider
role, shared transport evidence, no independent test execution, and the fact
that the ClinePass completion is a retry of its truncated response rather than
a new reviewer.

## Mandatory next-design inputs

1. Authenticated bootstrap, enrollment, rotation, compromise recovery, loss
   recovery, and last-valid-key behavior.
2. Durable authority/inbox saga states and proof-to-inbox causality.
3. Protected journal anchoring or a permanently narrowed consistency-only
   claim plus an OS-enforced sole-writer boundary.
4. Independent fixed P-256 canonicalization/interoperability vectors.
5. Preregistered multi-process, crash, disk, and replay boundary tests.
6. Rejection quotas, retention, monitoring, and exhaustion behavior.

## Provenance and limitations

The redacted packet was explicitly `cloud-ok`; prior local reviewer conclusions
were excluded from round one. Provider and fallback identities, failures,
token usage, latency, and reported accounting are retained in the manifests.
No credentials, absolute local paths, real keys, hardware operations, service
changes, or implementation authority were sent. A post-dispatch privacy scan
found one non-secret fixture requester label, `human:tiga`, inherited from the
attached test source. No credential, key material, or filesystem locator was
associated with it; the disclosure is retained here rather than concealed.

**DECIDE: authorize or decline the separate design-only ceremony operation.**
