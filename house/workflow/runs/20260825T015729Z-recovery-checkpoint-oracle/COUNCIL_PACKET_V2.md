# Blocking F1 council packet V2: schema-closed public oracle

Decision question: does the bounded V2 independent-verifier closure resolve the
round-one unknown-field acceptance path without changing fixture bytes or
widening authority?

## Frozen delta inputs

- parent F1 packet:
  `86680f088b8f25a822ff6af800512468a309d2c8af3ecad21fba0754f87d3ccf`
- `PLAN_DELTA_2.md`:
  `e21cd55d0aaeaa0677715bd175a7625c8357314ef95c89987a5c037efb008f81`
- `SOURCE_FREEZE_V2.json`:
  `22589dd6a3105e9c1e1168645fd79b76e0cdbf01cb1a5bb5e4e5611a931935d8`
- preserved `independent_verify_v1.py`:
  `3a96a44f5d7e61b19217ddf04655f6ed619bf826793ba0194f8d8b6a8ad7d75a`
- schema-closing `independent_verify.py` V2:
  `45f5bdd09c782141dbb8cc4c338dba70cc7ee0dbff96ca6bd4e30ead98da3add`
- `INDEPENDENT_VERIFICATION_V2.json`:
  `c2f88b5de111d9f280eb6d21f768877e963ff9b493307950d45c9c890c376a3f`
- `SCHEMA_CLOSURE_PROBE.json`:
  `f74cbd3d4bd32cbd2169d4a19c2d290c19057e42bc19fb612f183db3733dc714`
- `EVALUATION_RESULT_V2.json`:
  `7b548b53da46fe470458afdedbca8399e8359a60040be9d15083dd691f577366`
- unchanged A/B `fixture.json`:
  `0d52a694cf3e5c681c40faee2ff577fc8ac07c01222c59c6722c0a14ecedc25e`
- unchanged generator:
  `75e498b11e6846cd06d7a168af3f481a833fef2c36139d374de0ea83ab16eef1`

Reviewers must reproduce packet and cited hashes.

## Delta observations

- V1 remains byte-identical and is imported only after V2 schema closure.
- V2 rejects duplicate JSON keys and enforces exact field sets for the fixture,
  envelope, unsigned checkpoint, descriptor, ledger summary, receipt,
  intermediates, provenance, disclosure, artifact manifest, and artifact
  entries.
- V2 verifies the exact fixture-directory file set and every manifest hash and
  byte length before invoking V1 cryptographic checks.
- The disclosed scalar is parsed/hashed only as public schema evidence; V2 does
  not derive a key, sign, or cryptographically verify with it.
- An isolated temporary mutation added one unknown top-level fixture field:
  V1 returned PASS and V2 rejected the exact unknown field. The temporary copy
  was removed; frozen A/B outputs were not regenerated or modified.
- V2 passed both unchanged A/B fixtures. OpenSSL evidence is unchanged.

## Required checks

1. Are all decision-bearing schemas now mechanically closed, including nested
   evidence records and directory membership?
2. Does importing V1 only after V2 closure prevent the round-one falsifier?
3. Does parsing/hash-checking the explicitly public scalar disclosure preserve
   cryptographic independence and the never-authority boundary?
4. Did the delta leave generator/fixture/receipt bytes and all operational
   prohibitions unchanged?

Read-only static review only. Do not edit, execute, open DB/read clock/access
keys/hardware/sign/network/launch/dispatch/runtime. Return `ACCEPT_F1_ONLY`,
`REVISE`, or `NEEDS_REVIEW`, with direct observations, inference/falsifier,
unsupported claims, limitations, and smallest correction. No result authorizes
S1 or operational recovery.
