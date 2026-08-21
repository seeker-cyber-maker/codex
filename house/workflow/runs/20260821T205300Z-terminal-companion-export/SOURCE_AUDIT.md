# Pinned-source audit

Read-only audit of the pinned Codex source found:

- Final thread command items arrive in `item/completed` and include the final
  command presentation, cwd, status, aggregate output, exit code, and duration.
- The final-status enum is exactly `completed`, `failed`, and `declined`.
- `item/commandExecution/outputDelta` is partial display data and must not be
  merged into the authoritative final aggregate output.
- Codex redacts recognizable secrets in the client-facing command presentation;
  the same guarantee was not established for aggregate output.
- `command/exec/outputDelta` belongs to a distinct connection-scoped protocol
  and is excluded from this projector.

Evidence: `codex-rs/app-server-protocol/src/protocol/v2/item.rs`,
`protocol/item_builders.rs`, `protocol/event_mapping.rs`, and their generated
TypeScript schemas. The companion now enforces these boundaries.
