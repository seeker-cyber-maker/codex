# Operator command registry

This offline registry is the first shared command inventory for agents, the
future human dashboard, and the iTerm companion. One typed declaration supplies
the searchable label, parameters, target requirements, surface visibility, and
authority class. Public plugin registration cannot enter the separately
compiled first-party namespace, and identifier or hotkey collisions fail
closed. This is an API separation, not an OS security boundary or plugin-loader
qualification.

The registry only produces machine-readable manifests and
`PREPARED_UNAUTHORIZED` request envelopes. It has no dispatcher, controller
connection, browser, iTerm registration, provider access, or native Codex-state
write. A button or hotkey is therefore a view over the same declaration used by
an agent, not a second implementation of an action.

Commands that act on existing state require an explicit stable target. A later
asynchronous adapter must pass that target through unchanged instead of reading
whatever task, thread, window, or session happens to be focused when it runs.

```sh
python3 -m unittest discover -s house/operator_surface/tests -v
```
