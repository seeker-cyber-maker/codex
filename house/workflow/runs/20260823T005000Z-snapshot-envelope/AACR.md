# After-action review — immutable offline snapshot envelope

## Outcome

The persistence seam accepts only a fully validated caller-supplied snapshot
receipt, then creates one named target directory once. It writes each final
artifact with exclusive creation and removes its incomplete marker only after
the hash-bound canonical envelope is present. An existing target is never
reused or overwritten.

## Correction during implementation

The acceptance contract treats interruption as a recoverable audit state, not
as permission to auto-delete or retry. A leftover `.INCOMPLETE` marker blocks
inspection, preserving evidence that a human must disposition the partial
directory before any later explicit action.

## Boundary

This is an offline local write action when explicitly called. It is not a
snapshotter, retention service, cleanup mechanism, dashboard, relay transport,
task controller, browser/iTerm integration, or authority path.
