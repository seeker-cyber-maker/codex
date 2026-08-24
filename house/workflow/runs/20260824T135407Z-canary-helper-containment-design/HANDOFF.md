# Handoff: generated-canary helper containment design

## Status

Milestone complete: `ACCEPT_DESIGN_ONLY`.

## Canonical design

`CANARY_HELPER_CONTAINMENT_DESIGN_V1_1.md`

The original `CANARY_HELPER_CONTAINMENT_DESIGN.md` is the immutable reviewed v1
candidate and must not be mistaken for the accepted design.

## Verified receipts

- starting HEAD: `f0dd0653828f78e7edefa70f4e020eaaf4be240c`
- initial transport:
  `99ecfc7e183f4d8d40cc938c3869bc7d668b2de72930d59c86881852dfe1c819`
- final delta transport:
  `bec0c8a1195e1ff3d3259513a9e49c4460af149c6b860777e7e5ff2fe936541f`
- accepted v1.1 source:
  `e37fa7cae1d06fb6fd8705e6f120ed0ea895fb28cffdc11a93867ace8ce7652e`

## Authority boundary

No helper was built or launched. No process-spawn, network probe, Keychain,
YubiKey, provider delivery, real credential, or live Codex configuration was
authorized or exercised. Council review is advisory and did not widen that
boundary.

## Next action

Create the first implementation rung under `house/native/canary_helper/`:
fixed protocol codecs and native parent/helper sources with spawn disabled,
plus deterministic build/signature/entitlement inspection. Acceptance is a
source/build receipt only; stop before any helper launch.

Recommended lane for that bounded implementation: Terra/high. Reassess to
Sol/xhigh before the first runtime containment experiment or after any signing,
entitlement, or process-identity ambiguity.
