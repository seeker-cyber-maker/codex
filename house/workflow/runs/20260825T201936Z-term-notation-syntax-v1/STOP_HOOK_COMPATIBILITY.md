# Stop-hook compatibility disposition

## Status

`ROOT_CAUSE_BOUNDED / TERM_DIRECT_DEPENDENCY_NONE / SHARED_RUNTIME_PATCH_NOT_JUSTIFIED`

## Direct observations

- The supplied screenshot shows `UserPromptSubmit hook (completed)` followed by
  `Stop hook (failed)` and `hook returned invalid stop hook JSON output`.
- The affected task rollout is
  `/Users/tiga/.codex/sessions/2026/08/25/rollout-2026-08-25T07-57-28-01a038c8-55d6-72e1-a849-3b617883c363.jsonl`.
- That task recorded that `/Users/tiga/.config/iterm2/cc-status` had been
  registered directly as a global Stop hook and was then disabled by setting
  `"Stop": []` in `/Users/tiga/.codex/hooks.json`.
- The current hooks file does contain `"Stop": []`. The current
  `/Users/tiga/.codex/config.toml` still preserves a trust-state record for the
  former `stop:0:0` registration; a trust record is not an active hook.
- `codex-rs/hooks/src/engine/output_parser.rs::parse_stop` accepts only an
  object that deserializes as `StopCommandOutputWire`.
- `codex-rs/hooks/src/events/stop.rs::parse_completed` reports nonempty invalid
  output from a control-capable Stop handler as
  `hook returned invalid stop hook JSON output`.
- `codex-rs/core/src/session/tests.rs` contains direct evidence that an
  explicit user-config or runtime-config refresh reconstructs the session hook
  registry. A renderer-only restart is not that refresh operation.
- The Dream House branch has no diff from `upstream/main` in
  `core/src/session/turn.rs`, `core/src/hook_runtime.rs`, or the Stop event
  parser; this incident sits on the shared Codex base rather than a Dream
  House-specific hook fork.

## Root-cause conclusion

The observed incident is a local hook-protocol mismatch: the iTerm status
helper was directly registered for Stop but its Stop-event stdout did not match
the Codex Stop JSON contract. The handler was already removed from the current
global hooks file, while the preserved application engine continued to show
the previously loaded handler after a renderer-only restart.

This evidence does not establish a general defect in the Codex Stop parser.
It also does not establish the exact bytes emitted by `cc-status`; the visible
parser failure is sufficient to establish that those bytes did not satisfy the
required schema.

## Dream House effect

TERM notation has no direct hook dependency. Its parser is a pure
`house/term_notation` module and its acceptance tests do not use the CLI,
session lifecycle, stop hooks, or the terminal companion.

The compatibility invariant is now explicit in the machine-readable
dictionary and tests: TERM parsing must never depend on lifecycle or stop-hook
delivery. A later convenience integration may observe TERM records from an
already admitted transcript, but hook delivery cannot become the correctness,
task, or authority boundary.

## Deferred adapter boundary

If `cc-status` is re-enabled for Stop, a small terminal-companion adapter—not
the TERM module—should own event-specific input decoding and emit one exact
Codex Stop JSON object on stdout. Diagnostic text must go to stderr or an
external receipt, never alongside the JSON object. That adapter needs a
separate failing fixture using the current helper behavior before any fix is
implemented.

No Codex Rust source or global hook configuration is modified by this run.
