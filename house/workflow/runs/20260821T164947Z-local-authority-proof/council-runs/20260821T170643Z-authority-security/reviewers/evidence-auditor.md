# Review: evidence-auditor

Packet SHA-256: `0436e658830ee87e754aa3508bb6ee1f624e6672bc0b5fa036e6ede88b0782ca` (independently confirmed)
Dispatch model/provider: inherited current Codex model; local Codex subagent harness
Reviewer self-report: unknown
Harness: Codex multi-agent; version unknown
System-prompt profile: council worker plus evidence-auditor role
Memory: unknown
Reasoning mode: unknown
Disposition: completed

## Verdict

Accept progression only to a separately authorized real-key ceremony design.
Do not accept real-key enrollment, production use, or promotion as a security
boundary.

## Direct observations

- All twelve primary-artifact hashes matched the packet.
- Strict proofs bind principal, content-derived key ID, action, target/content
  digest, nonce, issuance, and expiry under P-256/SHA-256.
- Authorization checks time, enrollment, revocation, signature, ownership,
  permission, action, binding, and accepted-nonce replay.
- Revocation and proof acceptance share one SQLite transaction.
- Bootstrap is serialized, closes after the first bootstrap event, and records
  `EXTERNAL_SETUP_ASSERTED`; it does not authenticate the setup actor.
- Authority acceptance commits before the separate inbox transaction.
- Journal verification proves internal hash-chain consistency, not protection
  against a writer that can coherently rewrite SQLite.
- Rejection entries are bounded in content but not in count.
- The generated signature fixture is a round-trip through one cryptography
  implementation, not an independent fixed known-answer vector.
- The council packet reports test success but does not include raw test output.

## Inferences

- The cooperative API signature gate likely meets its narrow claim. Falsifier:
  an invalid, replayed, or revoked proof mutates the inbox through the gate.
- Fresh-proof recovery likely covers the tested failure, but not the full
  crash-after-inbox-commit/before-receipt matrix. Falsifier: a bounded crash
  matrix demonstrating deterministic durable correlation at every boundary.
- A sole root can self-revoke into permanent lockout. Falsifier: independently
  tested replacement and recovery semantics.

## Unsupported or contradicted claims

- Physical or adversarial append-only storage is unsupported.
- Journal integrity must mean consistency, not authenticity.
- `known-answer` overstates the generated fixture.
- The returned signer receipt shows present authorization, not necessarily
  causation of a pre-existing idempotent inbox row.
- The council did not independently establish the reported 51-test result.

## Recommendation

Permit ceremony design while keeping promotion blocked on authenticated
bootstrap/rotation/recovery, journal anchoring or sole-writer enforcement,
bounded rejection storage, cross-database crash reconciliation and receipt
semantics, and fixed independent interoperability vectors.

## Limitations

- Static local read-only review with no test execution, hardware, network, raw
  runtime logs, or hostile-process testing.
- Shared model family and evidence packet weaken independence.

**ACCEPT**
