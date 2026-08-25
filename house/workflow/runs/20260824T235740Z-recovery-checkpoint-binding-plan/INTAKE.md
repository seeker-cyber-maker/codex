# Intake: synthetic recovery-checkpoint binding plan

## Objective

Define the smallest source-only verifier interface that can bind a signed
single-YubiKey recovery checkpoint to an exact synthetic recovery-ledger
summary and to a separately supplied expected checkpoint identity.

This advances the accepted lost-primary recovery design's rollback boundary.
It does not create or protect a checkpoint and does not make recovery ready.

## Classification

- Existing project; resume from accepted handoffs and source seals.
- New work inside the repository: plan-only security-containment slice.
- Recovery disposition: `RESUME_FROM_HANDOFF`.
- Profile: full.
- Case type: `security_containment`.

## Current boundary

The pure recovery reducer and disposable synthetic ledger are sealed. The V6
single-YubiKey policy requires an independently protected checkpoint before
revocation can safely resist restoration of pre-consumption state. The missing
external protection and latest-checkpoint authority remain explicitly absent.

No real key, YubiKey, Keychain, certificate, signing, storage, database,
network, controller, worker, CLI, dispatch, or recovery ceremony is authorized.
