# Intake: canary candidate source plan

## Objective

Resolve the gap between the accepted spawn-disabled contracts and a future
signable parent/helper candidate without inspecting certificates, accessing
Keychain, linking, signing, or launching anything in this phase.

## Observed starting state

- Repository HEAD: `4644fe65f72753bc735821df5fd1da24b294475f`.
- Worktree was clean at entry.
- `parent_contract.c` and `helper_contract.c` contain no `main` and explicitly
  report `DH_CANARY_LAUNCH_DISABLED`.
- No candidate bundle or `Info.plist` exists.
- `signing_policy.json` contains proposed relative paths but remains
  `NOT_CONFIGURED_NO_LAUNCH` with null identity and artifact fields.
- The previous milestone accepted tool hardening only.

## Authority

Authorized: read-only inventory, plan artifacts, hashing, deterministic
source-only design review, and an outside council over the immutable packet.

Not authorized: source implementation, compiling or linking parent/helper,
creating a candidate bundle, certificate or Keychain discovery, identity
signing, candidate launch, dynamic inspection, network probes, generated
canary, YubiKey, providers, or real secrets.

## Claim ceiling

This run may accept, revise, or reject one source-only implementation plan. It
cannot qualify a candidate, signature, sandbox, process, canary, or secret.
