# Review: adversarial-methodologist

Packet SHA-256: cf1daf7ca5e0227a8e4dad1639d0838ad79d06168cbf23ff51402a90ee2b39f6
Dispatch: local same-model review. Disposition: completed.

## Verdict

Narrow accept conditional on atomic non-reacquirable intent semantics.

## Direct observations

- Existing acquisition can reacquire an expired lease even if a live intent
  exists, unless reconciliation happens separately.

## Inferences

- Tests must create an intent, expire the lease, and prove another holder
  cannot acquire it.  Incomplete intent recovery must become `UNKNOWN_NOT_RERUN`.

## Unsupported or contradicted claims

- Existing fixture-only callback naming is not a technical execution barrier;
  this new slice must not touch it or add any callback/runner.

## Recommendation

Add migration, stale fence, intent-crash recovery, and no-reacquire tests.

## Limitations

Read-only static review; no process or provider was invoked.
