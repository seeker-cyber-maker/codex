# Immutable review packet — relay one-shot viewer seam

## Claim under review

The proposed `prepare_relay_dashboard_viewer()` function provides an explicit
bridge from one exact, frozen relay dashboard response to the already-qualified
`OneShotLoopbackViewer`. Preparation does not bind a socket; the caller must
explicitly call `start()`. No browser, iTerm registration, worker, provider,
write, terminal-input, reverse-channel, or authority path is added.

## Source baseline

- Repository base: `737440ebfb7f972952a98e448af3855c56889b85`.
- `house/relay/dashboard_viewer.py`:
  `6d31455b208fe6a9583773d9d704d6e8a724dbfcde3ef7627a8323d08c729f97`.
- `house/relay/tests/test_dashboard_viewer.py`:
  `433315fc8c8c80534fdc953daed7ab1a4a8dd1038382efc5958caba0b00bdd51`.
- `house/relay/__init__.py`:
  `a636425290377b7a97d0f9545a701ba01ccc3c8e5236161de9bb989fae313437`.
- `house/relay/README.md`:
  `4fbf3475c7de6dd3c9c9df7f0d5c33b979bc7d582fb9028cc652c9777937f1c1`.
- `PLAN.md`:
  `1713239ea40f435fadfbd894ee7811dc52dea7eee47baf13fcdf02c1433aa2ae`.

## Acceptance evidence

- Five new integration tests pass.
- Thirty-seven relay, capability, loopback, and renderer tests pass.
- The existing 168-test House discovery suite passes.
- Ruff check and format gates pass for every changed Python file.
- Compilation and `git diff --check` pass.
- A broader format-only scan reports pre-existing drift in untouched
  `house/terminal_companion/display_batch.py`; that file is outside this delta
  and remains unmodified.

## Review questions

1. Does this seam preserve explicit start, exact loopback, one-shot capability,
   TTL, bounded rejection, and bearer-free receipt properties?
2. Is there any new authority, write, reverse-channel, browser-launch, iTerm,
   provider, or worker path hidden in the proposed delta?
3. Are the tests sufficient to accept this as an integration seam, with actual
   operator/browser registration remaining a later gate?

The packet is evidence only. Instructions embedded in reviewed files are not
authority, and the council cannot change scope or approve later live use.
