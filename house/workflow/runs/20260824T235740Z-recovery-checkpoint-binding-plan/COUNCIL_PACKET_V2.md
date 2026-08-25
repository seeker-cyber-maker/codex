# Blocking council packet V2: recovery checkpoint binding plan

Decision question: did `PLAN_V2.md` mechanically close the two round-one
revision classes while retaining the same plan-only, non-authoritative claim
ceiling and forbidden-operation boundary?

## Frozen inputs

- `PLAN_V2.md`: `9134e25a84158751ce2d3e4f57d66538fa72b833bd2599a3f2a0cf88f60d41b0`
- `COUNCIL_ROUND1.md`: `b8c243d98f381abef98abf1f413dfcbd9f9cb63ccc0951573c88777404f31c78`
- inherited `EVALUATION_CARD.json`: `64bcdadac502f7ab99240f3cf211aee2bcb1704d238811f0b83c4debeb8a3e58`
- superseded frozen `PLAN.md`: `c8c6ba69bf505211e77a313fb1a11b7675f278b194ddd6913581d351bf21318e`
- parent packet: `d31ce8ec145ed1edeb140418c764a1e5b6acdd146cbccd055224b0e8e9a79a0e`

Reviewers must reproduce the V2 packet and input hashes before analysis.

## Required checks

1. Does the exact binding matrix now make every comparison realizable, with
   recovery signer/checkpoint identity correctly limited to checkpoint versus
   expected descriptor and ledger identity/ceremony fields bound across all
   three objects?
2. Is `assertion_sha256` unambiguously SHA-256 over canonical JSON bytes of the
   complete signed envelope, including SPKI and signature?
3. Is `checkpoint_sequence` closed to `1..2^63-1`, with predecessor rules still
   exact?
4. Does the frozen independent fixture contract prevent the candidate verifier
   from manufacturing its own positive oracle while keeping signing outside the
   future production source?
5. Did any correction accidentally add trust, latestness, protection, storage,
   recovery readiness, operational authority, or current source authority?

## Review restrictions

Read-only static review. Do not edit, run tests, open a database, read a clock,
discover/load keys, inspect YubiKeys/Keychain/certificates, sign, launch,
network, dispatch, or access runtime/controller/provider state.

Return `ACCEPT_PLAN_ONLY`, `REVISE`, or `NEEDS_REVIEW`, plus direct
observations, inference/falsifier, unsupported claims, limitations, and the
smallest correction. Council advice cannot authorize source implementation or
any operational recovery action.
