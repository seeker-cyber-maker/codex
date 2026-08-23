# Design review: evidence-auditor

Packet SHA-256: 9effcb178e9187de9e4355eebb0a9e4e696417cee2731cdd89cfb929162db17f
Dispatch model/provider: nvidia/nemotron-3-super-120b-a12b:free / OpenRouter
Reviewer self-report: Independent architecture council member, blind review, no prior knowledge of design beyond packet
Harness: provider-orchestration explicit-free catalog proxy
System-prompt profile: council role only; otherwise unknown
Memory: unknown
Reasoning mode: unknown
Disposition: completed

## Proposed boundary
Minimum implementable architecture: 
- Trusted Computing Base (TCB) comprises: 
  1. Broker-specific storage backend (new module) extending `codex-secrets` with: 
     - Namespace-scoped Keychain account derivation: `compute_broker_keyring_account(codex_home, namespace, epoch)` 
     - Zeroizing plaintext handling: `SecretsBackend` trait extended with `get_zeroing(&self, scope: &SecretScope, name: &SecretName) -> Result<Option<ZeroizingVec>>` where `ZeroizingVec` implements `
