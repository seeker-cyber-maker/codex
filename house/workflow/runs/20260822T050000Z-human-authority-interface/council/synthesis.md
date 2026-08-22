# Council synthesis

All three local reviewers verified packet SHA-256
`5280d422f9527400eb7467fa583dd17f8cab389a43c8bff021ba1b0398c472cb`.
They narrowly accepted only a disjoint, always-refusing authority interface.

The interface must never share a schema with a future signed authority, accept
callbacks or configurable execution fields, or call the controller.  A future
YubiKey/FIDO2 path needs separate qualification of enrollment/revocation,
RP-ID/origin, challenge/signature, user-presence policy, token counter policy,
physical access, and atomic one-time consumption with spawn intent.

Configured authority and all execution remain blocked.
