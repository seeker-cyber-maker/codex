# Independent security council synthesis

## Outcome

**ACCEPT for a separately authorized ceremony-design stage only.** Keep the
candidate blocked from production, real-key enrollment, YubiKey integration,
sole-writer authority, and live Codex or worker use.

All three reviewers independently confirmed packet SHA-256
`0436e658830ee87e754aa3508bb6ee1f624e6672bc0b5fa036e6ede88b0782ca`
and all twelve primary-artifact hashes. No reviewer failed, timed out, or
requested expanded access. Round two was unnecessary because there was no
decision-bearing disagreement.

## Confirmed observations

- The cooperative API strictly binds and verifies signer, action, content,
  nonce, time, permission, key state, and replay before enqueue authorization.
- Bootstrap is serialized and single-event, but its actor is externally
  asserted rather than authenticated by this candidate.
- Proof consumption and revocation are atomic inside the authority database.
- Authority acceptance and inbox enqueue span two independent commits. A fresh
  proof plus content-bound inbox idempotency recovers the tested failure, but
  durable proof-to-inbox causality is incomplete across the full crash matrix.
- The hash chain detects internal inconsistency, not coherent rewriting or tail
  truncation by a local database writer.
- Rejection content is bounded but rejection volume is not.
- The P-256 fixture is a same-library round-trip, not a fixed independent
  interoperability vector.
- Enrollment after bootstrap, rotation, replacement, recovery, and last-key
  protection do not yet exist.

## Disputed interpretations and narrowed claims

- `append-only` is accepted only as an API discipline. It is not a physical or
  adversarial storage property.
- `journal integrity` means internal chain consistency, not authenticated or
  tamper-evident history.
- `known-answer` should be replaced by `generated round-trip fixture` until an
  independent fixed vector exists.
- A returned signer receipt proves current authorization of the binding. For an
  already-existing idempotent inbox row, it does not prove that signer caused
  the original enqueue or that the composite receipt is durable provenance.

## Unsupported claims rejected

- Production security boundary, hostile-process resistance, YubiKey behavior,
  private-key custody, atomic cross-database enqueue, full crash recovery,
  durable signer causality, and tamper-proof logging remain unsupported.
- The reviewers did not independently rerun the 51 tests because the council
  was read-only and raw execution logs were not part of round one. The chair's
  sealed validation remains execution evidence, not independent council
  reproduction.

## Decision and confidence

Decision: **accept ceremony design; keep implementation promotion blocked.**

Confidence is high for this narrow decision because the source, tests, claim
ceiling, and three independent static readings agree. Confidence is only medium
as a security review because all reviewers inherited the same model family,
source packet, and prompt lineage, and none exercised concurrency or crashes.

## Mandatory design inputs

1. Authenticated bootstrap, enrollment, rotation, replacement, loss recovery,
   compromise recovery, and last-valid-key behavior.
2. Durable reconciliation and causality semantics for the authority/inbox
   two-database saga.
3. A protected journal-head anchor or a permanently narrowed consistency-only
   claim plus an OS-enforced sole-writer boundary.
4. Fixed independent P-256 canonicalization/interoperability vectors and a
   bounded multi-process/crash test matrix.
5. Rejection rate, quota, retention, alerting, and exhaustion behavior.

## Smallest next action

Obtain a new authority grant for a **design-only, no-real-key operation** that
produces the ceremony threat model, state machine, recovery table, portable
signing-vector specification, and preregistered failure tests. Do not implement
or operate the ceremony under this council decision.

## Provenance and limitations

This was a local-only, zero-provider-request, three-agent same-model council.
Each reviewer was blind to the other responses in round one. The normalized
reviewer reports are stored under `reviewers/`; the original responses remain
in the Codex task transcript. Shared model family and shared evidence are
correlated dependencies, not three fully independent model confirmations.

**DECIDE: authorize or decline the separate design-only operation.**
