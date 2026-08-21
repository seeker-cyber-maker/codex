# Handoff

## Completed

Added `house.integration_health`, a dependency-free read-only health-contract
evaluator. It detects missing artifacts, dangling or external symlinks,
executable loss, byte-digest drift, malformed JSON, partial expected-value loss,
and stale expected values. It never executes or repairs an inspected target.

## Verification

- Six focused health-gate tests pass.
- Ruff, compileall, and `git diff --check` pass.
- The complete House suite passes: 135 tests.

## Integration disposition

This is the narrow iTerm2 health-monitoring principle made reusable for future
terminal, provider, cache-path, and hook bindings. It remains unbound: no real
configuration was inspected, no watcher was started, and every repair requires
a separate explicitly authorized operation.

## Next boundary

When one actual iTerm or provider binding is ready, seal a contract from its
documented configuration and run this evaluator at the relevant operation
boundary. Do not add an always-on poller or automatic repair as part of that
first binding.
