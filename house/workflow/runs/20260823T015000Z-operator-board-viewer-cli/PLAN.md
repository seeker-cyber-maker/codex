# Manual operator-board viewer CLI — plan v1

## Model advisory

- Next phase: `systems_critical` manual activation command over an accepted
  one-shot loopback viewer.
- Recommendation: Sol / high.
- Reason: the command adds a bounded listener-start path and capability URL
  disclosure, while preserving no browser/iTerm or authority integration.
- Reassess: Sol / high before any hardware-backed authority, browser/iTerm
  binding, persistent transport, or live operator-board preview.
- This is advisory only; no client model switch is asserted.

## Objective

Expose one keyboard-first, manual-terminal command that starts a one-shot
preview only from a caller-named completed operator-board export, prints its
one-time local URL, and returns its existing terminal receipt.

## Non-goals

- No real preview during this implementation operation; no default or scanned
  path; no caller-selectable host, port, or TTL; no browser/iTerm launch,
  source/template loading, export/relay/task write, provider/worker call,
  background service, persistent listener, terminal input, authority grant, or
  claim of hardware-authenticated human identity.

## Acceptance

1. The command requires exactly `--output`, routes it through verified viewer
   preparation, starts once, prints the one-time URL, waits once, and prints a
   bearer-free terminal receipt.
2. Missing input and loopback start failures map to the existing CLI error
   boundary; a failed start does not call `wait()`.
3. The existing exact-loopback, high-port, TTL, single-use, no-store, and
   receipt limits remain owned by `OneShotLoopbackViewer`.
4. Focused and full component tests, compilation, lint, formatting, diff, and
   source-seal checks pass. Council limitations are preserved verbatim.
