# R1 observer/trust-root admission plan

## Objective

Define the smallest future admission path that can turn an inert
`OBSERVED_NOT_QUALIFIED` host-observation bundle into a *verifiably signed,
policy-bound, reference-time-bounded claim*—without treating structural hashes
as proof of observer independence or truth.

## Confirmed starting state

- `host_observer.py` can make bounded read-only observations and returns only
  `OBSERVED_NOT_QUALIFIED`; its pure verifier returns a structural receipt.
- P1 (`runtime_binding.py`) binds caller-supplied claims, including attestation
  fields, but returns only
  `UNTRUSTED_INPUT_STRUCTURE_AND_CROSS_BINDINGS_ONLY` and no authority.
- `authority_stage0/profile.py` supplies deterministic P-256 signature and
  public-key structural verification primitives, but is not an R1 trust policy.

## Proposed staged boundary

| Stage | Scope | Required independent evidence | Success ceiling |
|---|---|---|---|
| R1-P | source-only schema/policy design | no host/key material | plan only |
| R1-S | pure verifier with generated test vectors | sealed public trust-policy fixture | signature/policy structure only |
| R1-A | human-authorized anchor registration | named human authority, public key, key epoch, revocation policy | registered anchor, not live observation |
| R1-O | bounded observer operation | separately sealed request, observer signature, attested reference-time decision | signed observation claim only |
| R1-R | runtime admission | R1 output plus independent provider/isolation/output checks | still no dispatch until a new admission gate |

This run may perform only R1-P. R1-S through R1-R require separate sealed
authority records. In particular, no existing user/App Store/YubiKey/certificate
material is an implicit R1 anchor.

## R1-S contract to design later

The future pure verifier must require exact, content-bound records:

1. A versioned trust policy with trust-policy digest, allowed observer role,
   key identifier, key epoch, revocation/supersession rule, and scope.
2. A registered public key whose fingerprint equals the key identifier. Raw
   account IDs, private keys, tokens, and Keychain locators are forbidden.
3. A signed envelope whose payload binds the host-observation bundle digest,
   policy digest, key identity/epoch, observer role, reference-time decision,
   validity interval, and self-issue disposition.
4. An attested reference-time decision that is independently identified and
   whose provenance is represented as a claim—not inferred from local clock.
5. A receipt with explicit states `TRUST_POLICY_AND_SIGNATURE_VERIFIED` or
   `TRUST_CLAIM_REJECTED`, never `RUNTIME_QUALIFIED`, `DISPATCHED`, or
   `AUTHORITY_GRANTED`.

## Non-negotiable rejection rules

- unknown, revoked, expired, or policy-mismatched key/epoch;
- malformed/noncanonical signature or payload;
- bundle/policy/key/reference-time digest mismatch;
- self-issued claim where policy disallows it;
- absent or ambiguous reference-time decision;
- raw secret material, Keychain identifier, account identifier, or network
  assertion in a source/test fixture;
- a receipt that attempts to prove host truth, key custody, present freshness,
  runtime qualification, or dispatch from structural inputs alone.

## Blocking human decision

Before R1-A, a human must choose and authorize the trust-anchor class,
registration/revocation owner, and independent reference-time source. This is
not resolved by a generic developer certificate or existing YubiKey presence.

## Acceptance for this plan-only run

- Preserve the P1 ceiling and legacy MCU ineligibility.
- Make no host or credential operation.
- Receive a council disposition on whether the staged boundary has a hidden
  authority escalation or missing non-negotiable prerequisite.
