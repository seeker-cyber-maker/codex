# Offline authority candidate handoff

The Dream House task inbox now has an optional signed producer surface backed
by a separate append-only, hash-chained trust registry. The registry directly
enrolls P-256 public keys, verifies strict short-lived proofs, consumes nonces,
enforces action permissions, records bounded rejection fingerprints, and
supports proof-authorized atomic revocation. It never stores private keys.

The enqueue gate verifies authorization before the inbox changes. A deliberate
failure after proof acceptance can be recovered by issuing a new proof for the
same enqueue identity; the existing inbox idempotency rule prevents duplicate
work. Corrupted authority history, replay, tampering, wrong principals,
permissions, time windows, keys, actions, or bindings fail closed in the
deterministic fixtures.

All 51 behavioral tests pass: 13 authority tests, 26 earlier task-spine tests,
and 12 auto-switcher tests. Static checks, formatting, compilation, source
hashes, and the sealed operation hash also pass.

This is a candidate trust registry, not a certificate authority and not a
production security boundary. Direct SQLite access is still cooperative, no
hardware key was touched, and rejection telemetry has no rate or storage cap.
Independent security review is the blocking next step. Only after review may a
separate operation design real enrollment/recovery and optional YubiKey PIV
signing; live Codex or worker integration remains later still.
