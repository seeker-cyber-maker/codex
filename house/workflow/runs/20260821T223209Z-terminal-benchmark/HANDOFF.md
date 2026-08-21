# Handoff

## Done

- Inventoried all five installed terminal versions and protected the live iTerm
  process plus three user shells.
- Reviewed official repositories for launch and command-control semantics.
- Qualified exact iTerm API automation and bounded Kitty/Ghostty command lanes.
- Captured common and explicit-render proxy receipts for iTerm2, Kitty, and
  Ghostty.
- Excluded human-gated startup timing, unsafe Warp/Wave routes, and unsupported
  screenshot scoring.
- Reconciled to only the original iTerm application and shell processes.

## Current truth

The benchmark is useful but partial. It supports iTerm2 as the automation host;
it does not establish a rendering-performance winner. A Ghostty preferences
plist changed during the run, so the strict zero-mutation gate failed. No
rollback was attempted without a byte-for-byte pre-run snapshot.

## Next bounded step

If the user wants a full visual/performance comparison, start a fresh run with:

1. byte snapshots of each app's preferences and saved-state records;
2. an explicit human-assisted foreground/permission phase excluded from timing;
3. fixed geometry/font/display/power state;
4. five independent invocations per case;
5. hardware or high-frame-rate capture for input-to-pixel latency and frame
   pacing; and
6. a manual identical-fixture aesthetics card.

Do not carry forward launch-to-prompt or time-to-first-token from this run.
