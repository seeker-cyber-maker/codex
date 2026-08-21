# Preregistered authority failure-test plan

No test in this plan was executed during the design run. Test IDs, invariants,
and pass criteria are frozen before implementation so later results cannot move
the goalposts.

## Test stages

| Stage | Surface | Authority needed |
|---|---|---|
| 0 | Pure canonicalization, signature-vector, schema, and state-machine fixtures | Local test code only |
| 1 | Single-process temporary authority/inbox databases | Local test code only |
| 2 | Multi-process races, kill points, disk/clock fault injection | Separate implementation-test authorization |
| 3 | Dedicated-user service, IPC, permissions, backup and anchor recovery | Separate OS/service authorization |
| 4 | Software PIV emulator or test-only signer interoperability | Separate dependency/component intake |
| 5 | Physical owner/recovery YubiKey qualification | Explicit hardware/key authorization |
| 6 | Full disposable disaster-recovery drill | Explicit drill plan and human approval |

Stages do not imply promotion. Each stage must seal its own source, environment,
raw results, negative cases, and independent replay.

## Frozen tests

| ID | Fault or experiment | Pass criterion | Claim impact on failure |
|---|---|---|---|
| FV-01 | Verify published deterministic software vector in candidate verifier and independent implementation | Exact canonical bytes/digest/key ID; signature accepted by both | Portable-signing claim blocked |
| FV-02 | Run every malformed/canonicalization/high-S negative vector | Every vector rejected with frozen error class and zero mutation | Signing profile blocked |
| FV-03 | Change each domain/binding field one at a time | Digest changes and original signature fails | Cross-context isolation blocked |
| BS-01 | Launch N concurrent bootstrap attempts against one empty registry | Exactly one bootstrap event/key; all losers fail; every attempt accounted | Bootstrap blocked; RED incident |
| RP-01 | Launch N processes with one reserved challenge/proof | Exactly one accepted consumption and at most one intent | Replay boundary blocked; RED incident |
| RV-01 | Race authorization against suspension/revocation at controlled commit barriers | Result matches total journal order; pending intent scope is exact | Revocation model blocked |
| DG-01 | Attempt child capabilities with superset action, resource, lifetime, depth, generation, or non-delegable right | Every expansion rejected before persistence | Delegation blocked |
| SG-01 | Kill at every authority/inbox saga boundary, including response loss | One durable intent, at most one inbox row, one reconciled terminal receipt | Durable causality blocked |
| SG-02 | Reuse idempotency key with identical and conflicting content | Identical returns same intent; conflict fails with zero extra effect | Idempotency blocked |
| SG-03 | Revoke signer while intent is pending, leased, and committed | Pending/leased quarantine according to scope; committed stays historical | Compromise containment blocked |
| JR-01 | Mutate payload, kind, sequence, previous hash, and event hash independently | Full verification fails before mutation access | Consistency claim blocked |
| JR-02 | Coherently rewrite chain or truncate before protected checkpoint | Checkpoint comparison detects mismatch and enters lockdown | Tamper-evidence claim blocked |
| JR-03 | Crash after journal tail commit but before administrative checkpoint | Tail is classified unanchored and explicitly reconciled; never silently active/deleted | Anchor recovery blocked |
| LK-01 | Request revocation of last recovery-capable key through every interface | Ordinary revoke rejected; only explicit lockdown/retirement path remains | Last-key safety blocked; RED incident |
| DV-01 | Present zero, one wrong, and two matching hardware/emulated devices | Zero signature requests until exactly one fingerprint/slot is selected | Device ceremony blocked |
| CK-01 | Move clock backward/forward across skew, expiry, and durable max-seen time | Mutation stops in `CLOCK_UNTRUSTED`; no challenge reuse | Freshness claim blocked |
| ST-01 | Fill authority, inbox, anchor, and telemetry storage at each commit point | No false terminal success; reserve permits incident receipt; restart reconciles | Storage safety blocked |
| TM-01 | Flood repeated and unique invalid requests beyond hot-segment ceiling | Repeat counts conserved, bytes bounded, segments sealed, saturation stops admin writes | Monitoring bound blocked |
| OS-01 | Contractor/model process opens or modifies DB/anchor paths directly | OS denies access; attempt becomes near miss; service remains consistent | Sole-writer claim blocked |
| OS-02 | Send malformed, oversized, unknown-field, and arbitrary-SQL IPC messages | Rejected before mutation/parser expansion; bounded error metadata only | Service boundary blocked |
| BK-01 | Restore good, corrupt, rewritten, and anchor-behind backups in isolation | Only exact compatible backup activates; originals preserved; gaps explicit | Restore claim blocked |
| KY-01 | Rotate primary and recovery keys through staged readiness and old-key suspension | Replacement verified before old revoke; epochs/challenges never reused | Rotation blocked |
| KY-02 | Simulate loss of both owner keys | No cryptographic recovery claim; old generation retires and new ID is required | Honest continuity invariant blocked if bypassed |
| GF-01 | Restart while persistent gone-fishin/lockdown policy is set; try model/UI/config exit | Remains locked until selected owner/recovery touch-signs exit | Persistent lockdown blocked |

`N` is frozen by each stage manifest before execution and must be large enough
to create overlapping transactions on the tested host. A pass with no observed
overlap is inconclusive, not success.

## Fault-injection discipline

- Each kill point is named before execution and produces an exit/process/store
  receipt.
- Tests operate only on disposable temporary registries and explicitly labeled
  test keys.
- The verifier starts in a clean process and receives observed artifacts only
  after the run terminates.
- Negative and inconclusive results are retained; retries create new run IDs.
- A model's prose disposition cannot override counts, hashes, database rows,
  checkpoint signatures, OS denial receipts, or independent vector results.

## Promotion sequence

1. Stage 0 and 1 must pass before candidate implementation review.
2. Stage 2 must pass before any concurrency/crash claim.
3. Stage 3 must pass before sole-writer or protected-anchor wording.
4. Stage 4 must pass before selecting a PIV client.
5. Stage 5 requires a fresh user grant and must pass before real-key enrollment.
6. Stage 6 is optional but required before disaster-recovery readiness wording.

Any RED-class failure stops the affected promotion branch after the first
failed layer, even if a later layer prevents an external effect.
