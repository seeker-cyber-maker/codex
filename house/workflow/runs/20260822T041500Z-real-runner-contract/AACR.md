# After-action council review

The design review isolated the runtime-profile and authority contract before
any runner code.  The key finding was that generic subprocess and fixture
callback primitives are not structural real-execution barriers.  The resulting
mock-only layer deliberately avoids them.  Real execution stays a separate
reviewed phase.
