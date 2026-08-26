# Revised Phase 1 planner reconciliation

Status: `CANDIDATE REFERENCE ACCEPTED / UNMERGED / NO RUNTIME AUTHORITY`

Candidate accepted as the source-only reference:

- branch: `codex/local-metal-phase1`
- commit: `c0474a4cd819cc60acf0cea22ac3a2fa2f485c68`
- worktree: `/Users/tiga/Documents/Codex_Projects/.worktrees/dream-house-local-metal-phase1`

Independent verification completed successfully:

- 19 focused unit tests passed;
- `ruff check house/local_metal_admission` passed;
- candidate commit diff whitespace check passed.

## Reconciled requirements

The revision implements the five source-only revisions recorded in
`PHASE1_CANDIDATE_RECONCILIATION.md`:

1. explicit exact/precedent/documented/conservative footprint states;
2. exact capacity-profile matching for compatible admission;
3. high-water versus settled-low variance plus fixed-floor safety margin;
4. exclusive calibration for provisional/new racks and fresh exclusive
   re-admission for a resize; and
5. fail-closed contradictory launcher identity and observed-swap checks.

It also preserves the earlier safety properties: separate `local_metal` pool,
once-counted baseline/reserve, no priority preemption, expiry not treated as
reclamation, deterministic replay, and no runtime/host side effects.

## Remaining non-promotions

This acceptance does not merge the candidate into the dirty checkout or grant
it runtime authority. The next shared-journal review still needs append-only
lifecycle and rack-supersession replay, real legacy ZeroGPU compatibility,
trusted observer/baseline provenance, authoritative lease writing/reclamation,
and enforcement/bypass containment.

`compatibility_mode` is presently a typed planner input, not a trusted workload
classification. The future authoritative journal must bind that choice to a
validated workload/rack profile; a caller must not gain co-residency merely by
labelling itself `compatible`.
