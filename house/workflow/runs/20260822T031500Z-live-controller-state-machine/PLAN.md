# Live controller state-machine plan

## Objective

Add and test only the durable controller transitions that a future explicit
live-launch boundary would require.  This slice does not launch a subprocess,
invoke Codex, contact a provider, reserve an output path, or change task state.

## Proposed boundary

The controller alone may advance a controller-owned operation through:

```text
PREPARED -> LEASED -> SPAWN_INTENT -> RUNNING -> TERMINAL_OBSERVED -> BLOCKED
```

`SPAWN_INTENT` is written while a current fence is held.  A future runner may
start a process only after obtaining that immutable intent receipt.  It must
then bind one process identity and call `record_running`; later it may submit a
terminal observation.  Any recovery that sees an intent without a terminal
observation resolves to permanent `BLOCKED_AMBIGUOUS_LIVE_INTENT`, never retry.

## Non-goals

- No `Popen`, shell, provider, network, or Codex CLI call.
- No `--execute` command and no default real runner.
- No task-result import, task completion, output reservation, retry, lease
  renewal, automatic resume, or queue draining.
- No change to the already sealed MCU operation or its local database.

## Authority and limits

This is a local, reversible source change on the active branch.  It changes
only `house/worker_exec/` and its tests.  Existing database rows remain readable
through compatible schema migration.  All new state transitions require a
current holder and fencing token; a lease expires no later than the controller's
existing 300-second limit.  The future real runner must reject operations whose
hard wall cap exceeds its first reviewed lease design; that policy is not
implemented here.

## Acceptance

1. Tests prove stale/expired/mismatched fences cannot create an intent or
   running/terminal observation.
2. Only one intent and one process identity can bind an operation.
3. A terminal observation is blocked, never admitted as a task result.
4. Every incomplete intent recovers to `UNKNOWN_NOT_RERUN`.
5. Existing offline fixture and no-dispatch behavior remains unchanged.
6. No test starts a real Codex process or sends a provider request.

## Required review

An outside council must evaluate this design before implementation.  A later
fresh review is required for any code that can start a real process.
