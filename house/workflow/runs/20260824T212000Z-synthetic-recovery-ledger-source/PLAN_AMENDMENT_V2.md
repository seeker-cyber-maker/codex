# Synthetic Recovery Ledger Plan Amendment V2

Status: `PROPOSED__STOP_BEFORE_BOUNDED_REMEDIATION`

Parents:

- accepted plan: `28459d9494ca6f6936aca5200845a0cf77a2d7116bb9b715abf574725b22702c`
- accepted compatibility amendment: `66521a326570a0a469c9f0e0382e43a9a4b50d119a71b60986b64b207b524077`
- C1 packet: `d4cde742ce587fbcce9cb6027e781af1c01cfb2a16f3671417b565a9159ecde2`

## Trigger and reconciliation

C1 returned one `ACCEPT`, one `NEEDS_REVIEW`, and one
`BOUNDED_REMEDIATION`. The constructive role correctly observed that the
dedicated test changed after Amendment V1 froze its input hash. Those changes
closed explicit original-plan coverage gaps for meta corruption, nested receipt
corruption, semantic replay drift, and live path-identity replacement, but they
lacked a new hash-bound receipt. This amendment regularizes that exact test
candidate; it does not retroactively claim it was already authorized by V1.

The adversarial role identified one source defect: stored accepted duplicates
verify nested-receipt hashes but not the nested reducer receipt's closed schema,
fixed no-authority fields, accepted result/code, or bindings to the outer
manifest/prior/next digests. A coordinated self-consistent substitution could
therefore pass the non-semantic fast path.

## Exact pre-remediation inputs

- `recovery_ledger.py`: `063f94e98d5c624d60cefab88e0ac7f498fc615d8968a3e2dff3121b6f832ca5`
- `test_recovery_ledger.py`: `ae8e48473c95fc5c0032b8dd28ef0b7b5f6072bcf135fbe6c3864b1517624db8`
- `test_recovery_policy.py`: `aaf6ec39c22e0d54f23469914000a103f4ffce584c4706e81e3620acb39d0c15`

## Proposed bounded remediation

Authorize only:

1. Treat the exact current dedicated test hash above as the new T1 base.
2. Add a closed nested reducer-receipt validator in `recovery_ledger.py` for
   stored accepted entries: exact field set, reducer schema and fixed claim
   literals, `ACCEPTED`/`OK`, null original receipt, valid internal digest, and
   equality of manifest/prior/next digests with the outer ledger receipt.
3. Add a test that rewrites a stored nested receipt and recomputes its nested
   digest, outer digest, receipt JSON, and event digest; `reopen` and the exact
   duplicate path must reject the substituted record without repair or write.
4. Rerun the same 24-test deterministic gate plus the new substitution test,
   compilation, line ceiling, and diff checks, then freeze a new C1 packet.

The duplicate path must still make no fresh reducer candidate call. The module
may validate only the stored reducer receipt's closed structural and semantic
bindings; it may not claim authenticity against an actor able to rewrite all
SQLite history and state consistently. Combined source plus dedicated tests
remain at most 800 lines.

No other file, schema, authority, runtime, database target, key, hardware,
network, provider, controller, worker, CLI, dispatch, or recovery-ready claim is
authorized. Stop before any edit unless this exact amendment is accepted.
