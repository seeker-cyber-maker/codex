# Plan delta 1 — integration documentation

## Reason

Integration review found that `house/README.md` and `house/PATCH_LEDGER.md` are
the established discovery and downstream-patch records for every accepted
`house/worker_exec` slice. Omitting them would leave the new public interface
undiscoverable and the upstream-merge boundary incomplete.

## Added write scope

- `house/README.md`
- `house/PATCH_LEDGER.md`

This is documentation-only. It does not change the verifier contract,
authority, runtime behavior, or acceptance gates.
