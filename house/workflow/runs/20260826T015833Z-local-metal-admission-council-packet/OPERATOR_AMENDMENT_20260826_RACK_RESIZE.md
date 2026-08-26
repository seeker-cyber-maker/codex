# Operator amendment: rack resize requires re-admission

Status: `OPERATOR REQUIREMENT / SOURCE-ONLY / NO IMPLEMENTATION`

A `local_metal` rack lease binds the declared rack topology, member set,
aggregate envelope, and internal concurrency. It does not reserve future
expansion capacity.

Consequently, a lease admitted for a 64-member rack does **not** authorize a
128-member rack. Before adding members or otherwise increasing the live rack
envelope, the controller must submit a resize request containing the new
topology and complete aggregate evidence. The deterministic gate then either:

- grants a new fenced lease and records the preceding 64-member lease as
  superseded at a verified handoff point; or
- denies/defer the expansion while the existing 64-member rack remains bounded
  by its original lease.

The controller may not start additional members during a pending resize, reuse
the original fence for the expanded topology, or treat spare historical memory
as an implied reservation. Shrinking records a new lower envelope or releases
the lease; it does not erase the original observed envelope or disposition.

This requirement is compatible with ordinary independent workloads: each new
concurrent workload is itself a separate admission request. It does not
authorize runtime resize handling, model execution, or automatic preemption.
