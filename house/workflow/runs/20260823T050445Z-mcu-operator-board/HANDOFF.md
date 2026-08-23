# MCU task operator board — handoff

## Accepted milestone

One offline operator-board bundle was created beside the existing MCU task
state and independently replayed. Its exact local path is:

```text
.house-state/mcu-infinity-war/operator-board-20260823-v1/operator-board.html
```

The bundle contains exactly one task card, `Explain the MCU Infinity War
timeline`, from the caller-named task spine. It records no relay-registration
source and no viewer or task dispatch.

## View it

From the Dream House repository, run:

```bash
python3 -m house.relay.cli start-operator-board-viewer \
  --output /Users/tiga/Documents/Codex_Projects/codex-dream-house/.house-state/mcu-infinity-war/operator-board-20260823-v1/operator-board.html
```

This is a loopback-only, one-shot static viewer. It does not refresh,
authenticate, submit a task, or mutate the task spine.

## Verified boundary

The named task-spine journal replayed to
`5b330bfeaaab9193f5b977a10ef20bfbb3c3fd2bb449b7c9b323a49cfefda461` both
before and after the bundle build. Bundle inspection passed with state
`COMPLETE_OFFLINE` and authority `NOT_GRANTED`.

## Next gate

Task admission or dispatch remains separate work. It requires an explicit
controller/worker authority path and must not treat this snapshot as approval.
