# After-action review — operation v2.1 structural first slice

## Outcome

The accepted first implementation slice is complete at its structural claim
ceiling. Ten numbered falsification cases, two additional invariant tests, and
the complete Dream House Python suite pass. No real worker became eligible.

## What worked

- V2 lives beside v1, so no compatibility guess or launcher/controller change
  entered the slice.
- Exact built-in dictionaries and lists prevent custom mapping methods from
  hiding ambient work inside the supposedly pure boundary.
- Operation assembly deep-freezes caller descriptors by canonical JSON copy,
  preventing later caller mutation from changing sealed record contents.
- Independent descriptor input during verification catches project-inventory
  drift rather than trusting the operation's embedded copy alone.
- CLI supported flags are hash-bound before the project-config-ignore strategy
  can be represented.

## Corrections during implementation

- One test originally expected an inner binding error, while the implementation
  correctly failed earlier at the outer record hash. The assertion was narrowed
  to the stronger fail-fast result.
- A full-suite command was first launched from `codex-rs`, where `house` is not
  importable. It was rerun from repository root and passed 190/190. This was a
  command-context mistake, not a product failure.
- Review found a mutable-alias risk in nested descriptor inputs. Canonical
  deep-copying and a regression assertion closed it before sealing.

## Size and reviewability

The structural module is 644 lines and its deliberately explicit fixture suite
is 420 lines. This is one coherent accepted boundary, but it is already beyond
the preferred compact change size. Future observer, signature, reservation,
controller, or launcher work must use new modules and separate reviewed gates;
do not extend this file into a general worker runtime.

## Next gate

Design a separate read-only descriptor observer and effective-context inventory
contract. It must prove executable/CLI-contract identity and enumerate project
contributors without granting authority or reserving output. Because that gate
introduces host observation, it requires a fresh security-focused plan and
review before implementation.
