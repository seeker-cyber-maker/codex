# Manual operator-board viewer CLI — handoff

## Accepted milestone

The manual command is available:

```bash
python3 -m house.relay.cli start-operator-board-viewer \
  --output /absolute/path/to/completed-operator-board.html
```

It requires an existing, verified board export and opens one exact-loopback,
single-use preview at the existing fixed 30-second TTL. It prints the URL only
to the invoking terminal, then prints a bearer-free terminal receipt. It does
not open a browser/iTerm or start a service.

## Evidence

- Focused relay CLI, operator-board viewer/export, and dashboard-viewer tests
  pass, including missing output and loopback-start error mapping.
- The external council transport packet and raw outcomes are preserved. The
  synthesis is **ACCEPT WITH LIMITED INDEPENDENT COVERAGE**, not consensus.
- Full House verification, source hashes, and exact checks are in
  `VALIDATION.json` and `SOURCE_SEAL.json`.

## Authority limitation

This command is explicit and manual, but it is not a YubiKey-backed human
identity check and cannot be treated as a delegable authority primitive.

## Next gate

To use it, provide one completed export path and directly request one preview.
Hardware-backed authority, browser/iTerm integration, persistent transport,
and automatic source selection remain separate blocked projects.
