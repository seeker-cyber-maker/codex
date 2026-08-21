# Downstream patch ledger

| Patch | State | Upstream surface | Merge effect | Acceptance |
|---|---|---|---|---|
| `house/` control and evidence layer | active | none | additive downstream-only files | JSON validity, source seal, baseline fixture |
| Source-built CLI/app-server equivalence | planned | build outputs only | none | bounded offline comparison |
| Conserved event/session-tree thin slice | accepted | none; additive `house/context_tree` and schemas | no upstream merge conflict | 8 offline tests, Ruff, JSON, privacy, scope, diff, and remote identity checks |
| Live app-server ancestry adapter | parked | app-server notifications and fork-request receipts | exact seam follows fixture acceptance | restart, pagination, and historical-fork fixture |
| ChatGPT-family auto switcher v0.1 | accepted offline policy | additive `house/auto_switcher` only | no upstream merge conflict | 12 deterministic no-dispatch tests, CLI smoke, compilation, diff check, and live OMP configuration cross-check; role selection remains separate from native auto thinking |
| Offline task-spine v0 core | accepted offline authority path | additive `house/task_spine` only | no upstream merge conflict | 12 isolated task-spine tests plus 12 auto-switcher regressions; happy path, routing receipt, metadata-only WIP, authorization/buffer/basis/actor failures, late results, envelope dispositions/amendments, revoked/expired leases, journal verification, and transactional interrupted rebuild pass |
| Typed task-submission adapter v0 | accepted offline intake path | additive `house/task_spine/submission.py` and CLI surface | no upstream merge conflict | 6 adapter tests plus 24 spine/router regressions; exact retry, conflicting-key rejection, partial resume, compound continuation, strict fields, and CLI/API parity pass; requester identity remains asserted/unverified |

Core modifications are not admitted without an entry naming the exact upstream
files, incompatibility, rollback, rebase risk, and independent acceptance test.
