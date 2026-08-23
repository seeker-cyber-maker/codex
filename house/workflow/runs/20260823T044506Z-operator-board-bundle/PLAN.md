# Offline operator-board bundle — plan v1

## Model advisory

- Case type: `semantic_implementation`.
- Recommendation: Terra / high.
- Reason: the work joins sealed local artifacts and a read-only task projection
  into a user-facing command, while preserving the no-dispatch and no-hidden-
  source boundaries.
- Reassess: before any live refresh, browser/iTerm binding, authority service,
  or automatic source discovery.
- This is advisory only; no client model switch is asserted.

## Objective

Add one keyboard-first command that writes a complete, inspectable, offline
operator-board bundle from explicitly supplied sources.  The command may build
an intentionally empty bootstrap bundle, but must label absent sources as
absent rather than infer that no live work exists.

## Non-goals

- No source scanning, default state database, live refresh, relay mutation,
  worker dispatch, provider call, browser/iTerm launch, background service,
  authority grant, or hardware identity claim.
- No replacement of the existing operator-board export or one-shot viewer.
- No claim that an empty bootstrap bundle represents the complete system.

## Graph and interfaces

1. `builder`: validate only named JSON registration input and, if supplied, an
   existing task-spine database opened read-only; render the existing static
   components; create a new bundle directory containing a self snapshot,
   inventory board, final board export, and canonical provenance manifest.
2. `verification`: replay the bundle's component receipts and test the CLI
   success and failure boundaries.  The real listener remains outside this
   implementation operation.

## Acceptance

1. `build-operator-board --output-dir ABSOLUTE_NEW_DIRECTORY` creates a new
   immutable bundle with an explicit source-scope manifest, a valid snapshot
   envelope, valid inventory board, final board and final receipt.
2. Optional sources are never discovered: registration input is an exact JSON
   list; task cards come only from a caller-named existing task-spine database
   opened read-only.  Omitted sources are marked `NOT_SUPPLIED`.
3. The task-spine read path verifies its journal and cannot create a database
   or schema.  Failed builds retain an incomplete marker and do not overwrite
   any pre-existing target.
4. The final board remains compatible with the existing viewer preparation.
5. Focused and complete tests, compilation, lint/format, diff, source seal,
   and secret-pattern scan pass.

## Authority and closure

This is a core-profile local implementation.  It has one implementation lane,
no external or long-running operation, and no promotion claim.  The existing
viewer council evidence remains scoped to the viewer-start command only.
