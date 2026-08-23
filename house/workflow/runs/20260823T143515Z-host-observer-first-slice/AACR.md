# After-action council review - host observer first slice

## Outcome

The first implementation slice is accepted as non-runtime structural evidence.
All deterministic checks pass and all three outside lanes returned
`ACCEPT_FIRST_SLICE` at the bounded claim ceiling.

## What worked

- The prior design review exposed the path-to-bytes race before implementation;
  descriptor-relative reads and dedicated race fixtures closed it directly.
- Exact schema and cross-record binding checks kept the observer and verifier
  independently falsifiable.
- Failed attempts expose no partial descriptor, and retry tests prove the next
  attempt starts from an empty observation set.
- The council packet contained the exact source and fixtures, and every lane
  confirmed the same hash.

## What needed correction

- Raw CLI capture initially rejected the ordinary trailing newline from
  `--version`; the validator now accepts raw bounded text while the existing CLI
  contract performs semantic normalization.
- One replacement-race fixture initially mutated the wrong directory during
  the executable read. The corrected fixture races the config descriptor it
  intends to test.
- Cross-input policy/grammar/capture binding checks were duplicated only in the
  observer at first; they are now shared with the pure verifier.
- The OpenRouter Gemma primary returned 429. Its explicit-free Nemotron fallback
  completed, but retained response-template placeholders despite a substantive
  acceptance verdict.

## Lessons

- Capture bytes and normalized semantic values are different types and should
  not share a whitespace validator.
- A race fixture must identify the exact descriptor and parent directory it is
  mutating.
- Negative-state cleanliness and retry isolation deserve direct tests, not
  inference from the happy path.
- Secret pattern rejection is a useful containment layer, not a proof of
  semantic non-secrecy.
- The 1,118-line formatted module is closed and tested, but should not grow;
  later behavior belongs in separate grammar/projection modules.

## Next gate

Design a source-versioned context-grammar producer and semantic secret-safe
projection. Keep it isolated from live execution and from arbitrary private
configuration until separately reviewed.
