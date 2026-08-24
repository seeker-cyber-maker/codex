# Review: adversarial-methodologist

Packet SHA-256: b8c955ef4b2e5ed8bd099a8b60345c9bd9dbaec802d1b9ffaa04894f474439d5
Dispatch model/provider: cline-pass/deepseek-v4-flash / ClinePass
Reviewer self-report: unknown
Harness: provider-orchestration ClinePass OpenAI shim
System-prompt profile: council role only; otherwise unknown
Memory: unknown
Reasoning mode: unknown
Disposition: completed

## Verdict
ACCEPT_NON_RUNTIME_REFERENCE

## Direct observations

1. The candidate commit `74b2a04a1bd1842a82e11d69c2064015ede435c4` implements protocol/state types, mock controller signatures using generated HMAC keys, independent per-namespace/epoch mock keyring, temp-file encrypted storage accepting only `GENERATED_CANARY_ONLY:` prefixed values, zeroizing buffers with best-effort clearing, and deterministic crash/replay fixtures. [E1]

2. All 26 focused vault/context tests and 236 total House tests pass; ruff checks, Python compilation, Git whitespace, and source-seal verification all pass. [E5]

3. The implementation explicitly cannot read macOS Keychain, spawn a process, open a network connection, or return stored plaintext. The module docstring and constraints section list these limitations. [E1, evidence packet constraints]

4. Generated fixture values must begin with `GENERATED_CANARY_ONLY:` and the storage layer rejects values without this prefix. [E1: `put_generated` method]

5. The controller key (`MockControllerKey`) combines signing and verification; the threat model delta (D3) states this is not the final controller trust boundary. [E1, E4]

6. `AtomicNonceLedger` uses `O_EXCL` for a single local nonce-claim primitive; this tests one atomic primitive, not the full multi-process authority ledger. [E1]

7. The crash classification function (`classify_crash_v1`) implements monotonic exposure: `last_durable_state` before `DELIVERY_ATTEMPTED` yields `NOT_EXPOSED`; at or after yields `POSSIBLE_EXPOSURE`; uncertain state also yields `POSSIBLE_EXPOSURE`. [E1]

8. Rotation advances epoch and revision, creates a new key in the mock keyring, writes a tombstone record, and destroys the old key. [E1: `rotate_generated`]

9. The public API (`house.worker_exec.__all__`) excludes `GeneratedVaultStorage` and all secret-related operations. [E2: test_11]

10. Static analysis of imports shows no `socket`, `subprocess`, `keyring`, `requests`, `urllib`, `os.environ`, or Keychain references. [E2: test_12]

## Inferences

1. **The candidate faithfully implements the accepted design for its claimed scope.** The code matches the described "first implementation boundary" from the threat model delta (D7): protocol/state types, mock controller signatures, generated independent namespace keys, mock KeyringStore, temp storage, zeroizing buffers, and deterministic crash/replay fixtures. Nothing in the threat model for this stage requires macOS Keychain, real resolver spawning, network, or real secret consumption. [Confidence: high; Falsifier: any evidence that the design explicitly required a feature for this stage that is absent — none found]

2. **The nonce ledger's O_EXCL claim provides a correct primitive for single-process atomic nonce claim.** The implementation validates the nonce pattern, writes payload with fsync, and correctly raises "already claimed" on collision. The evidence packet explicitly states this is not the final multi-process authority ledger, so the limitation is properly disclosed. [Confidence: high; Falsifier: a test showing a race condition could bypass O_EXCL — none provided, but O_EXCL is correct per POSIX semantics]

3. **All local denies occur before nonce claim and storage access.** `validate_policy_and_claim_v1` performs full intent verification, controller ticket verification, policy field matching (12 fields), incident-lock check, and minimum-revision check, *then* calls `ledger.claim`. Storage access happens only in explicit `put_generated` calls after claim. [Confidence: high; Falsifier: a code path where storage access occurs before a field-level deny — no such path exists]

4. **The `ZeroizingBuffer` provides best-effort clearing, not production zeroization.** The implementation explicitly notes this in both code comments and constraints. The clear method iterates over the buffer and sets each byte to 0, but Python's garbage collector could retain copies, and the `clear()` is not guaranteed for all memory views. [Confidence: high; Falsifier: production zeroization claim — none made]

## Unsupported or contradicted claims

- **No unsupported or contradicted claims found.** All claims in the evidence packet are either directly supported by code, properly caveated as "not implemented," or explicitly listed as "known unknowns." The design documents correctly identify this as protocol-only mock stage. The candidate does not claim runtime containment, real-secret handling, or final security properties.

## Recommendation

Stop. Accept this candidate as a non-runtime reference. No revision is required for the declared scope. The only potential improvement would be adding an explicit test that a `ZeroizingBuffer` with non-canonical values is cleared after `put_generated` even on failure, but this is not a defect — the `finally` block in `put_generated` guarantees clearing regardless of exception.

## Limitations

- This review only assesses the supplied transport packet. It does not verify the 236 other House tests or assess whether mock storage behavior correctly predicts real storage behavior.
- The `MockControllerKey` uses a shared symmetric key for both signing and verification; the threat model explicitly states this is not the final asymmetric controller trust boundary (D3).
- Python memory security: bytearray/ZeroizingBuffer clearing does not guarantee removal from all copies, garbage-collected intermediates, or Python's internal string/intern caches — this is properly acknowledged in constraints.
- No runtime containment testing is performed (no spawned processes, no macOS Keychain, no network — as designed).
- File system behavior tests run only on the local temp directory of the test machine; NFS or other non-local filesystems could have different O_EXCL semantics.
- The review cannot verify the source-seal or commit hash independently.
