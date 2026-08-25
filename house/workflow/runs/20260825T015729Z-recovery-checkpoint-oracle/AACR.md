# After-action review: F1 candidate oracle

## What worked

- The accepted plan prevented real-key or hardware scope drift.
- Two deterministic generations and two public verification paths produced
  strong cryptographic evidence.
- Retaining the import-path failure made the execution history honest.
- The adversarial first-round finding produced a concrete unknown-field probe.

## What failed

The V2 remediation treated schema closure mainly as exact field names. It did
not enumerate every fixed discriminator/security literal or all filesystem
entry types. That gap appeared only at the final allowed council round.

## Process lesson

For closed object contracts, plan review should require a matrix with three
separate columns: exact fields, exact fixed values, and exact container entry
types. “Closed schema” must not be used as shorthand for only the first column.

## Disposition

Close this operation as `NEEDS_REVIEW`, preserve all candidate and negative
evidence, and require a separately authorized bounded delta. Do not promote F1
or begin S1.
