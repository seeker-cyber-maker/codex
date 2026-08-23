# Design review: adversarial-methodologist

Packet SHA-256: 36d0742c83fce26019692d81ff77295aedad189de04effb90417e86cd265167a
Dispatch model/provider: gemini-2.5-flash-lite / Google Antigravity
Reviewer self-report: Independent architecture council member; expert in security boundary analysis.
Harness: provider-orchestration Antigravity text-only OpenAI shim
System-prompt profile: council role only; otherwise unknown
Memory: disabled
Reasoning mode: Chain-of-thought enabled
Disposition: completed

## Proposed boundary
The architecture implements a **Staged-Compiler-Verifier (SCV)**. The TCB is strictly partitioned:
1. **LocalContextFirewallV1 (Secrecy TCB)**: The only component authorized to parse raw bytes into semantic projections. Zero external network/process/extension capability. 
2. **PureContextVerifierV1 (Integrity TCB)**: A stateless, deterministic function rejecting any output not cryptographically bound to the sealed ruleset and parent-stage digests.
3. **VaultBrokerV1 (Authority TCB)**: A minimal lease-resolver with no internal storage keys, operating only via OS-keyring-mediated decryption of scoped, single-use, sink-bound leases.
4. **Implementation Delta**: Firewall and Verifier are separate, binary-auditable units.

## Authority-bearing facts
*   **Ruleset Truth**: The signed `CodexContextRulesetV1` is the sole arbiter of projection classifications and precedence.
*   **Observation Manifest**: Observer output is treated as untrusted metadata (digests/epochs); content is only admitted upon firewall success.
*   **Lease Binding**: Authority is verified via an `AuthorityReceipt` (worker identity + task plan hash + current lease epoch).

## Contradiction handling
*   **Precedence**: Ruleset > Project/Session. No dynamic runtime overrides permitted.
*   **Freshness**: Strict epoch/digest pinning at every stage. Any drift at observation-time forces a full restart from the affected stage.
*   **Fail Behavior**: All failures (unknown keys, secret collisions, epoch mismatch) are hard-coded to `INCOMPLETE_*` terminal states, ensuring no downstream execution with partial or compromised context.

## Stop and human escalation
*   **Machine Stop**: Immediate halt on `INCOMPLETE_PRIVATE_TEXT` or `RULESET_SOURCE_MISMATCH`. Zero retry logic.
*   **Human Escalation**: Any failure to write an audit event for a lease resolution forces a terminal quarantine of the specific vault namespace until manual operator override.

## Failure containment and recovery
*   **Component Compromise**: Firewall compromise is mitigated by the Pure Verifier's rejection of output violating the ruleset schema. Vault Broker compromise is mitigated by the lack of storage-key persistence; the broker only holds active, ephemeral, lease-scoped memory.
*   **Revocation**: Global secret epoch invalidation immediately voids all active leases. Recovery requires re-authentication.

## Falsification experiments
1. **Secret-Leakage Injection**: Inject a raw secret into a `BEHAVIOR_VALUE` field; if the secret or its digest appears in stdout/logs/projection, the design fails.
2. **Observer Malice**: Provide inconsistent observer bytes for the same digest; the Verifier must halt via `UNSTABLE_STAGE_RETRY_REQUIRED`.
3. **Path Mutation**: Modify a source file between stage derivation and final launch; the re-observation check must detect the digest mismatch and invalidate the receipt.
4. **Broker Bypass**: Request a lease via the broker without a valid `AuthorityReceipt` or with an incorrect sink class; the broker must return `403` and generate an incident log.
5. **Post-Injection Audit Failure**: Simulate an audit-write failure post-injection; the consumer process must be terminated and the lease status marked `ROTATION_REQUIRED`.

## Assumptions and limitations
*   **Trust Assumptions**: Assumes the host's OS keyring is immutable to the broker-controller and that the `PureContextVerifierV1` binary is verified via independent cryptographic signature.
*   **Residual Risks**: Metadata leakage via stage-request patterns (traffic analysis of observation requests).
*   **Implementation Note**: `VaultRefV1` metadata must remain local; committing them to Git (as suggested in previous drafts) is rejected to prevent durable secret-discovery leaks.
