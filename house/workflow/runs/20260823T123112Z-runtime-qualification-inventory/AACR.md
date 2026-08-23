# After-action review — runtime qualification inventory

## Outcome

The read-only inventory reduced two previously generic gaps to concrete local
facts: this installation uses ChatGPT authentication, and persisted native
rate-limit evidence identifies the metered pool as `codex` on plan `prolite`.
The account is represented only by a domain-separated fingerprint.

## Positive evidence

- The installed executable is the same canonical regular file and SHA sealed
  into the operation.
- Login status agrees with the auth record's structural metadata.
- Codex's own rate-limit protocol defines `limit_id` as the metered bucket key,
  and the latest persisted event supplies `codex`.
- No live provider request was needed for the inventory.

## Blocker discovered

The prepared operation cannot be repaired by filling a profile. It has no
explicit model or isolation flags. The current builder can add `--model` only
by converting task-card recipient metadata into execution selection, which the
prior council rejected as an authority boundary.

## Remaining uncertainty

The source default ChatGPT base URL is only a candidate egress identity because
managed/cloud configuration can affect effective runtime configuration. No
isolated credential projection, runtime roots, race-safe output reservation,
filesystem trace, or independent evidence producer exists yet.

## Disposition

Stop before changing the operation contract. The next phase needs a sealed v2
operation-preparation design and council review. No current operation is
eligible for dispatch.
