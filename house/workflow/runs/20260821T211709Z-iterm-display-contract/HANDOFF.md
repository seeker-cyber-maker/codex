# Handoff

## Completed

- Added versioned, one-way iTerm display batches over accepted terminal cards.
- Added deterministic batch and source-card identities.
- Added strict sequence-zero origin, predecessor requirements, and complete
  in-memory chain verification.
- Converted terminal controls, C1 controls, Unicode format controls, and lone
  surrogates to visible plain text before they enter a display batch.
- Enforced card-count, raw-output, and post-escape encoded-byte bounds.
- Preserved observe-only, no-dispatch, no-transport, and no-reverse-channel
  invariants in code and tests.

## Verification

Eighteen terminal-companion tests and all 86 House tests pass. Ruff, formatter,
compilation, JSON parsing, CLI smoke, and diff checks pass. An independent
read-only review found the control-injection and chain-verification gaps; both
were repaired and rechecked.

## Next

The next admissible slice is a local presentation adapter using iTerm2's public
Python API. It must render the batch as plain UI text, never through terminal
input, and must stay one-way. It remains blocked from live implementation until
the user chooses whether to update the paired beta9/Buddy-build-7 installation
and until the adapter's exact iTerm UI surface is selected.

Live Codex event capture remains a separate architecture gate: Dream House must
own a Unix-listening source app-server or add a reviewed upstream event mirror.
