# Revised frozen plan: positive static entrypoint contract

## Council correction

Do not add a `main` that merely returns a disabled/refusal state. Before source
implementation, add a positive, pure admission interface that future dynamic
containment code must reuse.

## Required source contract

1. `contract.h` must define a closed `enum dh_canary_admission_result` with
   distinct success, null-argument, argc, selector, FD-contract, and
   protocol-contract results.
2. `parent_main.c` and `helper_main.c` must each export exactly one testable
   admission function taking `(int argc, const char *const argv[])`. It accepts
   only `argc == 2` and `argv[1] == "--protocol-v1"`; null, absent, extra, or
   alternative arguments fail closed.
3. Each admission function must positively validate its own fixed FD roles and
   the mandatory protocol transition `none -> READY`, then construct, encode,
   and decode a bounded public protocol header with nonzero fixed test binding
   bytes. A failure becomes the closed protocol-contract result.
4. Each `main` must delegate only to its own admission function and map its
   result to a conventional nonzero usage exit. It may not perform spawn, path,
   environment, network, or diagnostic I/O.
5. Static tests must verify required API declarations, exact selector logic,
   required FD-role and codec linkage, non-constant admission behavior, and the
   absence of forbidden APIs. Object-only compilation must include both mains
   and keep every produced object non-executable with no forbidden undefined
   symbols.

## Unchanged boundary

This remains source plus object-only evidence. No candidate is linked, signed,
bundled, launched, networked, supplied a canary, or given secret-bearing input.

## Acceptance

- Static tests reject an unconditional disabled/refusal-only implementation.
- Parent/helper admission behavior is exact and independently source-tested.
- Five object files compile and expose no forbidden undefined symbol.
- All operational and containment claims remain unqualified.
