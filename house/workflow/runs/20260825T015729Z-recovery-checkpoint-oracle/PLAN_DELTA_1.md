# F1 bounded invocation delta 1

The frozen generator and verifier sources are unchanged.

The first command wave failed at module import before either generator entered
`write_fixture`; neither output directory exists. The invocation omitted the
repository root from Python's module path.

Authorize exactly one corrected command wave with:

`PYTHONPATH=/Users/tiga/Documents/Codex_Projects/codex-dream-house`

The corrected wave may create attempt A and B and run the already sealed
verifiers. It does not increase the two-output fixture budget, change fixture
bytes, widen write scope, or authorize production/real-key/hardware work. No
further automatic retry is permitted if the corrected wave fails.
