# Evidence packet: final targeted entrypoint-plan review

Council ID: `20260824T182208Z-entrypoint-static-plan`
Round: `3`
Mode: `meta-review`
Decision question: Does `PLAN_V3.md` close the remaining valid-input-always-
refuses shortcut without making an unsupported candidate-runtime claim?
Deliverable: `ACCEPT_STATIC_RUNG`, `REVISE_STATIC_RUNG`, or `BLOCK`.
Privacy: `local-only`
Cost ceiling: `one bounded Luna reviewer`

## Previous review record

- Round one required a positive exact-argv/FD/protocol interface and corrected
  evidence paths.
- Round two confirmed those corrections but required a canonical valid-input
  success oracle.

## Revised plan

`PLAN_V3.md`, SHA-256
`654dd0985fdc457f047b2f43c9ab2cec38be15ba3cf2d3ca16ee36f49cde4ede`.

It introduces a controlled pure C unit test that links real admission functions
with production `main` symbols omitted by a test macro. It requires canonical
success and distinct malformed failures, while preserving no candidate bundle,
signature, parent/helper launch, network, canary, or secret input.

## Constraints

- Read-only file/hash review only. Do not modify, delegate, execute project
  code, or invoke build/link/sign/launch/network/canary/Keychain/YubiKey/
  provider/secret operations.
- The planned unit-test process is a compiler-test artifact only; it cannot be
  used to claim sandbox, containment, signed identity, or runtime behavior.

## Reviewer instruction

Review the remaining shortcut only. Return the council reviewer response
contract, name any remaining untestable requirement, and stop at a decision.
