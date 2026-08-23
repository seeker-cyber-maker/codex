# Design review: adversarial-methodologist

Packet SHA-256: 9effcb178e9187de9e4355eebb0a9e4e696417cee2731cdd89cfb929162db17f
Dispatch model/provider: gemini-2.5-flash-lite / Google Antigravity
Reviewer self-report: Unbiased security architecture reviewer
Harness: provider-orchestration Antigravity text-only OpenAI shim
System-prompt profile: council role only; otherwise unknown
Memory: unknown
Reasoning mode: unknown
Disposition: ACCEPT_WITH_REQUIRED_DELTA

## Proposed boundary
The architecture requires a hard severance between the **Orchestrator** (the current agent host) and the **Vault Resolver**. 
1. **Resolver Isolation:** The Resolver must be a singular-purpose, statically-linked binary injected with only one `NS_ID` (Namespace ID) via a restricted, non-inherited `CLOEXEC` pipe.
2. **Keying:** Abandon `codex_home`-based key derivation. Implement `NamespaceKey = KDF(MasterKey, NS_ID)` where `MasterKey` resides in a namespace-specific Keychain entry.
3. **Memory Hardening:** The Resolver must utilize zeroizing containers (e.g., `secrecy` crate) for all decrypted material. The `McpOAuth` cache must be deleted; the Resolver holds secrets in-memory only for the duration of a single, bounded request-response cycle.

## Authority-bearing facts
*   **Provenanced:** `NS_ID` (Namespace ID) and `Epoch_ID`. These must be passed as non-spoofable hardware-backed or strictly signed metadata.
*   **Advisory:** `SecretName`, `SecretScope`, and `ref_id`. These are diagnostic and used for mapping but hold no authority to trigger decryption.

## Contradiction handling
*   **Precedence:** Explicit `NOT_EXPOSED` state wins over `DELIVERY_ATTEMPTED`. If an audit log entry is missing, the system must assume failure.
*   **Freshness:** Epoch mismatch (due to rotation) immediately invalidates all active leases.
*   **Fail Behavior:** Any crash or `fsync` failure during the transaction window triggers a forced `POSSIBLE_EXPOSURE` event, mandating a total credential rotation for the involved namespace.

## Stop and human escalation
*   **Machine Stop:** Any attempt to read `local.age` or `codex_auth.age` by the Resolver must trigger an immediate process termination and alert.
*   **Human Adjudication:** Any `POSSIBLE_EXPOSURE` event triggers a block on all `Vault` operations until an operator manually performs a YubiKey-verified secret rotation and audit clearance.

## Failure containment and recovery
*   **Containment:** The Resolver binary must use the provided `process-hardening` library, specifically `PT_DENY_ATTACH` and `RLIMIT_CORE=0`, enforced as a pre-main condition. 
*   **Recovery:** Since `NS_ID` is distinct, compromise is isolated to one namespace. Rotation of the specific Keychain entry for that `NS_ID` restores integrity without affecting the global auth state.

## Falsification experiments
*   **Experiment:** Attempt to inject a dummy `LD_PRELOAD` library into the Resolver process while it is in the `DELIVERY_ATTEMPTED` state.
*   **Pass/Fail:** The experiment fails if the Resolver succeeds in reading the secret material or executing the library. The design is falsified if the `pre_main_hardening` is bypassed or if environment variables are not successfully scrubbed before the vault file is opened.

## Assumptions and limitations
*   **Assumption:** The macOS `securityd` (Keychain) will permit per-process access to a specific account entry without granting broader system-wide access.
*   **Risk:** The design assumes that the `CLOEXEC` pipe cannot be hijacked by a parent process that forks before the Resolver executes.
*   **Cost:** Significant development overhead for the new binary boundary; runtime cost is negligible as it avoids unnecessary caching.
