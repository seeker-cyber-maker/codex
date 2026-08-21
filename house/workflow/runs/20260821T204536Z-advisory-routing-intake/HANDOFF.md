# Handoff

The auto-switcher now emits `model_advisory` alongside the existing deterministic
route receipt. It advises Terra for ordinary implementation, Sol for consequential
planning/review, and Luna for routine leaves; Spark is an eligible leaf worker
only and cannot be dispatched by this slice.

`manual_route_id` is accepted by the typed task-submission adapter. It is
validated before any journal write, bound into idempotency, and saved as an
independent manual-selection receipt in each Task Packet and read model. The
automatic recommendation/route is not overwritten.

This remains an offline control-plane fixture. A future UI/app-server adapter
may display or enact an operator-approved recommendation only after separate
qualification; it must not infer that a model switch occurred from these
receipts.
