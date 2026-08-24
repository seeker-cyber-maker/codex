# Source-only plan delta v2: closed output and isolation contract

This delta supersedes `PLAN.md` where they differ. All original source, claim,
test, and stop boundaries remain in force.

## Closed outputs

The module defines one exact `VerificationResult` schema. It is constructed only
inside the verifier and never accepted as input. Every success, refusal, and
replay result contains these fixed literals:

- `claim_ceiling=SYNTHETIC_RECOVERY_POLICY_STRUCTURE_AND_TRANSITIONS_ONLY`;
- `authority=NOT_GRANTED`;
- `dispatch=NOT_ATTEMPTED`;
- `hardware=NOT_ACCESSED`;
- `key_material=NOT_ACCESSED`;
- `runtime_admission=NOT_ATTEMPTED`.

The remaining exact fields are `schema`, `result`, `code`,
`manifest_sha256`, `prior_state_sha256`, `next_state_sha256`,
`original_receipt_sha256`, and `receipt_sha256`. No caller-supplied evidence,
state, or manifest field is copied into a claim-ceiling field. The receipt hash
binds every field except itself. Tests deep-compare whole result objects and
reject unknown/missing input fields; there is no input field for a caller to
override or omit the output literals.

The verifier never mutates caller input. It returns a new canonical state only
for `ACCEPTED`; refusal and replay return no replacement state.

## Exact request and evidence matrix

`authority.lockdown.enter` is not an authority-bearing transition. It uses a
separate closed `ProtectiveLockdownRequest` containing the exact state bindings,
protective-rule digest, ceremony/fencing data, reason, and `REMAIN_LOCKED`.
Signer, key, signature, challenge, possession, replacement, or task fields are
not in that schema and therefore fail as unknown fields. It can only reduce
`ACTIVE` to `LOCKDOWN` and grants no authority.

Every other action uses one `TransitionManifest` and exactly one challenge:

| Action | Required signer | Additional evidence | Forbidden signer |
| --- | --- | --- | --- |
| `suspend-primary` | current recovery ID/epoch | verified recovery signature | primary/replacement |
| `recover-primary` | current recovery ID/epoch | recovery signature plus exact replacement possession | old primary/replacement alone |
| `checkpoint.admin.sign` | current recovery ID/epoch | recovery signature plus changed checkpoint digest | primary/replacement |
| `revoke-primary` | current recovery ID/epoch | recovery signature plus replacement-ready state | old primary/replacement |
| `lockdown.exit` | exact replacement ID/new epoch | replacement signature plus readiness/checkpoint binding | recovery/old primary |

Signature and possession booleans are evidence inputs, not cryptographic claims.
They must bind the exact manifest digest and expected signer/replacement IDs;
the output remains synthetic-only.

## Replay outputs

An exact already-committed manifest returns a distinct result with
`result=REPLAY`, `code=ALREADY_CONSUMED`, no next state, and
`original_receipt_sha256` equal to the stored accepted receipt digest. It does
not relabel or reproduce the original accepted receipt. Reuse of a consumed
challenge with different manifest bytes returns `REFUSED` and
`CHALLENGE_CONFLICT`.

## Closed-world isolation check

The acceptance test parses `recovery_policy.py` with `ast` and requires an exact
import allowlist containing only pure standard-library modules needed for data
validation/canonical hashing. It rejects imports/calls for `authority`,
`authority_crypto`, inbox/controller/CLI/provider modules, filesystem/path APIs,
SQLite, subprocess, socket/network, environment/process APIs, time/clock,
serialization key loading, cryptography/key generation/signing/encryption,
`eval`, `exec`, `compile`, `__import__`, and dynamic attribute/import helpers.

The test also scans package exports and production modules to prove this new
module is not imported or re-exported anywhere except its dedicated test. This
is a source-graph claim only, not OS-level containment.
