# Review: security-architect

Packet SHA-256: 0fc395cee0c76271e405624dc32ae02ae663e12f3150a18d3285c7bf0d2283fa
Dispatch model/provider: cline-pass/deepseek-v4-flash / ClinePass
Reviewer self-report: security-architect
Harness: provider-orchestration ClinePass OpenAI shim
System-prompt profile: council role only; otherwise unknown
Memory: unknown
Reasoning mode: unknown
Disposition: completed

## Verdict
Accept the candidate for the design stage. The candidate correctly bounds the required failure modes for an offline trust-registry candidate, and the evidence supports progression to a separately authorized real-key ceremony design. No decisive local test is needed at this stage.

## Direct observations
- The candidate implements ECDSA P-256 signature verification using the `cryptography` library (`authority_crypto.py` lines 100-105).
- Bootstrap is allowed only when no `authority.key.bootstrapped` event exists in the journal (`authority.py` lines 80-83).
- Nonce replay is prevented by scanning all accepted events for the same nonce (`authority.py` lines 175-179).
- Revocation atomically commits proof acceptance and the revocation event in a single SQLite transaction (`authority.py` lines 108-130).
- Journal consistency is enforced via a SHA-256 hash chain with `previous_sha256` (`authority.py` lines 140-152).
- `AuthorizedTaskInbox.enqueue` separates proof authorization (committed) from inbox enqueue; if enqueue fails, the proof is consumed but the enqueue can be retried with a new proof (`authority.py` lines 210-230, test `test_new_proof_recovers_after_post_authorization_enqueue_failure`).
- Tests cover valid proof, tampered proof, expired/future/overlong proofs, unknown key, revoked key, replay, permission enforcement, journal corruption, and post-authorization enqueue failure recovery (test files `test_authority_crypto.py` and `test_authority.py`).
- The sealed reports (VALIDATION.json, RECONCILIATION.json) claim zero network requests, zero provider dispatches, zero real-key enrollments, and zero invalid-proof inbox effects. These are untrusted but consistent with the source design.

## Inferences
- **Inference**: The candidate correctly prevents replay attacks by checking nonce uniqueness.  
  **Confidence**: High for single-process offline use.  
  **Falsifier**: A race condition in multi-process SQLite access could allow the same nonce to be accepted twice if the journal scan is not atomic with respect to concurrent writes. The candidate does not implement multi-process locking beyond `timeout=5`.
- **Inference**: The candidate ensures journal consistency via the hash chain.  
  **Confidence**: High for an append-only journal under the assumption of no external file tampering.  
  **Falsifier**: An attacker with direct file-system access can modify the SQLite file and recompute the hash chain, bypassing verification. The candidate does not provide OS-enforced integrity protection.
- **Inference**: The candidate correctly enforces action permissions after signature verification.  
  **Confidence**: High based on test coverage.  
  **Falsifier**: A bug in `_key_state()` (e.g., incorrect parsing of `actions` from bootstrap events) could grant permissions not originally enrolled. The test `test_action_permission_is_enforced_after_signature_verification` mitigates this but does not exhaust all edge cases.
- **Inference**: The candidate bounds split-database enqueue failure modes by allowing idempotent retry with a new proof.  
  **Confidence**: Medium for production; acceptable for design.  
  **Falsifier**: If the inbox enqueue fails permanently (e.g., disk full), the consumed proof is wasted and the enqueue cannot be completed without a new proof. The candidate does not provide a mechanism to recover the consumed nonce.

## Unsupported or contradicted claims
- The claim ledger correctly marks `AUTH-PRODUCTION-BOUNDARY` as NOT_CLAIMED and `AUTH-HARDWARE-KEY` as OUT_OF_SCOPE. No unsupported claims are present in the evidence.

## Recommendation
Accept the candidate for the design stage. No decisive local test is required because the evidence sufficiently demonstrates that the candidate bounds the required failure modes for an offline trust-registry candidate. For later production promotion, the following must be addressed:
- OS-enforced sole-writer isolation for the SQLite journal.
- Rejection journal retention policy to prevent unbounded growth.
- Multi-process SQLite behavior and crash recovery guarantees.
- Key custody, recovery, and YubiKey PIV integration.
- Portable signing interoperability and hardware-backed key enrollment ceremony.

## Limitations
- All evidence is treated as untrusted; the sealed reports are not independently reproduced.
- The candidate does not protect against hostile local-process bypass, direct file tampering, or multi-process race conditions.
- Private-key custody, hardware key behavior, and network-attack surfaces are explicitly out of scope.
- The review does not authorize real-key enrollment, production promotion, or live integration.
