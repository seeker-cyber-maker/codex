# Handoff: R1 observer/trust plan parked at policy boundary

Status: `NEEDS_HUMAN_TRUST_POLICY_DECISION`.

P1 remains sealed source-only. The host observer remains evidence-only. R1 was
planned through three council rounds but not implemented because trust-anchor,
time/revocation, and replay semantics are policy-bearing external facts—not
details a structural verifier may invent.

To reopen R1, first provide a human-approved decision covering:

- anchor-authority class and the owner of registration/revocation;
- independently authenticated reference-time and revocation snapshot source;
- whether replay prevention uses sealed snapshots or an authorized stateful
  consumption service;
- whether any certificate/YubiKey is in scope, and if so, its narrow role.

Then seal a new exact schema/evaluation-order contract before writing source.
Do not use the existing certificate, YubiKey, local clock, or an observer's own
signature as a substitute for those decisions.

## Later bounded decision: sole-YubiKey recovery

The user subsequently selected one narrow offline recovery authority as the
backup for loss of the sole routine YubiKey. The accepted plan-only contract is
`PLAN_V6_SINGLE_YUBIKEY_RECOVERY.md`; its council synthesis is
`SINGLE_YUBIKEY_RECOVERY_COUNCIL_SUMMARY.md`.

This resolves the recovery topology and authority ceiling, but does not make
Dream House recovery-ready and does not resolve the remaining R1 reference-time
and general trust-admission implementation questions above. No real recovery
key/package was generated or enrolled. The next gate is a separately authorized
source-only implementation plan; a real key ceremony requires further explicit
authorization after that implementation is accepted.
