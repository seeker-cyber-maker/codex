# Test scope receipt

`python3 -m unittest discover -s house -p 'test_*.py'` is not the complete
House suite: Python's discovery rules skip several non-package `tests/`
directories, including `house/relay/tests`. This milestone therefore verifies
each component test directory directly:

- `house/authority_stage0/tests`
- `house/auto_switcher/tests`
- `house/context_tree/tests`
- `house/integration_health/tests`
- `house/operator_surface/tests`
- `house/relay/tests`
- `house/task_spine/tests`
- `house/terminal_companion/tests`
- `house/worker_catalog/tests`
- `house/worker_exec/tests`

All ten suites passed, totaling 231 tests. The missing unified test-runner is
an infrastructure improvement, not a claim that the static snapshot itself
reached a live integration boundary.
