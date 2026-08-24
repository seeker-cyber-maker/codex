# Plan delta v5: non-circular attestation-content binding

This plan supersedes the `self_issue_decision_sha256` definition in `PLAN_V4.md`.

An `ATTESTED_CLAIMED` observation must include `attestation_content_sha256`.
It is the SHA-256 digest of the canonical observation payload containing every
attestation input except `attestation_content_sha256` and
`self_issue_decision_sha256`. The payload includes the observation state,
subject/issuer identities, account fingerprint and policy fields, model,
provider, usage-pool, route/operation bindings, supplied policy/key/reference
decisions, and all attestation evidence descriptors.

`self_issue_decision_sha256` is the SHA-256 digest of the canonical tuple:
`attestation_subject_id`, `attestation_issuer_id`, `self_issue_disposition`,
and `attestation_content_sha256`. P1 recomputes both digests before returning
its unchanged untrusted structural receipt. No digest proves the truth of an
attestation claim.
