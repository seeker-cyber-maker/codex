# Candidate Council V2 Summary

Packet SHA-256:
`ae1b9c1762d28b536ebe833be23d0f4d4bfbabc72081043248c32611689fd966`

Root disposition: `ACCEPT_SOURCE_SEAL_AT_SYNTHETIC_CEILING`.

All three local same-provider read-only roles reproduced the packet and three
candidate hashes and returned `ACCEPT`. They observed the closed nested reducer
receipt validation, coherent-substitution rejection, preserved no-fresh-reducer
duplicate rule, fixed outer ceiling, and reconciled scope/provenance.

Council independence is limited to separate local agents using the same
provider family. No reviewer ran tests, opened SQLite, edited files, accessed
runtime state, or used network, keys, hardware, controller, worker, or CLI.
Their acceptance corroborates static evidence; it is not operational authority.

Unsupported after acceptance: coordinated full-history SQLite authenticity,
OS containment, fsync/crash durability, protected checkpoints, trusted time,
cryptographic verification, key custody, hardware recovery, dispatch, runtime
admission, or recovery readiness.
