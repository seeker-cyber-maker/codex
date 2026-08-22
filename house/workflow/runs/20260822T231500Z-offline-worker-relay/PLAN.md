# Offline worker relay thin slice

## Objective

Evolve the Dream House mailbox concept into a durable local rendezvous relay
for independent workers, without creating a worker transport, dispatch path, or
authority path.

## Scope

- Strict, addressable envelopes and threaded replies.
- SQLite store-and-forward queue, acknowledgements, read-only lookup, and a
  hash-chained event journal.
- Finite TTL/hop and reply-turn budgets.
- Hash-bound artifact references and exact contract-version labels.

## Exclusions

- No provider calls, sockets, workers, process starts, model selection,
  artifact execution, or human-authority ceremony.
- No dynamic capability lookup; a future bridge can consume the separately
  sealed local-worker catalog only after a dedicated compatibility review.
- No adoption of upstream Codex's network/Noise rendezvous protocol.
