# After-action council review — relay preview card

## Outcome

The new card consumes the existing registration descriptor instead of reopening
the relay/dashboard response. That creates a strict information boundary: an
operator can confirm exactly what pending display action exists without seeing
unnecessarily broad content or a capability.

## Correction during implementation

The validator intentionally rejects invalid fixed state before comparing the
outer registration digest. The test now asserts that safer fail-closed order.
Mechanical import and formatter checks were applied before final validation.

## Boundary

This is static HTML only. Any aggregation listener, live refresh, browser/iTerm
registration, viewer start, or authority integration is a separate later gate.
