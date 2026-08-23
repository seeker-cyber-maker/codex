# Root synthesis - host observer v1.1 first slice

## Outcome

`ACCEPT_FIRST_SLICE_NON_RUNTIME` with high confidence at the stated claim
ceiling.

The implementation may be committed and privately backed up. It does not
qualify a runtime, authenticate provenance, reserve output, read credentials,
mutate the controller, launch Codex, contact a provider, or admit a result.

## Council coverage

All three reviewers received and confirmed transport SHA-256
`6fc1215678ca040b3979cadf494a4acfa315edb5fe1d786c080cfbb134265c07`.

- ClinePass / `cline-pass/deepseek-v4-flash`: completed; accepted with no
  blocking defect.
- Google Antigravity / `gemini-2.5-flash-lite`: completed; accepted with no
  blocking defect.
- OpenRouter primary Gemma returned HTTP 429. The explicit-free Nemotron
  fallback completed and returned `ACCEPT_FIRST_SLICE`, but retained template
  placeholders in its metadata fields. Root classifies it
  `SUBSTANTIVE_ACCEPT_WITH_RESPONSE_TEMPLATE_DEFECT`, not pristine contract
  completion.

The three reviews are distinct provider/model lanes but share the same council
prompt profile and evidence packet. Agreement is corroboration, not authority.

## Root decision

Direct source and executed fixtures support acceptance:

1. descriptor-relative, no-follow reads bind bytes to one open descriptor;
2. file, parent, and final directory-entry identity checks detect tested races;
3. retries restart with empty observations and a fresh budget;
4. symlink, hard-link, FIFO, missing-file, mount, collision, secret, and limit
   paths fail closed;
5. negative bundles expose no partial observations or descriptors;
6. request, grammar, policy, CLI capture, and executable bindings are checked
   independently by the verifier; and
7. the verifier's reachable call graph contains no filesystem, clock,
   environment, subprocess, or network call.

## Claim ceiling

`OBSERVED_NOT_QUALIFIED` means closure over the caller-supplied, sealed grammar
only. This slice validates a grammar; it does not derive that grammar from the
actual Codex loader.

The built-in secret filters are conservative controls, not proof that arbitrary
benign-looking text cannot encode a novel secret. Therefore arbitrary private
configuration remains inadmissible, and the produced digest set cannot enter a
runtime profile until a separately reviewed secret-safe projection and grammar
producer exist.

## Smallest next action

Design and review a version-pinned producer that derives the finite contributor
grammar from Codex source/config inputs and emits a semantic, secret-safe
projection. Do not wire this observer into operation-v2 or run it against live
private configuration in that design phase.
