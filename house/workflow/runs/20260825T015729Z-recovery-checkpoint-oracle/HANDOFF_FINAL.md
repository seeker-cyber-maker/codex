# Final handoff: F1 synthetic checkpoint oracle accepted

Status: `ACCEPTED_F1_ONLY__STOP_BEFORE_S1`

## Accepted artifacts

- Fixture SHA-256:
  `0d52a694cf3e5c681c40faee2ff577fc8ac07c01222c59c6722c0a14ecedc25e`
- V3 independent verifier SHA-256:
  `4e8a433f7cc56f7ddd9e666e469636352d71814ad785ed8b78567f381cbe9580`
- Complete signed-envelope SHA-256:
  `94caf0b9b70ee5e3e1ec325b2a5c7400f211fc7b5ea345c6548b011d8684e97c`
- Expected receipt SHA-256:
  `7222f1e7ba1e1b314b8e2620e9405f4fa2df629e7d4389939db7749b918ccf9f`
- Final council packet SHA-256:
  `5f2cc0cd1be8bcec2fa7b9548657994af70270f6d82b9e9b959b323015a032e0`

Attempts A and B are byte-identical. Cryptography V1, schema/path V3, and
OpenSSL verification pass. All three final reviewers returned
`ACCEPT_F1_ONLY`.

## Claim ceiling

`FROZEN_PUBLIC_SYNTHETIC_CHECKPOINT_ORACLE_BYTES_INDEPENDENTLY_VERIFIED`

The disclosed scalar is public test evidence and makes the fixture deliberately
forgeable. It is suitable as a deterministic known answer, never as an anchor,
recovery key, or authority record.

## Still not established

- production checkpoint-verifier source;
- trusted anchor, latestness, protection, rollback detection, or persistence;
- real backup/recovery package or replacement-key ceremony;
- YubiKey loss revocation in the live system;
- runtime admission, authority, dispatch, or recovery readiness.

## Next gate

S1 is a separate source implementation run and requires a new user continuation
event. It may change only the two files accepted in PLAN_V2 and must test
against this frozen F1 oracle without importing its generator.

MODEL ADVISORY

Next implementation: Codex Terra / high. Reassess to Codex Sol / high before
the S1 promotion council.
