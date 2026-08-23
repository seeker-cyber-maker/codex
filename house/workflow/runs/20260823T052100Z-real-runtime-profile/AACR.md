# After-action review — real runtime-profile verifier

## Outcome

Accepted within the council's narrow claim ceiling. The implementation adds a
strict structural verifier and makes the current MCU operation's missing
prerequisites explicit without changing its controller state.

## Corrections during verification

The first focused run exposed macOS temporary-path canonicalization through
`/private`; the fixture was corrected to use the operation's already canonical
workspace and output bindings. The second run reached stricter earlier gates
than two test assertions expected; the assertions were aligned to those
fail-closed operation and identifier checks. No production guard was weakened.

## What the slice proved

Exact-field and canonical-hash checks reject drift, implicit identities,
operation mismatches, extra environment keys, unbounded output, config/hook
drift, and missing model argv. Receipts never claim dispatch or authority, and
the actual MCU database remained byte-identical.

## What it did not prove

An external evidence bundle may still be false even when its bytes and profile
bindings are internally consistent. Real qualification needs an independently
governed producer and provenance policy. Hardware authority, replay-safe intent
consumption, process supervision, provider identity, filesystem tracing, and
result admission remain separate future gates.
