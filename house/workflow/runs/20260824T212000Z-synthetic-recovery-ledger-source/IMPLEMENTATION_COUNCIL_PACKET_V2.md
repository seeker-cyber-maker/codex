# Synthetic Recovery Ledger Candidate Council Packet V2

Decision question: after the accepted V2 bounded remediation, does this exact
candidate meet only
`SYNTHETIC_RECOVERY_LEDGER_LOCAL_TRANSACTION_ONLY` and qualify for a source
seal/commit/push?

## Authority chain

- plan: `28459d9494ca6f6936aca5200845a0cf77a2d7116bb9b715abf574725b22702c`
- compatibility amendment: `66521a326570a0a469c9f0e0382e43a9a4b50d119a71b60986b64b207b524077`
- remediation amendment V2: `3879760df109d9d7af8fb47b60ede81ae5b0a21dc0d07610ff0ccfd45c63250e`
- V2 council: three `ACCEPT` responses.

## Exact candidate

- `house/task_spine/recovery_ledger.py`: `5f47b675d9cde29e4722e1ae4156e79af346a2069826f6019ac6eb74d85fcf6d`
- `house/task_spine/tests/test_recovery_ledger.py`: `7bd03abfabdd8faa7afe375addc6bc8718a72189a74e656003a0d74a5c8b87ca`
- `house/task_spine/tests/test_recovery_policy.py`: `aaf6ec39c22e0d54f23469914000a103f4ffce584c4706e81e3620acb39d0c15`
- source plus dedicated test: 792 lines.

Reviewers must reproduce these hashes. V2 adds exact closed validation of the
stored reducer receipt and a coherent-substitution test. The duplicate path
still must not invoke a fresh reducer candidate.

## Supplied validation

`IMPLEMENTATION_VALIDATION_V2.json` records 25 passing required tests,
warning-as-error focused execution, compilation, line ceiling, and diff check.
This is supplied evidence, not reviewer observation.

## Review limits and ceiling

Read-only static review only. Do not edit, run tests, open SQLite, or access
runtime state, network, keys, hardware, provider, controller, worker, or CLI.

The candidate does not authenticate SQLite against a coordinated full-history
rewrite, provide an OS sandbox, prove fsync/crash durability, protect a
checkpoint, grant authority, dispatch, or establish recovery readiness.
`ACCEPT` authorizes only source seal, scoped commit, and private backup push.
Otherwise return the smallest bounded remediation or `NEEDS_REVIEW`.
