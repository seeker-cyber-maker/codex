# Synthetic Recovery Ledger Plan Amendment V1

Status: `PROPOSED__STOP_BEFORE_TEST_COMPATIBILITY_EDIT`

Parent accepted plan SHA-256:
`28459d9494ca6f6936aca5200845a0cf77a2d7116bb9b715abf574725b22702c`

## Trigger

The focused S1/T1 candidate passes all six dedicated tests with
`ResourceWarning` promoted to an error and is exactly 800 combined lines. The
unchanged legacy reducer suite then fails its source-isolation assertion because
that assertion forbids the literal reducer module name in every other Python
file. This directly conflicts with the accepted plan's required private adapter
dependency on the sealed reducer.

## Proposed bounded delta

Permit one additional test-only edit to
`house/task_spine/tests/test_recovery_policy.py`. Its production-reachability
scan may exclude exactly these two test-only sanctioned paths in addition to
itself and the reducer:

- `house/task_spine/recovery_ledger.py`
- `house/task_spine/tests/test_recovery_ledger.py`

Because the new adapter's reciprocal source-isolation test rejects the literal
adapter name in all other Python files, the legacy test must construct those two
exact basenames from fixed string fragments. This is only a static scan
compatibility mechanism; it does not import or expose the adapter.

No other source, scope, receipt, authority, claim, or test limit changes. The
legacy test must still reject all other Python references to the reducer, and
the new dedicated test must still reject all other Python references to the
adapter. The complete deterministic suite must pass after the edit.

## Frozen candidate inputs

- `recovery_ledger.py`: `063f94e98d5c624d60cefab88e0ac7f498fc615d8968a3e2dff3121b6f832ca5`
- `test_recovery_ledger.py`: `5a55876977f0d2068361fe25f7f8c0b6734bf02fe2f2d67072290e29229fccab`
- unchanged `test_recovery_policy.py`: `37e08de7c2ed774bdabcb9e25fcbf7704502ad844511bf0d723bfa68da2ae9aa`

## Gate

No edit to the legacy test is authorized unless the amendment council accepts
this exact amendment. An acceptance authorizes only that narrow compatibility
edit and deterministic rerun; it does not promote or seal the candidate.
