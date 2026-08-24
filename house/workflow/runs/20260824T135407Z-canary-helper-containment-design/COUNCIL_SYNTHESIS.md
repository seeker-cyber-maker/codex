# Initial outside-council synthesis

## Transport and participation

- immutable transport SHA-256:
  `99ecfc7e183f4d8d40cc938c3869bc7d668b2de72930d59c86881852dfe1c819`
- attempted reviewers: 3
- completed by runner contract: 2
- partial: 1
- failed: 0

The Antigravity reviewer returned a complete substantive
`REVISE_BEFORE_IMPLEMENTATION` review. The ClinePass reviewer was truncated but
its retained prefix recommended `ACCEPT_DESIGN_ONLY`; missing required sections
prevent treating it as complete. The OpenRouter fallback exhausted its output
on response-format deliberation and did not reach a substantive review; it is
retained as non-substantive evidence, not counted as support.

## Chair disposition

`REVISE_BEFORE_IMPLEMENTATION`

The complete reviewer correctly identified that entitlement text and static
signing evidence do not prove an active sandbox. Its suggested nonexistent-path
probe was tightened: `ENOENT` proves nothing, so v1.1 requires an existing,
same-user-readable sentinel outside the allowed container and expects
`EPERM`/`EACCES`, plus bounded connection and spawn probes before canary
injection.

Independent packet reconciliation found two additional blocking defects:

1. v1 applied `POSIX_SPAWN_SETSID` to both launches, allowing the helper to
   escape the parent's kill group.
2. v1 statically verified the helper path before spawn but lacked a post-spawn
   dynamic code-object identity check, leaving a verify-path-then-exec race.

## Accepted corrections in v1.1

- Only the parent creates a new session; the helper remains in the parent's
  process group and group/session escape is a containment failure.
- Static signature/entitlement inspection is followed by post-spawn dynamic
  code identity before canary injection.
- Limits and capability probes have an explicit order; the parent spawns the
  helper before setting its own `RLIMIT_NPROC=0`, while the helper sets its
  limit as its first production action.
- The controller gate is named `SINK_RELEASE_DURABLE`, avoiding a false claim
  that bytes were already written while preserving conservative
  `POSSIBLE_SINK_EXPOSURE` semantics after the gate.
- The mock-sink read/write ends and parent-close obligations are explicit.
- Network falsifiers require a separately bounded runtime-test authority; no
  provider or real destination is implied.

The reviewer's proposed credential rotation is not adopted for this
generated-canary-only rung because there is no credential. A containment
failure quarantines the candidate build and blocks promotion. Real credential
rotation remains a later real-secret incident rule.

## Remaining claim ceiling

v1.1 is still design only. It authorizes no build, spawn, App Sandbox claim,
network probe, Keychain access, provider delivery, YubiKey use, or real secret.
It may proceed to implementation only after a final immutable delta review
accepts the corrected contract.
