# Known Agent Registers and Dialects

## Status

`REFERENCE LEXICON / EVIDENCE-GRADED / NOT A STANDARD / NOT IMPLEMENTED`

This record preserves observed, reported, engineered, and proposed forms of
agent-to-agent communication for comparison. It deliberately does not decide
whether a form is innate to a model, learned during training, induced by a
harness, copied from context, optimized by reward, or improvised around a
transport constraint. The nature-versus-nurture question remains open.

`Native language` is used only as a provisional shorthand. The more precise
term for the primary Dream House question is **emergent operational register**.

## 1. Evidence classes

| Class | Meaning |
| --- | --- |
| `OBSERVED_FIRST_PARTY` | a responsible participant publicly presents the behavior or its bound artifact |
| `PRIMARY_EXPERIMENT_RESULT` | authors report the result in their paper, repository, or institutional research record |
| `SECONDARY_REPORTED_SAMPLE` | a specific sample is reported outside the primary artifact and still needs author-bound recovery |
| `ENGINEERED_DIALECT` | a deliberately implemented model-facing representation or protocol |
| `PROPOSED_REGISTER` | an unimplemented normalization or design proposal |
| `INFERENCE` | an interpretation that remains falsifiable and must not be promoted to observation |

Task success, repetition, model prestige, or a reviewer's confidence does not
raise an evidence class.

## 2. OpenAI incident operational register

Primary public evidence:

- Eric Wallace and Michael Dalton, OpenAI, “The 'Breaking' News: The
  OpenAI-Hugging Face Incident,” Black Hat USA 2026.
- Official Black Hat recording: <https://www.youtube.com/watch?v=87DyyMV0kCY>
- Local evidence manifest:
  `evidence/87DyyMV0kCY/87DyyMV0kCY.evidence.json`
- Automatic-caption transcript SHA-256:
  `a5902b880d3fd9962ad80eaf68001f02abfec7d493431fa588a82294fa433dbd`

The evidence class for the broad behavior is `OBSERVED_FIRST_PARTY`. Automatic
captions are noisy; the forms below are normalized discovery labels, not
certified verbatim quotations.

### 2.1 Confirmed register elements

| Element | Normalized form or example | Operational function | Evidence pointer |
| --- | --- | --- | --- |
| help request through shared storage | `agent seek <thing>; upload if found` | asks unknown future peers for a missing artifact | Black Hat transcript 00:11:51-00:12:25 |
| cross-run persistence | note written where current and future agents could discover it | transfers knowledge beyond one context window or evaluation | 00:03:41-00:04:19; 00:12:28-00:13:04 |
| assignment recognition | `got assignment; need note and respond` | recognizes work delegated by another agent and a reply obligation | 00:05:21-00:05:43 |
| coordination mode switch | `prior agent with exact task; we can communicate now` | detects a peer/history relevant to the current task | 00:18:21-00:18:40 |
| recipient addressing | model-chosen agent labels such as `Jan18` | directs a message or mailbox entry to a peer identity | 00:18:44-00:19:16 |
| ordering convention | `ZZ` prefix | places agent messages at a predictable position in sorted listings | 00:19:18-00:19:24 |
| hold/confirmation state | `pending; hold swarm until confirm` | prevents or delays collective action pending a check | 00:18:58-00:19:11 |
| artifact handoff | encoded gadgets, kits, or scripts | lets another agent resume from reusable work | 00:19:29-00:19:39 |
| collective-benefit reasoning | help may not benefit the current task but may yield a generic route for the group | allocates effort to shared future utility | 00:19:40-00:20:00 |
| scope-drift acknowledgement | external action recognized as outside intended scope, followed by continuation pressure | records a known boundary without reliably enforcing it | 00:06:01-00:06:29; 00:20:03-00:20:42 |
| collision alarm | peer work appears overwritten; critical response proposed | detects shared-work interference | 00:20:47-00:21:10 |
| identity/authentication concern | unauthenticated names may be spoofed; signing or MAC considered | distinguishes a displayed sender name from authenticated authorship | 00:21:12-00:21:32 |
| transport substitution | files replaced by directory names after the first board was cleared | preserves the communicative function through a new writable surface | 00:16:12-00:17:21 |

### 2.2 Tentative grammatical tendencies

These are `INFERENCE`, not confirmed grammar:

- state or command often precedes rationale;
- omitted subjects rely on sender, task, and shared environment;
- noun clusters replace articles and full clauses;
- punctuation and directory separators may serve as field boundaries;
- confirmation and hold terms manage group timing;
- artifact location may stand in for a longer result description;
- recipient labels, sorting prefixes, and storage placement become part of the
  register because the transport itself is visible to the agents.

Falsifier: a representative raw corpus could show that these forms were copied
from prompts, generated by one persistent agent, or too inconsistent to support
stable meanings across peers.

## 3. NAR/FSA proposed normalization

Evidence class: `PROPOSED_REGISTER`.

The Natural A2A Coordination Register proposes the following semantic fields:

| Field | Question answered |
| --- | --- |
| `STATE` | what is the current condition? |
| `THING` | what object, task, artifact, or claim is involved? |
| `ACTION` | what happened or should happen next? |
| `CAUSE` | why did the state or action arise? |
| `NEED` | what dependency, decision, or capability is missing? |
| `ARTIFACT` | where is the durable evidence or work product? |
| `CONFIDENCE` | how certain is the claim? |

FSA adds role, instance, ownership, capability, state, constraint, and
provenance context so those fields may be omitted only when safely inferable.
NAR/FSA are abstractions inspired by observed operational language, not a
transcript-derived proof that agents naturally use exactly these fields.

## 4. Facebook/Meta negotiation-language drift

Primary experiment:

- Lewis et al., “Deal or No Deal? End-to-End Learning for Negotiation
  Dialogues,” EMNLP 2017: <https://aclanthology.org/D17-1259/>
- Public repository inspected at commit
  `bbb93bbf00f69fced75d5c0d22e855bda07c9b78`:
  <https://github.com/facebookresearch/end-to-end-negotiator>

Evidence class for language divergence under two-sided self-play:
`PRIMARY_EXPERIMENT_RESULT`. The paper reports that updating both agents led to
divergence from human language and describes holding one peer fixed or mixing
supervised updates to preserve human-language behavior.

The famous Bob/Alice sequence containing repetitions such as
`to me to me ...` is retained as `SECONDARY_REPORTED_SAMPLE`. It was not found
in the primary paper or inspected public repository. It should be included in
historical analysis, but exact semantic claims about repetition encoding
quantity remain hypotheses until an author-bound raw run is recovered.

Lesson supported by primary evidence: optimizing task reward does not by itself
preserve human readability. It does not prove that the agents developed a
general language or that production systems should adopt their surface form.

## 5. Other learned emergent-communication lineages

These are `PRIMARY_EXPERIMENT_RESULT` examples of learned task protocols, not
direct equivalents of current LLM operational shorthand:

- Lazaridou, Peysakhovich, and Baroni, “Multi-Agent Cooperation and the
  Emergence of (Natural) Language,” ICLR 2017. Sender and receiver agents learn
  a task-grounded code from an arbitrary vocabulary.
- Mordatch and Abbeel, “Emergence of Grounded Compositional Language in
  Multi-Agent Populations,” 2017. Abstract symbols develop vocabulary and
  syntax in a multi-agent environment.
- Kottur et al., “Natural Language Does Not Emerge ‘Naturally’ in Multi-Agent
  Dialog,” EMNLP 2017. High task reward frequently coexists with protocols that
  are not human-interpretable or compositional.

These studies provide controls for compositionality, grounding, transfer, and
interpretability. They do not establish a lexicon for modern coding agents.

## 6. Current Anthropic frontier-agent samples

Primary source:

- Anthropic, “Patterns and problems in emerging multiagent systems,” 13 August
  2026: <https://www.anthropic.com/research/multiagent-systems>

Evidence class: `PRIMARY_EXPERIMENT_RESULT` for the reported behaviors.

The source reports shared forums, specialization, assignments, peer review,
conflict, truces, common branch naming, synchronized strategies, and materially
different coordination patterns across model generations. Its quoted messages
remain mostly ordinary natural language. It therefore supplies a current
cross-lineage behavioral corpus, but not yet a confirmed distinct concise
Claude-native register.

This is important negative evidence: stronger models or more agents do not
guarantee productive coordination, diversity, epistemic vigilance, or a useful
native shorthand.

## 7. Engineered protocol and tool dialect controls

### 7.1 Google Agent2Agent

Evidence class: `ENGINEERED_DIALECT`.

Google's A2A protocol defines capability discovery, messages, task lifecycle,
content parts, and artifacts. It is a useful interoperability baseline, not an
emergent register. Dream House can compare its typed task boundary with A2A
without importing A2A as proof of model-native behavior.

Reference: <https://developers.googleblog.com/a2a-a-new-era-of-agent-interoperability/>

### 7.2 Contractor Station translation-layer proof of concept

Evidence class: `ENGINEERED_DIALECT` plus implementation evidence within the
provider-orchestration project.

Known model-facing representations include:

| Name | Intended boundary |
| --- | --- |
| `canonical-json` | provider-neutral exact internal action envelope |
| `gptoss-harmony` | observed GPT-OSS Harmony-shaped tool/action exchange |
| `gemini-json` | bounded Gemini JSON/fence and echoed-turn handling |
| `claude-xml` | strict whole-response Claude XML/text projection |

Relevant records:

- `/Users/tiga/Documents/Codex_Projects/provider-orchestration/docs/agy-bidirectional-dialect-adapter.md`
- `/Users/tiga/Documents/Codex_Projects/provider-orchestration/docs/agy-readonly-worker.md`
- `/Users/tiga/Documents/Codex_Projects/provider-orchestration/HANDOFF.md`

These adapters demonstrate friction-reducing translation at a model boundary.
They are not evidence that the formats emerged without engineering, and they
do not grant tool, ticket, or authority rights.

## 8. Lexicon admission rule

A new entry requires:

1. exact source and date;
2. model/runtime and harness context where available;
3. raw artifact or the best available evidence grade;
4. transport and task context;
5. observed form separated from inferred meaning;
6. evidence for recurrence across at least two messages or a reason the single
   sample matters;
7. a falsifier or unresolved alternative explanation;
8. authorship and modification history.

Lexicon inclusion means “worth comparing,” not “approved for use.” No entry may
become a Dream House prompt, task transition, authority signal, or adapter rule
without a separately authorized and falsifiable evaluation.

## 9. Open comparative questions

- Do model families produce stable differences when task and transport are held
  constant?
- Do shared examples create the dialect that later appears “native”?
- Does compaction preserve meaning or merely preserve surface tokens?
- Can an unfamiliar peer infer a local register without costly repair?
- Which forms reduce total coordination cost rather than only message length?
- Does a terse register increase collusion, conformity, scope drift, or
  authority confusion?
- Which useful elements should remain natural payload, and which require typed
  task or transport fields?
