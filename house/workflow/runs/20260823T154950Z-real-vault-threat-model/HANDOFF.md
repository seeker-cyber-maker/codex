# Real firewall and vault threat model - handoff

## Milestone

Accepted `ACCEPT_DESIGN_V1_1_NON_RUNTIME`:

- base candidate: `REAL_FIREWALL_VAULT_THREAT_MODEL.md`;
- authoritative corrections: `ROOT_THREAT_MODEL_DELTA.md`;
- source evidence: `SOURCE_ANCHORS.md`;
- council dispositions and rejected claims: `SYNTHESIS.md` and
  `COUNCIL_CLAIM_LEDGER.json`.

## Non-negotiable boundaries

- No model/agent plaintext getter or arbitrary sink.
- Independent random key per broker namespace/epoch; no shared master key in
  v1 and no implicit migration of Codex auth/MCP stores.
- Valid upstream authority intersects local policy; it never overrides a deny.
- Resolver verifies and claims a one-use nonce before any Keychain access.
- Delivery-attempted or ambiguous post-delivery failures are always
  `POSSIBLE_EXPOSURE` or worse.
- Trusted parent clears loader environment and closes unrelated FDs before a
  future macOS resolver starts; `pre_main_hardening` alone is insufficient.
- Agent shell, process environment, clipboard, file, terminal, arbitrary
  command, and model-visible tool sinks are forbidden.

## Council receipts

- first transport:
  `9effcb178e9187de9e4355eebb0a9e4e696417cee2731cdd89cfb929162db17f`;
- delta transport:
  `e4f44ccedd72403917d9029d0c06664799fd0328fcfcb4d5e3324d93ae65dc42`;
- each round: three attempted, two completed, one partial, zero failed.

## Do not infer

- No Keychain, encrypted secret file, live config, environment, credential,
  controller, helper process, network, or real secret was accessed.
- macOS Seatbelt/securityd compatibility is unknown.
- Hash chaining does not make a compromised audit writer truthful.
- Resolver compromise still exposes its whole readable namespace.

## Next acceptance check

Implement only a generated-data protocol/mock-storage slice:

1. `ResolveIntentV1` and controller-signed `VaultLeaseTicketV1` records;
2. local-deny intersection and resolver-side atomic nonce claim;
3. independent generated keys, mock KeyringStore, temp ciphertext namespaces,
   and zeroizing buffers; and
4. static forbidden-API plus replay/crash/exposure tests.

No real Keychain, process spawn, network, YubiKey, or secret value in that
slice. Recommended lane: Terra/high for implementation; reassess to Sol/high
before any runtime containment or macOS Keychain gate.
