# Context grammar synthetic first slice - handoff

## Milestone

Accepted synthetic-only implementation:

- `house/worker_exec/context_grammar.py`: sealed schemas, compiler, verifier;
- `house/worker_exec/mock_context_firewall.py`: fixture-only projection and
  non-executing immutable-binding decision;
- `house/worker_exec/mock_vault.py`: opaque mock vault references/leases/
  incidents/exposure/front-end records; and
- focused regression tests for all seven design-delta falsifiers.

Final gates: 13 focused tests and 223 House tests passed; Ruff, `py_compile`,
`just fmt`, and diff check passed. Controller remains `PREPARED` with zero
leases and zero launch intents.

## Review result

Council transport `2d8853c4c92b2718e8a3b74e748ae88eb46e8ebab3cc0eb1cdf6857fb8299a87`
received three completed responses. One narrow real issue—behavior-value lists
were not screened before retention—was accepted, fixed, and covered by
`test_02b_behavior_list_secret_is_rejected_before_projection`.

## Do not infer

- No live configuration, Codex app config, environment, Keychain, credential,
  vault storage, resolver, network, or process was read or used.
- No plaintext is retrievable from these APIs.
- No controller state, lease, or launch intent was changed.
- The mock firewall is not a proof of future real-parser isolation.
- Hashes prove deterministic record identity, not observer authenticity.

## Next acceptance check

Before real integration, create a new authority-gated threat-model packet that
defines the local firewall TCB, immutable read/binding mechanism, resolver
namespace limits, qualified sink, audit/incident path, and disposable test
environment. Use Sol/high or stronger for that security-sensitive design
review; do not silently reuse this synthetic implementation as a real vault.
