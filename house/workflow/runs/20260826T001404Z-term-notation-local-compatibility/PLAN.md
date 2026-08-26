# Plan: bounded TERM notation local compatibility

1. Persist structural intake and static-load receipts for six opaque variants.
2. Freeze the current TERM parser, dictionary, compatibility validator, and
   evaluator-only fixture set by hash.
3. Implement a no-dispatch local runner with five fixed prompt conditions per
   fixture and deterministic parse-plus-exact-field scoring.
4. Run each bound candidate once, append one receipt per candidate, then
   independently replay one selected completion from a clean model load.
5. Validate the receipt chain, write an explicit non-promotion verdict and
   AACR, then commit and back up only this run and its runner.

## Acceptance

- Every output is preserved and scored by the parser plus exact expected
  fields; malformed output remains negative evidence.
- The runner may load local model artifacts and write only this run directory.
- It may not call a provider, network, task, relay, authority, training, or
  candidate-promotion surface.
- The terminal verdict has the claim ceiling
  `SYNTAX_AND_FIELD_PRESERVATION_ONLY_NO_ROLE_OR_DIALECT_DECISION`.
