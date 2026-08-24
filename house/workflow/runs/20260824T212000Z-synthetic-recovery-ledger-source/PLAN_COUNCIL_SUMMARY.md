# Plan council summary: synthetic recovery-ledger source

## Root disposition

`ACCEPT_S1_T1_ONLY` under corrected plan SHA-256
`28459d9494ca6f6936aca5200845a0cf77a2d7116bb9b715abf574725b22702c`.

This permits only the private `recovery_ledger.py` implementation and its
dedicated test. It does not accept implementation evidence, authorize V1/C1/A1,
or widen any runtime, persistence, key, hardware, controller, provider, or
dispatch boundary.

## Review chronology

Round one used packet SHA-256
`b6104b01fa1f3dad1c69290a5bb9418d7bc16475421b360911976b2ec8a247bb`.
The constructive and adversarial reviewers accepted. The evidence auditor
identified a stronger, decision-bearing contradiction: the plan required
semantic replay from the initial state but stored only its digest. The
coordinator accepted that finding rather than deciding by vote.

The bounded correction retained three tables and added exact canonical initial
state JSON, its digest, and a genesis digest to metadata. Genesis is the
zero-entry head and sequence-one predecessor. Initialization stores an
independent current-state copy; reopen verifies and replays from the exact
stored initial state. Corruption tests cover all three genesis fields.

Round two used packet SHA-256
`aceb72c67c7296c267fb07ff30cff9fe7573b0cf242706c8390c42934f35b74c`.
All three reviewers echoed the full hash and accepted S1/T1 only. Their shared
provider/harness family makes this corroborative multi-agent review, not
cross-provider independence.

## Accepted claims

- The corrected source operation is mechanically bounded and reconstructible.
- The explicit `reopen` API is the necessary narrow delta to the parent plan.
- S1/T1 can be implemented without importing or changing operational surfaces.
- The fixed receipt ceiling, accepted-only writes, bounded replay, temporary
  fixture guard, 64-entry limit, and 800-line source/test budget remain intact.

## Unsupported claims

No code or database exists yet. No transaction, rollback, corruption, path,
receipt, replay, durability, crash, checkpoint, trusted-time, signature,
package, key, YubiKey/Keychain, controller, worker, provider, CLI, dispatch, or
operational recovery behavior is established.

## Next action

Implement S1 and T1 exactly. Stop before V1 if any sealed input hash changes,
the two-file scope is insufficient, or a fixed claim literal must change.
