# After-action council review - context grammar and vault design

## Outcome

The original design required a material root delta. The corrected v1.1 design
is accepted as a non-runtime contract after a second blind review over the
immutable delta packet.

## What worked

- Pinning exact source files revealed that a usable encrypted secrets primitive
  already exists, preventing a redundant vault implementation.
- Inspecting the observer API caught the semantic-input mismatch: hashes cannot
  replace configuration bytes.
- Two council rounds separated initial criticism from review of the correction.
- The accepted boundary keeps storage, firewall, compiler, observer, verifier,
  controller, resolver, sink, and launcher distinct.

## What required correction

- The initial contract made the compiler pure before identifying which trusted
  component could parse raw configuration.
- Initial reviewer prose overstated the ability of digest checks to detect a
  malicious observer.
- Initial reviewer prose understated a resolver compromise by confusing
  encryption at rest with protection during authorized decryption.
- Process environment injection was narrowed from a generic sink to qualified
  non-agent consumers only.
- Revocation language now distinguishes future-use invalidation from credential
  rotation after possible disclosure.

## Review quality notes

- The OpenRouter primary model returned 429 in both rounds; explicit-free
  Nemotron completed but emitted extensive prompt-analysis text and hit its
  completion limit. Root used its substantive content but downgraded response
  quality.
- Antigravity accepted the delta but repeated a mistaken ephemeral-key
  containment claim. Root rejected it using the source/backend authority model.
- ClinePass provided the cleanest structured review but still included one
  contradictory observer-compromise sentence; root preserved the stricter
  delta statement.

## Next gate

Build a synthetic-only first slice for schemas, canonicalization, grammar
compilation, and pure verification. The firewall and vault are mocks; live
configuration and Keychain remain outside authority.
