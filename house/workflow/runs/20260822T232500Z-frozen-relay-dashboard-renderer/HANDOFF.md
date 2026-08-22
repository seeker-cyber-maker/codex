# Frozen relay dashboard renderer — handoff

## Verified state

`house.relay.dashboard_view.render_dashboard_html()` turns one exact,
already-frozen dashboard-adapter response into a self-contained static HTML
document. It validates the response shape, bounds JSON and document sizes,
escapes dynamic values, and applies an inert CSP. It does not call the adapter,
relay, worker, provider, browser, listener, or authority path.

The existing `RelayDashboardAdapter` remains unbound. Its write-like routes
remain explicit `418` pending-integration receipts; the renderer displays that
state without changing its `NOT_ATTEMPTED` or `NOT_GRANTED` meanings.

## Acceptance evidence

- Focused relay tests: 14 passed.
- Full House suite: 168 passed.
- Compilation, Ruff, formatting, and diff checks: pass.
- Source identity is recorded in `SOURCE_SEAL.json`; commit identity is pending
  until the scoped change is committed.

## Model advisory receipt

- Case type: `semantic_implementation`.
- Recommendation: Terra / high.
- Rationale: bounded implementation with a strict non-listener/non-write
  contract and deterministic rendering tests.
- Reassess: Sol / high if a listener, browser write surface, or authority
  integration enters scope.
- This remained advisory; no client model switch was asserted.

## Next gate

A separately authorized live-binding review may feed a frozen document to the
existing one-shot loopback viewer, preserving its loopback-only, capability,
single-use, and observe-only constraints. It must not create an interactive
write surface or relax relay authority boundaries.
