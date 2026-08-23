# Council synthesis — manual viewer start

## Decision

**ACCEPT WITH LIMITED INDEPENDENT COVERAGE.** The incremental command may be
sealed as an interim manual-terminal path. It must retain the explicit claim
ceiling: it is not a YubiKey-backed proof of human identity and does not grant
authority.

## Evidence status

- `C-001` — The candidate calls verified preparation, starts once, prints the
  one-time loopback URL, then waits for the existing bearer-free receipt:
  **corroborated** by source/test evidence and the complete security-architect
  review. A direct start-failure-to-CLI-error test was added after review.
- `C-002` — Exact loopback, one-shot capability, TTL, no-store, and receipt
  constraints remain in the accepted underlying viewer: **corroborated** by
  source and existing direct tests; this CLI adds no host/port/TTL override.
- `C-003` — Manual invocation proves human or hardware identity: **rejected**.
  The code and documentation expressly do not make that claim.
- `C-004` — Three independent completed council reviews agree: **unknown**.
  One ClinePass review completed and accepted; OpenRouter returned an
  `ACCEPT` verdict but its required response contract was truncated; OpenCode
  timed out on both explicit models. These failures are retained, not retried.

## Disposition and limitation

The complete reviewer accepted the code as bounded and non-persistent. The
partial reviewer is supporting context only because its contract was incomplete.
No red-team content was obtained. This is sufficient for the narrowly scoped,
already-user-authorized manual command, but it is not a promotion of a hardware
authority or browser/iTerm integration.

## Next action

**blocked** on a user-supplied completed export and a direct request to start
one preview. The later YubiKey-backed authority service remains a separate
project gate.
