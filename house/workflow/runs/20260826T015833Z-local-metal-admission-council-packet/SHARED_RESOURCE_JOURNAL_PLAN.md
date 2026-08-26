# Shared resource-envelope journal: source-only integration plan

Status: `PLANNED / NO IMPLEMENTATION / NO MIGRATION / NO RUNTIME`

## Objective

Promote the accepted pure `local_metal` planner only into an additive,
append-only resource-envelope journal. The journal is the future authoritative
record of reservations and their lifecycle; the planner remains a deterministic
proposal generator, and the host observer/launcher remain separate future
components.

## Boundary decision

- Reuse Dream House's hash-chained append-only event and deterministic replay
  discipline.
- Do **not** reuse Task Spine's proposal/event-count lease as a memory lease;
  its semantics are task admission, not physical resource occupancy.
- Do **not** convert or rewrite the ZeroGPU roster. A read-only adapter must
  project legacy ZeroGPU records as immutable compatibility fixtures.
- `local_metal` has short just-in-time runtime leases. ZeroGPU retains its own
  quota-seconds and planning-horizon semantics.

## Phase 2 source-only records

All events carry a pool ID, reservation ID, immutable request digest, fencing
epoch, authoritative event sequence, previous event hash, and actor/assertion
provenance. `local_metal` adds the accepted capacity-profile and measurement
facts; it never receives a quota or credit field by default.

```text
resource.requested
resource.admission_proposed
resource.admitted | resource.denied
resource.process_bound
resource.heartbeat_observed
resource.calibration_recorded
resource.resize_requested
resource.superseded | resource.interrupted | resource.completed | resource.released
resource.expired
resource.reclaim_confirmed | resource.reclaim_denied
resource.override_recorded
```

An expiry event changes the lease's review state but never removes its capacity
envelope. Only a later `resource.reclaim_confirmed` with matching reservation,
fence, PID, start identity, and observer proof can do that.

## Deterministic replay tests

The disposable implementation must prove all of the following without reading
the host or launching a model:

1. incident replay serializes the second workload;
2. baseline/reserve/variance are counted exactly once;
3. missing, stale, duplicate, or contradictory request/observer facts deny;
4. a calibration receipt upgrades only its exact capacity profile;
5. an uncalibrated rack cannot co-reside; 64-to-128 creates a new request and
   preserves the 64-member record until an explicit supersession;
6. expiry, denied, interrupted, released, reclaimed, and override transitions
   are append-only and replay deterministically;
7. a stale observer cannot reclaim or enable a new lease;
8. legacy ZeroGPU roster fixtures project read-only and do not acquire,
   release, or reinterpret quota seconds as local memory.

## Deferred authority boundaries

No Phase 2 source slice may start a process, inspect live memory, touch a
model, modify the ZeroGPU roster, install a service, or bind LiteLLM/oMLX.
The later observer/launcher review owns trusted host identity, baseline
measurement, actual process liveness, service-account feasibility, and direct
backend bypass containment. Compatibility classification must be bound to a
validated workload/rack profile, never caller-supplied as a privilege label.

## Acceptance gate

Only after the source-only replay suite and legacy-adapter fixtures pass may a
separate review consider a passive observer. Runtime lease writing, automatic
reclamation, and any model launch remain distinct later gates.
