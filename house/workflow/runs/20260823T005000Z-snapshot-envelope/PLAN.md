# Immutable offline snapshot envelope — plan v1

## Model advisory

- Next phase: explicit local persistence and replay verification for a frozen
  operator snapshot.
- Recommendation: Terra / high.
- Reason: a small filesystem contract must precisely preserve no-overwrite,
  interrupted-write, and content-identity boundaries.
- Reassess: Sol / high before automatic capture, replacement/cleanup,
  retention policy, live source access, listener, browser/iTerm integration,
  task mutation/dispatch, or authority.
- This is advisory only; no client model switch is asserted.

## Objective

Store one caller-supplied, descriptor-verified relay preview index, task-card
index, and composed static snapshot in an explicit local directory beside
canonical descriptor and envelope receipts.

## Non-goals

- No source discovery or refresh; no database/relay/task state read; no
  replacement, deletion, cleanup, or retention policy; no listener, viewer,
  browser/iTerm, terminal input, provider/worker call, task mutation/dispatch,
  capability issue, authority action, or reverse channel.

## Acceptance

1. Only a caller-named absolute target under an existing parent is accepted;
   every existing target is refused without overwrite.
2. The descriptor is verified before the target is created. New files are
   created exclusive-only and a failed/interrupted write remains visibly
   incomplete rather than accepted.
3. Inspection requires the exact final file set, canonical receipt JSON, hash
   agreement, and descriptor-backed static replay.
4. Focused and all component tests plus compilation, lint, format, and diff
   checks pass.
