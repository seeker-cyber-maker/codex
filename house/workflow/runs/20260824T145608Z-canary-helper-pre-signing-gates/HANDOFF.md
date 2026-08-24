# Handoff: accepted canary-helper pre-signing gates

## Current state

Disposition: `ACCEPT_PRE_SIGNING_GATES_ONLY`

Repository: `/Users/tiga/Documents/Codex_Projects/codex-dream-house`

Branch: `codex/dream-house-auto-switcher`

Starting HEAD: `e51332d3c394f0eada70b85fa75adffb6af7e616`

The milestone commit is the first descendant of that starting HEAD containing
this handoff and `FINAL_SEAL.json`; resolve it locally with:

```bash
git log -1 --format='%H' -- house/workflow/runs/20260824T145608Z-canary-helper-pre-signing-gates/FINAL_SEAL.json
```

## Accepted work

- Static inspection now copies a no-follow pinned source descriptor into a
  private temporary snapshot, binds size and SHA-256, runs only absolute
  `/usr/bin/codesign` on the snapshot, validates exact signature metadata and
  entitlements, then rechecks both snapshot and source identity/content.
- Signing policy schema v2 adds sealed byte sizes and the default template
  remains deliberately ineligible.
- A disposable no-I/O codec-only executable directly tested the unchanged
  `protocol.c` wire format, round trip, validation errors, and transition table.
- A path-normalization edge that could escape as `IndexError` now refuses dot,
  dot-dot, empty, and absolute components and is covered by tests.

## Verification

- Focused native tests: 16 passed.
- Full House suite: 255 passed.
- Ruff, Python compilation, and `git diff --check`: passed.
- No compiled/executable artifact remained under the source directory.
- Three of three blind `gpt-5.6-luna`/medium same-provider reviewers verified
  the same packet hash and accepted the narrow milestone.

Primary council synthesis:
`council/synthesis.md`, SHA-256
`166bd5e75f6c9b400c18c7345ff12bc935b7ea4a6c5050ed7b833db7a5439265`.

## Claim ceiling

Accepted only:

1. snapshot-bound static inspection for strictly verified standalone Mach-O
   files, with ordinary source replacement/drift detection;
2. pure codec behavior under the declared v1 contract.

Not accepted: a signed parent/helper candidate, later launch-path identity,
bundle behavior, App Sandbox runtime containment, dynamic process containment,
same-UID hostile-host resistance, generated-canary safety, or real-secret
safety.

## Preserved next gates

- Enforce subprocess timeouts before using codesign/compiler inspection as a
  stronger admission boundary.
- Make the codec runner reserve its own private no-follow mode-0700 output
  namespace before treating it as a security boundary.
- In the next candidate-specific packet, include actual parent/helper sources,
  entitlement inputs, and bundle layout.
- A fresh explicit authority gate is required before certificate discovery or
  identity signing. Bind paths, sizes, hashes, CDHashes, Team ID, designated
  requirements, exact entitlements, and platform build, then pass static
  inspection before any separately authorized launch.

No certificate discovery, identity signing, parent/helper link or launch,
Keychain, network, provider, YubiKey, generated canary, or real secret was used
in this milestone.

Model advisory for the next phase: `gpt-5.6-sol` at `xhigh`, because the work
crosses identity signing and dynamic process-containment boundaries.
