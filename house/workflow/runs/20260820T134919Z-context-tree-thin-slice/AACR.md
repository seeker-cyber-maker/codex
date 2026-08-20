# After-action council review

No outside council was required for this downstream-only offline fixture.

## What held

- Source tracing prevented a premature upstream protocol patch.
- The fixture makes fork boundaries explicit instead of inferring them from a
  child response that does not contain them.
- Separating payload references from the journal exposed the difference between
  journal tamper detection and external artifact digest verification.
- Stale identity checks preserve task and authority separation.

## Limits

- No live app-server stream, restart, pagination, interruption, or secret
  redaction was exercised.
- Hash chaining proves detected mutation, not append-only filesystem policy or
  trusted timestamping.
- The session-root normalization is a downstream compatibility rule pending a
  live fixture and any future upstream protocol change.

## Adoption gate

Admit a live adapter only after a disposable app-server fixture reproduces the
same tree and context hashes across restart without opening native storage
directly. Revisit an upstream patch only if the adapter cannot capture an exact
boundary or stable session identity through supported protocol messages.
