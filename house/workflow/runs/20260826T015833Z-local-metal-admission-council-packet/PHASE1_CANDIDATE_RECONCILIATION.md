# Phase 1 planner candidate reconciliation

Status: `REVISE_AND_TEST / NO MERGE / SOURCE-ONLY PLAN DELTA`

Candidate inspected:

- branch: `codex/local-metal-phase1`
- commit: `ceef0b36da0fd960a63f3a954bd50fce4edbc2aa`
- worktree: `/Users/tiga/Documents/Codex_Projects/.worktrees/dream-house-local-metal-phase1`

The candidate is a useful pure-planner base. It has no host, process, model,
network, lease-writer, or scheduler side effects. Independent revalidation ran
its 13 focused tests, `ruff check house/local_metal_admission`, and commit diff
whitespace validation successfully.

## Accepted base behavior

- `local_metal` is separate from ZeroGPU and rejects the wrong pool.
- The historical overlap is denied.
- Active/request envelopes and the once-counted baseline/reserve are added
  correctly for its existing fixture.
- stale host/process observations, duplicate exact active identities, and
  incompatible exclusive requests fail closed.
- expiry alone does not remove a supplied active process; priority does not
  authorize preemption.

## Required source-only revision before adoption

1. **Measured versus provisional state.** An ordinary concurrent/rack request
   must identify whether its footprint is `observed_exact`,
   `observed_compatible_precedent`, `declared_documentation`, or a
   `conservative_estimate`. The current artifact/runtime-only check is not
   enough to distinguish a first calibration from ordinary admission.
2. **Capacity-profile matching.** A reusable measurement must bind an exact
   capacity-profile fingerprint: assets and runtime, host class, launch
   parameters, context/batch/data-shape bounds, training/optimizer and adapter
   layout, rack topology/shared-base arrangement, and internal concurrency. A
   same-model but different experiment may use a prior value only as a
   conservative precedent unless this fingerprint matches.
3. **Observed variance margin.** Measured profiles need a settled post-warm-up
   low-water mark and a high-water mark. Co-residency must add
   `max(fixed_minimum_reserve, 2 * sum(high_water - stable_low))` in addition
   to workload high-water envelopes, baseline, and system/interactive reserve.
   Missing or poorly sampled variance evidence prevents co-residency.
4. **Rack calibration and resize.** A new rack resource profile calibrates as
   the only local-Metal rack. A 64-member lease cannot become a 128-member rack
   without a new topology/envelope, fresh fenced admission, and append-only
   supersession or denial. A rack is either one measured aggregate lease or all
   members are separately accounted for.
5. **Identity-consistency and swap tests.** Two supplied active records that
   agree on PID, start identity, and fence but disagree on launcher observation
   are contradictory and must deny rather than be treated as separate. The
   pure input contract also needs an observed swap-delta field and a
   deterministic stop/deny test against the declared maximum; merely parsing
   the maximum is not a safety decision.

## Retained promotion blockers

The candidate correctly leaves append-only lifecycle replay, real legacy
ZeroGPU compatibility, host observation, authoritative lease writing,
reclamation, runtime enforcement, and bypass resistance outside its scope.
Those remain blockers to promotion, not reasons to widen this revision.

## Disposition

Do not merge `ceef0b36` into the dirty main checkout as-is. Use it as the
source-only base for a revised disposable candidate implementing the five
requirements above, then rerun the council's deterministic replay gates.
