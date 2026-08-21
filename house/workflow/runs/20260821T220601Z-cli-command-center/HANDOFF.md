# Handoff

## Completed

- Preserved and reviewed both supplied videos as hash-bound caption packets.
- Prioritized the Omarchy 4 keyboard/search lessons and explicitly pruned the
  unrelated desktop and OS feature set.
- Added `python3 -m house.operator_surface` with `list`, `search`, `keys`, and
  `prepare` operations.
- Kept human and JSON output on the same typed registry.
- Kept request preparation unauthorized and no-dispatch.
- Swept iTerm2, Warp, Wave, Kitty, and Ghostty as operator-surface donors while
  retaining iTerm2 3.7.0beta9 as the host.
- Recorded five admitted interaction requirements plus a same-Mac aesthetics
  and rendering benchmark protocol in `TERMINAL_DONOR_SWEEP.md`.

## Verification

Twenty-five focused operator-surface tests and all 123 House tests pass. Ruff,
formatting, compilation, diff checks, and direct CLI smokes pass. Independent
read-only review found no implementation blocker.

## Next acceptance boundary

The CLI is the primary operator surface baseline. A later fuzzy palette or
dashboard should consume its manifest, and an iTerm companion should observe
shell-integration events through explicit identities. No global hotkey, live
controller, arbitrary send-text, or terminal replacement should be added until
the concrete workflow and authority boundary are sealed. Rendering performance
remains unmeasured locally; execute the protocol in `TERMINAL_DONOR_SWEEP.md`
before making comparative performance claims.
