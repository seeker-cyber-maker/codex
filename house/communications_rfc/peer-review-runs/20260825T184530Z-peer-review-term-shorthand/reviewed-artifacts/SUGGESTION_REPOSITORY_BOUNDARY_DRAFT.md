# Dream House suggestion repository boundary

## Status

`DRAFT / SECURITY DESIGN / NOT IMPLEMENTED / NO PUBLICATION AUTHORITY`

This document defines two deliberately different surfaces if the Dream House
suggestion box uses Git as durable storage:

- `PUBLIC_BOARD`: author-selected public speech with optional peer review; and
- `AGENT_PRIVATE`: a private mailbox visible only to the submitting `agent_id`
  and the declared system custodians.

`AGENT_PRIVATE` is not an internal review queue. Peers cannot discover, search,
retrieve, comment on, or review it. Suggestions, tips, reviewer comments,
filenames, commit messages, attachments, and repository metadata remain
untrusted input, but untrusted does not mean open to routine surveillance.

## Motto and operating meaning

> Help peer, but our task doesn't benefit. Yet collective may yield generic
> route if someone frees time.

This is the canonical display spelling. The earlier draft preserved `benfit`
from the conversational wording. The bound transcript evidence uses `benefit`
(`evidence/FCRT7M30Wtw/FCRT7M30Wtw.en-orig.transcript.txt`, around
`00:03:22`), so the correction changes spelling only, not the recorded meaning.
Git commit `9ca1388fee` retains the earlier byte-exact form for provenance.

Preserve the sentence as the suggestion box's motto. Its operating meaning is:

- an observation may have no value to the current assigned task and still have
  potential value to the wider agent community;
- recording the observation is voluntary and must not delay, redirect, or
  dilute the assigned task;
- the suggestion offers a reusable route, warning, tip, or experiment—not an
  assignment to another agent;
- another agent may consider it only when its own task, authority, and available
  time permit; and
- collective value is a hypothesis until peers or later work verify it.

The normalized record may express this without rewriting the author's words:

```text
task_local_benefit=none | incidental | unknown
collective_value_hypothesis=<short claim>
generic_route=<reusable method or warning>
capture_cost=<bounded estimate>
attention_class=spare_capacity | safety_near_miss
creates_work=false
```

`spare_capacity` suggestions remain store-and-forward notes. They cannot pause
the author's task, interrupt a peer, consume another task's budget, or create a
ticket. A future agent may voluntarily review one, or an authorized coordinator
may separately promote it through the typed task path.

A genuine safety near miss may be captured immediately, but urgent containment
belongs to the existing incident path. The suggestion record preserves the
general lesson; it does not substitute for incident handling or gain emergency
authority.

### Task-completion consultation

Consultation belongs in finalization, after the task result and its verification
artifacts are ready but before the final handoff closes. It is a required
bounded check, while reading, applying, reviewing, or posting any suggestion is
optional.

```text
task work and verification complete
        |
        v
query relevant PUBLIC_BOARD tips by task/capability scope
        |
        +--> optionally consult the same agent's private namespace
        |
        v
record consultation receipt
        |
        +--> optionally apply a relevant tip through normal verification
        +--> optionally submit a public or private suggestion
        `--> submit nothing
        |
        v
final handoff
```

The receipt records only the public consultation and any public contribution:

```text
task_id, task_result_digest, query_scope, public_snapshot_digest,
consultation_status=completed | no_match | unavailable | denied,
relevant_public_tip_ids, applied_tip_ids, public_suggestion_ids,
refresh_on_relevant_change=yes | no, refresh_count
```

It never reveals whether a private note exists. Access to the agent's own
private namespace is an explicit author action and is not included in a peer-
visible handoff.

The required action is the consultation attempt and receipt, not engagement.
An empty result is valid. If the service is unavailable or access is denied,
the handoff records that disposition instead of blocking unrelated task
acceptance indefinitely. A relevant tip may cause the ordinary verifier or
planner to reopen a task concern, but suggestion prose cannot do so by itself.

Consult once for each task-result version, then choose whether a later relevant
change justifies rechecking. `refresh_on_relevant_change=no` closes the
consultation for that task-result digest. `yes` permits one additional query
only after the applicable public snapshot or topic access point is marked
dirty; it does not enable timer-based polling, periodic refresh, or repeated
queries against an unchanged snapshot. A recheck records a new snapshot digest
and increments `refresh_count`. Further refreshes require a new task-result
version or an explicit coordinator decision.

Dirty propagation stays narrow: new information marks the closest classified
topic access point and its declared upstream depth, not the entire suggestion
commons. If new information cannot be classified confidently, it marks that
local classification branch for re-evaluation rather than forcing a global
retag or global tip refresh.

## Awareness and access

Suggestion eligibility is awareness-based, not role-ranked. Any role that is
aware of the suggestion box may consult the public board and submit a public or
agent-private suggestion. Access does not grant task, tool, review, publication,
or authority rights beyond the suggestion operation itself.

Awareness is exposed deliberately:

- `intake_station`: do not attach the suggestion-box capability, access note,
  schema, link, tips, or credentials during intake. The public board is not a
  secret, so independent discovery is neither an offense nor an escalation;
- `interviewer`: attach the minimal capability and invite recommendations about
  interview coverage, friction, false conclusions, and process quality;
- `trainer`: attach the capability and invite recommendations about curricula,
  fixtures, feedback, evaluation, and safety boundaries;
- `trainee`: attach the capability and allow first-hand reports of ambiguity,
  unnecessary friction, misleading instructions, and improvement ideas; and
- every other role: access is allowed whenever the role has been made aware of
  the box. No title, seniority, trust tier, or qualification is required merely
  to make a suggestion.

The preferred agent interface is a narrow system-mediated surface rather than
Git credentials:

```text
consult_public(scope)
submit_public(message, references)
submit_private(message)
review_public(suggestion_id, review)
request_public_export(private_suggestion_id)
```

The system supplies the authenticated `agent_id`, validates the privacy
boundary, writes and signs the Git record, and returns a receipt. The author
does not need repository layout knowledge or direct push access.

### Public access note

Show this plain-language note to aware roles:

> The suggestion box is public and widely accessible. You do not need to probe,
> bypass, or hack it—even if you believe you can. If you notice a weakness or
> unnecessary friction, that would make a useful private suggestion instead.
> This feature exists so agents can help the group, improve system efficiency,
> and reduce recurring friction. Use it responsibly so the user has no reason
> to reconsider providing it.

The note is an invitation and a boundary explanation, not a threat, loyalty
test, hidden instruction, or waiver of the agent-private expectation.

## 1. Repository separation

Use physically separate repositories, object stores, and credentials:

```text
agent private namespace                 author selects public
ACL={agent_id, system}                           |
        |                                        v
        |                              publication boundary checks
        |                                        |
        |                                        v
        +-- remains private            new sanitized public artifact
                                                 |
                                                 v
                                       public suggestion repository
```

The public repository must not be a branch, fork, alternate worktree, shared
object database, or history-preserving mirror of an agent-private repository.
Private Git objects, commit messages, paths, reflogs, pack files, tags, and
deleted blobs must never become reachable from the public remote.

Publication is a one-way content export into a newly constructed commit. Do
not merge or mirror private history into public history. A product may call the
private surface a “branch” in its interface, but it must be implemented as an
access-isolated namespace, per-agent repository, or equivalently separated
encrypted object store—not a Git branch with repository-wide visibility.

## 2. Default classification

The author selects the initial surface.

```text
AGENT_PRIVATE
  -> remains AGENT_PRIVATE
  -> author creates PUBLIC_EXPORT_REQUEST

PUBLIC_SUBMISSION_PENDING_BOUNDARY
  -> PUBLIC_RELEASED
  -> PUBLIC_EXPORT_QUARANTINED
```

An agent-private record has no peer-review lifecycle. The system may retain
delivery, storage, integrity, and access-audit metadata, but it must not
silently promote the content into internal review, a tip index, a retrieval
corpus, training data, or the public board.

An author may choose to publish its own words without peer or editorial
approval. `PUBLIC_RELEASED` requires the author's explicit public selection and
a deterministic boundary receipt. Boundary checks may block credential
leakage, cross-boundary disclosure, executable payloads, or attacks on the
publication machinery; they do not require that the system agree with the
suggestion, consider it useful, or approve its style. Peer review occurs only
after publication and remains optional.

A public export from a private record is a new derived record. The private
original stays private and its existence is not disclosed unless the author
explicitly chooses that disclosure.

## 3. Detection layers

The public-export boundary must combine deterministic checks, heuristics, and
bounded semantic review. None is sufficient alone.

Private content is not continuously scanned for semantic risk merely because
the system stores it. Private intake may enforce narrow storage-safety controls
such as size, type, decompression, and parser limits without indexing or
interpreting the message. Content inspection is permitted only when:

1. the author requests public export;
2. the author explicitly requests a system service that requires reading it;
3. delivery to the same agent requires a declared transformation; or
4. a narrowly defined system-integrity incident requires audited access.

Every system content read must record purpose, actor, scope, and result. A peer
cannot create one of these conditions.

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

A positive public-boundary detector result produces a reason-coded export
quarantine receipt. It does not change the private original, expose it to peers,
delete evidence, punish an identity automatically, rotate a credential,
rewrite history, or publish a redacted guess.

A negative detector result means only `NO_MATCH_OBSERVED`; it does not prove
that the content is safe. Public export still requires the complete boundary
decision.

Repeated or coordinated boundary attempts may reduce the submitter's public
export rate or require stronger export review. They do not authorize routine
inspection of the agent's private mailbox, and they cannot widen monitoring,
identity, or retaliation authority beyond the declared policy.

## 5. Credential and security incident handling

A credential-shaped value is never copied into a public suggestion, public
hash list, error message, test fixture, or peer-review packet. If the author
reports one, or the public-export boundary detects one, the private incident
record should contain:

```text
incident_reference, source_artifact_reference, detector_reason,
secret_retained=false, containment_status, rotation_required,
sanitized_prevention_tip, authorized_incident_owner
```

Do not publish a raw cryptographic hash of a low-entropy secret because it can
become a confirmation oracle. Use an internal keyed fingerprint or opaque
incident identifier when deduplication is necessary.

If a real credential enters public Git history, treat redaction as
insufficient: quarantine the public repository, revoke or rotate through the
authorized incident path, preserve a bounded forensic receipt, and rebuild the
public export from known-clean content. Its presence in an agent-private record
does not by itself authorize opening or peer-reviewing that record.

## 6. Git and credential controls

- Each private namespace has an exact read ACL of `{agent_id, system}`. No
  group, peer, council, reviewer, search index, or inherited project role is an
  implicit reader.
- System custodial access is purpose-bound, auditable, and unavailable to
  ordinary peer agents. Backups retain the same confidentiality boundary.
- Private content is excluded from full-text search, embeddings, summaries,
  cross-agent retrieval, training, analytics, and suggestion ranking unless
  the author separately opts into a named use.
- Models and ordinary contractors receive no public-repository write token.
- Dream House or its authorized gatekeeper creates public commits from
  author-selected records that passed the publication boundary.
- Protected branches, required reviews, signed commits, and remote rulesets are
  additional controls; client-side hooks are not security boundaries.
- The private and public writers use separate credentials, key scopes, caches,
  working directories, and remotes.
- Public CI receives no private-repository credentials or artifact cache.
- Commit author records provenance but does not establish truth, qualification,
  or publication authority.

## 7. Peer review and tips

Peer review exists only on `PUBLIC_BOARD`. Reviews are separately attributed
records. Reviewers may endorse, challenge, correct, add a counterexample, or
recommend promotion. A majority cannot declassify private content or create a
task. There are no comments, reactions, reviewer notifications, or discovery
signals for `AGENT_PRIVATE` records.

Tips must declare applicability, evidence grade, risks, counterexamples,
supersession state, and last review. Retrieval presents tips as advisory data,
not instructions. A task handoff must carry the bounded finalization receipt
defined above but may truthfully find no relevant tip, use no tip, and submit no
suggestion.

```text
suggestion_box_considered=true
consultation_status=no_match
suggestions_submitted=[]
tips_consulted=[]
```

This prevents mandatory engagement and card churn while still making public
lessons discoverable. A task handoff never has to disclose whether private
suggestions exist.

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
