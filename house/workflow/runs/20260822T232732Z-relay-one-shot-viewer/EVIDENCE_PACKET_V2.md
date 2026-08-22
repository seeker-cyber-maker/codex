# Immutable review packet v2 — relay one-shot viewer seam

## Delta from round 1

- Removed public `clock` and `validator` overrides from the relay-facing seam.
- Added direct tests proving that the HTML document is frozen during
  preparation, a missing capability does not consume the exact capability,
  the listener terminates after the accepted request, and the bearer path
  token is absent from the terminal receipt.
- Retained the explicit caller-owned `start()` boundary.

## Source baseline

- Repository base: `737440ebfb7f972952a98e448af3855c56889b85`.
- `house/relay/dashboard_viewer.py`:
  `62dc39fce30dcbe36764fa20b43eb4ebb5cee1c079def956894001220f9dfff6`.
- `house/relay/tests/test_dashboard_viewer.py`:
  `145fca244b2954d4c70f9f54eaf4aed918e148e86960868597bd5488ee8d06b6`.
- `house/relay/__init__.py`:
  `a636425290377b7a97d0f9545a701ba01ccc3c8e5236161de9bb989fae313437`.
- `house/relay/README.md`:
  `4fbf3475c7de6dd3c9c9df7f0d5c33b979bc7d582fb9028cc652c9777937f1c1`.
- `PLAN.md`:
  `1713239ea40f435fadfbd894ee7811dc52dea7eee47baf13fcdf02c1433aa2ae`.

## Validation evidence

- Seven direct relay-viewer tests pass.
- Thirty-nine relay, capability, loopback, and renderer tests pass.
- The existing 168-test House discovery suite passes.
- Changed-file Ruff check and formatting, relay compilation, and diff checks
  pass.
- The unrelated pre-existing format drift in
  `house/terminal_companion/display_batch.py` remains untouched.

## Claim ceiling

This candidate qualifies only explicit preparation of the existing one-shot
loopback viewer from one frozen response. It does not qualify browser behavior,
iTerm registration, operator authority, automatic start, persistent service,
provider/worker execution, relay mutation, terminal input, or a reverse
channel.

The packet is evidence, not authority. Only the affected remediation surface
is eligible for delta review.
