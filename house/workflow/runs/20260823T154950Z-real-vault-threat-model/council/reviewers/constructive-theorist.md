# Design review: constructive-theorist

Packet SHA-256: 9effcb178e9187de9e4355eebb0a9e4e696417cee2731cdd89cfb929162db17f
Dispatch model/provider: cline-pass/deepseek-v4-flash / ClinePass
Reviewer self-report: constructive-theorist
Harness: provider-orchestration ClinePass OpenAI shim
System-prompt profile: council role only; otherwise unknown
Memory: disabled
Reasoning mode: unknown
Disposition: completed

## Proposed boundary

Minimum implementable architecture: three isolated processes – Policy Front End (PFE), Resolver Helper (RH), Qualified Sink Adapter (QSA). Trusted Computing Base (TCB): RH binary, QSA binary, OS kernel, Keychain daemon. PFE and Context Firewall are outside TCB for secret handling.

- **RH**: spawned per lease with only: one encrypted namespace file (read-only), Keychain access for that namespace’s key, one control FD from PFE, one output FD to QSA. No network, subprocess, arbitrary filesystem, or general IPC.
- **QSA**: spawned per sink with only: one input FD from RH, network access to a single bound endpoint (allowlist from plan). No other capabilities.
- **PFE**: verifies authority receipts, manages lease state machine, never touches ciphertext or plaintext. Audit writes to durable store.
- **Lease state machine**: PREPARED → INTENT_DURABLE → SINK_BOUND → DELIVERY_ATTEMPTED → CONSUMED → OUTCOME_DURABLE. Crash before DELIVERY_ATTEMPTED = NOT_EXPOSED; crash at/after = POSSIBLE_EXPOSURE.

## Authority-bearing facts

**Require authenticated provenance**: authority receipt (signed by trusted issuer), lease token (signed by PFE), sink binary hash (verified at spawn), namespace key epoch (from Keychain). **Advisory data**: namespace mapping (ref_id → label), configuration parameters, audit logs (non-secret, hash-chained).

## Contradiction handling

- **Precedence**: signed authority receipt overrides local policy if valid; otherwise reject.
- **Freshness**: lease TTL and nonce must be within bounds; expired or replayed leases rejected.
- **Uncertainty**: audit write failure before delivery → abort; after delivery → incident (POSSIBLE_EXPOSURE).
- **Fail behavior**: any verification failure (signature, hash, epoch, TTL, use count) → immediate rejection without secret access.

## Stop and human escalation

**Machine stop conditions**: hardening failure (exit code), crash before delivery (NOT_EXPOSED), crash after delivery (POSSIBLE_EXPOSURE triggers quarantine and rotation). **Human escalation**: POSSIBLE_EXPOSURE requires operator to rotate credentials and review audit; Keychain unavailability requires operator intervention; YubiKey failure for admin operations falls back to alternative operator ceremony.

## Failure containment and recovery

- **Component compromise**: RH compromised → assume entire namespace exposed; rotate namespace key and all secrets in that namespace. QSA compromised → assume delivered value exposed; rotate that secret. Both compromised → full credential rotation.
- **Revocation**: invalidate all leases for affected namespace/epoch; update audit.
- **Recovery**: operator generates new keys, re-encrypts secrets, updates Keychain, and verifies audit chain.
- **Audit**: all state transitions logged with hashes; integrity verified by chaining; no secret values in logs.

## Falsification experiments

1. **Network access test**: Spawn RH with canary value; monitor network connections. **Pass**: no connections made.
2. **Filesystem access test**: RH attempts to read/write files outside its designated encrypted file. **Pass**: all attempts fail.
3. **PFE decryption test**: Give PFE access to encrypted file and Keychain; attempt to decrypt. **Pass**: decryption fails.
4. **Replay test**: Capture valid lease token; replay it. **Pass**: token rejected (nonce/TTL).
5. **Crash window test**: Induce crash at each state transition; verify classification matches design (NOT_EXPOSED vs POSSIBLE_EXPOSURE). **Pass**: classification correct.
6. **Compromised resolver test**: Simulate RH compromise by allowing it to write to arbitrary FD; verify it cannot exfiltrate beyond bound sink FD. **Pass**: no exfiltration.
7. **Namespace isolation test**: Two RHs with different namespaces; attempt cross-namespace read. **Pass**: each RH can only read its own namespace.

## Assumptions and limitations

**Trust assumptions**: OS kernel and Keychain daemon uncompromised; hardware trusted; operator non-malicious; authority issuer trusted. **Residual risks**: side-channel attacks (timing, memory); covert channels via audit logs; simultaneous compromise of RH and QSA. **Availability costs**: increased latency from process spawning and IPC; dependency on Keychain availability; potential denial of service via lease exhaustion.
