# Design review: assurance-human-factors

Packet SHA-256: f8e111c09585ce48bb7c59555839393bb59bf8c101bb000bae056a503f740989
Dispatch model/provider: google/gemma-4-31b-it:free / OpenRouter
Reviewer self-report: independent member of expert architecture council
Harness: provider-orchestration explicit-free catalog proxy
System-prompt profile: council role only; otherwise unknown
Memory: disabled
Reasoning mode: unknown
Disposition: completed

## Proposed boundary
The architecture consists of a strictly decoupled **Observer**, **Pure Verifier**, and **Admission Gate**. 
- **TCB (Observer):** A read-only process restricted to `lstat` and byte-reading of files explicitly permitted by a version-pinned discovery grammar and a `HostObservationRequestV1`. It is prohibited from executing any binary, following symlinks, or accessing network/IPC.
- **TCB (Verifier):** A pure function that operates solely on provided data values (request, snapshot, grammar) to validate hashes and closure. It has zero host I/O capabilities.
- **TCB (Admission Gate):** An external component that consumes the Verifier's receipt to make authority decisions.

## Authority-bearing facts
- **Authenticated Provenance:** Executable byte hashes, discovery grammar hashes, observation-policy hashes, and the `HostObservationRequestV1` parameters.
- **Advisory Data:** CLI-capture descriptors (treated as `ASSERTED_BINDING_ONLY`), `observed_at_utc` timestamps, and `NOT_EXECUTED` flags.

## Contradiction handling
- **Precedence:** The discovery grammar defines the effective precedence of configuration layers.
- **Freshness:** Handled by the Admission Gate via `observed_at_utc` and `expires_at_utc`; the Observer/Verifier only ensure the timestamps are internally consistent.
- **Uncertainty:** Any ambiguity (symlinks, hard-links > 1, Unicode collisions, or missing contributors) triggers an immediate transition to a negative terminal state (`INCOMPLETE_CONTEXT_CLOSURE` or `UNSTABLE_RETRY_REQUIRED`).
- **Fail Behavior:** Fail-closed. No partial descriptors are emitted on failure.

## Stop and human escalation
- **Machine Stop:** The Observer must terminate and emit `OBSERVER_ERROR` or `LIMIT_EXCEEDED` if any numeric limit (bytes, depth, duration) is hit or if a forbidden file type (socket, FIFO) is encountered.
- **Human Escalation:** Required if the discovery grammar cannot be closed due to a new, unreviewed contributor class in the Codex source, or if the Admission Gate rejects a verified observation due to policy mismatch.

## Failure containment and recovery
- **Component Compromise:** A compromised Observer can only misreport host facts; it cannot grant authority because the Verifier only checks structure/closure, and the Admission Gate requires separate provenance/signatures.
- **Revocation:** Handled by the Admission Gate via expiration timestamps.
- **Recovery:** `UNSTABLE_RETRY_REQUIRED` triggers a full restart of the observation; mixing entries from different attempts is prohibited.
- **Audit:** The Merkle-style directory receipts and content-addressed descriptors provide a complete audit trail of what was observed.

## Falsification experiments
- **Symlink Bypass:** Attempt to include a project instruction via a symlink. **Pass:** State is `INCOMPLETE_CONTEXT_CLOSURE`. **Fail:** File is hashed and included.
- **Secret Leak:** Request a file named `auth.json` via the grammar. **Pass:** State is `INCOMPLETE_SECRET_DEPENDENCY` or `REJECTED_REQUEST`. **Fail:** File bytes appear in the bundle.
- **TOCTOU Attack:** Modify a file between the first and second metadata read. **Pass:** State is `UNSTABLE_RETRY_REQUIRED`. **Fail:** Bundle is emitted as `OBSERVED_NOT_QUALIFIED`.
- **Verifier I/O:** Patch the Verifier's environment to raise an error on any `open()` or `socket()` call. **Pass:** Verifier completes successfully. **Fail:** Verifier crashes or hangs.

## Assumptions and limitations
- **Trust Assumptions:** The Pure Verifier's implementation is assumed to be truly pure (no side effects). The discovery grammar is assumed to be an exhaustive list of all possible Codex context contributors.
- **Residual Risks:** The "ASSERTED_BINDING_ONLY" nature of the CLI capture means the link between the executable and its help text is a claim, not a proof, until the Admission Gate intervenes.
- **Availability Costs:** Strict refusal of symlinks and hard-links may cause legitimate but non-standard project layouts to fail observation, requiring manual layout correction.
