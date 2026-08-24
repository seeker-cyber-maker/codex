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
