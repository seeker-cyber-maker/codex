# Downstream patch ledger

| Patch | State | Upstream surface | Merge effect | Acceptance |
|---|---|---|---|---|
| `house/` control and evidence layer | active | none | additive downstream-only files | JSON validity, source seal, baseline fixture |
| Source-built CLI/app-server equivalence | planned | build outputs only | none | bounded offline comparison |
| Conserved event/session-tree thin slice | accepted | none; additive `house/context_tree` and schemas | no upstream merge conflict | 8 offline tests, Ruff, JSON, privacy, scope, diff, and remote identity checks |
| Live app-server ancestry adapter | parked | app-server notifications and fork-request receipts | exact seam follows fixture acceptance | restart, pagination, and historical-fork fixture |
| ChatGPT-family auto switcher v0.1 | accepted offline policy | additive `house/auto_switcher` only | no upstream merge conflict | 12 deterministic no-dispatch tests, CLI smoke, compilation, diff check, and live OMP configuration cross-check; role selection remains separate from native auto thinking |
| Offline task-spine v0 core | accepted partial authority path | additive `house/task_spine` only | no upstream merge conflict | 7 isolated task-spine tests plus auto-switcher regression; happy path, routing receipt, metadata-only WIP, authorization/buffer/basis/actor failure, and deterministic rebuild pass; leases, amendments, and interrupted-rebuild fixtures remain later work |

Core modifications are not admitted without an entry naming the exact upstream
files, incompatibility, rollback, rebase risk, and independent acceptance test.
