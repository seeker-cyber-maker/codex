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

The optional display-batch wrapper adds an explicit protocol revision,
compatibility floor, sequence, previous-batch link, deterministic batch id, and
an offline full-chain verifier. It is one-way (`CODEX_TO_ITERM`), observe-only,
and prohibits a reverse channel. Raw source cards are not put into the display
batch: terminal control characters and invisible Unicode format controls are
made visible, the adapter is restricted to plain-text presentation, and each
safe card retains the SHA-256 identity of its untouched source card. The hashes
prove deterministic byte identity only; they are not signatures or authority
receipts. This adopts iTerm2 Buddy's useful compatibility and flow-boundary
patterns without using or impersonating Buddy's relay protocol.

```sh
PYTHONPATH=/absolute/path/to/codex-dream-house \
  python3 -m house.terminal_companion --input exported-notifications.json

PYTHONPATH=/absolute/path/to/codex-dream-house \
  python3 -m house.terminal_companion --jsonl --input exported-notifications.jsonl

PYTHONPATH=/absolute/path/to/codex-dream-house \
  python3 -m house.terminal_companion --jsonl --display-batch --sequence 0 \
  --input exported-notifications.jsonl
```
