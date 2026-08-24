# Review: constructive-theorist

Packet SHA-256: b8c955ef4b2e5ed8bd099a8b60345c9bd9dbaec802d1b9ffaa04894f474439d5
Dispatch model/provider: deepseek-v4-flash / OpenCode Go
Reviewer self-report: unknown
Harness: provider-orchestration OpenCode Go catalog proxy
System-prompt profile: council role only; otherwise unknown
Memory: unknown
Reasoning mode: unknown
Disposition: completed

## Verdict
ACCEPT_NON_RUNTIME_REFERENCE

## Direct observations
- The candidate module `vault_protocol_mock.py` implements the generated-only boundary: it imports no socket, subprocess, keyring, requests, or urllib modules, and contains no `os.environ` access (source inspection, evidence 1).
- `create_resolve_intent_v1` validates exact types and formats for all fields, including `_exact_id`, `_exact_hash`, `_exact_ref`, `_exact_nonce`, and integer range checks for revision, epoch, time, and TTL (evidence 1, lines 1-120).
- `validate_policy_and_claim_v1` performs all local policy checks (operation, hashes, ref, namespace, epoch, audience, sink, incident lock, revision) before calling `ledger.claim`, which is the only storage-access step (evidence 1, function body).
- `AtomicNonceLedger.claim` uses `O_EXCL` and writes the ticket hash before returning a `CLAIMED_BEFORE_STORAGE_ACCESS` receipt (evidence 1, class definition).
- `GeneratedVaultStorage.put_generated` rejects any value not starting with `GENERATED_CANARY_ONLY:` and clears the input buffer in a `finally` block (evidence 1, function body).
- `rotate_generated` requires `new_epoch > old_epoch` and `new_revision > old_revision`, writes a tombstone with `O_EXCL`, and destroys the old key after the new value is stored (evidence 1, function body).
- `classify_crash_v1` maps any state at or after `DELIVERY_ATTEMPTED`, or any `state_uncertain=True`, to `POSSIBLE_EXPOSURE` with rotation required (evidence 1, function body).
- Tests cover tamper rejection, incident-lock precedence, nonce single-claim, expiry, sink qualification, key independence, file modes, corruption, wrong-key failure, rotation, crash monotonicity, and public API surface (evidence 2, tests 01-12).
- `VALIDATION.json` reports 26 focused tests and 236 full-suite tests passing, plus lint, format, compile, and whitespace checks (evidence 5).

## Inferences
- The candidate faithfully implements the corrected first implementation boundary from `ROOT_THREAT_MODEL_DELTA.md` D7, which permits only protocol/state types, mock signatures, generated keys, mock keyring, temp storage, zeroizing buffers, and deterministic crash/replay fixtures. Confidence: high. Falsifier: any code path in the candidate that invokes Keychain, spawns a process, opens a network connection, or reads a real secret would contradict this.
- The deny-before-claim ordering is correct: all local checks complete before `ledger.claim` is called, and the claim is the only storage write in that path. Confidence: high. Falsifier: a test that mutates policy state between the checks and the claim call and observes a claim despite a now-failing policy condition.
- The crash classification is monotonic and conservative: `NOT_EXPOSED` is only recorded when no delivery attempt is proven and no uncertainty flag is set. Confidence: high. Falsifier: a state transition that downgrades `POSSIBLE_EXPOSURE` to `NOT_EXPOSED` without a separately proven reconciliation artifact.
- The rotation semantics match the design: old ciphertext is retained, old leases are marked invalidated, and the old key is destroyed only after the new value is durably stored. Confidence: high. Falsifier: a crash between `put_generated` and `keyring.destroy` that leaves the system with both keys active and no tombstone.

## Unsupported or contradicted claims
- The packet's claim that "source-seal verification passed for all four sealed implementation/design files" is not directly evidenced in the attached artifacts; `VALIDATION.json` does not list a source-seal check. This is an unsupported claim in the authoritative-status section, though it does not affect the decision because the code itself is attached and reviewable.
- The packet's claim that "26 focused vault/context tests passed" is supported by `VALIDATION.json`, but the specific test names and pass/fail details are not independently verifiable from the attached evidence; the reviewer must trust the chair-observed result.

## Recommendation
Accept the candidate as a non-runtime reference. No revision is required for the stated decision. The smallest useful next action is to record this acceptance and proceed to the next ladder rung (helper containment) only after a separate authority record is issued, per the delta's corrected boundary.

## Limitations
- I could not execute the tests or inspect the filesystem; all observations are from the attached source and validation receipt, which are treated as untrusted evidence.
- I could not verify the source-seal claim or the exact test execution environment.
- The review is limited to the generated-only boundary; production containment, Keychain behavior, and real-secret handling are explicitly out of scope and not assessed.
