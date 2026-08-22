# Evidence packet

Council ID: 20260822-050000-human-authority-interface
Mode: independent-review
Decision question: Is a schema-only, always-refusing human-authority interface
the correct next prerequisite, without probing or enrolling YubiKeys and with
all real execution still blocked?
Deliverable: accept, reject, or narrow the interface and identify the minimum
future YubiKey/FIDO2 qualification invariants.
Privacy: local-only
Cost ceiling: no external provider, hardware interaction, or task execution

## Status

- Current branch: `codex/dream-house-auto-switcher` at
  `9aaba6752154763e9d7f5ba03953d854de03c0c6`.
- Existing mock-admission source SHA-256:
  `c320fab3bbf6448627a466fa336e3840ac30ef795ba3fcb329d98786248d6ae1`.
- Existing controller source SHA-256:
  `44bf2b96211344731126d1ee33b4cff64020c5b5a74b298940e047fadd9ac8fb`.
- Latest runner-contract council synthesis SHA-256:
  `806fd5b28fa0e1fc52464a0ce36dbf8a5062b6a2e15c82c2c41b8bcafb009039`.
- Known unknowns: token model/firmware, enrollment state, origin/RP-ID, one or
  two registered keys, host platform APIs, key revocation workflow, user
  presence behavior, and physical access policy.

## Constraints

- No USB or hardware probing, browser, Keychain, credential, or network action.
- The initial backend must be incapable of authorizing anything.
- A task card, UI control, model, or caller callback cannot create authority.
- Council cannot authorize a real execution path.
