# TERM notation syntax v1 plan

## Sealed first slice

1. Freeze the existing design inputs and exact write scope.
2. Send a compact evidence capsule to the supervised Chat/Work lane. Treat its
   response as advisory and locally verify every adopted point.
3. Add a versioned dictionary and an unambiguous line grammar.
4. Add a deterministic, side-effect-free parser/validator plus positive,
   malformed, and control-effect negative fixtures.
5. Inspect the current Codex stop-hook path and record whether TERM depends on
   it. Do not patch that shared runtime in this slice.
6. Run focused tests, validate evidence, write a handoff/AACR, and commit only
   the declared scope.

## Write scope

- `house/term_notation/**`
- `house/workflow/runs/20260825T201936Z-term-notation-syntax-v1/**`
- `house/communications_rfc/PACKET_MANIFEST.json` only if the completed slice
  is admitted into that packet

## Acceptance

- Dictionary and syntax have stable version identifiers.
- Parser accepts every declared form and returns typed data.
- Unknown operators, fields, duplicates, ambiguous delimiters, oversized
  inputs, and task/authority-like extensions fail closed.
- Preference is explicit and independent from meaning agreement.
- Parser performs no I/O, execution, dispatch, task mutation, or authority
  mutation.
- Chat/Work advice is preserved with transport limitations and local
  disposition.
- Stop-hook compatibility conclusion is evidence-bounded.
- Unrelated dirty work remains unstaged.
