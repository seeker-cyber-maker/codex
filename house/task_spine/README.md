# Offline task spine v0

`house.task_spine` is the first headless Dream House authority-path fixture.
Its canonical record is an append-only SQLite journal; its task read model is
derived and disposable. A Task Packet stores the no-dispatch routing receipt
from `house.auto_switcher`.

Candidate admission requires all of the following: a sealed task-scoped worker
buffer, complete result envelope, import proposal, explicit lead authorization,
a fresh journal-head basis, and the `trusted_writer` actor. The derived WIP view
contains only the buffer hash, never the report body.

It is intentionally offline and local. It does not start a worker, read or
write native Codex state, contact a provider, or mutate the Archive.

```bash
PYTHONPATH=/absolute/path/to/codex-dream-house \
  python3 -m house.task_spine --db /tmp/task-spine.sqlite demo
PYTHONPATH=/absolute/path/to/codex-dream-house \
  python3 -m house.task_spine --db /tmp/task-spine.sqlite rebuild
```
