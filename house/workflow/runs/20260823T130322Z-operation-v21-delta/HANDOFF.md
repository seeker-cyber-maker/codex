# Operation contract v2.1 — handoff

## Milestone

V2.1 is accepted for a structural, no-dispatch implementation slice.

- Baseline: `3632bb49fc`.
- Replacement review packet:
  `201a9c10539e801f7d7b60f67b384f61028dafd55c5569fa9e4e30a6d5a3fac4`.
- Review status: substantive and packet-confirmed, but length-truncated before
  the required disposition; do not trust the manifest's shallow
  `contract_valid` classification.
- Root disposition: `ACCEPT_V2_1` after a non-capability-expanding wording
  clarification that makes in-memory hashing explicit.
- Controller: SHA-256
  `977ce2be9ff3701f53afce5c02f1c772cf2fd06aa2d5adadfc13c62b8be6dd37`,
  operation `mcu-infinity-war-001` still `PREPARED`, no observation, zero
  leases, zero intents.

## Accepted implementation boundary

Implement only:

1. task-card-v2 structural verification;
2. route-selection assembly/verification with
   `STRUCTURE_BOUND_NO_DISPATCH`;
3. zero-host-I/O `assemble_operation_v2` and structural verification over
   caller-supplied descriptors; and
4. deterministic mutation/no-I/O fixtures.

Do not implement compatibility migration, host observation, output
reservation, CLI changes, runtime profiles, signatures, credentials,
controller mutation, launching, provider dispatch, or result admission.

## Next acceptance check

All ten falsification cases in `V2_1_OPERATION_CONTRACT.md` pass, and snapshots
prove no controller, workspace, output-root, subprocess, or network mutation.
The council contract validator false positive is a separate bounded harness
repair and does not expand the first slice.
