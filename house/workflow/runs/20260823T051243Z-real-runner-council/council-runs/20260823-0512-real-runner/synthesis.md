# Council synthesis — real local runner boundary

## Decision

`REVISE_DESIGN`, high confidence within static-source scope. Do not add a real
runner or execute the prepared MCU operation. The accepted next slice is a
pure, disabled-by-default real-runtime-profile verifier and deterministic
qualification-gap receipt.

## Confirmed observations

All three reviewers independently confirmed the packet hash and named source
hashes. All agree that the current operation is non-executable: its sealed argv
omits an explicit model, its start state is `DEFAULT_UNRESOLVED`, and its
provider and usage-pool identities are unknown. The current authority path
always refuses, mock admission is structurally non-executable, and the prepared
database has no lease or launch intent.

All three also agree that later authority consumption and intent creation must
be one replay-safe transaction before any process start. Existing lifecycle
source does not yet prove structured process identity, start-failure handling,
post-lease terminal reconciliation, hard total-output limits, or full
filesystem/provider containment.

## Disagreement and disposition

The adversarial reviewer preferred implementing the atomic no-spawn intent
transaction first. The other two preferred the pure runtime-profile verifier.
The chair accepts the verifier-first order because a real intent must bind a
qualified profile, while the only current profiles are deliberately
`MOCK_ONLY` and the current operation is known to fail real qualification.
Building the intent transaction first would either bind an unqualified record
or require an invented profile contract inside the same slice.

The atomic no-spawn intent transaction remains the immediately following
candidate slice after profile verification passes for a newly sealed explicit
operation. This preserves the minority finding rather than rejecting it.

## Accepted next-slice requirements

- Use a schema disjoint from `MOCK_ONLY`.
- Bind exact operation, executable path/hash/version, argv hash and explicit
  model, workspace/output identity, total output limits, exact environment,
  config/hook content evidence, provider/account, usage pool, egress class, and
  qualification-policy version.
- Reject unknown, default, inherited, fallback, wildcard, self-asserted, or
  unverified values.
- Return only `PROFILE_VERIFIED_NO_DISPATCH` on success. Convey no authority,
  lease, intent, hardware, subprocess, provider, or result-admission capability.
- Against the current MCU operation, return a hash-bound no-dispatch gap receipt
  naming its missing explicit model, provider/account, usage pool, and runtime
  qualification evidence.
- Mutation tests must fail before lease acquisition or intent/database writes.

## Claim ceiling and limitations

This was a blind local-only, same-model/shared-host council. Shared source and
model family weaken independence; agreement is not three-provider
corroboration. Review was static and read-only. No test, process, provider,
credential, hardware, or live CLI probe occurred. The decision is design
advice, not human authority and not launch approval.

## Root disposition

Accept the council finding and schedule one bounded implementation slice: the
pure real-runtime-profile verifier plus current-operation refusal receipt.
