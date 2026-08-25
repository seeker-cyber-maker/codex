# TERM compatibility preflight v1 handoff

## Result

The first evaluator-only synthetic corpus and pure compatibility preflight
validator are frozen under `house/term_notation`. The static manifest validates
only as `NOT_READY_NO_DISPATCH`; any execution request is rejected.

## Verified

- Eight canonical semantic families and five ordered conditions are present.
- Fixture identity is bound by canonical semantic SHA-256.
- A real model roster cannot enter this source-only manifest.
- Provider, prompt, task, relay, and authority effects must all remain
  `NOT_ATTEMPTED`.
- Eighteen focused tests pass, including four adversarial preflight mutations.

## Not established

No model compatibility, dialect need, token saving, preference, compaction
recovery, provider capability, or safety result has been measured.

## Next gate

Create a separately authorized experimental run with a qualified six-variant
roster, sealed decoding and budget rules, independent scorer, retention terms,
and explicit human authorization to collect offline model outputs. Do not reuse
this preflight as execution authority.
