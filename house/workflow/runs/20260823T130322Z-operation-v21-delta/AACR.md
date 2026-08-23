# After-action review — operation v2.1 delta

## Outcome

The five v2 correction requirements are closed at the design level. Root
disposition is `ACCEPT_V2_1` for the pure structural implementation slice only.

## What worked

- The replacement lane received one immutable transport packet and confirmed
  its SHA-256.
- Its analysis independently mapped the five corrections and actively probed
  hidden host-file hashing, stale bindings, provenance, capability leakage, and
  recovery scope.
- The design keeps every execution-bearing producer and consumer outside the
  accepted first slice.
- Controller bytes and the prepared MCU operation remained unchanged.

## What failed or needed correction

- The reviewer exhausted its response length before returning the requested
  filled contract and disposition.
- The council harness reported `contract_valid` because the model echoed the
  blank response template headings before its analysis. That validator result
  is false-positive evidence and is overridden only in root synthesis, not by
  altering the retained manifest.
- The phrase `canonical validation/hashing` was needlessly ambiguous. The final
  contract now limits this to schema checks, lexical string checks, and
  canonical in-memory record serialization/hashing.

## Lessons

- A response-schema checker must verify required enum values and reject
  placeholders; heading presence alone is insufficient.
- `finish_reason=length` cannot be called complete when the required terminal
  disposition is absent.
- A structural hash boundary must say what bytes are hashed and must not imply
  observation of the object named by a descriptor.

## Next gate

Implement the pure task-card-v2 verifier, route-selection record/verifier,
zero-host-I/O operation-v2 assembler/verifier, and deterministic fixtures.
Acceptance requires all ten falsification cases plus proof that controller,
workspace, and output roots are unchanged. No live worker path enters that
phase.
