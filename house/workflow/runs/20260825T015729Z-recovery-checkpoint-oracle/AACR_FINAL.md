# Final after-action review: accepted F1 oracle

## Outcome

F1 closed as `ACCEPTED_F1_ONLY`. The original deterministic cryptographic
fixture did not change across three verifier revisions.

## Improvements produced by review

- V1: canonical, digest, cross-object, receipt, and public cryptographic checks.
- V2: duplicate-key and exact-field-set closure.
- V3: exact fixed-value and filesystem entry name/type closure.

The negative probes demonstrate why all three layers matter. Future closed
contracts should declare fields, fixed values, and container entry types as
separate plan matrices before the first implementation.

## Limitations

The oracle is public and synthetic. It cannot authenticate a real signer or
prove a checkpoint is current, protected, persistent, or safe to restore.

## Adoption gate

Use this oracle only after S1 receives separate authority. Do not import the
generator, disclosed scalar, or workflow-run package into production source.
