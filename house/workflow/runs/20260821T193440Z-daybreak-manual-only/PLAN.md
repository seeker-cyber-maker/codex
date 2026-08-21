# Daybreak manual-only catalog guard

## Objective

Expose the already registered Daybreak Blue contractor lane to manual route
pickers without permitting the automatic selector to choose it while the usage
pool boundary is unresolved.

## Authority and boundaries

- Source: direct user instruction on 2026-08-21.
- In scope: offline Dream House route catalog, automatic exclusion, tests, and
  operator documentation.
- Out of scope: provider health probing, credentials, dispatch, quota claims,
  automatic admission, and changes to the provider-orchestration registry.

## Acceptance checks

1. The catalog lists `daybreak-blue-personal` at loopback port 4018.
2. The record is manual-selectable, auto-ineligible, and health-unverified.
3. Automatic selection records
   `manual_only:usage_pool_boundary_unknown` and cannot select the route.
4. Catalog callers cannot mutate policy state through the returned object.
5. Focused and full offline regressions, Ruff, compilation, and diff checks
   pass without provider access.
