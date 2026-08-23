# After-action council review - context grammar synthetic first slice

## Outcome

The synthetic slice is accepted after one outside-council finding was repaired
and deterministically revalidated. The work did not cross into a live secret
or runtime boundary.

## What worked

- The plan kept the runtime firewall, vault resolver, controller, and launcher
  explicitly out of scope, so source-level testing could be useful without
  accessing private inputs.
- Exact-schema sealed records made authority and execution overclaims directly
  testable.
- The independent review surfaced a concrete data-retention gap instead of
  generic architecture advice.
- The recommended repair was small, local, and directly covered by a new
  regression. The full suite increased from 222 to 223 passing tests.

## What was corrected

`project_mock_context_v1` previously applied its secret-looking check only to
scalar strings. A `BEHAVIOR_VALUE` list could therefore enter a projection and
be rejected only by the compiler. The final mock firewall validates scalar,
boolean/integer, and list forms before projection; unsafe/unsupported behavior
values produce a sterile terminal record.

## Review quality and provenance

- Council transport is preserved in `council-attempt-2` with all three valid
  response contracts and packet-hash echoes.
- OpenRouter used its explicitly declared Nemotron fallback after a 429 from
  the primary Gemma request.
- The council reviewed the immutable pre-fix transport snapshot. The final
  repair is supported by direct source inspection and deterministic tests, not
  by a false claim that the council reviewed final bytes.
- The preserved constructive-theorist response contains four Markdown
  hard-break trailing spaces. They are a known `git diff --check` exception in
  raw third-party evidence, not an authored-source formatting defect.
- Two live output directories are preserved. `council-attempt-2` is the
  explicitly observed completed run used for reconciliation. The earlier
  `council` directory later completed with the same transport hash and three
  contract-valid reviews after its initiating client wait yielded no session
  handle. It is retained as duplicate provenance, not counted as a separate
  independent review round.

## Next gate

Any real local firewall, Keychain/storage backend, resolver, trusted sink,
controller mutation, or launch binding requires a new authority decision and
security review. No part of this implementation grants it.
