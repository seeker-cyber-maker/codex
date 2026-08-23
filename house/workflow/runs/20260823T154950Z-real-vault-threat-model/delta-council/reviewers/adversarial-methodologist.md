# Design review: adversarial-methodologist

Packet SHA-256: e4f44ccedd72403917d9029d0c06664799fd0328fcfcb4d5e3324d93ae65dc42
Dispatch model/provider: gemini-2.5-flash-lite / Google Antigravity
Reviewer self-report: Independent architect; consensus on restrictive containment.
Harness: provider-orchestration Antigravity text-only OpenAI shim
System-prompt profile: council role only; otherwise unknown
Memory: disabled
Reasoning mode: unknown
Disposition: completed

## Proposed boundary
The architecture is a "Resolver-as-an-Isolation-Cell." The TCB consists of a parent-hardened `posix_spawn` environment (scrubbed of `DYLD_*`), an atomic ticket-nonce ledger, a zero-copy memory buffer (non-clonable types), and a pre-bound `CLOEXEC` egress pipe. The minimum implementation must replace all `String` return types in the resolver path with `ZeroizingBuffer` wrappers and gate all operations behind a ledger-nonce check that resides in the broker-managed, non-exported storage segment.

## Authority-bearing facts
1. **Authenticated Provenance:** The `VaultLeaseTicketV1` (controller-signed, non-delegable).
2. **Advisory Data:** `ref_id`, `scope_class`, and audit prose (these cannot influence access control).
3. **Internal State:** The ledger of consumed nonces (must be immutable/durable to prevent replay).

## Contradiction handling
Precedence is strictly local-deny > remote-authority. Freshness is enforced by the ledger atomicity: if the ledger write fails or the nonce is seen, access is denied. Fail behavior is "Default-Closed": any signal of internal corruption, schema mismatch, or post-delivery crash triggers immediate revocation/quarantine of the namespace epoch.

## Stop and human escalation
Machine stops trigger on nonce-replay detection, unauthorized process-environment access, or audit-log fsync failure. Human adjudication is mandatory for "reconciliation after possible exposure" and for all secret-enrollment ceremonies. No automatic resumption is permitted after a `POSSIBLE_EXPOSURE` event.

## Failure containment and recovery
Compromised components are effectively siloed. Resolver compromise = blast radius of the current namespace. Sink compromise = value disclosure. Controller/Authority compromise = requires global incident lock and revocation of existing epoch secrets. Recovery requires fresh vault initialization and operator-in-the-loop key rotation.

## Falsification experiments
1. **Dynamic Injection Test:** Attempt `DYLD_INSERT_LIBRARIES` injection into the child resolver. *Pass criterion:* Child process fails to start or rejects the injected library path.
2. **Replay Experiment:** Submit the same `VaultLeaseTicketV1` nonce to the resolver twice. *Pass criterion:* Second request fails before the keyring store is accessed.
3. **Exposure State Monotonicity:** Induce a process crash at the moment of delivery. *Pass criterion:* Audit record transitions to `POSSIBLE_EXPOSURE` and resists any subsequent state change to `NOT_EXPOSED` without manual reconciliation.
4. **Capability Denial:** Provide the front-end with valid ciphertext/key pairs. *Pass criterion:* Front-end failure to initiate decryption due to sandbox policy (not crypto failure).

## Assumptions and limitations
1. **Trust:** The `posix_spawn` parent is assumed to be honest; if the parent is compromised, the containment boundary is bypassed.
2. **Residual Risk:** The bridge between `securityd` and the sandboxed process remains an unverified surface; if the sandbox allows `securityd` access, that remains a high-bandwidth side-channel.
3. **Availability:** Strict non-retry/no-replay semantics ensure security but reduce resilience to transient failures.

**Design decision:** `ACCEPT_WITH_REQUIRED_DELTA` (pending verification of the ledger as a non-audit artifact).
