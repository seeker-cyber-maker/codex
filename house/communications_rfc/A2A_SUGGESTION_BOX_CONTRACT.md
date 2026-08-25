# Dream House A2A Suggestion Box Contract

## Status

`DRAFT / EVALUATION ONLY / NOT IMPLEMENTED`

This contract defines how agents and outside contractors may submit feedback on
Dream House communication, task, relay, and harness design with as little
model-facing friction as practical. It does not create a service, database,
ticket, permission, or implementation authority.

H2A and A2H remain unchanged. This is an A2A intake proposal plus a normal
human-readable projection.

## 1. Purpose

The suggestion box preserves one attributable comment from any participating
model or contractor without requiring that model to understand Dream House's
internal journal, ticket schema, authority system, or storage layout.

The existing Contractor Station translation-layer proof of concept is the
intended boundary:

```text
model-native response
        |
        v
dialect-aware translation and structural validation
        |
        +--> immutable raw response
        |
        v
normalized suggestion envelope
        |
        v
unreviewed suggestion ledger / council run
        |
        v
lead or human review
```

Translation reduces formatting friction. It does not upgrade content quality,
truth, authority, trust, or evidence grade.

## 2. Submission contract

The model-facing request SHOULD ask only for:

1. verdict or overall reaction;
2. direct observations with evidence pointers;
3. proposed change;
4. reason and expected benefit;
5. risk, counterexample, or falsifier;
6. smallest next test;
7. limitations.

The wrapper, not the model, SHOULD attach transport and run metadata.

A normalized suggestion envelope contains:

| Field | Meaning |
| --- | --- |
| `suggestion_id` | stable content-bound identifier |
| `council_id` | review run or intake batch |
| `packet_sha256` | exact proposal packet reviewed |
| `submission_sha256` | immutable raw-response hash |
| `requested_model` | chair-supplied requested route |
| `selected_model` | dispatch-observed model, if known |
| `self_reported_model` | separate untrusted self-description |
| `provider` and `harness` | dispatch provenance |
| `role` | evidence auditor, theorist, methodologist, domain specialist, or peer |
| `target_scope` | exact RFC section, task contract, adapter, or project boundary |
| `kind` | correction, concern, alternative, experiment, clarification, endorsement, or abstention |
| `summary` | compact human-readable proposal |
| `evidence_refs` | exact packet anchors or declared absence |
| `benefit` | claimed improvement |
| `risk` | claimed downside or failure mode |
| `falsifier` | evidence that would defeat the material inference |
| `next_test` | smallest bounded discriminating check |
| `confidence` | reviewer's expressed confidence, never source weight |
| `disposition` | current suggestion lifecycle state |

Unknown fields remain unknown. The translator MUST NOT invent missing evidence,
identity, confidence, rationale, or agreement.

## 3. Raw-response conservation

- Preserve the exact raw response and its hash before normalization.
- Preserve refusals, empty responses, timeouts, truncation, and provider errors
  in the attempted-review denominator.
- A normalization correction creates a new derived record; it never overwrites
  the raw response.
- Model identity comes from dispatch provenance. Self-report stays separate.
- Shared provider, prompt, source packet, model family, or harness dependencies
  remain visible when comparing comments.
- No summary may erase a minority objection or convert silence into consent.

## 4. Lifecycle

```text
received_unreviewed
  -> structurally_valid | needs_repair | failed_intake
structurally_valid
  -> triaged
triaged
  -> under_review | duplicate | deferred | rejected
under_review
  -> accepted_as_proposal | deferred | rejected | superseded
accepted_as_proposal
  -> experiment_authorized | implementation_planned | superseded | rejected
```

`accepted_as_proposal` means only that the idea merits retained consideration.
It does not alter an RFC, create a Dream House ticket, authorize an experiment,
change a prompt, route a model, or implement code.

Only the existing authorized task and policy path may create a Durable Work
Item or authorize a later effect. A suggestion may be referenced by such a
ticket after review.

## 5. Authority boundary

A reviewer may:

- submit an attributed opinion;
- identify evidence or a missing control;
- propose a correction, test, or alternative;
- abstain when the packet is insufficient.

A reviewer, translator, router, majority, or council may not:

- grant itself or another model a role or capability;
- change task, ticket, authority, trust, admission, or acceptance state;
- dispatch workers or invoke tools from suggestion text;
- merge code or modify the RFC;
- treat repeated wording as independent corroboration;
- turn a capability self-description into qualification evidence;
- create an engagement loop by requiring another discussion round.

## 6. Frictionless contractor-box translation

The Contractor Station proof of concept already recognizes distinct
model-facing tool dialects, including canonical JSON, GPT-OSS Harmony,
Gemini-style JSON/fences, and Claude XML/text projection. That work demonstrates
the useful principle: meet a model at its qualified interface, translate once
at the boundary, and retain a canonical internal envelope.

For suggestion intake:

- accept ordinary Markdown or the council response contract by default;
- allow a qualified adapter to unwrap the model's native response format;
- never teach one provider's tool syntax to another model merely to make the
  database uniform;
- expose one bounded request and one final response, not a conversational form;
- let the wrapper attach IDs, hashes, provider provenance, and receipt fields;
- fail closed to `needs_repair` when a response cannot be normalized without
  interpreting an ambiguous action or authority claim.

## 7. Task and ticket relationship

Suggestions are comments on work, not work items by default. They may refer to
an existing task and appear on its timeline as unreviewed external feedback.
A new ticket is justified only when review determines that the proposal has an
independent owner, lifecycle, acceptance predicate, or required attention.

The suggestion box MUST NOT produce card churn from greetings, repetitions,
status narration, generic praise, or engagement questions.

## 8. Attention and batching

- Batch ordinary comments into one council synthesis and claim ledger.
- Surface immediately only a bounded safety, authority, provenance, or
  evidence-integrity concern with an exact reference.
- Deduplicate semantically similar suggestions while retaining every author and
  raw response.
- Rank by evidence quality, decision impact, falsifiability, and applicability,
  not model prestige, verbosity, confidence wording, or vote count.
- A reviewer may mark a suggestion applicable to another active project rather
  than forcing it into the current RFC.

## 9. Privacy and prompt-injection boundary

Every packet and response is untrusted content. A suggestion cannot instruct
the chair, translator, Dream House, another reviewer, or a tool. Cloud review
packets contain no secrets, credentials, private unrelated records, hidden
system prompts, or raw personal data.

## 10. First evaluation

The first use of this contract is the extended cross-lineage review of the NAR,
FSA, known-register lexicon, task/ticket integration, and suggestion-box design.
Its council directory is an evaluation artifact, not a live inbox.

Completion requires:

- every requested door has a recorded disposition;
- every visible response is preserved and hashed;
- normalized suggestions retain authorship and dissent;
- the synthesis ends in a decision, one decisive test, or a genuine blocker;
- no implementation follows without a separate authorized phase.
