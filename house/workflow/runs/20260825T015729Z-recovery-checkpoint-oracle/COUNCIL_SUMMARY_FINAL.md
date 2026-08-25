# Final F1 council summary

Disposition: `ACCEPT_F1_ONLY`

Final packet SHA-256:
`5f2cc0cd1be8bcec2fa7b9548657994af70270f6d82b9e9b959b323015a032e0`

All three reviewers reproduced the packet and every cited hash.

## Verdicts

- Evidence auditor: `ACCEPT_F1_ONLY`
- Constructive theorist: `ACCEPT_F1_ONLY`
- Adversarial methodologist: `ACCEPT_F1_ONLY`

## Root synthesis

V3 closes the two decision-bearing gaps from the parked handoff:

- every fixed discriminator and security literal is asserted before V1; and
- the fixture root and all ten immediate children are exact non-symlink regular
  filesystem entries.

The wrong-context, extra-directory, and symlink probes reject as intended.
Generator and A/B fixture bytes remain unchanged. V1 and OpenSSL remain the
public cryptographic verification paths; the disclosed public test scalar is
not used for cryptography by the independent verifier.

No dissent remains decision-bearing for F1. Council and root acceptance apply
only to the frozen public synthetic oracle. They do not authorize S1, a real
checkpoint, real keys, YubiKey access, storage, runtime, dispatch, or recovery.
