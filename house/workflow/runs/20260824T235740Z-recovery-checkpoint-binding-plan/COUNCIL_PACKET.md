# Blocking council packet: recovery checkpoint binding plan

Decision question: is the proposed future source-only checkpoint verifier
precise and falsifiable while remaining honest that neither the anchor nor the
expected checkpoint is trusted, latest, or protected by this code?

## Frozen inputs

- `PLAN.md`: `c8c6ba69bf505211e77a313fb1a11b7675f278b194ddd6913581d351bf21318e`
- `EVALUATION_CARD.json`: `64bcdadac502f7ab99240f3cf211aee2bcb1704d238811f0b83c4debeb8a3e58`
- `RUN_MANIFEST.json`: `3457fe5854edf879e30d06545a5cf4e088bb1d46dd08cbe96302f843639cff20`
- `EVIDENCE_INDEX.jsonl`: `ab469004654e83ae438ada638df7fbac2cdecaef5d56e02dbec06de154b8dd98`

Authoritative evidence hashes are inside the evidence index. Reviewers must
reproduce the packet and plan hashes before analysis.

## Required attacks

1. Can a self-chosen SPKI or caller-chosen expected descriptor be mistaken for
   a trusted anchor, independently protected checkpoint, or latest checkpoint?
2. Are checkpoint self-digest, envelope digest, signature, expected descriptor,
   and ledger summary bound without circularity or an unbound semantic field?
3. Are sequence-one predecessor/null rules and later predecessor rules enough
   for this structural slice without implying monotonic external storage?
4. Can time/replay language accidentally reintroduce the unresolved R1 local
   clock or stateful consumption claims?
5. Is the donor Stage-0 verifier usage narrow enough, and are the future tests
   capable of falsifying malformed DER, high-S, key substitution, canonical
   ambiguity, cross-object splice, and claim inflation?
6. Does the plan advance the lost-YubiKey rollback boundary enough to justify a
   source slice, or is it redundant/vacuous without an external checkpoint?

## Review restrictions

Read-only static review. Do not edit, run tests, open a database, read a clock,
discover/load keys, inspect YubiKeys/Keychain/certificates, sign, launch,
network, dispatch, or access runtime/controller/provider state.

Return `ACCEPT_PLAN_ONLY`, `REVISE`, or `NEEDS_REVIEW`, plus direct
observations, inference/falsifier, unsupported claims, limitations, and the
smallest correction. Council advice cannot authorize source implementation or
any operational recovery action.
