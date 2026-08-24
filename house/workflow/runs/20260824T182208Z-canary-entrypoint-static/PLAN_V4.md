# Final accepted plan: test and production admission parity

`PLAN_V4.md` supersedes `PLAN_V3.md` for one mechanical rule: the
`DH_CANARY_ENTRYPOINT_UNIT_TEST` macro may guard only the two production `main`
definitions. It may not appear inside, alter, select, or conditionally compile
either admission-function body or any function it calls. Static tests must
reject conditional-compilation directives or macro references in the admission
implementation regions.

All `PLAN_V3.md` source, vector, test, private-output, and claim-boundary
requirements remain unchanged. This correction creates parity between the
unit-test-linked functions and the production-linked functions without launching
either candidate.
