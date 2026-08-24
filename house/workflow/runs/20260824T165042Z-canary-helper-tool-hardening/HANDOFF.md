# Handoff: accepted canary-helper tool hardening

## Current state

Disposition: `ACCEPT_TOOL_HARDENING_ONLY`

Repository: `/Users/tiga/Documents/Codex_Projects/codex-dream-house`

Branch: `codex/dream-house-auto-switcher`

Starting HEAD: `29eac0f7d345188f5e3d23242fa4cada077da376`

The milestone commit is the first descendant of that starting HEAD containing
this handoff and `FINAL_SEAL.json`; resolve it locally with:

```bash
git log -1 --format='%H' -- house/workflow/runs/20260824T165042Z-canary-helper-tool-hardening/FINAL_SEAL.json
```

## Accepted work

- Production static codesign uses a ten-second timeout and converts timeout to
  deterministic fail-closed inspection failure.
- Codec compile/link, codesign display, and execution use separate 30-, 10-,
  and 5-second bounds.
- The codec runner requires an existing non-symlink output-root leaf, pins its
  canonical parent, atomically reserves a randomized mode-0700 child, verifies
  inode/mode/regular-file properties, and performs exact descriptor-relative
  cleanup.
- Symlink-root refusal occurs before compiler invocation. Success and injected
  timeout paths clean the expected private output.

## Verification

- Focused native tests: 21 passed.
- Full House suite: 260 passed.
- Ruff, Python compilation, JSON/JSONL parsing, and `git diff --check`: passed.
- No compiled/executable artifact remained under the source directory.
- Real codec execution: exit 0, zero output, ad-hoc/no-Team-ID, mode 0700,
  cleanup complete, supplied output parent empty.
- Three of three blind `gpt-5.6-luna`/medium same-provider reviewers verified
  the same packet and all 14 indexed hashes, then accepted the narrow milestone.

Primary council synthesis: `council/synthesis.md`.

## Claim ceiling

Accepted only for finite configured subprocess bounds and ordinary same-user
private codec output lifecycle. Injected timeout tests are not measured
wall-clock hung-process evidence. Same-UID hostile processes and hostile
toolchains are excluded. Unexpected private-directory entries cause refusal and
are left for investigation; cleanup is not recursive.

Not accepted: compiler/codesign integrity, signed parent/helper identity,
bundle or App Sandbox behavior, dynamic launch-path identity, process
containment, hostile same-UID resistance, generated-canary safety, or
real-secret safety.

## Preserved next gate

A fresh explicit authority gate is required before certificate discovery or
identity signing. Freeze the actual candidate sources, bundle layout,
entitlements, and manifest; bind paths, sizes, hashes, CDHashes, Team ID,
designated requirements, exact entitlements, and platform build before any
separately authorized launch.

No parent/helper link or launch, certificate discovery, identity signing,
Keychain, network/provider, YubiKey, generated canary, or real secret was used.

Model advisory for the next phase: `gpt-5.6-sol` at `xhigh`.
