# Handoff: P1 runtime binding source seal

Status: `SOURCE_SEALED_NO_DISPATCH` pending the scoped git commit.

`verify_runtime_evidence_bindings` implements the sealed P1 v3 contract: it
invokes existing v2 verification first, binds exact untrusted caller-supplied
observations, and returns only a no-dispatch/no-authority receipt. Route-v1
`account_fingerprint` remains an opaque compatibility digest. The strict
RFC3339-UTC remediation is included.

Validation: 21 focused tests, 102 worker-exec tests, targeted Ruff, and
`git diff --check` passed. The full suite has one non-failing existing SQLite
ResourceWarning. Three local same-provider reviewers promoted the remediated
source; see `COUNCIL_PROMOTION_PACKET_V2.md` and `COUNCIL_SUMMARY.md`.

Do not alter the legacy MCU operation or begin R1 observer/trust, candidate,
provider, signing, launch, or secret work. The next gate is separately sealed.
