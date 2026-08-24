# Plan delta v4: complete claimed-attestation binding schema

This plan supersedes the `ATTESTED_CLAIMED` field list in `PLAN_V3.md`.

An `ATTESTED_CLAIMED` observation must contain these exact additional fields:

- `attestation_subject_id` and `attestation_issuer_id`;
- `self_issue_disposition` with one of `SELF_ISSUED`, `NOT_SELF_ISSUED`, or
  `UNDETERMINED`;
- `self_issue_decision_sha256`, defined over the canonical subject ID, issuer
  ID, self-issue disposition, and attestation content hash;
- the six policy/key/reference fields listed in `PLAN_V3.md`.

P1 validates only syntax, canonical hash recomputation, and cross-record
agreement. It rejects a missing/malformed self-issue decision, a subject/issuer
identity mismatch, or a self-issue decision hash mismatch. It cannot decide
whether the declared disposition is truthful; R1 remains responsible for that
determination under a later authenticated observer policy.

Regardless of input state, every P1 success receipt retains exactly
`UNTRUSTED_INPUT_STRUCTURE_AND_CROSS_BINDINGS_ONLY` and
`NOT_GRANTED`. `ATTESTED_CLAIMED` means only that an input makes an attestation
claim with structurally matching fields; it never makes the receipt a trust or
freshness assertion.
