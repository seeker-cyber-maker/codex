# After-action review — operator-board export path template

## Outcome

The example records only the three manually required path values in valid JSON
with intentionally nonexistent absolute placeholders. It is documentation, not
an input accepted by the relay CLI or a source of inferred defaults.

## Boundary

No code reads the template. It does not create or select a source/destination,
run an export, or activate relay, viewer, browser, iTerm, worker, provider,
task, or authority behavior.
