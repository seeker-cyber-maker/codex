# Council synthesis

## Decision

**Narrow accept: mock-only profile/authority records, no process factory.**
All three reviewers independently confirmed packet SHA-256
`77b8787f5ad63f22dcba30f6b862fb06f9c3e0467261b7db35e1b2e8519b826b`.
This was local same-model review and cannot authorize configured Codex/provider
execution.

## Required corrections

1. A task card's `specific_model` request cannot select a real execution model.
   A later profile and human authority must independently bind it or reject it.
2. Mock-only code must not reuse the generic supervisor or accept arbitrary
   callbacks.  It must have no executable or subprocess dependency.
3. Future profile fields must cover executable/version/help, config/home,
   hooks, environment allowlist, provider/account freshness, egress, expiry,
   and exact model identity.  Authority must be single-use and atomically
   coupled to spawn intent.

## Smallest next action

Implement canonical `MOCK_ONLY` runtime-profile and authority validation only.
Configured Codex and provider execution remain blocked.
