# Plan delta v3: closed authorization and time-assertion verifier contracts

This delta supersedes R1-A/R1-O verifier language in `PLAN_V2.md`.

## R1-A authorization verifier contract

R1-A is admissible only through a future pure verifier with one exact,
canonical signed authorization-record schema. It must bind the human-authority
issuer/key/epoch, trust-policy digest, anchor public-key fingerprint/epoch,
observer and deployment scope, registration/revocation owners, approved
time-source policy/key/epoch, authorization generation, unique challenge and
binding digest, issue/expiry interval, and a predecessor authority-policy
snapshot digest.

The verifier's issuer key is a pre-existing, separately authorized trust input;
the record cannot authenticate itself. It rejects unknown/revoked/expired or
policy/scope/key/epoch/challenge/binding-mismatched records. Its only success
receipt is exact:

`R1_ANCHOR_REGISTRATION_VERIFIED`,
`REGISTERED_ANCHOR_ONLY`,
`runtime_admission=NOT_ATTEMPTED`, `dispatch=NOT_ATTEMPTED`, and
`authority=NOT_GRANTED`, with verifier/policy identity and all bound-record
digests. A failure receipt is `R1_ANCHOR_REGISTRATION_REJECTED` with the same
negative dispositions and no partial anchor.

## R1-O time assertion verifier contract

R1-O requires a second exact, canonical signed time-assertion schema. It binds
assertion ID, unique observation-bound challenge, observation digest,
time-source policy identity/version and snapshot digest, pre-registered
time-source key/epoch, decision time, validity interval, issuer identity, and
revocation/supersession snapshot digest.

Its pure verifier must reject unknown/revoked/expired/mismatched keys,
substituted source IDs, swapped observer/time-source keys, observer/time-source
identity overlap without a separately verified exception, policy-digest mismatch,
decision time outside the assertion interval, not-yet-valid or expired
intervals, replayed assertion ID/challenge, and noncanonical/self-signed input.
It verifies the decision against the sealed assertion interval; it never reads a
local clock.

R1-O's only success receipt is exact:

`R1_SIGNED_OBSERVATION_CLAIM_VERIFIED`,
`SIGNED_OBSERVATION_CLAIM_ONLY`,
`runtime_admission=NOT_ATTEMPTED`, `dispatch=NOT_ATTEMPTED`, and
`authority=NOT_GRANTED`, with verifier/policy/anchor/time-assertion/observation
digests. Any R1-R consumer must reject this receipt type by default and accept
only a separately defined runtime-admission artifact.

## R1-S remains test-only

R1-S may exercise generated vectors for the two future verifiers, but every
fixture is non-authoritative. Its only success state is
`STRUCTURAL_ENVELOPE_POLICY_AND_SIGNATURE_VERIFIED` with
`TEST_FIXTURE_STRUCTURE_AND_SIGNATURE_ONLY`; it cannot emit an R1-A or R1-O
receipt type.

## Recheck acceptance

Approve only if a well-formed/self-signed authorization or time record cannot
be mistaken for a verified trust decision, and no R1 output is a runtime or
dispatch admission artifact.
