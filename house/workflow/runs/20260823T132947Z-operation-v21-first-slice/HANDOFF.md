# Operation v2.1 structural first slice — handoff

## Milestone

Implemented in:

- `house/worker_exec/operation_v2.py`
- `house/worker_exec/tests/test_operation_v2.py`
- `house/worker_exec/__init__.py`

The module provides exact task-card-v2 verification, route-selection assembly
and verification, operation-v2 assembly, and independent-descriptor operation
verification. Every receipt is `STRUCTURE_AND_BINDINGS_ONLY`, no-dispatch, and
no-authority.

## Verification

- focused: 12/12;
- numbered v2.1 falsification cases: 10/10 at the structural claim ceiling;
- complete Dream House suite: 190/190;
- Ruff, Python compilation, `just fmt`, diff, AST ambient-API audit, and
  credential scan: pass;
- controller remains SHA-256
  `977ce2be9ff3701f53afce5c02f1c772cf2fd06aa2d5adadfc13c62b8be6dd37`;
- `mcu-infinity-war-001` remains `PREPARED`, with no observation, lease, intent,
  process, provider call, or result.

## Do not infer

The implementation does not prove descriptor truth, present-time freshness,
authorship, project-inventory completeness, executable availability, output
reservation, credential safety, runtime qualification, or execution authority.
There is deliberately no v2 executor.

## Next acceptance check

Before any further code, seal and review a separate host-observer contract that
produces independently verifiable executable, CLI-contract, workspace, and
effective-context descriptors. Keep reservation, credentials, controller,
launcher, and result admission out of that next slice.
