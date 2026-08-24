# Frozen plan: canary-helper bounded-tool hardening

1. Add a fixed timeout to the production static-codesign runner and convert a
   host timeout into a deterministic fail-closed inspection receipt.
2. Require the codec output parent to pre-exist as a non-symlink directory,
   pin it with a no-follow directory descriptor, atomically reserve a random
   mode-0700 child directory, and clean only the expected executable plus that
   exact directory through descriptor-relative operations.
3. Bound codec compilation, signature inspection, and execution separately;
   classify timeouts without broad cleanup or candidate execution.
4. Add adversarial tests for codesign timeout refusal, output-root symlink
   rejection before compiler invocation, cleanup after compiler timeout, and
   successful private-directory cleanup.
5. Run focused and full deterministic validation, freeze evidence, conduct the
   scheduled read-only promotion review, seal, and commit.

Acceptance requires every timeout to fail closed, mode 0700 to be observed,
temporary output cleanup on success and timeout, zero parent/helper execution,
no staged compiled artifact, and full-suite regression success.

Maximum remediation attempts: two. Stop before certificate discovery or any
identity-bearing signing operation.
