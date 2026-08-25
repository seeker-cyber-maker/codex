# Blocking F1 council packet: public synthetic checkpoint oracle

Decision question: is this F1 oracle deterministic, mechanically complete,
independently verifiable, and honestly non-authoritative enough to become the
frozen known-answer input for a future separately authorized source slice?

## Frozen evidence

- accepted parent plan SHA-256:
  `9134e25a84158751ce2d3e4f57d66538fa72b833bd2599a3f2a0cf88f60d41b0`
- F1 `PLAN.md`: `0254b9f625a3e96c9ba147c89d2eaba9eccbb1c18f71f0f0b0d8ea67f51b5a0d`
- bounded `PLAN_DELTA_1.md`:
  `82b1c8bb8e5ec4dfb8cec33bde2314635077e5b0c8af52c94dbe48655b5a7bd0`
- `SOURCE_FREEZE.json`:
  `2646f212292de5a58f9600268c1abedbba89a5654d960cb7934f7e4fed0af0d4`
- `fixture_generator.py`:
  `75e498b11e6846cd06d7a168af3f481a833fef2c36139d374de0ea83ab16eef1`
- `independent_verify.py`:
  `3a96a44f5d7e61b19217ddf04655f6ed619bf826793ba0194f8d8b6a8ad7d75a`
- attempt A and B `fixture.json`:
  `0d52a694cf3e5c681c40faee2ff577fc8ac07c01222c59c6722c0a14ecedc25e`
- `ARTIFACT_HASHES.json`:
  `f08aea0fafd8cde6a6bfa62c48042df1c3a359f18b2375408e57661b72bd8f5c`
- `INDEPENDENT_VERIFICATION.json`:
  `4a8de0cd7b07191192efc6bb36901ba5d635079f256cfa0a3783b7bdbfe0c34f`
- `DETERMINISM_RECEIPT.json`:
  `e0363e8803524a8e395f9c67f05bcf3ae90a5383dbd510e42307debf087bf143`
- `OPENSSL_VERIFICATION.json`:
  `352295194ff62fffb5078012867a4f4146d7a7ac6244b6d6a1dded6ac829e4c4`
- `EVALUATION_RESULT.json`:
  `59c8f5012c954a85dfb2ecc49886458e4b4eee37249cf183eae8fad55fd69f2d`
- retained `EXECUTION_FAILURE_1.json`:
  `f8989fab7e1c572adfbf4f24f1d6d8514e84d6e4039ccaec98d6fa9eea9f976a`

Reviewers must reproduce the packet and all cited hashes.

## Direct execution observations

- The initial command wave failed at import before output creation; it is
  retained rather than erased.
- A bounded invocation delta added the repository root to `PYTHONPATH` without
  changing generator or verifier source.
- Attempts A and B contain the same ten filenames and are byte-identical.
- The independent verifier passed both attempts and imports no `house` module.
- OpenSSL 3.5.6 returned `Verified OK` over the exact frozen unsigned-checkpoint
  bytes, signature DER, and public SPKI.
- The public test-key scalar is disclosed and labeled never-authority. Only the
  generator reads/derives it; the independent verifier does not open that file.
- No production file, database, real key, YubiKey, Keychain, certificate,
  network, runtime, controller, worker, provider, or dispatch path was used.

## Required attacks

1. Does the fixture bind every field in accepted PLAN_V2, including complete
   envelope digest, descriptor, summary, key identity, and whole receipt?
2. Can the generator's use of the sealed Stage-0 signing donor make the oracle
   vacuous, given that the verifier imports no Dream House code and OpenSSL also
   verifies the frozen bytes?
3. Is the public test-key disclosure and warning strong enough to prevent the
   fixture key from being mistaken for authority or recovery material?
4. Does the exact expected receipt preserve every non-authority literal and
   avoid trust/latest/protection/readiness claims?
5. Is determinism actually established across all claimed files, and is the
   pre-generation failure/delta honestly bounded?
6. Are there unverified, circular, omitted, or ambiguously canonical bytes that
   would let a future candidate pass against a self-made oracle?

## Restrictions and response

Read-only static review of the frozen packet and cited local files. Do not edit,
run generator/tests, open databases, read clocks, access keys/YubiKeys/Keychain/
certificates, sign, launch, network, dispatch, or access runtime state.

Return `ACCEPT_F1_ONLY`, `REVISE`, or `NEEDS_REVIEW`, with direct observations,
inference/falsifier, unsupported claims, limitations, and smallest correction.
Council acceptance cannot authorize S1 or any operational recovery action.
