# Vault protocol and mock-storage slice - handoff

## Milestone

Implemented and locally verified a generated-only candidate:

- exact sealed resolve-intent and controller-ticket bindings;
- local-deny intersection and atomic one-use nonce claim;
- independent generated namespace/epoch keys and authenticated temp storage;
- generated rotation with retained superseded ciphertext, a non-secret
  tombstone, old-key destruction, and old-ticket epoch rejection;
- no public plaintext/storage export from `house.worker_exec`;
- monotonic crash/exposure classification; and
- static exclusions for live runtime and ambient secret APIs.

Validation: 26 focused tests and 236 complete House tests passed; Ruff,
formatting, Python compilation, and diff checks passed.

## Claim ceiling

This is a protocol/mock-storage fixture. It does not establish production
zeroization, controller trust, durable multi-process authority state, helper
containment, provider delivery, Keychain compatibility, or safe real-secret
handling.

## Deferred upstream seam

`DEFERRED_UPSTREAM_ADAPTER.md` records the verified Chrome native-host to Codex
app-server topology. It remains an adapter compatibility question and is not a
vault dependency.

## Next acceptance check

Obtain an independent security review of the sealed candidate. If accepted,
the next separately authorized rung is a generated-canary helper-containment
fixture with a trusted-parent spawn contract and mock sink. Do not combine that
with macOS Keychain or any real credential. Recommended lane: Sol/xhigh for the
review and runtime-containment design.
