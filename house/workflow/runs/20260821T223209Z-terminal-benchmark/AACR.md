# After-action review

## What worked

- The iTerm Python API provided exact object identity and exact cleanup without
  touching the user's existing window.
- Source inspection prevented unsafe substitutions: Warp launch YAML and Wave
  in-session credentials were correctly rejected.
- Paired default/render runs exposed a benchmark-semantic trap before a false
  terminal ranking was published.

## What failed or surprised us

- Human-gated permission/focus behavior invalidates unattended startup timing.
- Ghostty did not follow the expected one-command/automatic-exit lifecycle when
  launched through LaunchServices and created additional login children.
- The Ghostty preferences plist changed during the run even though its text
  config and saved-window restoration were disabled.
- Computer Use blocks terminal applications, preventing a common automated
  screenshot lane.

## Process improvement

Future GUI benchmarks must snapshot preferences and saved state before the
first launch, separate human activation from timed regions, and freeze exact
cleanup handles before opening a surface. Performance tools must declare which
terminal extensions they rely on; mode-dependent suppression cannot be treated
as equal work without a capability probe.

## Decision

Accept the evidence packet at a partial claim ceiling. Do not change the main
terminal, do not publish a winner, and do not reopen Warp/Wave automation until
a typed non-writing command interface or an explicitly authorized manual lane
exists.
