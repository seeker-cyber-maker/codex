# Local terminal benchmark plan

## Objective

Measure the locally installed iTerm2, Warp, Wave, Kitty, and Ghostty without
changing the user's terminal choice or disturbing existing sessions. Produce a
reproducible evidence packet that separates parser throughput, rendered-output
proxies, resource observations, correctness, and subjective presentation.

## Frozen scope

- Use only installed local applications and local fixtures.
- Preserve iTerm2 as the main host and leave all pre-existing iTerm2 windows,
  tabs, sessions, profiles, and preferences untouched.
- Do not update an application, log in, use cloud/AI features, create saved
  workspaces, install benchmark software, or write terminal configuration.
- Launch only isolated benchmark instances/windows that can be identified and
  closed exactly. If exact isolation or cleanup cannot be proved, record that
  lane as unqualified instead of forcing it.
- Store generated fixtures, raw measurements, screenshots, and reports only in
  this run directory.

## Measurement hierarchy

1. Inventory installed version, current process state, launch interface, and
   configuration locator without reading secrets.
2. Qualify a bounded way to run an identical local command and to close only
   the resulting benchmark surface.
3. Run at least five repetitions where a terminal has a comparable interface:
   ASCII, Unicode, and CSI parser throughput first; image protocols separately.
4. Treat any `--render` result as an asynchronous rendering proxy, not input
   latency or frame pacing. Do not claim keyboard-to-pixel latency without a
   hardware/high-frame-rate-camera measurement.
5. Capture an identical correctness/aesthetics fixture where safe. Review
   Unicode width, graphemes, color, links, legibility, focus recovery, visual
   grouping, and fatigue. Record effective defaults rather than changing them.
6. Sample bounded idle/output CPU and memory observations where the benchmark
   process can be attributed unambiguously. Do not infer GPU/energy results from
   CPU measurements.

## Fixtures and bounds

- The common parser driver is the installed `kitten __benchmark__` command.
- Initial workloads: `ascii`, `unicode`, and `csi`, five repetitions each.
- Optional lanes: `unique_unicode`, `long_escape_codes`, and `images` only
  after the common lane is stable.
- Each app qualification attempt is limited to one isolated instance and five
  minutes. Each benchmark case is limited to 60 seconds.
- No workload may use network access, credentials, or files outside this run
  directory except installed binaries and read-only configuration metadata.

## Cleanup and acceptance

- Record the pre-run process inventory.
- Close only exact benchmark instances/windows; never quit a pre-existing app
  process or interact with a pre-existing iTerm2 session.
- Reconcile post-run processes against the pre-run inventory.
- Acceptance requires raw receipts, explicit comparability labels, a result
  table, limitations, and zero unaccounted persistent application processes or
  configuration changes caused by the run.
- The benchmark may inform Dream House presentation decisions. It may not
  switch the user's main terminal or authorize a new renderer.
