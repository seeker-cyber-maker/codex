# Validation receipt

- `python3 -m unittest house.relay.tests.test_relay`: 5 passed.
- `python3 -m compileall -q house/relay`: passed.
- `ruff check house/relay`: passed.
- `ruff format --check house/relay`: passed.
- `python3 -m unittest discover -s house -p 'test_*.py'`: 168 passed.
- `git diff --check`: passed.

The full-suite command prints expected argument-validation errors from existing
negative CLI fixtures; its exit status is successful.

## Claim ceiling

This accepts an offline durable relay core only. It does not demonstrate a
callable worker, delivery to a real worker, any network transport, a runtime
profile, or any authority escalation.
