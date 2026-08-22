# Local worker catalog intake

This is the Dream House-side boundary for a sealed export from
`provider-orchestration`. It accepts only explicitly approved specialists and
keeps their provider-reported state distinct:

- `active` / `available` means eligible for a future, separately qualified
  runtime profile;
- `qualified` / `not_dispatchable` means visible for planning but unavailable
  for dispatch.

The module is entirely offline. It never reads a provider configuration, opens
a socket, discovers a model directory, selects a worker, or grants execution
authority. A later adapter must consume a committed provider export and pass
its source commit/tree through this receipt before any runtime review.
