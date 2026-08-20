# After-action council review

Disposition: source baseline accepted.

What worked:

- Keeping all downstream control files in `house/` left upstream core untouched.
- The repository-pinned Rust toolchain built the CLI and app-server on Apple
  Silicon within the disk and time budgets.
- Isolated `CODEX_HOME` probes captured useful release drift without inference
  or personal-state access.

Correction retained:

- The receipt script's first pass used a JSON-style lowercase Boolean in
  Python. It failed before writing output; the single bounded retry passed.
- A secret scan initially matched the public field name `access_token` in help
  text. The accepted check looks for token-shaped values, not harmless names.

Next run:

- Start from existing upstream session/event facilities and prove one conserved
  fork/replay/context-view thin slice.
- Keep Pi, Atomic, and OMP as separately pinned donor lanes until their exact
  identities, licenses, and fixtures are admitted.
- Do not activate providers, local models, or training from this baseline.
