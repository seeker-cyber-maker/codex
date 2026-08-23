# Snapshot inventory example — plan v1

## Objective

Document the exact, one-shot JSON input shape for named snapshot-envelope
inventory without introducing a real path, default source, or executable setup.

## Acceptance

1. The example is valid JSON and contains only clearly nonexistent absolute
   placeholder paths.
2. Documentation states that callers must replace placeholders explicitly and
   that missing paths are reported, not created or discovered.
3. The existing CLI help and focused CLI/inventory tests pass.
