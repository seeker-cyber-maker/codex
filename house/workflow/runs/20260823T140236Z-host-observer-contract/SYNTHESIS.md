# Root synthesis - host observer contract v1.1

## Outcome

`ACCEPT_OBSERVER_DESIGN_V1_1` for a future isolated implementation slice, with
medium confidence.

This accepts the reviewed v1 contract plus `V1_1_DELTA.md`. It does not accept
an observer implementation, qualify a runtime, authenticate provenance, grant
authority, reserve output, read credentials, mutate the controller, start a
process, call a provider, or admit a result.

## Council coverage

- All three lanes received the immutable transport packet with SHA-256
  `f8e111c09585ce48bb7c59555839393bb59bf8c101bb000bae056a503f740989`.
- ClinePass / `cline-pass/deepseek-v4-flash` completed, confirmed the packet
  hash, accepted the stated boundary, and identified a residual path-to-bytes
  race that could survive metadata-only comparison.
- OpenRouter explicit-free / `google/gemma-4-31b-it:free` completed, confirmed
  the packet hash, and accepted the observer/verifier/admission separation.
- OpenCode Go timed out on both `deepseek-v4-flash` and `qwen3.8-max`. It is
  classified `FAILED_UNAVAILABLE`, not abstention or agreement.
- The runner manifest reports two completed reviewers and one failed reviewer.
  It records packet privacy as `unknown` despite the packet's explicit
  `cloud-ok` text and the bounded `--allow-cloud` dispatch. Root preserves this
  mismatch as a council-runner receipt defect rather than rewriting evidence.

## Root corrections

The council's shared conclusion supports the design boundary, but reviewer
prose is advisory and contains two overclaims that are not adopted:

1. Observer execution does not authenticate provenance. A hash binds bytes,
   and the observer self-report remains unauthenticated until a later signer
   and trust policy is accepted.
2. The request is not assumed benign. Closed schema, canonical encoding,
   finite roots, bounds, and cross-record agreement must treat it as
   adversarial input.

Root adopts the security architect's residual race as a real repair. V1.1
requires directory-anchored no-follow descriptors, same-descriptor pre/post
`fstat`, hashing from that descriptor, and a final directory-entry-to-descriptor
identity check. There is no path-based fallback.

## Decision basis

The combined v1.1 design now:

1. separates observation, pure verification, and later admission;
2. expresses closure against a finite, source-versioned contributor grammar;
3. refuses project-config isolation claims unsupported by the current CLI;
4. excludes secrets and stable secret identifiers by construction;
5. makes incomplete, unstable, unknown, and over-limit states non-usable;
6. binds read bytes to descriptor identity during the observation interval;
7. treats CLI captures and observer output as asserted evidence rather than
   authenticated provenance; and
8. grants no dispatch or execution authority.

## Smallest next action

In a fresh bounded phase, implement only request/schema types, the read-only
observer, the pure verifier, and the 16 falsification fixtures plus the v1.1
descriptor-race fixtures. Do not add credentials, runtime admission, output
reservation, controller writes, launcher code, or provider dispatch.
