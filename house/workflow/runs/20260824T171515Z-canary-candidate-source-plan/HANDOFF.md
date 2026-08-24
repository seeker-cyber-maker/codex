# Handoff: revised canary candidate source plan

## Disposition

`REVISED_PLAN_ACCEPTED_PENDING_SOURCE_WRITE_AUTHORITY`

Repository: `/Users/tiga/Documents/Codex_Projects/codex-dream-house`

Branch: `codex/dream-house-auto-switcher`
Starting HEAD: `4644fe65f72753bc735821df5fd1da24b294475f`

## Verified state

- Current parent/helper contracts have no production entrypoint and remain
  launch-disabled.
- No candidate bundle, `Info.plist`, or compiled candidate artifact exists.
- Signing policy remains `NOT_CONFIGURED_NO_LAUNCH`.
- Three blind same-provider reviewers verified packet
  `6515fe7a9221381d58a07dda191fe5098e1a442967e91f0ce0bf36e91aac0940`
  and all 13 indexed hashes.
- All three chose `REVISE_SOURCE_ONLY_SCAFFOLD`.

## Accepted next plan

Use `PLAN_V2.md`: declarative candidate contract, exact or `UNRESOLVED`
platform/bundle/identity fields, pure JSON plan generation, and adversarial
tests. Do not add `main` or other executable-facing refusal source.

## Blocker

This run authorized planning and read-only council work only. Fresh human
source-write authority is required to implement `PLAN_V2.md`.

Even after that authorization, compiler, linker, bundle creation, certificate
or Keychain discovery, identity signing, candidate launch, network, generated
canary, and real-secret operations remain separately forbidden.

Model advisory for the implementation remains `gpt-5.6-sol` at `xhigh` because
the schema defines a future signing and containment boundary.
