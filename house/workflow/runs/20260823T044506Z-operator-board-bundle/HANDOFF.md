# Offline operator-board bundle — handoff

## Accepted milestone

The user-facing assembly command is now available:

```bash
python3 -m house.relay.cli build-operator-board \
  --output-dir /Users/tiga/codex-board-bootstrap-20260823
```

It writes a new sealed directory containing `operator-board.html`, its receipt,
the frozen snapshot envelope, inventory document, and `bundle.json`. With no
additional options it is a truthful bootstrap artifact: both possible source
records are marked `NOT_SUPPLIED`.

To view it once, use the explicit board path:

```bash
python3 -m house.relay.cli start-operator-board-viewer \
  --output /Users/tiga/codex-board-bootstrap-20260823/operator-board.html
```

The viewer still binds only exact loopback, issues one capability, expires in
30 seconds, and opens no browser or iTerm window.

## Named source options

- `--relay-registrations /absolute/path/registrations.json` accepts only a
  frozen JSON list; no discovery occurs.
- `--task-spine-db /absolute/path/tasks.sqlite` opens an existing regular file
  in SQLite read-only mode, verifies the journal, and projects its task cards.
  A missing or invalid path cannot create a database.

## Boundaries retained

The bundle is not a live dashboard. It does not refresh, scan, mutate relay or
task state, dispatch workers, contact providers, issue authority, or imply that
unsupplied sources are empty. Hardware-backed authority, live source selection,
and browser/iTerm integration remain separate future gates.
