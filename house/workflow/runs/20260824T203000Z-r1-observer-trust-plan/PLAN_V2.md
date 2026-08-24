# Plan delta v2: prevent structural fixture, time, and anchor substitution

This delta supersedes the staged-boundary and R1-S sections of `PLAN.md`.

## Corrected order and ceilings

| Stage | Scope | Success ceiling |
|---|---|---|
| R1-P | plan-only schema/policy design | plan only |
| R1-S | pure test-fixture signature verifier | `TEST_FIXTURE_STRUCTURE_AND_SIGNATURE_ONLY` |
| R1-A | separately authorized human anchor registration | registered anchor only |
| R1-O | bounded signed observer operation | `SIGNED_OBSERVATION_CLAIM_ONLY` |
| R1-R | separate runtime admission | no dispatch until another acceptance gate |

R1-S consumes only generated or sealed non-authoritative test fixtures. Its
success state must be `STRUCTURAL_ENVELOPE_POLICY_AND_SIGNATURE_VERIFIED`,
never a `TRUST_*` state. It validates only fixture shape, canonical signature,
public-key fingerprint binding, and digests. It must not register, select, or
interpret an operational trust root.

## R1-A required authorization record

No public key is a registered R1 anchor unless a separate sealed human-authority
record is verified. That record must content-bind the trust-policy digest and
identifier/version; public-key fingerprint and epoch; observer and deployment
scope; registration/revocation owners; approved reference-time source and its
trust-policy digest; authorization generation/challenge/binding; issuance and
expiry; and explicit no-dispatch/no-runtime-admission state.

An existing certificate, YubiKey, or public key cannot substitute for this
record. R1-A establishes only a registered anchor under the sealed policy; not
key custody, observer independence, host truth, present freshness, or runtime
eligibility.

## Independent reference-time rule

R1-O requires a separately authenticated time assertion binding the observation
digest, `time_source_id`, time-source key fingerprint/epoch, time-source
policy/revocation snapshot digest, decision time, and validity interval. Reject
observer/time-source identity or key overlap unless an explicitly
human-authorized exception says otherwise. A local clock, observer-created
provenance field, or unbound time-source name never satisfies this rule.

Only after R1-A records verify may R1-O use the reserved state
`TRUST_POLICY_AND_SIGNATURE_VERIFIED`. Even then the result is a signed claim,
not runtime admission or dispatch authority.

## Recheck acceptance

Acceptance requires explicit fail-closed separation among fixture structure,
human anchor registration, independent time authentication, signed observation,
and runtime admission.
