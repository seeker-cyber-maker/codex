# Plan delta v3: typed attestation claims and snapshot binding

This plan supersedes the P1 acceptance matrix in `PLAN_V2.md`.

## Typed observation states

P1 must distinguish two caller-supplied observation forms:

1. `UNATTESTED_STRUCTURE_ONLY`: contains no assertion of independent observer,
   trusted key, or freshness. It may receive only
   `RUNTIME_EVIDENCE_BINDINGS_VERIFIED_NO_DISPATCH` with the untrusted claim
   ceiling.
2. `ATTESTED_CLAIMED`: contains a supplied attestation disposition with exact
   `trust_policy_id`, `trust_policy_version`, `trust_policy_sha256`,
   `observer_key_id`, `observer_key_policy_sha256`, and
   `reference_time_decision_sha256`. P1 checks only presence, syntax, and
   cross-record/hash agreement. It rejects missing or mismatched supplied
   policy/key/self-issue/reference-time decisions. It does not decide whether
   that key is actually trusted, whether self-issue is factual, or whether the
   reference time is contemporaneously correct; those are later R1 claims.

An `UNATTESTED_STRUCTURE_ONLY` record must not carry an attested/fresh/independent
label. An `ATTESTED_CLAIMED` record that fails its supplied bindings must refuse.

## Canonical account fingerprint representation

The exact field is `account_fingerprint_sha256`. Its required companion policy
field is `account_fingerprint_policy_id` equal to `codex-house-account-id-v1`.
The policy is domain-separated SHA-256 over the non-secret account identifier.
P1 binds both fields across route, operation, and observation descriptors and
rejects raw account IDs, alternative account field names, policy mismatch, or
digest mismatch. P1 does not recover or inspect any account identifier.

## Controller snapshot binding

`CONTROLLER_SNAPSHOT.json` SHA-256 is
`31f97621260a06be0049972bdd5e2a36d5d020d6d3ed8a7e25079f4208b366e1`.
It was derived by a read-only SQLite query of the named `operation`, `lease`,
and `launch_intent` rows and is evidence only at
`READ_ONLY_CURRENT_ROW_SUMMARY`. It is neither an authentication receipt nor a
claim of contemporaneous state after its recorded observation time.
