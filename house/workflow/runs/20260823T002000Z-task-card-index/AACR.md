# After-action review — static task-card index

## Outcome

The renderer consumes only the existing task-spine card projection shape and
fails closed on schema, digest, advisory, dispatch, recipient, duplicate, and
size drift. It renders only escaped task-facing fields in inert HTML.

## Correction during implementation

Initial validation treated `case_type` as required. A direct task-spine replay
showed that an unclassified canonical card has an empty case type, so the
renderer was corrected and a regression test added. No task-spine contract was
changed.

## Boundary

This is a static presentation seam, not a task controller or dashboard
service. Any task-state read, refresh, listener, task mutation/dispatch,
browser/iTerm integration, or authority action remains a separate future gate.
