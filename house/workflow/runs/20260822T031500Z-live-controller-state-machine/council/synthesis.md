# Council synthesis

## Decision

**Narrow accept: implement a controller-only, database-only state machine.**
All three reviewers independently echoed packet SHA-256
`cf1daf7ca5e0227a8e4dad1639d0838ad79d06168cbf23ff51402a90ee2b39f6`.
This is a local same-model-family council, not cross-provider validation.  It
does not authorize real dispatch.

## Confirmed observations

- Existing controller transitions are persistence-only but an expired lease may
  currently be reacquired despite a prior live-intent row.
- The proposed slice excludes subprocesses, Codex/provider calls, output
  reservation, user execution controls, task result admission, and retries.

## Required corrections

1. A spawn intent must atomically bind the operation record hash and active
   fence, and make the operation non-reacquirable immediately.
2. A future process identity slot and terminal observation must be immutable;
   recovery with no terminal observation must block as `UNKNOWN_NOT_RERUN`.
3. The generic supervisor and injected fixture callback remain out of scope.

## Claim ceiling

The result is only a durable local state-machine prerequisite.  It establishes
neither real process safety nor provider, configuration, hook, egress, quota,
or account authorization.

## Smallest next action

Implement the corrected controller-only transitions and deterministic tests.
