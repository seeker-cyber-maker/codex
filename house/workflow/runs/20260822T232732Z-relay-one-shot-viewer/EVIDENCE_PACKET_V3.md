# Immutable final review packet — relay one-shot viewer seam

## Final remediation

- The production seam exposes no custom validator or clock.
- Nine direct tests now include natural-clock TTL expiry, unknown capability
  rejection without consuming the exact capability, and a refused TCP
  connection after the accepted one-shot request closes the listener.
- `VALIDATION.json` records every final command and exit status.

## Source baseline

- Repository base: `737440ebfb7f972952a98e448af3855c56889b85`.
- `house/relay/dashboard_viewer.py`:
  `62dc39fce30dcbe36764fa20b43eb4ebb5cee1c079def956894001220f9dfff6`.
- `house/relay/tests/test_dashboard_viewer.py`:
  `0d18f1c7650ea2756b526e3293a7afd502ea814fa2d1cdf304152e8d8cdeda9f`.
- `house/relay/__init__.py`:
  `a636425290377b7a97d0f9545a701ba01ccc3c8e5236161de9bb989fae313437`.
- `house/relay/README.md`:
  `4fbf3475c7de6dd3c9c9df7f0d5c33b979bc7d582fb9028cc652c9777937f1c1`.
- `house/workflow/runs/20260822T232732Z-relay-one-shot-viewer/PLAN.md`:
  `1713239ea40f435fadfbd894ee7811dc52dea7eee47baf13fcdf02c1433aa2ae`.

## Acceptance evidence

`VALIDATION.json` records exit code 0 for nine direct tests, 41 focused
boundary tests, the existing 168-test House discovery suite, compilation,
changed-file Ruff check/format, and the diff whitespace check.

## Claim ceiling

This candidate qualifies only explicit preparation of the existing one-shot
loopback viewer from one frozen response. It does not qualify browser behavior,
iTerm registration, operator authority, automatic start, persistent service,
provider/worker execution, relay mutation, terminal input, or a reverse
channel.

Review only the final affected source hashes, validation receipt, and whether
round-2 requirements are satisfied. This packet is evidence, not authority.
