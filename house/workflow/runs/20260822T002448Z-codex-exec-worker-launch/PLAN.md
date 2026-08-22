# Guarded Codex-exec worker launch plan

## Objective

Provide the terminal and future dashboard a real, bounded path from an admitted
task to the installed Codex CLI, with dry-run as the default and execution only
when the human explicitly supplies `--execute`.

## Authority and operation boundary

Every prepared launch is a hash-bound `project-operation/1` record. It binds
the canonical task card, resolved workspace, chosen sandbox, optional explicit
model, output path, wall-time cap, retry budget zero, and executable identity.
The record is prepared locally. Only an explicit `--execute` can create the
subprocess/provider effect; it uses argv, never a shell.

## Safe defaults

- sandbox: `read-only`
- approval: `untrusted`
- wall cap: 600 seconds
- model: configured Codex default unless the task explicitly requested a
  specific model
- retries: zero

`workspace-write` is available only as an explicit caller argument in a later
extension; this slice remains read-only to make the first live worker path
least-privileged.

## Non-goals

No autonomous queue draining, scheduler daemon, dashboard server, model
auto-selection, workspace mutation, provider fallback, key authority, or
result admission is added. A completed subprocess is an observation, not an
accepted task result.

## Acceptance

- A canonical task card creates a deterministic operation record and argv.
- A specific requested model is reflected; generic lanes do not turn advisory
  routing into a hidden model choice.
- Tampering, unknown task, non-directory workspace, unsafe sandbox, stale
  executable identity, and missing explicit execution consent fail closed.
- Fake-runner tests cover successful and failed subprocess observations without
  contacting a provider.
