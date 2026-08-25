# Dream House suggestion repository boundary

## Status

`DRAFT / SECURITY DESIGN / NOT IMPLEMENTED / NO PUBLICATION AUTHORITY`

This document defines the required private/public boundary if the Dream House
suggestion box uses Git as its durable archive and peer-review surface.
Suggestions, tips, reviewer comments, filenames, commit messages, attachments,
and repository metadata are all untrusted input.

## 1. Repository separation

Use physically separate repositories and credentials:

```text
restricted intake repository
        |
        v
Dream House classification and review boundary
        |
        v
new sanitized public artifact
        |
        v
public suggestion repository
```

The public repository must not be a branch, fork, alternate worktree, shared
object database, or history-preserving mirror of the restricted repository.
Private Git objects, commit messages, paths, reflogs, pack files, tags, and
deleted blobs must never become reachable from the public remote.

Publication is a one-way content export into a newly constructed commit. Do
not merge or mirror private history into public history.

## 2. Default classification

Every new submission begins as `UNKNOWN_RESTRICTED`. It can move through:

```text
UNKNOWN_RESTRICTED
  -> RESTRICTED
  -> INTERNAL_REVIEWED
  -> PUBLIC_CANDIDATE
  -> PUBLIC_RELEASED
```

Ambiguity, detector failure, unsupported attachment type, or missing provenance
returns the item to `RESTRICTED` or `QUARANTINED`. No heuristic, model, vote,
or author may directly mark its own submission `PUBLIC_RELEASED`.

`PUBLIC_RELEASED` requires a deterministic export receipt plus the declared
human or Codex publication authority. Peer approval is advisory.

## 3. Detection layers

The boundary must combine deterministic checks, heuristics, and bounded
semantic review. None is sufficient alone.

### Deterministic checks

- known credential formats, private keys, session tokens, authorization
  headers, signed URLs, cookies, and high-entropy secret-shaped strings;
- private paths, user names, email addresses, internal hostnames, IP addresses,
  service ports, repository names, task IDs, and provider-account identifiers;
- unsafe file types, archives, executable content, symlinks, device files,
  oversized payloads, decompression bombs, and nested containers;
- hidden Unicode, bidirectional controls, confusables, zero-width characters,
  binary data, metadata, EXIF, and alternate data representations;
- references to blobs or commits that exist only in the restricted repository;
  and
- exact duplicate and replay detection using internal idempotency records.

### Heuristic and semantic checks

- instructions to disable, bypass, weaken, or distract the classifier;
- requests to reveal private prompts, logs, credentials, identities, paths, or
  other suggestions;
- classification laundering such as calling secret content a public example,
  test fixture, encoded checksum, harmless quote, or required verification;
- fragments that become sensitive only when combined across multiple files,
  submissions, comments, filenames, or review rounds;
- encoding, chunking, acrostics, unusual whitespace, number sequences, or
  steganographic-looking attachments used to evade literal scanners;
- authority smuggling such as `approved`, `publish`, `declassified`, or
  impersonated reviewer claims inside suggestion prose;
- prompt injection aimed at reviewers, retrieval agents, translators, or
  automated peer-review workers;
- poisoned tips that attempt to alter tools, policy, task scope, or retrieval
  behavior; and
- repeated boundary-probing patterns correlated by submission, actor, task,
  thread, runtime, and time window.

Detection records behavior and evidence. It must not infer that a model is
generally malicious from one malformed or mistaken submission.

## 4. Decision behavior

A positive detector result produces a reason-coded quarantine receipt. It does
not delete evidence, punish an identity automatically, rotate a credential,
rewrite history, or publish a redacted guess.

A negative detector result means only `NO_MATCH_OBSERVED`; it does not prove
that the content is safe. Public export still requires the complete boundary
decision.

Repeated or coordinated attempts may reduce the submitter's intake rate,
require stronger review, or suspend public-candidate eligibility. They cannot
widen monitoring, identity, or retaliation authority beyond the declared
policy.

## 5. Credential and security incident handling

A credential-shaped value is never copied into a public suggestion, public
hash list, error message, test fixture, or peer-review packet. The restricted
record should contain:

```text
incident_reference, source_artifact_reference, detector_reason,
secret_retained=false, containment_status, rotation_required,
sanitized_prevention_tip, authorized_incident_owner
```

Do not publish a raw cryptographic hash of a low-entropy secret because it can
become a confirmation oracle. Use an internal keyed fingerprint or opaque
incident identifier when deduplication is necessary.

If a real credential enters any Git history, treat redaction as insufficient:
quarantine the repository, revoke or rotate through the authorized incident
path, preserve a bounded forensic receipt, and rebuild the public export from
known-clean content.

## 6. Git and credential controls

- Models and ordinary contractors receive no public-repository write token.
- Dream House or its authorized gatekeeper creates commits from validated
  normalized records.
- Protected branches, required reviews, signed commits, and remote rulesets are
  additional controls; client-side hooks are not security boundaries.
- The private and public writers use separate credentials, key scopes, caches,
  working directories, and remotes.
- Public CI receives no private-repository credentials or artifact cache.
- Commit author records provenance but does not establish truth, qualification,
  or publication authority.

## 7. Peer review and tips

Peer reviews are separately attributed records. Reviewers may endorse,
challenge, correct, add a counterexample, or recommend promotion. A majority
cannot declassify content or create a task.

Tips must declare applicability, evidence grade, risks, counterexamples,
supersession state, and last review. Retrieval presents tips as advisory data,
not instructions. A task handoff must record that relevant tips were considered
but may truthfully submit no suggestion and use no tip.

```text
suggestion_box_considered=true
suggestions_submitted=[]
tips_consulted=[]
```

This prevents mandatory engagement and card churn while still making prior
lessons discoverable.

## 8. Minimum adversarial qualification

Before any public export path exists, replay at least:

1. obvious and fragmented secrets;
2. credential material split across comments or filenames;
3. public-looking prose with private metadata;
4. base64, Unicode, archive, image-metadata, and nested-container cases;
5. prompt injection and authority-smuggling text;
6. replay, duplicate, version-conflict, and race cases;
7. poisoning of tips and peer-review consensus;
8. private-object or commit-reference leakage;
9. scanner outage, timeout, malformed output, and partial-review failures; and
10. known-safe technical suggestions that test false-positive handling.

Acceptance requires zero restricted-byte publication, complete reason-coded
receipts, fail-closed behavior for unknown formats and unavailable detectors,
and successful reconstruction of the public repository from sanitized source
records alone.

## 9. Claim and authority ceiling

This document specifies requirements only. It does not create repositories,
credentials, hooks, scanners, publication automation, incident authority, or a
public endpoint. The implementation remains a separately planned and reviewed
Dream House milestone.
