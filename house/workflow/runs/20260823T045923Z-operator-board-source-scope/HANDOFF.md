# Operator-board source-scope display — handoff

## Accepted milestone

New bundles render one source-scope line inside each frozen top-level section.
For a bootstrap build, Relay previews and Task cards each show:

```text
Source scope: NOT_SUPPLIED
```

Named relay registration input instead displays `NAMED_JSON`; a verified,
read-only named task-spine input displays `READ_ONLY_NAMED_DATABASE`.

## Use

Choose a fresh output directory because the earlier bundle remains immutable:

```bash
python3 -m house.relay.cli build-operator-board \
  --output-dir /Users/tiga/codex-board-bootstrap-20260823-v2
```

The resulting `operator-board.html` can be supplied to the existing one-shot
viewer command.

## Limits

The label identifies only the snapshot input boundary. It is not a live-state
query, completeness claim, task dispatch signal, or human-authority proof.
