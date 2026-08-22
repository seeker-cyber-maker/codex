# After-action review

The request exposed a viable local `codex exec` primitive, but not a safe
execution controller. The full-profile council narrowed the work to an offline
operation-controller test slice and explicitly blocked live launch. The accepted
`worker_exec` preparer now seals task/executable/prompt/argv identity, fixed
read-only containment, output reservation, model-selection truthfulness, and
explicit fake-runner consent tests. Its persistent controller adds exact
record-idempotency, expiring controller fencing, and a durable blocked-runtime
reconciliation state. This avoids misrepresenting a prepared
command, an advisory model route, or a subprocess exit as an assigned/accepted
agent result.

The required controller-owned lifecycle state, process-group
cancellation/reaping fixture, and version-pinned CLI argument contract are now
implemented as offline safety primitives. The captured installed grammar
confirms that `--ask-for-approval` is not admitted by `codex exec`, so it is
omitted from the fixed argv. This does not use the design review, the fixture,
or the fake runner as authority to consume provider quota or write a task
workspace. The next boundary is a fresh full-profile review of any proposed
live-launch interface and its pre-spawn/reconciliation behavior.
