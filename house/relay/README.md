# Offline worker relay

`house.relay` is the first durable rendezvous seam for worker-to-worker
coordination. It is local SQLite state only: no provider, socket, process,
model, task execution, or human-authority code is called.

Each strict envelope carries a sender, recipient, thread/reply relation,
contract version, hash-bound artifact reference, TTL/hop bound, and finite turn
budget. The relay appends hash-chained queue, delivery, and acknowledgement
events. A stored or delivered proposal never grants any authority.

`RelayDirectory` may expose a sealed `worker_catalog` receipt as static
recipient/capability metadata. It preserves a catalog's `NOT_ATTEMPTED` runtime
disposition; even an `active` catalog label remains descriptive and cannot
select, probe, contact, or dispatch a worker.

The keyboard-first interface is available through `python3 -m house.relay.cli`.
`directory-address` and `directory-capability` require an explicit sealed
receipt path; `submit`, `receive`, `acknowledge`, `status`, and
`verify-journal` require an explicit local relay database. It opens no socket
and reads no provider configuration.

`RelayDashboardAdapter` is the corresponding pure request contract for a future
loopback dashboard. It binds no port: `GET` can prepare directory/capability or
envelope-status views, while each write-like route returns `418` with an
explicit pending-integration receipt. A listener, browser session, and human
authority gate remain separate future work.

`render_dashboard_html()` turns one exact, already-frozen adapter response into
an inert, self-contained dashboard document. It does not call the adapter or
bind a viewer; any later one-shot viewer binding must preserve the established
loopback capability and observe-only gates.

`prepare_relay_dashboard_viewer()` is that explicit preparation seam. It
constructs the existing capability-bound `OneShotLoopbackViewer` from a frozen
response but does not call `start()`, launch a browser, register with iTerm, or
open any worker, provider, write, terminal-input, or authority path.

`build_relay_preview_registration()` adds the preceding offline operator
contract: it hashes the inert document and prepares an exact display-only
operator request. The descriptor contains neither the document nor a capability
URL, and it does not construct/start a viewer or contact a browser or iTerm.

`render_relay_preview_card_html()` is the descriptor-only presentation layer.
It verifies both descriptor and command hashes, displays fixed control-plane
fields and hashes, and deliberately omits dashboard content and all capability
material. It has no interactive or transport behavior.

`render_relay_preview_index_html()` composes up to 32 independently verified
preview registrations into one deterministic, content-free, read-only index.
It rejects invalid or duplicate registrations and adds no refresh, listener, or
action behavior.

`render_task_card_index_html()` separately composes up to 32 exact canonical
`task_spine` task-card projections into deterministic, escaped static HTML. It
requires advisory-only routing and `NOT_ATTEMPTED` dispatch, rejects malformed
or duplicate cards, and neither consults nor changes task-spine state. It does
not create/mutate/dispatch tasks, bind a listener, start a viewer, call a
browser or iTerm, accept terminal input, grant authority, or open a reverse
channel.

`render_operator_snapshot_html()` composes the already-rendered relay-preview
and task-card indexes into one static operator document. It does not invoke
either renderer or read their backing state. Both source documents must carry
their exact static signatures and contain only the narrow supported fragment
grammar; malformed, swapped, or active fragments fail closed. The snapshot has
no refresh, listener, browser/iTerm call, terminal input, task/relay mutation,
worker/provider call, capability issue, authority action, or reverse channel.

`build_operator_snapshot_descriptor()` binds two caller-supplied frozen index
documents and their exact static composition by SHA-256. It stores no document
bodies, replays the static composition before issuing a descriptor, and records
only offline/no-authority control states. `verify_operator_snapshot_descriptor()`
repeats that bounded replay; neither function retrieves sources, refreshes
state, binds a listener, or makes an action available.

`write_operator_snapshot_envelope()` is the explicit local persistence seam for
one already-verified snapshot: it requires an absolute, non-existent target
directory under an existing parent, writes the two index documents, snapshot,
canonical descriptor, and hash-bound canonical envelope, and refuses every
existing target. An `.INCOMPLETE` marker remains if a filesystem write is
interrupted; `inspect_operator_snapshot_envelope()` fails closed on that marker,
unexpected files, noncanonical JSON, changed bytes, or failed static replay.
Neither function discovers sources, refreshes state, starts a viewer, binds a
listener, calls iTerm/browser/provider/worker code, accepts terminal input, or
grants authority.

`inspect_operator_snapshot_inventory()` provides selection evidence only for a
caller-supplied list or tuple of one to 32 absolute envelope paths. It does not
scan a parent or storage volume, create a missing path, retry an incomplete
write, repair/delete anything, or expose stored document bodies. Each named
path receives either its descriptor/envelope hashes or a separate rejection
reason, so a missing or invalid envelope cannot be mistaken for a valid one.

The keyboard-first `snapshot-inventory` relay CLI command takes one required
`--input` UTF-8 JSON array of those explicit paths and prints the same
content-free inventory. It does not accept a default path or any scan/write,
and it opens no relay database, listener, viewer, browser, iTerm, worker, or
provider connection.

Copy `examples/snapshot-inventory-paths.example.json`, replace every placeholder
with a real absolute envelope directory, then run:

```bash
python3 -m house.relay.cli snapshot-inventory --input /path/to/paths.json
```

The example paths are deliberately nonexistent; the command reports missing or
invalid named locations instead of creating, guessing, or scanning for them.

`render_operator_snapshot_inventory_html()` is the corresponding static status
board. It accepts only caller-supplied records already returned by the named
inventory, displays escaped path text and receipt hashes, and identifies valid
and rejected records separately. It neither calls the inventory nor reads a
path, so it is a frozen presentation—not a live dashboard.

`render_operator_board_html()` composes one caller-supplied frozen operator
snapshot and one caller-supplied inventory board into a single inert operator
page. It validates both source signatures and static fragments, and does not
run the inventory, access files, refresh data, or bind a viewer.

`write_operator_board_export()` is the explicit local persistence seam for the
composed page. It requires a new absolute output file below an existing parent,
writes that page and a canonical companion receipt without overwrite, and
leaves a sibling `.INCOMPLETE` marker if interrupted. The receipt binds the
board and its two caller-supplied source-document byte identities; it is an
integrity receipt, not proof of author identity or source correctness.
`inspect_operator_board_export()` verifies the board and companion receipt but
does not retrieve or replay source documents.

The keyboard-first `export-operator-board` command connects only explicit
frozen source files to that export seam. It requires all three paths and opens
no relay database or viewer:

```bash
python3 -m house.relay.cli export-operator-board \
  --operator-snapshot /path/to/frozen-operator-snapshot.html \
  --inventory-board /path/to/frozen-snapshot-inventory.html \
  --output /absolute/path/to/new-operator-board.html
```

The output must be a new absolute file path below an existing parent; an
existing board, companion receipt, or incomplete marker is rejected. The
command has no default source or destination, no source discovery, no scan,
no overwrite option, and no browser, iTerm, listener, worker, provider, or
authority behavior.

`build-operator-board` is the usable offline assembly command. It creates one
new bundle directory containing a frozen self-snapshot envelope, the matching
inventory document, the completed operator board, its receipt, and a canonical
`bundle.json` provenance manifest. With no optional sources it produces an
honest bootstrap bundle: both source records are marked `NOT_SUPPLIED`, rather
than implying that the machine has no relay previews or tasks. It does not
search for those sources.

Those two source states are also rendered inside the frozen Relay previews and
Task cards sections. They use only the fixed values `NOT_SUPPLIED`, `NAMED_JSON`,
and `READ_ONLY_NAMED_DATABASE`; the page does not turn an omitted source into a
claim that the corresponding live system is empty.

```bash
python3 -m house.relay.cli build-operator-board \
  --output-dir /absolute/path/to/new-operator-board-bundle
```

To include known data, name each source explicitly. `--relay-registrations`
is a UTF-8 JSON array of already-validated frozen preview registrations.
`--task-spine-db` is an existing absolute task-spine SQLite file opened in
read-only mode; its journal is verified before its task cards are projected.
Neither option has a default location and neither can create a state database.

```bash
python3 -m house.relay.cli build-operator-board \
  --output-dir /absolute/path/to/new-operator-board-bundle \
  --relay-registrations /absolute/path/to/relay-registrations.json \
  --task-spine-db /absolute/path/to/task-spine.sqlite
```

After a successful build, the completed board for the one-shot viewer is:

```text
/absolute/path/to/new-operator-board-bundle/operator-board.html
```

The bundle is a named-sources snapshot, not a live dashboard: it does not
refresh, mutate the relay or task spine, dispatch a worker, or claim that
omitted sources are empty.

`examples/operator-board-export-paths.example.json` is a copyable record of
the three required path values. It is deliberately **not** a CLI input or a
configuration file: replace its nonexistent absolute placeholders manually,
then pass those three values as the explicit command flags above. Nothing reads
it automatically, and it cannot select a source or destination for you.

`prepare_operator_board_viewer()` is the separately bounded viewer-preparation
seam. It accepts one explicit completed export path, verifies its board and
receipt, freezes the exact verified board bytes, and returns the existing
capability-bound `OneShotLoopbackViewer` without calling `start()`. It does not
scan for exports, load the path template, write or replace files, refresh data,
open a relay, launch a browser/iTerm, bind a listener, issue a capability, or
grant authority. A later caller must explicitly own any viewer start and its
separate authority/operation gate.

`start-operator-board-viewer` is the interim manual-terminal activation
command. It requires one explicit completed export path, starts exactly the
prepared loopback viewer with its fixed defaults (IPv4 loopback, an ephemeral
high port, and a 30-second TTL), prints its one-time local URL, then waits for
the bearer-free terminal receipt. It does not open a browser or iTerm, accept a
source/template/default path, refresh or write an export, contact a worker or
provider, or grant any authority. Manual invocation is not proof of human or
hardware identity; the separate YubiKey-backed authority service remains a
future gate.

```bash
python3 -m house.relay.cli start-operator-board-viewer \
  --output /absolute/path/to/completed-operator-board.html
```

This is intentionally distinct from the upstream Codex network rendezvous
transport and the Dream House task-spine controller. A later, separately
qualified bridge may connect them; it must not weaken either contract.
