# After-action council review

## Outcome

The generated-canary helper-containment design reached
`ACCEPT_DESIGN_ONLY` after one revision cycle. No runtime or secret-bearing
capability was exercised.

## What changed during review

The first candidate correctly separated the helper from the generic Python
supervisor but over-applied `POSIX_SPAWN_SETSID`, relied on static path identity,
and lacked an explicit pre-canary proof-of-capability gate. v1.1 makes the
parent the sole session leader, authenticates running code before canary
injection, orders limits safely, and requires bounded denial probes.

## Evidence quality

The strongest outside result is the complete Antigravity delta acceptance.
ClinePass is useful but truncated. OpenRouter/Nemotron is preserved as a
negative provider-quality receipt because it repeated prompt-format reasoning
and invented a literal placeholder absent from the transport packet. The chair
accepted only after direct source reconciliation.

## Reusable lesson

Static declarations and hashes bind intent and bytes; they do not prove active
containment. For helper work, admission needs both identity of the running code
and pre-secret capability falsifiers. Process-tree kill claims also require an
explicit session/group topology, not merely `start_new_session` everywhere.

## Next gate

Implement fixed codecs and spawn-disabled native sources, plus deterministic
build/signature/entitlement inspection. Stop again before the first process
launch.
