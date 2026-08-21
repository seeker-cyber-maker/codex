# Terminal companion thin slice

This is an offline projector for exported app-server `item/completed`
`commandExecution` notifications. It produces compact command cards containing
the redacted command presentation supplied by Codex, cwd, terminal status,
exit code, duration, and aggregate output.

It does not connect to iTerm, sockets, running Codex, rollouts, or native
databases. Capture and live subscription are separate future integrations.

```sh
PYTHONPATH=/absolute/path/to/codex-dream-house \
  python3 -m house.terminal_companion --input exported-notifications.json

PYTHONPATH=/absolute/path/to/codex-dream-house \
  python3 -m house.terminal_companion --jsonl --input exported-notifications.jsonl
```
