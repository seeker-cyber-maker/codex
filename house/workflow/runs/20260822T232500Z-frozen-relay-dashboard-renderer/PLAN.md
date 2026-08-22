# Frozen relay dashboard renderer — plan v1

## Workflow classification

- Project: existing; recovery disposition: resume from the sealed relay handoff.
- Profile: core.
- Case type: `semantic_implementation`.
- Single implementation node: render a previously prepared dashboard response.
- Independent verification: focused renderer tests, static analysis, and the
  complete existing House suite.

## Objective

Render one already-frozen `RelayDashboardAdapter` response as static,
self-contained HTML suitable for a later one-shot loopback viewer.

## Non-goals and authority boundary

- Do not call the dashboard adapter, relay, provider, worker, browser, or
  listener from the renderer.
- Do not create a listener or an interactive page.
- Do not add a write route, YubiKey operation, authentication mechanism, or
  automatic worker selection.

## Acceptance

1. Exact response schema and bounded body are required.
2. Dynamic text is HTML-escaped.
3. The document forbids script, network, form, image, and reverse-channel use.
4. Both normal (200) and explicit pending-integration (418) receipts render
   without changing their authority/dispatch meaning.
5. Focused tests, formatting, static analysis, full House tests, and diff
   checks pass.

## Model advisory

Recommend Terra / high. The current bounded semantic implementation has a
clear reference pattern and deterministic acceptance. Reassess to Sol / high
if a listener, browser write surface, or authority integration becomes in
scope. This is advisory only; no client model switch is asserted.
