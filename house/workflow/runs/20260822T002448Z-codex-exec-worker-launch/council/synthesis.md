# Council synthesis

## Decision

**Narrow accept:** build only an offline, fake-runner-tested operation
controller. **Do not enable a real `codex exec` subprocess yet.**

All three same-family, local-only reviewers verified the identical evidence
packet hash and independently reached this boundary. Their agreement does not
constitute cross-provider validation.

## Confirmed observations

- The installed `codex-cli 0.147.0` exposes `exec`, workspace, model, sandbox,
  JSON, and final-message-output options.
- The existing task spine and operator gateway preserve requested recipient but
  explicitly do not dispatch.
- The route/model receipt is advisory and cannot silently become a model
  selection.
- The operation contract requires controller-owned idempotency, lease/fencing,
  cancellation, resource caps, expected artifacts, and reconciliation.

## Corrections to the proposal

- Do not include `--ask-for-approval untrusted` in the first fixed argv: its
  availability under `codex exec` was not demonstrated by the observed help.
- The future record must say that local preparation is private but a live
  configured Codex provider may receive task data; it must not call this
  provider execution `local-only`.
- Generic recipients must omit `--model`; only `specific_model` with an
  idempotency-bound identifier may add it.
- A subprocess exit is an observation, never result acceptance.

## Required guard matrix before live dispatch

1. Immutable controller-owned operation record with owner, authority/egress
   classification, task/prompt/argv/executable hashes, idempotency binding,
   lease/fencing, zero retries, output reservation, and reconciliation state.
2. Immediate pre-spawn revalidation of record, executable, task snapshot,
   workspace containment, output containment, and stale lease.
3. Process-group timeout/cancellation/reaping with ambiguous outcomes retained
   as blocked rather than re-run.
4. Deterministic fake-runner tests proving no execution without explicit
   consent, no shell, no generic implicit model, no arbitrary output overwrite,
   and no automatic result import.
5. Version-pinned CLI argument contract test before enabling a real subprocess.

## Smallest next action

Implement the offline controller and deterministic fake-runner guard matrix as
a separate bounded slice. Reopen live dispatch only after its independent
verification; it is not authorized by this review.
