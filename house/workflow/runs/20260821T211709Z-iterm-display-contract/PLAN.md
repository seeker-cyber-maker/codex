# Versioned iTerm display contract

## Objective

Implement the smallest offline, one-way bridge contract from accepted Codex
terminal cards to a future local iTerm2 presentation adapter.

## Invariants

- Codex app-server cards remain the semantic source of truth.
- Every card remains `DISPLAY_ONLY` with `dispatch: NOT_ATTEMPTED`.
- Protocol revision 1 has no reverse channel and performs no transport.
- Compatibility is explicit and independent of application version numbers.
- Batches are bounded, sequence-labeled, predecessor-linked, deterministically
  identified, and verifiable as a complete in-memory chain.
- Display text is plain-text-only with terminal controls and invisible Unicode
  format controls made visible; raw source cards remain outside the batch.
- Identity hashes prove byte identity only; they are not signatures or authority.

## Acceptance

Focused tests must prove deterministic identity, compatibility decisions,
sequence/replay linkage, bounded input, fail-closed authority fields, and CLI
projection. The full House test suite, Ruff, compilation, JSON parsing, and diff
checks must pass without contacting iTerm, Buddy, a relay, Codex, or a provider.

## Model advisory

Routine bounded implementation: Terra/medium. Reassess before live transport or
any security-sensitive reverse channel.
