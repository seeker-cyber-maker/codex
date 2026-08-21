# Operator command registry

This offline registry is the first shared command inventory for agents, the
future human dashboard, and the iTerm companion. One typed declaration supplies
the searchable label, parameters, target requirements, surface visibility, and
authority class. Public plugin registration cannot enter the separately
compiled first-party namespace, and identifier or hotkey collisions fail
closed. This is an API separation, not an OS security boundary or plugin-loader
qualification.

The registry produces machine-readable manifests and `PREPARED_UNAUTHORIZED`
request envelopes. Its one admitted stateful adapter is `enqueue-task`: it
validates the declared task request and writes one idempotent record to an
explicit local `TaskInbox`. It does not acquire a controller lease, admit the
task to the spine, start the requested recipient, select a provider, or grant
authority. A button or hotkey is therefore a view over the same declaration
used by an agent, not a second implementation of an action.

Commands that act on existing state require an explicit stable target. A later
asynchronous adapter must pass that target through unchanged instead of reading
whatever task, thread, window, or session happens to be focused when it runs.

```sh
python3 -m unittest discover -s house/operator_surface/tests -v

python3 -m house.operator_surface list
python3 -m house.operator_surface search terminal preview
python3 -m house.operator_surface keys
python3 -m house.operator_surface prepare codex.house.task.inspect \
  --target-kind task --target-id task-123
python3 -m house.operator_surface enqueue-task \
  --inbox-db /tmp/codex-house-inbox.sqlite --enqueue-id review-001 \
  --requested-by human:tiga --title "Review QP2A evidence" \
  --summary "Review the bounded evidence packet and leave a signed report." \
  --recipient reviewer --case-type evidence_review
```

The CLI is the first operator surface. It is intentionally non-interactive and
dependency-free: shell history, ordinary terminal navigation, and exact command
arguments remain visible and scriptable. A future palette or dashboard must
call the same `enqueue_task()` adapter and consume this manifest instead of
introducing another action catalog. `specific_model` requires an explicit
`--recipient-id`; it records a requested recipient only and never launches it.
