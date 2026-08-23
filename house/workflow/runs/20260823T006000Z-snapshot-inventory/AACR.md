# After-action review — named offline snapshot inventory

## Outcome

The inventory is a pure read-only adapter over explicit locations. It checks no
paths other than the one-to-32 inputs supplied by the caller. Every input is
represented in output order: valid envelopes produce only the two bounded
receipt hashes; invalid input or envelope state produces a distinct rejection.

## Correction during implementation

On macOS, canonical path resolution expands `/var` to `/private/var`. This is
intentional identity normalization, not a path rewrite or a storage scan; the
test now asserts canonical identity and duplicate detection uses it too.

## Boundary

This is not a filesystem indexer, cleanup system, retention policy, snapshot
capture mechanism, dashboard, relay transport, task controller, browser/iTerm
integration, or authority path.
