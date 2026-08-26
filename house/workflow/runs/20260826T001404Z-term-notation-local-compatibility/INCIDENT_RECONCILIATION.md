# Local-Metal incident reconciliation

Status: `RECONCILED / TERM OUTPUT COLLECTION PAUSED`

This append-only record supersedes only the causal wording in
`candidate-receipts/local-term-candidate-02-INTERRUPTED.md`. That earlier
record remains valid evidence that no TERM result was retained, but it must
not be read as proof that an operator `SIGTERM` reached the process.

## Observed timeline

- `local-term-candidate-01`, bound to the local 7B BF16 artifact, completed
  its 40 rendered cases at `2026-08-26T00:32:37Z`.
- `local-term-candidate-02`, bound to the local 24B 4-bit artifact, began at
  `2026-08-26T00:33:05.981Z`.
- The concurrent Training task began its local 8x7B Layer-8 probe at
  `2026-08-26T00:35:04.266Z`.
- Both later processes were absent after the user-reported unified-memory
  interruption. Neither emitted a completed result receipt.

The TERM candidate and Training probe therefore overlapped. Candidate 01 did
not overlap the Training probe.

## Capacity evidence

- Host physical memory: `34,359,738,368` bytes (32 GiB).
- Training artifact weight payload: `21,397,286,683` bytes; separately
  measured prior peak: approximately `21.48 GB`.
- TERM candidate-02 artifact weight payload: `15,102,831,624` bytes; the
  in-flight process was observed near 44% resident memory, an approximate
  `15.1 GB` only, not an instrumented MLX peak.
- Combined payload lower bound: `36,500,118,307` bytes, already above
  physical memory before model runtime allocations, the operating system,
  Codex, or interactive reserve.

## Disposition

No remaining TERM candidate may be loaded until the separately proposed
shared `local_metal` admission policy is reviewed and accepted. The policy is
not implemented by this record. Its required council gates are:

1. Admission uses the maximum of payload-byte lower bound and
   measured/predicted peak, plus declared system and interactive reserve.
2. Lease expiry never implies that memory is free: a host observer must first
   verify that the exact bound process identity is absent.
3. Priority and preemption rules must forbid a training workload from silently
   evicting interactive use or another admitted experiment.

The completed candidate-01 syntax result remains a narrow parser/field-format
observation only. Candidate 02 and the Training probe remain `INTERRUPTED /
NON_RESULT`.
