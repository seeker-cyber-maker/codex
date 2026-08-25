# Final blocking F1 council packet V3

Decision question: does PLAN_DELTA_3 close the remaining fixed-value and exact
filesystem-entry-type gaps without changing the frozen oracle or widening any
authority, so F1 alone may be accepted?

## Frozen inputs

- prior handoff commit:
  `851e27235d139d45e7d0da716814f58466ca7254`
- parent round-two packet:
  `657107cd796e8e608e58ffca3092ac0b3f638d1141da6646d1cd5c2c045be9a6`
- `PLAN_DELTA_3.md`:
  `9695784d9283e5b6960f147996c3134449abe3f1bf8f022c3b71af0ebb0bb5f8`
- `SOURCE_FREEZE_V3.json`:
  `98d17c2ffa0c38fdc3f335424d922635fff007c12a87371eb307ee2d819450bd`
- `independent_verify.py` V3:
  `4e8a433f7cc56f7ddd9e666e469636352d71814ad785ed8b78567f381cbe9580`
- preserved V1:
  `3a96a44f5d7e61b19217ddf04655f6ed619bf826793ba0194f8d8b6a8ad7d75a`
- unchanged generator:
  `75e498b11e6846cd06d7a168af3f481a833fef2c36139d374de0ea83ab16eef1`
- unchanged A/B fixture:
  `0d52a694cf3e5c681c40faee2ff577fc8ac07c01222c59c6722c0a14ecedc25e`
- `INDEPENDENT_VERIFICATION_V3.json`:
  `36e22766969135a5f596e0e8fc034c9ca39d2b9a3b9437dde74c71c29a903839`
- `CLOSURE_PROBES_V3.json`:
  `3e212caf1ce915a04792d80fb15f0c9e2bcc89de649444459c19061f6f770b22`
- `EVALUATION_RESULT_V3.json`:
  `d9c8301717574a5dc52548d09df96191a83f3acd427aca697ae81125d96a2217`
- unchanged OpenSSL receipt:
  `352295194ff62fffb5078012867a4f4146d7a7ac6244b6d6a1dded6ac829e4c4`
- unchanged determinism receipt:
  `e0363e8803524a8e395f9c67f05bcf3ae90a5383dbd510e42307debf087bf143`

Reviewers must reproduce this packet and every cited hash.

## Delta observations

- V3 requires exact fixture/envelope/checkpoint/descriptor/summary/receipt/
  provenance/disclosure/manifest discriminator and security-literal values.
- Dynamic identity and digest fields remain validated by V1 whole-object and
  cryptographic checks after V3 closure.
- V3 first requires the fixture root to be a real directory and every exact
  immediate child to be a non-symlink regular file. It rejects unknown/missing
  names and every non-regular entry type.
- V3 passed attempts A and B; their fixture and generator bytes are unchanged.
- Isolated temporary probes changed the checkpoint context, added an extra
  directory, and replaced signature DER with a symlink. All were rejected for
  the intended V3 reason; temporary copies were not retained.
- No production file, real key, YubiKey, Keychain, certificate, database,
  network, runtime, provider, worker, or dispatch surface was accessed.

## Required attacks

1. Does V3 now enforce every fixed decision-bearing literal while leaving
   dynamic digest/identity relationships to the already preserved V1 checks?
2. Can any missing, unknown, duplicate, directory, symlink, socket, device, or
   other non-regular immediate entry evade the declared fixture boundary?
3. Does calling V1 only after V3 closure preserve canonical and cryptographic
   independence without using the public disclosed scalar for crypto?
4. Did the delta change any generator, fixture, expected receipt, OpenSSL, or
   authority semantics?
5. Is any remaining limitation decision-bearing for accepting F1 as a frozen
   positive oracle, rather than a future S1/operational concern?

## Restrictions and response

Read-only static review of the frozen packet and cited files. Do not edit,
execute, open a database/read a clock/access keys or hardware/sign/network/
launch/dispatch/runtime.

Return `ACCEPT_F1_ONLY`, `REVISE`, or `NEEDS_REVIEW`, plus direct observations,
inference/falsifier, unsupported claims, limitations, and smallest correction.
This is the final authorized council round. Acceptance may promote only F1; it
cannot authorize S1 or operational recovery.
