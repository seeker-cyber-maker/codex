# After-action council review — relay preview index

## Outcome

The index reused the preview-card validator through a safe identifier-only
projection, instead of copying validation logic or reopening dashboard
content. Canonical sorting and duplicate rejection make identical input sets
produce identical output regardless of caller order.

## Correction during implementation

The shared preview-card target normalization was simplified while adding the
safe projection. Functional behavior was unchanged; the source now directly
compares the exact target rather than constructing it indirectly.

## Boundary

This is a static index, not a dashboard service. Any state refresh, listener,
browser/iTerm registration, task/relay mutation, viewer start, or authority
action remains a separate future gate.
