# Synthetic Recovery Ledger Candidate Council Packet

Decision question: does this exact candidate implement the accepted synthetic
ledger contract without exceeding
`SYNTHETIC_RECOVERY_LEDGER_LOCAL_TRANSACTION_ONLY`?

## Authority and plan

- Accepted plan SHA-256: `28459d9494ca6f6936aca5200845a0cf77a2d7116bb9b715abf574725b22702c`
- Accepted amendment SHA-256: `66521a326570a0a469c9f0e0382e43a9a4b50d119a71b60986b64b207b524077`
- Amendment council: three `ACCEPT`; one reviewer hash-transcription defect is recorded in `AMENDMENT_COUNCIL_SUMMARY.md`.

## Exact candidate

- `house/task_spine/recovery_ledger.py`: `063f94e98d5c624d60cefab88e0ac7f498fc615d8968a3e2dff3121b6f832ca5`
- `house/task_spine/tests/test_recovery_ledger.py`: `ae8e48473c95fc5c0032b8dd28ef0b7b5f6072bcf135fbe6c3864b1517624db8`
- `house/task_spine/tests/test_recovery_policy.py`: `aaf6ec39c22e0d54f23469914000a103f4ffce584c4706e81e3620acb39d0c15`
- Combined source plus dedicated-test size: 788 lines.

Reviewers must verify these hashes before inspection. The third file may differ
from the original only by the exact-path static-scan compatibility edit allowed
by the amendment.

## Deterministic evidence

`IMPLEMENTATION_VALIDATION.json` records 24 passing required tests, successful
bytecode compilation, `git diff --check`, and warning-as-error focused tests.
The dedicated suite covers the six-transition ceremony, exact accepted
duplicate, challenge/submission conflicts, uncached reducer refusal/replay,
rollback/retry, entry cap, independent structural corruption, nested-receipt
corruption, semantic replay drift, unsafe paths/names/symlink, live inode
replacement, payload cap, and reciprocal source-graph isolation.

## Review limits

Read-only static review only. Do not edit, run tests, open any SQLite fixture,
access runtime state, keys, hardware, Keychain, network, provider, controller,
worker, or CLI. Treat the test record as supplied evidence, not as reviewer
observation.

The candidate is private and test-only. Its temp-root/name/inode checks are not
an OS sandbox. It grants no authority, makes no dispatch, and establishes no
checkpoint protection or recovery readiness. `ACCEPT` authorizes only source
seal/commit/push with this fixed ceiling; otherwise return the smallest bounded
remediation or `NEEDS_REVIEW`.
