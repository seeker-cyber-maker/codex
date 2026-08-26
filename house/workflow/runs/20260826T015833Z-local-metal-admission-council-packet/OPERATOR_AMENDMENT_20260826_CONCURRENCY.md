# Operator amendment: safe co-residency and racks

Status: `OPERATOR REQUIREMENT / SOURCE-ONLY / NO IMPLEMENTATION`

This append-only amendment refines the short-lived lease requirement. It does
not authorize a model load, a runtime gate, or an enforcement change.

## Ordinary small workloads

Independent small training or evaluation workloads are allowed to run
concurrently. They must each request a short-lived `local_metal` lease, and
they may be admitted together only when the planner's separate-envelope sum,
observed baseline, and single system/interactive reserve fit the declared
safety margin.

The initial "exclusive heavyweight" fallback applies when compatibility or
envelope evidence is absent, stale, contradictory, or insufficient. It is not
a blanket one-workload rule and must not serialize two bounded workloads that
the deterministic safety calculation can admit.

## Rack workloads

A rack is not silently treated as many unaccounted small jobs. It must use one
of two explicit shapes:

1. **Aggregate rack lease:** a validated rack controller declares the complete
   member set, combined envelope, shared-base assumptions, internal
   concurrency, and stop/recovery behavior. The planner admits the rack as one
   workload envelope and keeps its internal membership receipted.
2. **Independent member leases:** absent that validated aggregate evidence,
   every concurrently running member has its own lease and contributes its own
   envelope to the admission sum.

No shared-base, weight-sharing, or rack label reduces the reservation by
assumption. Any claimed sharing benefit requires measured or otherwise accepted
evidence in the future planner contract.

## Retained safety conditions

All concurrent leases retain PID-plus-start-identity-plus-fence binding,
fresh-observer requirements, append-only disposition receipts, and immediate
verified release. A blocked request remains a normal short-term denial, not a
multi-day reservation or a reason to evict an already admitted workload.
