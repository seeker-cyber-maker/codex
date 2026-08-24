# Intake: canary declarative candidate contract

## Objective

Implement the council-revised `PLAN_V2.md`: a source-only declarative
candidate contract, a pure non-executing plan generator, and adversarial tests.

## Authority

Explicitly authorized by the user: source and test implementation for PLAN_V2.

Forbidden: compiler or linker execution, candidate bundle creation,
certificate or Keychain discovery, codesign execution, identity signing,
candidate launch, network, canary, provider, YubiKey, or secret operations.

## Claim ceiling

The implementation may establish only schema validation, source/entitlement
binding, unresolved-field refusal, and deterministic plan-data generation. It
cannot qualify any executable, signature, bundle, sandbox, runtime, canary, or
secret.
