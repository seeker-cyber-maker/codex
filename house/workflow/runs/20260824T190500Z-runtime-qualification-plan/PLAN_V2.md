# Plan delta v2: structural binding is not observation qualification

This plan supersedes the P1/P3 terminology in `PLAN.md`.

## Accepted council corrections

1. P1 is renamed **untrusted runtime-evidence binding verifier**. Its only
   success state may be `RUNTIME_EVIDENCE_BINDINGS_VERIFIED_NO_DISPATCH` with
   claim ceiling `UNTRUSTED_INPUT_STRUCTURE_AND_CROSS_BINDINGS_ONLY`.
2. P1 may reject absent, malformed, mismatched, implicit, default, fallback,
   and explicitly expired **attested** records. It cannot assert that a bundle
   is independent, that an issuer string is truthful, or that evidence is
   presently fresh.
3. The canonical non-secret account representation is
   `account_fingerprint_sha256`, using the existing domain-separated account
   fingerprint policy. P1 must reject a raw account ID field, a differently
   named account representation, or cross-record fingerprint mismatch.
4. A later R1 observer plan must supply an authenticated observer identity,
   content-bound signature or equivalent trust-root decision, registered key
   policy, and an attested reference-time decision. The P1 verifier only binds
   those supplied decisions; it cannot establish them.
5. P3 is only a source-only promotion. It may not use "qualified", "external",
   "independent", or "fresh" terminology for caller-supplied evidence.

## Revised P1 acceptance matrix

- reject task/route/operation digest mismatch;
- reject model/provider/account-fingerprint/usage-pool mismatch;
- reject reconstructed argv/CLI contract/output/roots/config/hooks/filesystem
  evidence mismatch;
- reject untrusted observer key, missing trust-policy binding, self-issued
  evidence, malformed validity interval, and an explicitly expired attestation
  relative to its supplied sealed reference time;
- return a no-dispatch structural receipt for a valid but unauthenticated or
  freshness-unknown bundle, with no authority grant;
- prove no host I/O, clock, process, network, credential, controller, or
  persistent-write path in source and tests.

The current controller statement is now directly bound by
`CONTROLLER_SNAPSHOT.json`. It supports only the listed row state; it does not
make the legacy operation eligible.
