# Design review: constructive-theorist

Packet SHA-256: e4f44ccedd72403917d9029d0c06664799fd0328fcfcb4d5e3324d93ae65dc42
Dispatch model/provider: cline-pass/deepseek-v4-flash / ClinePass
Reviewer self-report: constructive-theorist
Harness: provider-orchestration ClinePass OpenAI shim
System-prompt profile: council role only; otherwise unknown
Memory: unknown
Reasoning mode: unknown
Disposition: completed

## Proposed boundary
The minimum implementable architecture is a non-runtime protocol layer and mock-storage test harness that enforces the following TCB partitions:

- **VaultLeaseTicketV1** is a signed, one-use, nonce-bearing structure independently verified by the resolver before any secret-material access.
- **Broker namespace keys** are freshly generated, independent random values stored under distinct Keychain accounts (one per namespace/epoch). No derivation from a shared master KDF in v1.
- **Authorization** is the intersection of a valid controller-signed receipt and local deny policy; the receipt alone never overrides local rules.
- **Exposure classification** is monotonic: `NOT_EXPOSED` may be recorded only when no delivery attempt is proven; `DELIVERY_ATTEMPTED` or uncertain crash forces `POSSIBLE_EXPOSURE`; confirmation forces `EXPOSED`. Downgrade requires a separately audited reconciliation artifact.
- **Replay protection**: the resolver atomically claims the ticket nonce in a durable spent/active ledger before accessing the namespace key. The front end is not trusted for nonce freshness.
- **macOS spawn** requires a trusted parent to construct a minimally clean environment (scrub `DYLD_INSERT_LIBRARIES`, close unrelated FDs) before `posix_spawn`/exec of a hardened resolver. Source-level `pre_main_hardening()` alone is insufficient.
- **Capability testing** verifies denied capabilities (e.g., the front end cannot open broker ciphertext paths or query namespace Keychain accounts) rather than relying on impossible decryption from co-present key and ciphertext.
- **Next slice** is protocol-only + mock storage: typed records, mock controller signatures, generated namespace keys, mock KeyringStore, temp storage, zeroizing buffers, and deterministic crash/replay fixtures. No real Keychain, network, process spawn, or real secrets.

## Authority-bearing facts
- The delta document (`ROOT_THREAT_MODEL_DELTA.md`, SHA-256 `edf2d5e905a63b771e181ebad7e199f63c557497c125a79aafeacbaa54b03214`) is authoritative where it conflicts with the original candidate. It supplies the necessary corrections for key isolation, replay, exposure monotonicity, deny precedence, macOS loader boundary, and TCB correction.
- The claim ledger documents council consensus but is advisory for design; only the delta’s explicit corrections carry design authority.
- Original candidate statements contradicted by the delta (e.g., “signed receipt overrides local policy”, “NOT_EXPOSED may override DELIVERY_ATTEMPTED”, “pre_main_hardening is sufficient”, “front end should fail decryption with key+ciphetext”) have been superseded and are not binding.

## Contradiction handling
- **Precedence**: local deny policy, current epoch, sink allowlist, binary identity, TTL, use count, and incident locks always take precedence over a valid signed authority receipt.
- **Freshness**: the resolver enforces nonce freshness via a durable spent/active ledger. A ticket with an expired, replayed, or unclaimed nonce fails before any secret-material access.
- **Uncertainty**: any delivery attempt without final durable outcome defaults to `POSSIBLE_EXPOSURE`; no optimistic-pessimistic choice downgrades severity.
- **Fail behavior**: all contradictions result in hard termination of the operation; no fallback to a less secure path. Audit failure after delivery is an incident, not a success-with-warning.

## Stop and human escalation
- **Machine-stop conditions**:
  - `DELIVERY_ATTEMPTED` without a final durable outcome => quarantine the sink and invalidate the lease/vault epoch; require operator reconciliation.
  - `POSSIBLE_EXPOSURE` automatically locks all consumption tokens for the affected namespace until human clearance.
  - Corrupt ciphertext, schema version mismatch, namespace ID mismatch, or Keychain read failure => terminal abort with no retry.
  - Duplicate nonce, expired ticket, wrong audience, or already-claimed nonce => reject before any key material access.
  - Child process crash or detection of injected `DYLD_INSERT_LIBRARIES` during test => fail with `NOT_EXPOSED` only if proven no delivery attempt; else escalate.
- **Bounded human adjudication**: `POSSIBLE_EXPOSURE` requires a human operator to review audit records (which contain no secret material) and decide on credential rotation and incident closure. The YubiKey is not the sole clearance mechanism in v1; a working recovery procedure must exist without any single device. Human escalation is bounded to the affected namespace and does not require review of plaintext secrets.

## Failure containment and recovery
- **Component compromise**:
  - **Front end** (policy/lease forwarder): can deny service and attempt valid-ticket misuse, but cannot mint tickets or access plaintext storage. Compromise requires no credential rotation.
  - **Resolver**: exposes its entire readable broker namespace. Automation marks that namespace exposed; all lease tokens and keys for that namespace must be revoked and rotated.
  - **Sink**: exposes the delivered value and any reachable destinations. The sink is isolated by per-operation boundary; compromise triggers rotation for the specific secret and auditing of all delivered requests.
  - **Controller/lease issuer**: can mint apparently valid tickets. Triggers global incident lock, rotation of controller signing key, and reissuance of all authority structures.
- **Revocation**: credential rotation invalidates current key epoch and all outstanding leases; supersession records preserve non-secret history.
- **Recovery**: operator reconciliation for `POSSIBLE_EXPOSURE`; credential rotation for compromised namespace or controller; restoration from backup only with fresh keys and human verification.
- **Audit**: contains only identifiers, hashes, epochs, and exposure classification; no secret values or value-derived fingerprints. Hash-chained for tamper evidence, not for truth from a compromised writer.

## Falsification experiments
1. **Key isolation**: Two mock namespaces (A and B) with independent keys. Encrypt a message under key A; attempt decryption under key B. **Pass**: decryption fails (auth tag error). **Fail**: decryption succeeds.
2. **Deny precedence**: Generate a valid `VaultLeaseTicketV1` for namespace X. Set a local policy `deny_all` for namespace X. Attempt resolve. **Pass**: resolver rejects before any key material fetch. **Fail**: resolver proceeds to fetch key or attempt decryption.
3. **Exposure monotonicity**: Induce a crash after `DELIVERY_ATTEMPTED` but before `OUTCOME_DURABLE`. Inspect final audit record. **Pass**: classification is `POSSIBLE_EXPOSURE`. **Fail**: classification is `NOT_EXPOSED`.
4. **Replay prevention**: Successfully consume a nonce for namespace X. Re-submit the same ticket. **Pass**: second attempt fails before namespace key access count increments. **Fail**: second attempt reads mock keyring.
5. **macOS loader injection**: Spawn the resolver helper from a parent that intentionally sets `DYLD_INSERT_LIBRARIES` to a test injection path. **Pass**: the helper detects the variable, fails closed, and does not access Keychain or ciphertext. **Fail**: helper proceeds to execution with the injected library.
6. **Capability denial**: Start the policy front end with access to a mock namespace key file (ciphertext) but no path to the broker ciphertext directory. **Pass**: front end cannot open the broker ciphertext file (test via `access()` or IO error). **Fail**: front end reads the broker ciphertext.
7. **Mock-only boundary**: Compile the next-slice code with an API gate that forbids `SecItem*` calls, `posix_spawn`, `fork`, `exec`, `socket`, `connect`. **Pass**: compilation succeeds with zero forbidden symbol imports (detectable via link-time or static analysis). **Fail**: any forbidden symbol imported.

## Assumptions and limitations
- **Trust assumptions**:
  - The controller/lease issuer signing key remains confidential and available.
  - The OS kernel, Keychain/securityd, and trusted spawn path are not compromised; the design does not guard against root/OS-level compromise.
  - The nonce ledger has durable, consistent storage (no split-brain) and is protected from unauthorized modification.
  - Audit integrity relies on the audit writer being non-compromised; hash chaining provides tamper evidence but cannot prove truth from a compromised writer.
  - The YubiKey, if used later, is not the sole recovery path; a functional recovery procedure independent of any single device must exist.
- **Residual risks**:
  - Covert channels in the resolver or sink (e.g., timing, memory pressure) cannot be fully eliminated; resolver compromise still marks the namespace as exposed.
  - macOS containment (Seatbelt + Keychain compatibility) is unverified until tested with generated credentials under direct user observation; the current design assumes it may fail and defers that test to a later stage.
  - The qualified sink adapter’s endpoint/TLS/proxy identity binding is not specified in this slice and may introduce new risks at later promotion.
- **Availability costs**:
  - Nonce ledger persistence adds latency and a durable storage requirement.
  - `POSSIBLE_EXPOSURE` automatic lock may cause temporary denial of service for a namespace until human reconciliation.
  - Credential rotation invalidates all active leases, potentially disrupting long-lived agents.

**Decision**: `ACCEPT_DESIGN_V1_1_NON_RUNTIME`. The delta closes the material authority, exposure-state, replay, key-isolation, and macOS loader-boundary problems without widening the next stage beyond mock/generated data.
