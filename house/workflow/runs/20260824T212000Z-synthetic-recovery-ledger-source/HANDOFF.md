# Handoff: synthetic recovery-ledger source sealed

Status: `SOURCE_SEALED_AT_SYNTHETIC_CEILING`.

The accepted source plan is [`PLAN.md`](PLAN.md), SHA-256
`28459d9494ca6f6936aca5200845a0cf77a2d7116bb9b715abf574725b22702c`.
Its operation record canonical hash verifies. The blocking corrected council
packet SHA-256 is
`aceb72c67c7296c267fb07ff30cff9fe7573b0cf242706c8390c42934f35b74c`.

The implementation and dedicated tests are sealed at:

- `recovery_ledger.py`: `5f47b675d9cde29e4722e1ae4156e79af346a2069826f6019ac6eb74d85fcf6d`
- `test_recovery_ledger.py`: `7bd03abfabdd8faa7afe375addc6bc8718a72189a74e656003a0d74a5c8b87ca`
- amended legacy test: `aaf6ec39c22e0d54f23469914000a103f4ffce584c4706e81e3620acb39d0c15`

The final V2 council packet is `ae1b9c1762d28b536ebe833be23d0f4d4bfbabc72081043248c32611689fd966`;
all three read-only local same-provider roles accepted it. Twenty-five tests
passed, including coherent nested-receipt substitution rejection. Source plus
dedicated tests are 792 lines.

The maximum claim remains `SYNTHETIC_RECOVERY_LEDGER_LOCAL_TRANSACTION_ONLY`.
Do not infer real recovery, database authenticity, crash durability, OS
containment, checkpoint protection, keys, hardware, trusted time, authority,
dispatch, or runtime admission.

Any future change requires a new plan/hash/council cycle. Operational recovery
and sole-YubiKey loss procedures remain parked outside this source-only slice.
