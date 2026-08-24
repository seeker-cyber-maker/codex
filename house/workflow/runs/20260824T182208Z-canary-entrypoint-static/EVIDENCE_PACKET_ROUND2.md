# Evidence packet: targeted entrypoint-plan review

Council ID: `20260824T182208Z-entrypoint-static-plan`
Round: `2`
Mode: `meta-review`
Decision question: Does `PLAN_V2.md` fully resolve the round-one objections
without widening the static-only authority boundary?
Deliverable: `ACCEPT_STATIC_RUNG`, `REVISE_STATIC_RUNG`, or `BLOCK`.
Privacy: `local-only`
Cost ceiling: `one bounded Luna reviewer`

## Immutable round-one record

- Original packet SHA-256:
  `849682ccccfab9e62cf11571e36f9d95c069e4120fe1e8c6f501120b27063e2c`.
- All three reviewers returned `REVISE_STATIC_RUNG`.
- Findings: correct source paths; define a positive exact-argv admission API;
  define closed results; require FD-role and codec linkage; mechanically reject
  a constant refusal-only main.

## Revised plan

`PLAN_V2.md`, SHA-256
`f5c3c4e7da26d99437bd616acb866aa48858aa5157f6b882df32de068646accc`.

Corrected current source paths, relative to this run directory:

- `../../../native/canary_helper/contract.h`
- `../../../native/canary_helper/protocol.h`
- `../../../native/canary_helper/protocol.c`
- `../../../native/canary_helper/parent_contract.c`
- `../../../native/canary_helper/helper_contract.c`

## Constraints

- Read-only file/hash review only; no mutation, delegation, project-code
  execution, build, link, signing, launch, network, canary, Keychain, YubiKey,
  provider, or secret operation.
- The output claim remains static source interface plus object-symbol evidence.
- Runtime, sandbox, signing, containment, canary, and secret claims remain
  explicitly rejected.

## Reviewer instruction

Re-evaluate only the round-one objections against the revised plan. State which
are resolved, whether a new shortcut remains, and the smallest next action.
Return the council reviewer response contract.
