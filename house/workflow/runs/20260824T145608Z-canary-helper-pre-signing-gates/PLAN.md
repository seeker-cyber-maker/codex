# Frozen plan: canary-helper pre-signing gates

1. Preserve the two host `codesign` probes: reject `/dev/fd` as unsupported;
   admit a private pinned-descriptor copy only for standalone Mach-O artifacts
   that pass strict verification from the snapshot.
2. Change static inspection to copy from one no-follow pinned source descriptor
   into a private `0700` temporary namespace, verify the copied hash, inspect
   only the snapshot, then revalidate source path identity and content before
   returning a static qualification.
3. Add adversarial unit fixtures for source replacement during inspection,
   snapshot-only tool paths, and copy/hash invariants.
4. Add a no-I/O C codec test executable covering the exact big-endian wire
   image, valid round trips, every validation error, and the complete legal and
   illegal transition matrix.
5. Link and run only that codec test under a five-second timeout in a fresh
   temporary directory. Parent/helper objects remain unlinked and unlaunched.
6. Run focused and full validation, conduct the scheduled read-only promotion
   council, seal evidence, and commit. Stop before identity discovery or
   signing.

Acceptance requires deterministic refusal on source mutation, snapshot-bound
`codesign` calls, codec exit zero, full-suite regression success, no staged
compiled artifacts, and zero parent/helper candidate execution.
