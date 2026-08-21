# Advisory routing and manual-route intake

## Objective

Make the existing ChatGPT-family policy usable at task admission without
silently switching models or weakening route authority.

## Scope

1. Add deterministic model/effort advisory metadata to auto-route receipts.
2. Preserve an explicit manual Daybreak choice independently from the automatic
   route receipt.
3. Bind that choice to submission identity and reject bad choices before a
   journal mutation.

## Acceptance

- Coding recommends Terra/medium; consequential review recommends Sol/high;
  routine bounded work recommends Luna/low with Spark leaf eligibility only.
- Automatic route and manual selection remain separately hash-bound and both
  say `NOT_ATTEMPTED` for dispatch.
- Unknown and automatically selected routes fail closed without task creation.
- Focused tests, lint, compilation, and diff checks pass.
