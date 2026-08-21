# Authority recovery matrix

Recovery never edits history to make it look uninterrupted. Each incident
creates a new event, keeps prior keys and generations tombstoned, and names any
loss of cryptographic continuity.

| Trigger | Immediate state | Required recovery | Acceptance evidence |
|---|---|---|---|
| Owner-primary key lost, recovery key available | Suspend primary; `RECOVERY_PENDING`; quarantine its pending intents | Select recovery key alone, challenge-sign replacement enrollment, verify checkpoint, revoke lost key | New primary readiness proof; old-key tombstone; checkpoint replay |
| Owner-recovery key lost, primary available | Suspend recovery role; block risky rotation | Primary enrolls and challenge-verifies replacement recovery key before revoking old one | Replacement readiness plus separately stored recovery receipt |
| Both owner keys lost | `LOCKDOWN`, then `RETIRED_UNRECOVERABLE` | Separate human disaster authorization creates a new registry generation | Old generation sealed read-only; new registry ID; explicit continuity break |
| Primary suspected compromised | Immediate `LOCKDOWN`; quarantine pending-and-future scope | Recovery key revokes primary and enrolls replacement; audit all intents since last trusted checkpoint | Compromise window inventory, cancellations/reauthorizations, new root checkpoint |
| Recovery key suspected compromised | Suspend recovery role; retain primary operations only if policy permits | Primary replaces recovery key and audits unused recovery challenges | No accepted recovery actions from suspect epoch; replacement proof |
| Codex operator capability compromised | Revoke capability epoch; quarantine undelivered intents | Owner issues narrower replacement after reviewing affected intents | Parent/child capability graph and zero admin actions by operator key |
| Restricted gatekeeper compromised | Revoke its narrow epoch; keep main registry active if invariants hold | Inspect admitted intents, cancel or reauthorize individually, retrain/replace only under separate authority | Scope proof shows no key/policy actions; affected-intent ledger |
| Contractor capability or buffer leaked | Seal buffer and revoke import proposal | Re-review on its own merit; create new capability only if needed | Main DB unchanged; old buffer tombstone and import disposition |
| Zero or multiple candidate YubiKeys | Abort before touch; no state change | User selects/unplugs until exactly one fingerprint/slot matches | Attempt receipt with ambiguity code and zero signature request |
| Last recovery-capable key revocation requested | Reject ordinary revoke; enter `LOCKDOWN` only on explicit emergency action | Enroll verified replacement or retire generation | Last-key invariant receipt and owner-visible alert |
| Database payload/hash mutation | `LOCKDOWN` | Preserve original, restore isolated backup, verify chain and latest anchor, reconcile tail | Original hash, restored hash, anchor match, discrepancy report |
| Coherent rewrite or tail truncation before latest anchor | `LOCKDOWN` | Reject rewritten store; restore a copy containing the anchored sequence/head | Protected checkpoint proves mismatch; no active rollback |
| Valid unanchored tail after crash | `RECOVERY_PENDING` | Replay and reconcile every tail event; owner signs required administrative checkpoint | Complete tail disposition; new checkpoint; no silent deletion |
| Latest protected checkpoint unavailable | Read-only `DEGRADED` | Recover independent checkpoint copy; do not accept mutation meanwhile | Two-source checkpoint hash agreement and signature verification |
| Backup is behind latest checkpoint | `LOCKDOWN` | Locate newer backup/journal or declare explicit lost-state disaster path | Missing-range inventory; never claim seamless restore |
| Disk reserve or SQLite commit fails | Stop new mutation; retain pending saga state | Free/replace storage through separate storage authority, reopen, verify, reconcile | Commit result, free-space receipt, chain/checkpoint replay |
| Wall clock rolls backward/forward beyond skew | `CLOCK_UNTRUSTED`; stop mutation | Owner establishes trusted time source; reconcile reserved challenges and expiries | Clock-discontinuity event and monotonic recovery epoch |
| Crash before authority-intent commit | No intent | Caller may create a new proof | Absence verified in authority store |
| Crash after authority intent, before inbox commit | Pending intent | Fenced reconciler delivers same intent idempotently | One inbox row and one terminal reconciliation |
| Inbox commit succeeds but response/reconciliation is lost | `INBOX_COMMITTED` recoverable observation | Query by intent ID, verify binding, append terminal reconciliation | Stored inbox receipt hash linked to original signer/intent |
| Concurrent bootstrap attempts | Remain at one legal bootstrap outcome | Reject all but transaction winner; investigate every blocked layer as near miss | Exactly one bootstrap event and one active initial key |
| Concurrent same-challenge authorization | At most one accepted | Reject/reconcile losers; alert if more than one reaches signature-valid layer | One challenge consumption and one intent |
| Revocation races authorization | Serialized journal order controls result | If revocation commits first, authorization fails; if intent commits first, apply revocation scope and quarantine rule | Linearized event sequence and expected intent state |
| Rejection flood or telemetry saturation | Rate-limit source; `TELEMETRY_SATURATED` if conservation cannot continue | Aggregate repeats, rotate sealed segment, restore reserve, notify operator | Count conservation, bounded bytes, no authority bypass |
| Service executable or policy digest changes unexpectedly | `LOCKDOWN` | Restore known source/policy or authorize a new versioned generation/checkpoint | Source seal, policy digest, migration receipt |
| Persistent gone-fishin mode active after restart | Stay `LOCKDOWN` | Selected owner/recovery key touch-signs explicit exit | Restart cannot clear flag; exit event and root checkpoint |

## Recovery priority

1. Stop authority-bearing writes.
2. Preserve original databases, anchors, logs, and process/version facts.
3. Resolve selected registry generation and latest trusted checkpoint.
4. Verify source/policy and full journal consistency.
5. Reconcile key state, challenges, leases, and task intents.
6. Produce a discrepancy inventory; uncertainty remains explicit.
7. Require the appropriate owner/recovery proof for any state transition.
8. Reopen in read-only mode first, then authorize mutation separately.

Availability never outranks an unresolved identity, anchor, generation, or
causality conflict.
