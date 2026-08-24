# Spawn-disabled native canary-helper sources

This directory implements only the accepted design's first source/build rung.

- `protocol.[ch]` fixes the v1 80-byte big-endian header and strict message
  order.
- `parent_contract.c` and `helper_contract.c` expose constants and pure state
  checks only. They contain no `main`, process launch, network, arbitrary-file,
  environment, logging, or secret-storage API.
- `parent_main.c` and `helper_main.c` are fixed-argument admission entrypoints.
  They perform only pure role/transition/codec checks and return a closed result
  code; they do not spawn, open, connect, read the environment, or handle a
  canary. The unit-test macro can omit only their production `main` definitions.
- `build_objects.py` compiles relocatable `.o` files with `clang -c`, checks
  undefined symbols with `nm`, and never links or executes a candidate.
- `artifact_inspection.py` verifies a future sealed candidate using the absolute
  Apple `codesign` inspector against a private byte-for-byte snapshot copied
  from a pinned no-follow descriptor. Each host inspection has a fixed timeout;
  timeout returns a fail-closed refusal. It never runs or loads the artifact.
- `run_codec_tests.py` requires an existing non-symlink output parent, reserves
  a randomized mode-`0700` child itself, bounds compile/inspection/execution,
  and descriptor-cleans only its exact disposable test executable before
  returning a receipt. It links and runs only disposable pure codec and
  entrypoint-contract test programs, never either candidate executable.
- `signing_policy.json` is deliberately `NOT_CONFIGURED_NO_LAUNCH`; null Team
  ID, sizes, hashes, CDHashes, and designated requirements make it ineligible.
- `candidate_contract.json` is a closed declarative description of the future
  bundle subject. Its source inputs, including the entrypoints, are hash-bound;
  platform and identity fields remain explicitly `UNRESOLVED`, so it cannot
  produce plan operations.
- `candidate_plan.py` validates source and entitlement bindings and can emit a
  bounded JSON compile/link/assembly/signing order only for a fully resolved
  test fixture. It imports no process runner, exposes no executor, and never
  creates a bundle or invokes a described command.

The entitlement plists are exact expected sets, not runtime proof. The parent
requests only App Sandbox. The helper requests exactly App Sandbox plus
inheritance. A later sealed policy must bind actual content sizes, hashes,
CDHashes, Team ID, designated requirements, and platform build before static
inspection can return `QUALIFIED_STATIC_ARTIFACTS_NO_LAUNCH`.

No source in this slice starts or launches another process. Tool processes used
during validation are limited to the compiler, symbol inspector, static
code-signature inspector, and disposable pure contract-test executables;
candidate launch, candidate linking, App Sandbox claims, generated-canary
delivery, network probes, Keychain, YubiKey, providers, and real secrets remain
outside this rung.

The declarative contract and any emitted plan are source/design evidence only.
They do not qualify an executable, bundle, signature, App Sandbox profile,
runtime process, generated canary, or secret path.
