# MCU task operator board — plan v1

## Model advisory

- Case type: `service_operations`.
- Recommendation: Terra / medium.
- Reason: this is one bounded local artifact operation over an already verified
  task journal, with a deterministic replay verifier and no worker launch.
- Reassess: before task admission, controller lease acquisition, dispatch, or
  writing any worker result.

## Objective

Write one immutable offline operator-board bundle next to the existing MCU task
state using its caller-named task-spine database as the sole live projection
source.

## Boundaries

- Read only: `.house-state/mcu-infinity-war/task-spine.sqlite`.
- Write only: the new sibling directory
  `.house-state/mcu-infinity-war/operator-board-20260823-v1`.
- No relay-registration source, refresh, inbox/controller action, provider
  call, network operation, browser/iTerm launch, task mutation, or dispatch.

## Acceptance

1. The completed bundle reports exactly one `READ_ONLY_NAMED_DATABASE` task
   source and zero named relay-registration sources.
2. The final board includes the MCU task card and both visible source-scope
   labels.
3. The source journal bytes/hash remain unchanged; bundle inspection and the
   normal source/receipt checks pass.
