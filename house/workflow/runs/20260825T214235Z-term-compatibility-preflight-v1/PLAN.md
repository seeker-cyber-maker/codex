# Plan: TERM compatibility preflight v1

1. Freeze the existing TERM and offline-A2A RFC sources by hash.
2. Add an evaluator-only synthetic corpus with closed semantic fields.
3. Add a pure validator that checks corpus identity, explicit no-effect state,
   no execution authority, empty roster, and outstanding prerequisites.
4. Add normal and adversarial tests: altered effect, roster, fixture, and
   condition inputs must fail closed.
5. Verify, source-seal, commit, and privately back up only this run's files.

## Acceptance

- The valid static preflight reports `NOT_READY_NO_DISPATCH`.
- `require_execution_authority` always rejects this preflight.
- No model, provider, task, relay, prompt, or authority surface is called.
- The static corpus and manifest pass the pure validator; adversarial mutations
  fail; source identity is sealed.
