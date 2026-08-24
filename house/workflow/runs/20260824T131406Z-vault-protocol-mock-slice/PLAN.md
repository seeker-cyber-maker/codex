# Vault protocol and mock-storage slice - frozen plan

1. Implement exact `ResolveIntentV1` and generated controller-signed
   `VaultLeaseTicketV1` records.
2. Intersect signed authority with local policy and atomically claim a nonce
   before any mock storage operation.
3. Implement independent generated namespace/epoch keys, authenticated temp
   storage, restrictive modes, and best-effort zeroizing buffers without a
   plaintext-return API.
4. Implement monotonic crash/exposure classification.
5. Test wrong binding, local deny, replay, expiry, forbidden sinks, independent
   keys, corrupt/newer storage, wrong key, rotation, crash windows, public API
   absence, and forbidden runtime imports.
6. Run focused and complete House regressions, seal exact sources, and stop
   before helper/runtime/Keychain work.

Acceptance requires all tests and static checks to pass with no change outside
`house/` and no live authority or secret access.
