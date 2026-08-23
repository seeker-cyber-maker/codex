# After-action review — operation v2 council

## Outcome

The council successfully tested the design across external provider lanes and
supported the central separation of routing, operation, qualification, and
authority. Root disposition is `REVISE_DESIGN`, not majority acceptance.

## What worked

- Dry-run and live dispatch used the same 44,645-byte transport packet and
  SHA-256.
- Two substantive responses independently confirmed the packet hash.
- The OpenRouter lane completed at zero reported cost; ClinePass produced a
  detailed review before its completion ceiling.
- The failed OpenCode lane and both timeouts remain visible in the denominator.

## What changed

The synthesis corrected three subtle but consequential problems:

1. disagreements refuse; no later record has precedence to repair an earlier
   record;
2. a hash is identity, not authenticated provenance; and
3. a pure assembler cannot perform hidden filesystem observation.

It also requires typed routing semantics and an explicit project-config
strategy before implementation.

## Cost and failure note

ClinePass reported `0.01046716` in provider accounting despite use of the
existing lane. This is retained as observed accounting, not silently rounded
to free. OpenCode Go consumed two 90-second attempts with no visible response;
the run did not add another retry or substitute a different unplanned lane.

## Next gate

Produce v2.1 as a bounded design delta, then obtain one replacement adversarial
review over the delta. Implementation remains paused.
