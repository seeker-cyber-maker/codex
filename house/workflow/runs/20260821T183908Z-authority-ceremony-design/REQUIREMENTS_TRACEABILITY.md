# Council-requirements traceability

| Council requirement | Normative design location | Frozen falsification tests | Status |
|---|---|---|---|
| Complete key lifecycle, bootstrap, rotation, loss/compromise recovery, and last-key behavior | `AUTHORITY_LIFECYCLE.md`, `CEREMONY_SPEC.md`, `RECOVERY_MATRIX.md` | `BS-01`, `LK-01`, `KY-01`, `KY-02`, `GF-01` | Mapped |
| Durable authority/inbox causality and crash reconciliation | `SAGA_AND_ANCHORING.md` | `SG-01`, `SG-02`, `SG-03`, `ST-01` | Mapped |
| Protected journal anchoring or permanently narrowed consistency claim | `THREAT_MODEL.md`, `SAGA_AND_ANCHORING.md` | `JR-01`, `JR-02`, `JR-03`, `BK-01` | Mapped |
| Independent fixed P-256 canonicalization/interoperability vectors | `SIGNING_VECTOR_SPEC.md` | `FV-01`, `FV-02`, `FV-03` | Mapped |
| Multi-process, crash, disk, replay, and concurrency testing | `FAILURE_TEST_PLAN.md`, `RECOVERY_MATRIX.md` | `BS-01`, `RP-01`, `RV-01`, `SG-01`, `CK-01`, `ST-01` | Mapped |
| Rejection rate, quota, retention, monitoring, and exhaustion behavior | `MONITORING_AND_QUOTAS.md` | `TM-01`, `ST-01` | Mapped |
| Sole-writer/hostile-process boundary | `THREAT_MODEL.md`, `SAGA_AND_ANCHORING.md` | `OS-01`, `OS-02` | Mapped |
| Two possible YubiKeys without simultaneous polling | `AUTHORITY_LIFECYCLE.md`, `CEREMONY_SPEC.md` | `DV-01`, `KY-01` | Mapped |
| Replacement models cannot expand or redelegate authority | `THREAT_MODEL.md` | `DG-01` | Mapped |
| Every failed safety layer is surfaced as a near miss | `MONITORING_AND_QUOTAS.md` | `TM-01` plus layer-specific event assertions in every test | Mapped |

## Cross-document invariants

- `LOCKDOWN` always blocks mutation and cannot be cleared by a model, restart,
  timeout, dashboard, or configuration edit.
- Owner-primary and owner-recovery keys are alternatives. No rule requires both
  to be simultaneously inserted or polled.
- Private owner keys never enter model context, database content, receipts,
  logs, backups, vectors, or source control.
- Revocation never rewrites delivered history; pending work is quarantined or
  explicitly reauthorized.
- The service records durable intent causality but does not claim exactly-once
  distributed execution.
- Internal hash chains are described as consistency checks until protected
  checkpoint and sole-writer tests pass.
- Both-owner-key loss creates a new registry generation and an explicit
  continuity break.
- All implementation, hardware, service, provider, and production work remains
  separately authority-gated.
