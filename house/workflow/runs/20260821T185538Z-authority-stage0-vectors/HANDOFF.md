# Authority Stage 0 handoff

Stage 0 is complete and sealed as a software fixture only. The isolated module
under `house/authority_stage0/` produces one public deterministic RFC 6979
P-256 vector, enforces a restricted integer-only canonical JSON profile, and
retains 11 explicit negative vectors. The public scalar is intentionally unsafe
for real authority use.

Exact regeneration, strict parser and encoding rejection, low-S enforcement,
domain/binding mutation, and verification by pure-Python math, cryptography
45.0.7, and OpenSSL 3.5.6 pass. Fourteen Stage 0 tests and all 51 existing
task-spine and auto-switcher regressions pass. No provider, network, service,
database, hardware, live authority, or real-key operation occurred.

The next admissible rung is Stage 1: a separately authorized single-process
candidate using temporary authority and inbox databases. Stage 0 does not grant
that authority. Stages 2 through 6 remain independently gated by the frozen
failure-test plan.
