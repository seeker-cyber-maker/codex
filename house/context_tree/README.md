# Conserved context-tree thin slice

This standalone downstream module proves three Dream House invariants without
changing Codex core or opening native Codex databases:

1. app-server thread records can be projected into an exact fork/spawn tree;
2. canonical exported events can be mirrored into an append-only hash chain;
3. context blocks can be excluded, restored, pinned, or replaced without
   deleting the source event.

It uses only the Python standard library. Run the focused suite from the
repository root:

```sh
python3 -m unittest discover -s house/context_tree/tests -v
```

The CLI accepts exported or fixture data:

```sh
python3 -m house.context_tree.codex_house_context project-tree threads.json tree.json --require-fork-points
python3 -m house.context_tree.codex_house_context verify-journal events.jsonl
python3 -m house.context_tree.codex_house_context create-view events.jsonl view-spec.json view.json
python3 -m house.context_tree.codex_house_context apply-view events.jsonl view.json operation.json next-view.json receipt.json
```

`forkPointTurnId` is house intake metadata captured from the corresponding
`thread/fork` request. Current app-server `Thread` responses expose the source
thread as `forkedFromId`, but do not expose the historical boundary used for the
fork. The projector therefore fails closed when `--require-fork-points` is used
and that receipt is absent.

The journal is downstream evidence, not a replacement for the upstream rollout
or thread store. It stores references and hashes, not private transcript bodies.
