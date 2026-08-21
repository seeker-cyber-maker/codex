# Terminal companion thin slice

This is an offline projector for exported app-server `item/completed`
`commandExecution` notifications. It produces compact command cards containing
the redacted command presentation supplied by Codex, cwd, terminal status,
exit code, duration, and aggregate output.

The source command is shown with `redaction_state: UPSTREAM_ASSERTED`: the
projector relies on Codex's exported presentation and does not claim to
independently discover every secret. Aggregate output is separately marked
`output_redaction_state: NOT_ATTESTED`; it may be sensitive and needs a later,
separate display/redaction policy. Projected command/output content is always
`DISPLAY_ONLY` data, never an instruction to the companion. Input count and
capture/output sizes are bounded and malformed terminal fields fail closed.

This accepts thread/turn `item/completed` records only. It deliberately ignores
partial `item/commandExecution/outputDelta` events and does not interpret the
separate connection-scoped `command/exec/outputDelta` protocol.

It does not connect to iTerm, sockets, running Codex, rollouts, or native
databases. Capture and live subscription are separate future integrations.

```sh
PYTHONPATH=/absolute/path/to/codex-dream-house \
  python3 -m house.terminal_companion --input exported-notifications.json

PYTHONPATH=/absolute/path/to/codex-dream-house \
  python3 -m house.terminal_companion --jsonl --input exported-notifications.jsonl
```
