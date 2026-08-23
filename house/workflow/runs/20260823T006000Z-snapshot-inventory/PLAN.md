# Named offline snapshot inventory — plan v1

## Model advisory

- Next phase: evidence review of explicitly named local envelope paths.
- Recommendation: Terra / high.
- Reason: path identity, per-item failure classification, and receipt privacy
  need deterministic handling without turning selection into storage discovery.
- Reassess: Sol / high before arbitrary scanning, retention, cleanup, live
  source capture, listener/browser/iTerm integration, task mutation/dispatch,
  or authority action.
- This is advisory only; no client model switch is asserted.

## Objective

Provide compact, content-free selection evidence for one to 32 caller-supplied
absolute operator-snapshot envelope paths.

## Non-goals

- No directory/volume search, glob expansion, missing-path creation, retry,
  repair, deletion, cleanup, retention, source capture/refresh, database/task/
  relay state access, listener/viewer/browser/iTerm call, terminal input,
  provider/worker call, task mutation/dispatch, capability issue, authority
  action, or reverse channel.

## Acceptance

1. Only a bounded list or tuple is accepted. Relative, malformed, and duplicate
   canonical paths receive a separate input rejection; no path is inspected
   twice.
2. Each valid named path returns either content-free envelope/descriptor hashes
   or a separate envelope rejection reason. A failing path does not hide other
   paths' outcomes.
3. The inventory never returns stored document bodies and makes no filesystem
   mutation.
4. Focused and all component tests plus compilation, lint, format, and diff
   checks pass.
