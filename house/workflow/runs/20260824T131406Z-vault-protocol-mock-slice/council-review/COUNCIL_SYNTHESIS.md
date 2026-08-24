# Council synthesis - original candidate

## Outcome

`REVISE_BEFORE_ACCEPTANCE`

The two contract-complete round-one reviewers returned
`ACCEPT_NON_RUNTIME_REFERENCE`, but both selected DeepSeek V4 Flash after their
requested primary models failed. Their agreement is correlated. The retried
Nemotron evidence auditor returned `REVISE_BEFORE_ACCEPTANCE`, but its only
alleged defect was a hallucinated set of `[ADDRESS]` placeholders absent from
both the sealed source and the hash-identical transport packet. That allegation
is contradicted and receives no decision weight.

Chair reconciliation nevertheless found a different, directly reproducible
rotation defect inside the claimed mock-storage boundary. The original method
trusted caller-supplied old revision metadata, did not authenticate the old
ciphertext before superseding it, and could strand a new key/file when
tombstone creation failed.

## Proven reproductions

- Actual stored revision `1` was accepted and tombstoned as caller revision
  `99`.
- Corrupt old ciphertext was accepted as a rotation source and its old key was
  destroyed.
- A tombstone-path collision raised after leaving the epoch-2 key and
  ciphertext present.

## Disputed and rejected claims

- Rejected: literal `[ADDRESS]` placeholders occur in source. Exact grep over
  source and both materialized transport packets returned no matches;
  `py_compile` passed; hashes matched.
- Preserved limitation: cloud reviewers did not execute the test suite or
  independently establish the Git commit/source seal.
- Deferred: production atomicity, crash recovery, and filesystem adversary
  behavior remain outside this non-runtime fixture.

## Smallest decisive action

Authenticate and validate the old record before mutation, require its stored
revision to equal the caller's old revision, preflight deterministic path
collisions, roll back new generated state after failure, and submit only that
delta for independent review.
