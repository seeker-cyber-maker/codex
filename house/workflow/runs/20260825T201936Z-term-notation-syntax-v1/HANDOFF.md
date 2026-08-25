# TERM notation syntax v1 handoff

## Result

The first standalone TERM notation syntax and dictionary are implemented under
`house/term_notation`. The module parses exactly one versioned record into an
immutable typed projection and fails closed on syntax outside the dictionary.

## Verified behavior

- `TERM?`, `TERM=`, `TERM~`, `PREF?`, and `PREF=` are supported.
- Fields are closed, unique, canonically ordered, and bounded.
- `ALT` is accepted only with `not_preferred`.
- `not_stated` is wrapper-only and cannot be emitted as a valid model response.
- Fifteen focused tests and Ruff pass.
- The parser has no I/O, hook, prompt, task, relay, execution, admission, or
  authority dependency.

## Chat/Work contribution

One supervised, tool-free Chat/Work review completed. Duplicate-field and ALT
grammar findings were adopted. Its preference response was contract-invalid,
so the recorded preference is `not_stated`.

## Stop-hook branch

The visible Stop failure is a local `cc-status` output-contract mismatch. The
global Stop registration has already been disabled, while an engine preserved
through a renderer-only restart can continue displaying the loaded handler.
TERM has no direct dependency, and this run changes neither Codex Rust nor the
global hook configuration.

## Authority boundary

This milestone is source-only. It does not activate TERM in prompts, task
records, compaction, relay traffic, or the operator board. Empirical benefit
and cross-model preference remain unproven.

## Next gate

Design and freeze the offline compatibility experiment before any prompt or
task integration. Separately, if Stop status updates are desired again, build
and test a terminal-companion adapter against the exact current Codex Stop JSON
contract.
