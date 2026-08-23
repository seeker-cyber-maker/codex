# After-action council review - real firewall and vault threat model

## Outcome

The original candidate required a root delta. The corrected v1.1 threat model
is accepted at a non-runtime claim ceiling after a second blind review.

## What worked

- Direct source inspection separated existing encrypted storage capability from
  the missing broker/containment boundary.
- Modeling each component compromise prevented at-rest encryption from being
  mistaken for protection from an active resolver.
- The conservative delivery state machine avoids false `NOT_EXPOSED` claims in
  crash windows.
- A second, shorter council packet tested the corrections rather than repeating
  the full narrative.

## What required correction

- Ciphertext filenames were initially easy to mistake for independent key
  namespaces; source shows they share one current Keychain passphrase.
- Authority precedence needed an explicit intersection rule.
- Replay protection needed a resolver-verified durable authority ledger,
  distinct from audit evidence.
- macOS hardening needed to begin at trusted spawn/loader configuration, not
  merely inside Rust `main`.
- Capability isolation tests must withhold ciphertext/key access rather than
  expect cryptography to fail after both inputs are granted.

## Review quality notes

- In both rounds OpenRouter's primary Gemma returned 429 and the declared
  Nemotron fallback produced useful but contract-incomplete output at the token
  limit. Both lanes are recorded as partial, not counted as completed votes.
- The constructive ClinePass lane produced the most complete correction review.
- Antigravity was fast and useful but proposed two unsafe precedence/testing
  details across the rounds; root rejected those with the source and exposure
  model.
- Council agreement remains advisory. The design is accepted because the root
  corrections are internally consistent and falsifiable, not because two
  completed reviewers agreed.
- Raw first-round reviewer files contain several trailing spaces. They are
  preserved byte-for-byte as provider evidence and recorded as the only scoped
  `git diff --check` exception.

## Next gate

Protocol/mock-storage implementation with generated values only. Real macOS
Keychain, helper spawn, Seatbelt, provider egress, YubiKey ceremony, and real
secret admission remain separately gated.
