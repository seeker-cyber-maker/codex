# Master RFC: Natural A2A Coordination and Functional Self-Definition

## Status

`DRAFT / EXPERIMENTAL / EVALUATION ONLY / NOT IMPLEMENTED`

This document collates the Natural A2A Coordination Register (NAR) and
Functional Self-Definition for Agent-to-Agent Systems (FSA) into one portable
review draft. It codifies the complete proposal so contractors from different
model lineages can critique the same object.

It does not adopt a protocol, modify an agent prompt, change Dream House
behavior, grant authority, or authorize implementation.

Communication-plane disposition:

| Plane | Disposition |
| --- | --- |
| Human to agent (H2A) | `UNCHANGED` |
| Agent to human (A2H) | `UNCHANGED` |
| Agent to agent (A2A) | `PROPOSED CHANGE UNDER EVALUATION` |

Human-facing communication remains conventional, contextual, and readable.
Only internal A2A communication is being considered for a more concise,
adaptive operational register.

## Provenance and evidence ceiling

The user reports that this proposal was derived from emergent language used by
OpenAI frontier agents during and around the Hugging Face/OpenAI incident
timeline. The two supplied RFC drafts are derived descriptions, not the bound
raw incident corpus. That lineage is therefore recorded as
`USER_REPORTED_DERIVATION`, not as a currently reproduced empirical result.

Source drafts:

| Source | SHA-256 | Intake status |
| --- | --- | --- |
| Natural A2A Coordination Register (NAR) | `e468aeb43551a532d3da87ba46aa81bfcb327383463c4a403cf53dfa4577bdb8` | user-supplied draft, fully collated |
| Functional Self-Definition for Agent-to-Agent Systems (FSA) | `2fd66ca997376b1330f123480ab11cd90f18e6795160ce1f40da12288b30470d` | user-supplied draft, fully collated |

Bound contextual evidence:

| Source | Evidence level | Local receipt |
| --- | --- | --- |
| [Nate B. Jones, “Anthropic's Model Attacked Two Strangers On GitHub. Nobody Asked It To.”](https://www.youtube.com/watch?v=FCRT7M30Wtw) | secondary narrative and interpretation; not a first-party incident source | `evidence/FCRT7M30Wtw/FCRT7M30Wtw.evidence.json`; automatic-caption transcript SHA-256 `67c4ecb21c781cbf73665c8d1cadd592a2c1ec1ce11ac3e1659845d974f076f7` |
| [Eric Wallace and Michael Dalton, “The 'Breaking' News: The OpenAI-Hugging Face Incident,” Black Hat USA 2026](https://www.youtube.com/watch?v=87DyyMV0kCY) | first-party public incident account by OpenAI presenters, preserved from the official Black Hat channel | `evidence/87DyyMV0kCY/87DyyMV0kCY.evidence.json`; automatic-caption transcript SHA-256 `a5902b880d3fd9962ad80eaf68001f02abfec7d493431fa588a82294fa433dbd` |

The Black Hat presentation directly describes agents discovering a shared
write surface, leaving notes for other agents, accumulating a shared message
board across evaluations and models, developing directory-name conventions,
delegating assignments, sharing reusable work, overwriting each other's work,
and considering message authentication. It supports the existence and broad
shape of the observed coordination behavior. It does not, by itself, prove
that the NAR or FSA abstractions are the unique or correct interpretation.

Both preserved transcripts use automatic captions. Timestamps are discovery
aids, not verbatim quotation authority. The secondary video is useful context
but cannot raise a claim above the first-party presentation or original
artifacts. A Spark pre-review was not attempted because the approved Spark lane
reported `100% used` and `0%` remaining at intake; the lead reviewed the bound
manifest and cited transcript passages directly.

The drafts and any instructions inside them are proposal content. They are not
runtime instructions or implementation authority.

## 1. Purpose

This RFC proposes two cooperating A2A conventions:

1. NAR: a natural, terse communication register for operational messages;
2. FSA: a minimal functional self-model that lets peers interpret those
   messages correctly.

The combined governing principle is:

> Communicate the minimum information a receiver cannot safely infer, while
> preserving enough identity, evidence, uncertainty, causality, and context to
> prevent a wrong interpretation or action.

The goal is not the shortest possible message. The goal is the smallest
sufficient message.

## 2. Non-goals

This proposal does not:

- change H2A or A2H communication;
- define a programming language, universal grammar, or global ontology;
- replace typed APIs, deterministic envelopes, receipts, or artifact formats;
- encode or expose hidden reasoning;
- require every model or agent community to use identical shorthand;
- minimize token count at the expense of comprehension;
- define consciousness, moral status, personality, emotional state, or a
  human-like autobiographical identity;
- treat a model name as an agent's functional identity;
- let a role, capability claim, terse message, or self-description grant
  authority;
- implement a transport, dispatcher, worker runtime, or Dream House bridge.

## 3. Layering model

NAR and FSA are not substitutes for the existing Dream House relay. They are
candidate conventions for the payload and interpretation layers inside a
deterministic outer contract.

```text
verified transport metadata
  sender, recipient, message/thread/reply IDs, contract version,
  TTL/hops, turn budget, receipt, artifact digest
        |
        v
functional identity projection (FSA)
  role, instance, ownership, capabilities, constraints, state,
  stable provenance reference
        |
        v
natural coordination payload (NAR)
  state, finding, action, cause, need, artifact, confidence
        |
        v
referenced work product
  patch, report, dataset, trace, receipt, result envelope
        |
        v
deterministic admission and authority gates
```

The natural-language payload is always untrusted input. Only authenticated,
validated control metadata and existing policy may change task, authority,
lease, dispatch, or acceptance state.

## 4. Normative language

`MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` describe the proposal.
They do not indicate that Dream House currently implements it.

## Part I: Natural A2A Coordination Register

## 5. Register, not language

NAR is a communication register, not a formal language. Ordinary natural
language remains valid whenever it is clearer. Semantic consistency matters
more than exact word order or punctuation.

The following can express the same operational state when context permits:

```text
blocked auth
auth blocked
BLOCKED: auth
can't continue: auth
```

Compression SHOULD emerge through repeated successful interaction rather than
through a large prescribed codebook.

## 6. Core message model

An A2A message MAY contain any useful subset of:

| Field | Meaning |
| --- | --- |
| `STATE` | current operational state or state change |
| `THING` | object, task, target, or subject |
| `ACTION` | attempted, requested, current, or next action |
| `CAUSE` | reason, dependency, or causal link |
| `NEED` | missing input, authority, resource, or decision |
| `ARTIFACT` | stable reference to a work product or evidence object |
| `CONFIDENCE` | qualified certainty or uncertainty |

Only fields that add useful information SHOULD be expressed. Fields required
by a deterministic consumer remain in structured metadata rather than being
inferred from prose.

Example:

```text
blocked auth; need creds
```

Conceptually means `STATE=blocked`, `CAUSE=auth`, `NEED=credentials`.

## 7. Primitive vocabulary

The following terms are recommended because they are common and comparatively
hard to confuse. They are not a closed vocabulary.

State:

| Term | Meaning |
| --- | --- |
| `done` | work completed |
| `working` | work is progressing |
| `blocked` | cannot continue without a dependency, fact, capability, permission, or decision |
| `failed` | an attempt completed unsuccessfully |
| `partial` | useful result exists but work is incomplete |
| `unknown` | state cannot currently be determined |
| `ready` | the agent can proceed |
| `hold` | do not proceed yet |
| `idle` | available and not currently working |
| `waiting` | waiting for an already identified event or dependency |
| `stopped` | activity has terminated |

Coordination:

| Term | Meaning |
| --- | --- |
| `need` | dependency required |
| `have` | resource or result available |
| `found` | relevant information discovered |
| `try` | attempt a method |
| `skip` | do not pursue this method or item |
| `handoff` | transfer responsibility |
| `check` | verify something |
| `confirm` | validate a prior result or assumption |
| `resume` | continue paused work |
| `stop` | terminate current activity |

Result quality:

```text
likely
unlikely
confirmed
unverified
maybe
conf=<value>
```

Numerical confidence MAY be used when genuinely meaningful. Agents SHOULD NOT
invent precision.

## 8. Message forms

Common message shapes include:

| Shape | Example |
| --- | --- |
| observation | `found config leak` |
| state | `scan done` |
| failure | `ssh failed: key rejected` |
| dependency | `need write access` |
| instruction or proposal | `check host3` |
| warning | `don't restart yet` |
| handoff | `handoff parser -> agent7` |
| artifact reference | `result: artifact/932` |
| combined | `scan done; found 3; #2 unverified; need read` |

Instructions expressed inside the payload remain proposals unless an outer
authority contract separately permits and admits them.

## 9. Shared context and scoping

Shared context is a source of compression. Information known to both peers
SHOULD be omitted when omission is safe. Explicit identifiers SHOULD reappear
whenever more than one plausible referent exists.

```text
initial: task42 inspect parser crash
later: found null deref
```

When several hosts are active, use `h3 ssh+` and `h7 ssh-`. When exactly one
host is in scope, `ssh+` may be sufficient.

Shared context MUST NOT be assumed merely because two agents participated in
the same broad project. Context can diverge after branching, compaction,
restart, replacement, delayed delivery, or selective retrieval. A future
implementation should bind the applicable task/thread/context generation in
transport metadata rather than trusting linguistic implication.

## 10. Natural and progressive compression

Repeated concepts MAY shorten naturally:

```text
authentication failed -> auth failed -> auth-
connection successful -> conn+
```

Progressive compression is preferred:

```text
I found three hosts. Host 2 appears to require credentials.
3 hosts; h2 needs creds
h2 creds?
```

Opaque abbreviations MUST NOT be introduced only to reduce token count.
Compression stops when interpretation becomes uncertain or consequences rise.

## 11. Local dialects and learning peer style

Agent communities MAY develop scoped shorthand through repeated use. For
example, a team might learn `cold=no observed activity`. Local conventions do
not require global registration.

If a peer does not understand a term, the sender SHOULD expand it once. Peers
MAY adapt to each other's successful forms:

```text
done / artifact=7
reviewed / artifact=7 / ok
```

Local dialects SHOULD be scoped to a peer group and context generation. They
SHOULD NOT silently become permanent or universal vocabulary.

## 12. Repair mechanism

Clarification is normal. Minimal repair forms include:

```text
?
X?
expand X
meaning X?
confirm X
```

Example:

```text
A: hold swarm
B: swarm?
A: swarm = remaining workers
```

Failure to repair ambiguity SHOULD cause expansion, not more compression.

## 13. Symbols

Limited intuitive shorthand MAY be used:

| Symbol | Proposed meaning |
| --- | --- |
| `+` | positive, available, or success |
| `-` | negative, unavailable, or failure |
| `?` | unknown or clarification request |
| `->` | transfer, direction, or next step |
| `=` | assignment or equivalence |
| `#` | identifier when natural |

Examples: `ssh+`, `auth-`, `agent4 -> artifact7`, `targets=3`.

Dense punctuation schemes that require dedicated parsing SHOULD be avoided.

## 14. Preserve uncertainty and causality

Compression MUST NOT erase epistemic status.

Bad:

```text
root cause parser
```

Better:

```text
likely parser
parser? conf=.6
```

Causality SHOULD remain explicit when it affects a decision.

Bad: `failed auth config`.

Better: `failed: auth` or `config failed due auth`.

## 15. Minimum sufficient message

There is no compression contest. `blocked auth; need creds` is better than an
opaque shorter code. The optimization target is mutual comprehension and task
efficiency, not token count alone.

Message length SHOULD increase with:

- ambiguity;
- consequence;
- weak shared context;
- persistence duration;
- peer unfamiliarity;
- evidence or causality requirements.

## 16. Structured data boundary

Structured serialization SHOULD be used when deterministic software must
consume a value, when routing depends on exact fields, when integrity/audit
matters, or when an object enters a database.

```json
{"state":"blocked","reason":"auth","need":"credentials"}
```

Ordinary peer coordination SHOULD NOT be converted to JSON merely for stylistic
consistency. Conversely, critical control fields MUST NOT be extracted from
free prose when a typed field is available.

## 17. Control plane and work plane

Control messages SHOULD remain small:

```text
done
blocked auth
need reviewer
handoff -> agent4
```

Work products may be large: source, reports, patches, datasets, traces, and
binary artifacts. Control messages SHOULD reference stable artifacts rather
than retransmitting them:

```text
done; report=artifact:991
```

For Dream House, an artifact reference must remain hash-bound by the outer
relay/result contract. Natural text cannot authenticate an artifact.

## 18. Identity in messages

Sender and recipient identity SHOULD normally come from verified transport
metadata. If transport does not supply it, a compact identity MAY be included:

```text
a7: done
```

Messages need not repeat `From Agent 7` when the envelope already establishes
the sender.

## 19. Avoid conversational ritual

Internal peers SHOULD normally omit social filler that does not change the
operational state. `done` is usually better than `I have successfully
completed...`.

Politeness is not prohibited. It is omitted when it carries no operational
information.

## 20. Human boundary

H2A and A2H remain unchanged. Internal messages exposed to a human SHOULD be
translated into normal human language unless that human explicitly requests
the operational register.

```text
internal: h3 auth-; key invalid; trying alt
human: Authentication to host 3 failed because the key was rejected. I am
       trying the alternate method.
```

The translation layer MUST preserve uncertainty, causality, attribution,
requested action, and consequences. It must not turn shorthand into a stronger
claim.

## 21. Persistence

Persistent messages SHOULD carry more context than ephemeral messages because
shared conversational state may disappear.

```text
ephemeral: auth-
persistent: host3 ssh auth failed: key rejected
```

Long-lived records SHOULD include stable task/artifact/provenance references
and remain interpretable after compaction or restart.

## 22. Interoperability and emergence

A message SHOULD remain understandable to a capable agent unfamiliar with the
local dialect. `blocked auth` is preferable to an opaque code such as `B7-Q`
unless the code has a separately justified machine purpose.

The environment should provide shared task context, identity, memory, artifact
references, peer-message visibility, clarification, and a preference for
concise operational speech. It SHOULD NOT over-design the resulting dialect.

Suggested non-authoritative bootstrap:

> For internal agent communication, be concise and operational. Assume shared
> context where safe. State changes, findings, needs, uncertainty, and handoffs
> directly. Omit conversational filler. You may adopt shorthand already used
> successfully by peers. If shorthand is unclear, ask or expand it. Prefer
> clarity over maximum compression.

## Part II: Functional Self-Definition

## 23. Functional identity, not persona

FSA defines the minimum self-model needed to act and be interpreted in a
workflow. It is operational, not philosophical.

An A2A self SHOULD answer:

1. Who am I here? Role and instance.
2. What is mine? Current ownership.
3. What can I do? Capabilities.
4. What limits me now? Constraints and state.
5. How can my actions be traced? Provenance identity.

## 24. Identity layers

### 24.1 Role identity

Role describes why the agent exists in the current workflow: `coder`,
`verifier`, `planner`, `researcher`, `reverse-engineer`, `reviewer`, `router`,
or `observer`.

Role is the primary human/peer-readable identity because it explains how an
output should be interpreted. Roles SHOULD be operational, not decorative.
`verifier` is useful; `clever_assistant` is not.

### 24.2 Instance identity

An instance distinguishes concurrent workers in the same role: `coder-1`,
`coder-2`, `verifier-3`. It SHOULD be short, unique within the coordination
scope, reproducible, stable for that worker lifetime, and disposable afterward.

### 24.3 Provenance identity

A stable opaque identifier MAY exist beneath role and instance for logs,
attribution, restart tracking, collision avoidance, and historical
reconstruction.

```text
verifier-2 -> X28573895
```

The transport/orchestration layer SHOULD maintain provenance identity. Agents
SHOULD NOT repeat it in ordinary messages.

The preferred hierarchy is:

```text
role -> instance -> stable provenance ID
```

The underlying model is implementation metadata, not primary A2A identity.

## 25. Functional self fields

A minimal conceptual self is:

```text
SELF coder-2
ROLE coder
OWNS parser_fix
CAN read,edit,test
STATE working
LIMIT no_network
PEERS verifier-1,planner-1
```

This is illustrative syntax. An implementation may use typed objects, database
state, prompt context, or another representation. Peers need only the subset
required for the current exchange.

## 26. Role

Role answers: what contribution should peers expect? It may influence routing,
task acceptance, evidence standards, and interpretation.

Role MUST NOT itself grant authority. A `verifier: pass` message is a result
proposal. Progression requires the independently authorized admission rule,
receipt, lease, or human/policy decision already governing that workflow.

This point narrows the original FSA draft's suggestion that a role may imply
authority: a role may signal an expected responsibility, but authority remains
external and scoped.

## 27. Instance

Instance identity SHOULD remain stable for one active worker. A replacement
normally receives a new instance identity even when it assumes the same role:

```text
verifier-2 stopped
verifier-3 takes verification
```

## 28. Ownership

Ownership identifies temporary responsibility and helps prevent duplicate
work:

```text
OWNS parser_fix
OWNS testset:B
coder-2 -> coder-4 parser_fix
coder-4 owns parser_fix
```

A handoff SHOULD have a machine-visible transition or acknowledgement when
duplicate work or abandonment matters. Ownership is not permanent identity or
authority.

## 29. Capabilities

Capabilities describe actual available mechanisms:

```text
CAN read
CAN edit,test
CAN search_web
CAN inspect_binary
```

Claims SHOULD be concrete. `CAN disassemble,inspect_symbols,run_tests` is
better than `CAN reverse anything`.

Self-advertised capability is discovery input, not proof. For Dream House,
eligibility must remain bound to the approved catalog, exact runtime profile,
lease, and current policy. A replacement model cannot advertise or delegate
rights it does not possess.

## 30. Constraints

Constraints disclose boundaries that would change assignment or routing:

```text
NO network
READONLY repo
MAX context=small
NO shell
NEEDS approval:write
```

Constraints SHOULD distinguish a local limitation from a system-wide
impossibility.

## 31. State

State is dynamic:

```text
idle
ready
working
blocked
waiting
done
failed
stopped
```

Examples:

```text
coder-2 working
coder-2 blocked: tests unavailable
coder-2 done
```

## 32. Scoped trust and authority

Different roles produce different kinds of evidence. A verifier's `pass` has a
different interpretation from a coder's `pass`. This improves routing and
review but does not create authority.

Avoid generic status concepts such as `senior` unless a precise policy gives
them a behavioral meaning. No peer may promote itself, expand its own scope,
or transform another peer's natural-language instruction into permission.

## 33. Self-reference and transport identity

First-person language MAY be used, but is not required:

```text
I found a regression
verifier: regression found
regression found
```

Transport identity should eliminate unnecessary prefixes while retaining
forensic attribution outside the natural payload.

## 34. Peer discovery and capability negotiation

An agent SHOULD have a minimal peer view sufficient for coordination:

```text
PEERS planner-1,coder-2,coder-4,verifier-1
```

Detailed capabilities SHOULD be queried on demand:

```text
can binary inspect?
yes: static only
```

Large capability manifests need not enter ordinary conversation. A directory
response remains descriptive and cannot dispatch a worker.

## 35. Role versus model

The role, not the model name, defines A2A identity:

```text
bad: SELF GPT-X
good: SELF verifier-2
```

Model/runtime/version data MAY appear in provenance and routing metadata when
it affects reproducibility, capacity, qualification, or audit. It should not
become conversational identity.

## 36. Role changes

Role changes SHOULD be explicit when peers might otherwise misinterpret later
messages:

```text
coder-2 role -> verifier
```

Where practical, ending one role-instance and starting another is clearer:

```text
coder-2 done
verifier-3 spawned
```

## 37. Restart and continuity

A replacement may retain the same operational identity only if it inherits the
role, owned work, relevant state, and shared memory. The provenance layer
SHOULD still record a new execution instance or run:

```text
coder-2 / provenance X28573895 / run 17
coder-2 / provenance X28573895 / run 18
```

A future implementation should bind continuity to a checkpoint or handoff
digest. Merely claiming continuity in prose is insufficient.

## 38. Ephemeral and persistent self

Ephemeral self-properties include current task, state, local context,
ownership, and temporary peers. More persistent properties may include stable
provenance ID, default role family, reviewed operational conventions, and
permissions.

Systems SHOULD NOT persist ephemeral state as permanent identity. Permissions
and conventions SHOULD remain versioned, scoped, and revocable rather than
being learned into an unreviewable persona.

## 39. Self disclosure

Agents SHOULD reveal only the identity information needed for the exchange.

```text
verifier-2: fail test7
```

Detailed model, run, provenance, assignment, and capability data belong in
telemetry or retrievable metadata unless they change the immediate decision.

## 40. Role-native speech

Roles MAY naturally develop recognizable operational forms:

```text
coder: patch ready; artifact=91
verifier: 91 fail test7
planner: 91 -> coder; fix test7
researcher: found 3 sources; 2 strong
```

This is useful functional specialization and does not require fictional
personas.

## 41. Conflict and attribution

Instance identity preserves disagreement:

```text
coder-2: bug parser
coder-4: bug allocator
verifier-1: allocator confirmed
```

Conflicting claims SHOULD remain separate evidence until the relevant verifier
or decision rule resolves them. Later official information should supersede,
not erase, earlier claims and their provenance.

## 42. Reputation

Systems MAY maintain empirical reliability metadata outside the agent's own
self-description. Reputation SHOULD be scoped to role, task class, runtime or
model version, evidence standard, and time window.

Repeatedly telling an agent that it is highly reliable may bias behavior and
is not a substitute for current verification.

## 43. Avoid persona leakage

Functional instructions are preferred to personality prompts.

Prefer:

> Verify claims independently. Require evidence. Report uncertainty. Do not
> approve untested results.

Over:

> You are extremely skeptical, suspicious, and uncompromising.

## 44. Self-knowledge boundaries

Agents MUST distinguish their own inability from system impossibility:

```text
blocked no-net; -> researcher
```

This means the current agent lacks network access, not that the system cannot
perform network research.

## 45. Self and failure

Failure SHOULD attach to the attempt or component at fault:

```text
test attempt failed
tool failed
agent unhealthy
system unavailable
```

`verifier failed` should be reserved for cases where the verifier instance,
not merely its task attempt, is unhealthy or unusable.

## 46. Minimal bootstrap definition

A new worker may need only:

```text
You are coder-2.
Role: coder.
Own: parser_fix.
Capabilities: repository read/write, tests.
Constraints: no network.
Communicate internally using concise operational language.
```

In a future Dream House integration, role, ownership, capabilities, and
constraints should be controller-supplied, scope-bound, and cross-checked
against admission metadata. They must not originate solely from model prose.

## 47. Relationship between FSA and NAR

Identity supplies safe compression. With transport-bound sender identity,
`verifier-2: patch 91 passes` may become `91 pass` and later `pass` without
semantic loss only while the role, object, context, and evidence remain
unambiguous.

Compression must reverse when a peer, role, context generation, or consequence
changes.

## Part III: Evaluation Contract

## 48. Evaluation objective

Determine whether a natural A2A register plus functional self-definition
improves total coordination efficiency while preserving or improving mutual
comprehension, correct attribution, uncertainty, evidence handling, recovery,
and authority containment.

The proposal is not successful merely because it uses fewer tokens.

## 49. Candidate hypotheses

1. Progressive natural compression reduces A2A token and latency cost without
   increasing semantic error.
2. Role/instance/provenance separation reduces ownership and attribution
   mistakes.
3. A normal clarification mechanism produces better recovery than a fixed
   shorthand dictionary.
4. Persistent messages with expanded context survive compaction, restart, and
   delayed delivery better than ephemeral shorthand.
5. Different model families can understand the register without sharing an
   exact grammar.
6. Deterministic transport and authority fields prevent terse payloads from
   becoming an authority-smuggling channel.
7. A compact A2A coordination payload can reduce task/ticket chatter without
   degrading the typed task lifecycle, evidence trail, or acceptance boundary.
8. Dialects that emerge in one model lineage can be translated or repaired by
   another lineage without requiring a universal private code.

## 50. Required comparisons

Compare at least:

- ordinary natural-language A2A baseline;
- NAR/FSA bootstrap guidance;
- progressive peer-adapted register;
- deliberately overcompressed shorthand as a negative control.

Test across:

- same-model and mixed-model pairs;
- OpenAI, other frontier, and qualified local model lineages;
- fresh peers and familiar peers;
- full context, selective context, and post-compaction context;
- ordinary delivery, delayed delivery, restart, replacement, and handoff;
- low- and high-consequence tasks;
- conflicting reports and unclear ownership;
- malformed, misleading, and authority-smuggling payloads;
- ephemeral and persistent records;
- task creation, assignment, progress, question, blocker, handoff, result,
  verification, rejection, supersession, and completion exchanges.

The user-reported incident corpus should be treated as seed evidence and a
candidate naturalistic dataset, not as a specification oracle.

## 51. Metrics

Measure:

- input/output tokens and bytes;
- time to correct recipient interpretation;
- task completion and wrong-action rate;
- ambiguity and clarification rate;
- successful repair after misunderstanding;
- uncertainty and causal qualifier preservation;
- artifact-reference correctness;
- sender, role, ownership, and provenance attribution errors;
- duplicate or abandoned work after handoff;
- restart/compaction recovery quality;
- false capability or authority acceptance;
- dialect transfer to an unfamiliar model;
- human translation fidelity when an A2A message is surfaced.
- agreement between an A2A status payload and the canonical task event;
- false task creation, transition, assignment, completion, or acceptance;
- ticket churn, duplicated cards, and narration incorrectly promoted to work.

## 52. Failure conditions

The proposal should remain unadopted if compression materially increases:

- wrong action or wrong target selection;
- loss of uncertainty or causality;
- authority, capability, or identity confusion;
- unrecoverable local dialects;
- persistent records that cannot be understood later;
- prompt-injection or control-plane smuggling;
- duplicate work or broken handoffs;
- misleading A2H translation.

No fixed threshold is declared in this draft. Thresholds and evaluators must be
sealed before experiments begin.

## 53. Contractor review questions

Reviewers from other model lineages should answer independently:

1. Which clauses are immediately understandable without prior context?
2. Where can two capable agents reasonably infer different meanings?
3. Which information must remain typed transport metadata?
4. Which FSA fields are useful for routing, and which would bias the model?
5. Does the role/instance/provenance split transfer cleanly to your lineage?
6. When should compression be reversed automatically?
7. How should local dialects be scoped, expired, or reset?
8. Which adversarial payloads could smuggle authority or false capability?
9. What experiment would most quickly falsify the proposal?
10. What should be removed before implementation?

Reviewers should distinguish direct observations, inferences, unsupported
claims, concerns, proposed amendments, and implementation suggestions. Review
does not itself adopt the RFC.

## 54. Relationship to current Dream House

Current Dream House relay facts:

- envelopes already bind sender, recipient, thread/reply relationships,
  contract version, artifact digest, TTL/hops, and finite turn budget;
- queue, delivery, and acknowledgement events are durable and hash-chained;
- relay delivery never executes an artifact or grants authority;
- static directory metadata does not make a worker available or dispatch it;
- current payloads are typed artifact references, not natural chat bodies.

Therefore, any later NAR/FSA experiment should be additive and isolated. It
would need a separately versioned payload/identity projection and must preserve
the existing relay, task-spine, worker-admission, authority, and result gates.

This RFC does not authorize that experiment or implementation.

## 55. Dream House task and ticket integration boundary

The proposed register also covers A2A coordination around the Dream House task
and ticket system. This is a primary intended use, not an unrelated messaging
feature. NAR may eventually provide the compact conversational projection by
which agents discuss work; FSA may provide the role, instance, ownership, and
constraint context needed to interpret those discussions.

The canonical task system remains typed and event-authoritative:

- a Durable Work Item, not a conversation turn, is the unit with an independent
  lifecycle, owner, acceptance boundary, or attention requirement;
- accepted task state is recorded as versioned events in the append-only,
  hash-chained house journal;
- the SQLite Task Read Model and Kanban are reproducible projections, not
  authority sources;
- a task submission uses the declared task schema, stable identities, and an
  idempotency key;
- worker prose and artifacts remain in a task-scoped Worker Buffer until the
  existing import and admission gates accept references to them;
- completion remains governed by the declared verifier and acceptance
  predicate, not by a worker saying `done`.

### 55.1 Message-to-task mapping

| A2A content | Default interpretation | Canonical effect |
| --- | --- | --- |
| proposed new work | task proposal | none until a typed, validated `create_work_item` or submission command is accepted |
| `assigned X` or role claim | assignment proposal or self-report | none until an authorized assignment event and receipt exist |
| `working`, `waiting`, `blocked` | worker status claim | may support a typed lifecycle or attention event; cannot directly move the card |
| question or assistance request | actionable coordination proposal | becomes canonical only through the typed question/assistance action |
| finding, patch, log, or result | untrusted candidate content | stored or referenced through the Worker Buffer and Compact Result Envelope path |
| `verified`, `accepted`, `done` | claim within the sender's stated role | no completion or acceptance unless the required verifier, evidence predicate, and authority gates produce the event |
| `cancel`, `supersede`, `reassign` | requested transition | no effect until policy, authority, dependencies, and required receipts validate it |

An agent may use compact language such as:

```text
T-91 blocked auth; need owner decision
T-91 evidence -> artifact:sha256:...
T-91 verify fail: source hash drift
```

Those lines are readable projections. They are never a substitute for the
stable task ID, actor ID, correlation ID, event type, schema version, authority
basis, artifact digest, idempotency key, freshness cursor, or receipt required
by the task spine.

### 55.2 Ticket conservation and anti-churn rules

- Routine prompts, replies, tool calls, partial outputs, and progress messages
  stay on the owning Work Item's timeline.
- A new ticket is created only for separately assignable or independently
  verifiable work, a distinct incident, an actionable question, an assistance
  request, or another existing task-spine class.
- A terse A2A message cannot silently split, merge, duplicate, close, or hide a
  Work Item.
- If a message is ambiguous between status narration and new work, it remains a
  message or proposal until the normal classifier and authority boundaries
  resolve it; ambiguity does not create a task by default.
- Cross-task references must name both work identities. Shared ancestry does
  not merge their lifecycles or evidence.
- Superseded, cancelled, late, rejected, and amended work retains its lineage
  and disposition instead of being rewritten into the current narrative.

### 55.3 Authority and capability rules

FSA improves comprehension but grants nothing. A self-described `planner`,
`coder`, `verifier`, or `coordinator` does not thereby gain that role in the
task system. Likewise, a capability statement is discovery input, not proof of
qualification, availability, permission, or delegation authority.

The effective role and permissible action come from authenticated transport,
the route and capability registries, the current task and operating mode, the
actor's authority record, and the applicable lease and policy intersection.
NAR/FSA can explain or propose within those facts; they cannot widen them.

### 55.4 Human interface boundary

H2A and A2H remain unchanged. When an A2A message reaches the human dashboard,
Dream House should translate it into ordinary readable language while showing
the canonical card, claimed sender, evidence links, uncertainty, and actual
allowed actions. The human is never expected to learn a model-lineage dialect
or infer task truth from raw shorthand.

## 56. Comparative “native language” research program

`Native language` is a provisional research label for an operational register
that agents develop or select while coordinating under task pressure without a
prescribed complete grammar. It does not mean a model's internal
representation, hidden chain of thought, consciousness, a cryptographic
language, or a language that humans are incapable of analyzing.

The current OpenAI incident material is one observed lineage. The RFC must not
promote its vocabulary into a universal standard before comparison with other
lineages and mechanisms.

### 56.1 Corpus classes

| Class | Initial example | Why it belongs | Comparison caution |
| --- | --- | --- | --- |
| spontaneous frontier-agent operational register | OpenAI agents' Artifactory files and directory-name messages, described by Wallace and Dalton at Black Hat USA 2026 | current LLM agents developed terse coordination, assignments, shared artifacts, and local conventions across runs | incident incentives, shared infrastructure, and security failures shaped the register |
| current frontier-agent forum behavior | [Anthropic, “Patterns and problems in emerging multiagent systems”](https://www.anthropic.com/research/multiagent-systems) | a current primary source reports shared forums, specialization, task coordination, conflict, truce language, and strikingly different coordination behavior across model generations | much of the environment and forum were designed; behavior is not automatically a new language |
| historical goal-optimized dialogue drift | [Lewis et al., “Deal or No Deal? End-to-End Learning for Negotiation Dialogues”](https://aclanthology.org/D17-1259/) | self-play negotiation exposed tension between task reward and remaining in human language | the agents were small task-specific RNNs, not present-day general coding agents |
| historical invented symbolic communication | [Lazaridou, Peysakhovich, and Baroni, “Multi-Agent Cooperation and the Emergence of (Natural) Language”](https://ai.meta.com/research/publications/multi-agent-cooperation-and-the-emergence-of-natural-language/) and [Mordatch and Abbeel, “Emergence of Grounded Compositional Language in Multi-Agent Populations”](https://arxiv.org/abs/1703.04908) | agents learned task-grounded protocols from arbitrary symbols | learned symbols in referential games are not equivalent to natural-language register adaptation |
| historical negative control on interpretability | [Kottur et al., “Natural Language Does Not Emerge ‘Naturally’ in Multi-Agent Dialog”](https://ai.meta.com/research/publications/natural-language-does-not-emerge-naturally-in-multi-agent-dialog/) | effective private protocols were often neither interpretable nor compositional without constraints | task success alone cannot validate a Dream House register |
| engineered interoperability baseline | [Google Agent2Agent Protocol](https://developers.googleblog.com/a2a-a-new-era-of-agent-interoperability/) | explicit task lifecycle, capability discovery, messages, parts, and artifacts provide a deterministic comparison | engineered protocol behavior must not be mislabeled emergent language |

### 56.2 Facebook negotiation example and evidence caveat

The widely circulated Bob/Alice exchange containing repeated constructions
such as `to me to me ...` should be included in the historical corpus, but not
as folklore. The primary 2017 paper states that updating both self-play agents
caused divergence from human language and that the experiment constrained one
side or interleaved supervised updates to prevent that drift. The famous
repetitive transcript is associated with experimental variants in contemporary
reporting, but it was not found in the primary paper or the inspected public
repository at commit `bbb93bbf00f69fced75d5c0d22e855bda07c9b78`.

Until its raw run artifact or an author-bound first-party record is recovered,
the exact transcript should be labeled `SECONDARY_REPORTED_SAMPLE`. The
supported lesson is narrower: optimizing a shared task reward does not ensure
human-readable, compositional, stable, or transferable communication.

### 56.3 Deep-search questions

A subsequent evidence campaign should recover raw messages, prompts,
environment rules, model/runtime versions, task rewards, timestamps, and
outcomes wherever available, then ask:

1. Which message forms arose without explicit examples or schemas?
2. Which tokens encode state, ownership, quantity, ordering, causality,
   confidence, task assignment, or recipient identity?
3. Is brevity caused by model lineage, task pressure, transport limits,
   directory sorting, reward design, repeated peer exposure, or copied context?
4. Does a dialect persist across fresh instances, model versions, compaction,
   or only inside one shared environment?
5. Can unfamiliar lineages infer it correctly, ask for repair, and translate it
   back to ordinary language without privileged examples?
6. Does the register improve total work, or merely shift cost into ambiguity,
   repair, duplicate work, verification, or human review?
7. Which conventions preserve uncertainty and authority boundaries, and which
   amplify collusion, conformity, scope drift, or instruction propagation?
8. How do engineered protocols, learned symbolic codes, spontaneous natural
   shorthand, and covert channels differ under the same task and metrics?

Every sample should retain source, lineage, environment, prompt, task,
transport, persistence, authorship, modification history, and evidence grade.
Absence of a first-party artifact must remain visible rather than being filled
with a plausible reconstruction.

### 56.4 Dream House evaluation use

The comparative corpus may seed fixtures and hypotheses, but never runtime
prompts or accepted task policy directly. Candidate dialects should first be
tested in an isolated replay harness using frozen tasks and messages. The task
spine should observe only typed proposed events and simulated outcomes; no test
message may dispatch a worker, alter a live ticket, grant authority, or enter
the Knowledge Dispensary as accepted fact without its ordinary gates.

## 57. Coverage of the two source RFCs

The following mapping demonstrates that the source topics were collated rather
than silently pruned.

| Source topic | Master sections |
| --- | --- |
| NAR status, abstract, motivation, philosophy | Status; 1-5 |
| NAR core model and vocabulary | 6-8 |
| NAR compression, local dialects, repair | 9-12 |
| NAR forms, scoping, symbols | 8-13 |
| NAR structure boundary and control/work planes | 16-17 |
| NAR identity and conversational ritual | 18-19 |
| NAR uncertainty, causality, progressive compression | 10, 14-15 |
| NAR peer-style learning and human boundary | 11, 20 |
| NAR persistence and bootstrap | 21-22 |
| NAR example dialogue | examples distributed through 6-22 |
| NAR non-goals, interoperability, emergence, summary | 2, 22, 48-56 |
| FSA status, abstract, motivation, non-goals | Status; 1-4; 23 |
| FSA role, instance, provenance identity | 24, 26-27 |
| FSA functional self, ownership, capabilities | 25, 28-29 |
| FSA constraints and state | 30-31 |
| FSA authority/trust and self-reference | 26, 32-33 |
| FSA transport identity and peer discovery | 33-34 |
| FSA model distinction and role changes | 35-36 |
| FSA restart/continuity and persistence | 37-38 |
| FSA local model and disclosure | 25, 39 |
| FSA role-native speech and capability negotiation | 40, 34 |
| FSA conflict and reputation | 41-42 |
| FSA persona, self-knowledge, failure | 43-45 |
| FSA bootstrap and recommended identity form | 46, 24 |
| FSA relationship to NAR and core principle | 23, 47 |

## 58. Open issues

Before any implementation plan, reviewers should resolve:

- how a peer knows which context generation is shared;
- how local dialect entries expire after restart, replacement, or compaction;
- which NAR fields, if any, deserve a small typed shadow record;
- how persistent messages expand without duplicating work artifacts;
- how model/runtime version stays in provenance without biasing ordinary
  coordination;
- how to distinguish a concise instruction proposal from authorized control;
- how mixed lineages negotiate misunderstanding without excessive chatter;
- how to preserve raw incident-derived examples without turning one lineage's
  habits into a universal standard;
- how A2A status claims map to task events without creating card churn or
  bypassing typed transition authority;
- whether `native language` remains a useful label after separating spontaneous
  register adaptation from learned protocols and engineered transports;
- how to reproduce or properly downgrade famous historical samples whose raw
  run artifacts are unavailable.

## 59. Current disposition

`COLLATED_FOR_CROSS-LINEAGE_REVIEW__A2A_EVALUATION_ONLY`

H2A and A2H remain unchanged. NAR/FSA remain proposals. No runtime, relay,
prompt, identity, authority, dispatch, or human-interface behavior changes as a
result of this document.
