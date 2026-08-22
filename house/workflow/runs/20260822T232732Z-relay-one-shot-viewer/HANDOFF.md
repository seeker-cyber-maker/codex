# Relay one-shot viewer seam — handoff

## Accepted milestone

`prepare_relay_dashboard_viewer()` converts one already-frozen relay dashboard
response into the existing `OneShotLoopbackViewer`. Preparation is inert and
unbound; an explicit caller-owned `start()` remains mandatory.

The relay-facing API intentionally does not expose custom validator or clock
objects. The inherited viewer retains exact loopback addresses, a single-use
bearer capability, a 1–300 second TTL, bounded request rejection, one accepted
response, and a bearer-free terminal receipt.

## Evidence

- Nine direct relay-viewer tests pass.
- Forty-one focused relay/loopback boundary tests pass.
- The existing 168-test House discovery suite passes.
- Compilation, changed-file Ruff check/format, and diff checks pass.
- Two final outside reviewers independently verified the final packet and
  returned `ACCEPT`.

## Model advisory receipt

Sol / high was recommended before the security-boundary implementation phase.
No client model switch is asserted. With the contract and adversarial fixtures
now sealed, the next bounded offline implementation may return to Terra / high.
Escalate to Sol / high before browser/operator/iTerm authority or persistent
transport work.

## Next gate

The next admissible slice is an offline operator-registration descriptor and
approval contract. It may describe how an operator explicitly consumes the
one-shot capability, but must not open a browser, call the iTerm API, start a
listener, or introduce write/authority behavior until separately reviewed.
