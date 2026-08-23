# Host observer contract v1.1 - handoff

## Milestone

Design accepted as the immutable reviewed `HOST_OBSERVER_CONTRACT.md` plus
`V1_1_DELTA.md`.

The observer will inventory executable bytes, caller-supplied CLI capture,
workspace/project inputs, and source-derived effective-context contributors.
Its only success state is `OBSERVED_NOT_QUALIFIED`; it grants no authority.

## Outside review

- Transport packet SHA-256:
  `f8e111c09585ce48bb7c59555839393bb59bf8c101bb000bae056a503f740989`.
- ClinePass security architect: completed and accepted; raised the path/byte
  binding residual risk adopted in v1.1.
- OpenRouter explicit-free assurance reviewer: completed and accepted.
- OpenCode Go red teamer: both bounded attempts timed out; no review exists.

## Corrections and limits

- Use directory-anchored, no-follow file descriptors, same-descriptor pre/post
  `fstat`, and a final entry-to-descriptor identity check.
- Never read or hash credentials or secret values.
- Never execute the observed binary or invoke Codex/Git/plugins/MCP/hooks.
- Treat request data as adversarial.
- Neither observer output nor its hash authenticates provenance.
- The accepted design does not change the prepared MCU operation or create a
  worker eligibility path.

## Coordinator

The user delegated Dream House project-coordinator authority to Codex during
this phase. `COORDINATOR_AUTHORITY.md` records the working scope and retains
separate gates for credentials, cost, destructive work, public release, and
live execution.

## Next acceptance check

In a fresh bounded phase, implement only the request/schema, observer, pure
verifier, and required falsification fixtures. Stop on any need for output
reservation, credential/account evidence, controller mutation, launcher,
provider call, result admission, or path-based fallback.
