# Validation receipt

- `python3 -m unittest house.relay.tests.test_relay house.relay.tests.test_directory`: 7 passed.
- `python3 -m compileall -q house/relay`: passed.
- `ruff check house/relay`: passed.
- `ruff format --check house/relay`: passed.
- `python3 -m unittest discover -s house -p 'test_*.py'`: 168 passed.
- `git diff --check`: passed.
- Sealed provider catalog `90c02fc791bc781c1ba4e0dd8588766feeb0f91c` imported into
  `RelayDirectory`: passed; catalog SHA-256
  `248e1b48291ae596bfa609eb5b5970112fc871cd7bd2f613082f3c9ec32ecb42`.

The full-suite command prints expected argument-validation errors from existing
negative CLI fixtures; its exit status is successful.

## Claim ceiling

This accepts an offline durable relay core only. It does not demonstrate a
callable worker, delivery to a real worker, any network transport, a runtime
profile, or any authority escalation.
