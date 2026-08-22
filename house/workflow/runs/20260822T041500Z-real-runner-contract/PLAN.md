# Real runner contract: design only

## Council correction

The controller-only operation record currently permits `specific_model` to
change its sealed argv.  It remains a task request, not real-execution
authority.  A future real runner must require the runtime profile and human
authority to independently bind the permitted model identity; a mismatch
blocks.  The next implementation is therefore restricted to a typed,
non-executable `MOCK_ONLY` profile and authority record.

## Objective

Specify the smallest future runner that can execute one controller-owned,
explicitly authorized, read-only Codex operation exactly once and return only a
non-admitted observation receipt.  This design phase creates no runner and
does not execute the prepared MCU task.

## Proposed boundary

The runner would accept only an operation ID, controller database path, and a
separate explicit execution authority record.  It would never accept caller
argv, workspace, model, environment, or output paths.  It would:

1. Load the controller-owned hash-bound record and re-verify it.
2. Reserve the output directory through a race-safe controller-owned function.
3. Acquire a lease whose supported cap is no shorter than the sealed wall cap.
4. Atomically record `SPAWN_INTENT`; no crash after this point is eligible for
   retry without reconciliation.
5. Start only the sealed absolute executable using list argv, a fresh process
   group, bounded streamed capture, and an explicit environment profile.
6. Bind an immutable process identity, reap/cancel at the sealed cap, record
   the terminal observation, and block the operation as not admitted.

## Mandatory qualification gate

Before a real process is eligible, a separately approved runtime profile must
record: exact executable/version/help contract, selected config/home roots and
their freshness, enabled hooks or an explicit no-hook configuration, inherited
environment allowlist, provider/account identity as `UNKNOWN` unless directly
verified, intended egress, and a human execution authority with expiry and
single-use binding.  A missing or changed profile blocks before spawn.

## Non-goals

- No automatic dispatch, retries, resume, queue draining, fallback provider,
  model switching, task-result admission, or dashboard execution button.
- No reading/exporting credentials, no disabling safeguards, and no bypass of
  Codex's own approval/config mechanisms.
- No actual Codex subprocess, provider request, or modification in this phase.

## Initial scope and hard caps

- One user-supplied, read-only operation; wall cap no more than 240 seconds.
- One local output directory, newly created with exclusive containment checks.
- One explicit authority record, zero retry budget, no automatic renewal.
- A terminal process exit is an observation only and always blocks the
  operation pending a separate result-admission path.

## Acceptance for a later implementation

- Mocked process factory proves the runner cannot use caller-derived argv or
  environment and does not run without a valid fresh authority/profile.
- Crash points before/after intent, after child start, and during capture all
  reconcile permanently without rerun.
- Process group timeout and streamed receipt limits are verified with local
  fixtures before any configured Codex invocation.
- A new full-profile council reviews the implementation and qualification
  evidence before any real `codex exec` call.

## Immediate implementation boundary

Implement only canonical validation/sealing for `RuntimeProfile` and
`ExecutionAuthority` records whose mode is exactly `MOCK_ONLY`.  Such records
must contain no executable target, provider, egress, model selection, command,
environment, callback, or subprocess path.  The validation result is a
no-process receipt, not a spawn authority.
