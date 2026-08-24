# Handoff: synthetic recovery-ledger source plan accepted

Status: `PLAN_ACCEPTED_S1_T1_ONLY`.

The accepted source plan is [`PLAN.md`](PLAN.md), SHA-256
`28459d9494ca6f6936aca5200845a0cf77a2d7116bb9b715abf574725b22702c`.
Its operation record canonical hash verifies. The blocking corrected council
packet SHA-256 is
`aceb72c67c7296c267fb07ff30cff9fe7573b0cf242706c8390c42934f35b74c`.

No implementation file or SQLite fixture has been created. S1 is now ready;
T1 follows S1. Only these files may be added:

- `house/task_spine/recovery_ledger.py`
- `house/task_spine/tests/test_recovery_ledger.py`

The plan's important delta is explicit `reopen(...)` plus persisted canonical
initial-state JSON, its digest, and a genesis digest. Preserve the fixed outer
receipt envelope, accepted-only writes, bounded 64-entry replay, temporary
fixture guard, three-table schema, and 800-line combined source/test cap.

Do not modify the sealed reducer, authority, inbox, controller, CLI, provider,
package, exports, README, zookeeper spec, or `.house-state`. Do not use any real
database, key, package, hardware, Keychain, trusted time, network, worker, or
dispatch surface.

After S1/T1, stop at V1 if hashes or scope drift. Otherwise run the exact
deterministic suite, then build a new sealed candidate packet for C1. Plan
council acceptance is not candidate acceptance.
