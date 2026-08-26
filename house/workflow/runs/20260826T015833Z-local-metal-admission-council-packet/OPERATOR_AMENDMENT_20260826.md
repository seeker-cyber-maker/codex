# Operator amendment: short-lived local-Metal leases

Status: `OPERATOR REQUIREMENT / SOURCE-ONLY / NO IMPLEMENTATION`

This append-only amendment records the operator's decision after the packet's
creation and the subsequent `REVISE_AND_TEST` council synthesis. It does not
alter the immutable packet, authorize an implementation, dispatch a worker, or
permit a local model load.

## Lease horizon

`local_metal` reuses the accountability questions of the ZeroGPU reservation
ledger, but it is a just-in-time runtime lease rather than a capacity plan.
The ZeroGPU 36--48 hour planning horizon does **not** apply.

- A request may be made whenever a managed workload is ready to start.
- The deterministic gate grants it only when the current host evidence and
  active compatible leases admit it; otherwise it returns a bounded denial or
  block reason.
- The lease covers only the bounded launch and active runtime window, with a
  short heartbeat/TTL and immediate release after verified completion, abort,
  or reaping.
- Expiry is never evidence that memory is free: reclamation still requires a
  fresh observer confirmation of the exact fenced process identity's absence.

## Required ledger facts

Each request and final receipt retains the equivalent accountability facts:
owner and task/project identity; purpose and job/batch ID; resource pool and
mode; requested/observed timing; workload fingerprint; payload lower bound;
predicted, measured, and actual peak; baseline freshness; system and
interactive reserve; allowed swap delta; priority; compatibility; interruption
cost; checkpoint/recovery state; disposition; and release or denial reason.
`local_metal` records capacity and memory observations rather than quota
seconds, credits, reset dates, or a future scheduling horizon.

## Admission and reservation-before-start rule

For a future source-only planner, calculate a separate envelope for each
active compatible workload and the incoming request:

```text
workload_envelope(i) = max(payload_lower_bound(i), predicted_peak(i), applicable_measured_peak(i))

admit only if:
  sum(workload_envelope(active compatible leases))
  + workload_envelope(request)
  + observed baseline excluding admitted workloads
  + system/interactive reserve
  <= physical memory
```

Baseline and reserve are counted exactly once. Missing, stale, or contradictory
required evidence fails closed.

Every workload launched through the future Dream House managed path --
including a Codex-originated local model task -- must obtain a `GRANTED`
reservation before model initialization. The future enforcement-boundary review
must state separately what it can prove about direct/manual oMLX, web UI, or
MLX launches outside that managed path; this amendment does not claim those
bypasses are already prevented.

## Boundaries retained

The council's required PID-plus-start-identity-plus-fence binding and
stale-observer fail-closed rule remain mandatory. Phase 1 remains limited to a
disposable source/schema/planner and deterministic tests; it does not include
launch enforcement, service identities, daemon installation, model execution,
or automatic preemption.
