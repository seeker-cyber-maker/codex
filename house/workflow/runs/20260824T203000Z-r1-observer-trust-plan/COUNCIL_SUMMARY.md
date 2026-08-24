# R1 plan council summary

Final disposition: `NEEDS_HUMAN_TRUST_POLICY_DECISION`.

Three local-only same-provider reviewers verified packet
`COUNCIL_PACKET_V3.md`, SHA-256
`b709c39c052f0a469491c588a9bba10da21191580f5b347ed1bb2ec3a736314b`.
They agree that the no-dispatch boundaries are sound, but correctly reject an
implementable R1 contract without the following externally owned facts.

1. A separately authorized issuer trust basis for human anchor-registration
   records, including key selection, epoch, scope, and revocation ownership.
2. An authenticated reference-time and revocation/supersession snapshot design,
   including trusted key, digest, validation order, interval/skew semantics,
   and failure behavior without a local-clock claim.
3. A replay/consumption model: either a sealed scope-bound immutable consumed
   assertion snapshot for pure verification, or a separately authorized
   stateful ledger; a pure verifier cannot detect replay across invocations.
4. Exact versioned schemas and receipts linking R1-O to the verified R1-A
   authorization digest/scope and forcing R1-R consumers to reject R1 claims
   unless they independently verify their own runtime-admission artifact.

No host observation, clock, Keychain, certificate, signing, network, provider,
controller, candidate, launch, or secret operation occurred. Existing developer
certificates and YubiKeys remain non-authoritative inputs unless deliberately
selected in a later human-approved anchor policy.
