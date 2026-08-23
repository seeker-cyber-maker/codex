# Operator-board source-scope display — plan v1

## Model advisory

- Case type: `semantic_implementation`.
- Recommendation: Terra / high.
- Reason: a visible provenance statement must follow the same exact input
  contract as the frozen documents it describes.
- Reassess: before showing source paths, adding a refresh control, or binding
  a live task or relay source.

## Objective

Render the source-state of each top-level board projection directly inside the
frozen Relay previews and Task cards sections. The bootstrap board must visibly
say `NOT_SUPPLIED`; named input states must be distinguishable without
displaying unbounded source content or implying completeness.

## Non-goals

- No new input discovery, source reads, state writes, refresh, task dispatch,
  provider call, browser/iTerm action, or authority behavior.
- No source paths, task bodies beyond existing cards, or source documents added
  to the board beyond the currently sealed component projections.

## Acceptance

1. The two component renderers accept only their respective declared scope
   states or no scope annotation, and reject unknown scope text.
2. The bundle renderer passes its validated source states into those
   components; a bootstrap bundle visibly retains `NOT_SUPPLIED` twice.
3. Existing no-annotation component outputs remain compatible with prior
   snapshot, envelope, board, and viewer contracts.
4. Focused and full tests, lint/format, compilation, diff, and source-seal
   checks pass.
