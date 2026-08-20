# Downstream patch ledger

| Patch | State | Upstream surface | Merge effect | Acceptance |
|---|---|---|---|---|
| `house/` control and evidence layer | active | none | additive downstream-only files | JSON validity, source seal, baseline fixture |
| Source-built CLI/app-server equivalence | planned | build outputs only | none | bounded offline comparison |
| Conserved event/session-tree thin slice | parked | app-server/state surfaces, exact seam TBD | unknown until source trace | focused protocol and replay tests |

Core modifications are not admitted without an entry naming the exact upstream
files, incompatibility, rollback, rebase risk, and independent acceptance test.
