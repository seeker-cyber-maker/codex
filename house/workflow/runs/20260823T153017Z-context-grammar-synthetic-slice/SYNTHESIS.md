# Root synthesis - context grammar synthetic first slice

## Outcome

`ACCEPT_SYNTHETIC_SLICE_WITH_COUNCIL_FIX_APPLIED`.

The first implementation slice is complete and is deliberately incapable of
reading real configuration, Keychain state, vault storage, environment,
network, process state, controller state, or secrets. It derives and verifies
only sealed in-memory records. It does not qualify or execute a launch.

## What is directly verified

- `context_grammar.py` canonicalizes and seals rules, projections, grammars,
  and verification receipts; rejects schema, binding, and authority overclaims;
  and emits only `NOT_GRANTED` / `NOT_QUALIFIED` grammar state.
- `mock_context_firewall.py` accepts test fixtures only. On unsafe behavior
  data, unknown class, or missing public-content admission, it returns a
  contributor-free terminal record. Its mock launch binding returns
  `NOT_ATTEMPTED` and refuses mismatched digest observations.
- `mock_vault.py` creates opaque reference, lease, incident, exposure, and
  front-end records. It provides no storage, resolver, plaintext getter, or
  launch injection route.
- Final deterministic gates passed: 13 focused tests, 223 House tests, Ruff,
  `py_compile`, `just fmt`, `git diff --check`, and a static forbidden-import
  audit. The protected controller's hash/state did not change.

## Outside-council reconciliation

All three blind reviewers received transport SHA-256
`2d8853c4c92b2718e8a3b74e748ae88eb46e8ebab3cc0eb1cdf6857fb8299a87`.
OpenRouter's requested Gemma model returned HTTP 429; the declared Nemotron
fallback completed. ClinePass and Antigravity completed on their requested
lanes.

The constructive-theorist found a material source-level gap: only scalar
strings were screened before a `BEHAVIOR_VALUE` was placed in a projection;
a list with a secret-looking string could survive until later grammar
validation. The root accepted this finding. The mock firewall now validates
the complete admitted behavior-value shape before retaining any of it, and
`test_02b_behavior_list_secret_is_rejected_before_projection` proves the
terminal record omits the list's secret-looking literal and digest.

The other two `ACCEPT_SLICE` verdicts are supporting review signals, not
independent proof. No reviewer observed a real runtime, and their conclusion
does not widen the scope.

## Preserved limitations

- A real local parser/firewall will be a secrecy TCB; pure verification cannot
  prove that parser did not exfiltrate while reading raw data.
- The pure verifier cannot authenticate a coherently false observer.
- A real resolver can expose every namespace it can decrypt; at-rest encryption
  is not resolver containment.
- Revocation cannot retract a value delivered before an incident.
- The mock fixture scanner is intentionally not a claim that regex identifies
  every secret.

## Decision

Stop at this milestone. The next legitimate work is a separately authorized
real-integration design/review, beginning with a bounded firewall threat model
and disposable test namespace—not a direct Keychain or launcher connection.
