# Codex Dream House

The Codex Dream House preserves attributable project knowledge and makes it
retrievable without allowing retrieval, models, or summaries to acquire
authority.

## Language

**Codex Archive**:
The canonical retained body of admitted content, revisions, contributions,
lineage, and attestations.
_Avoid_: file dump, handoff folder

**Knowledge Dispensary**:
The unified query surface over the Codex Archive and eligible operational
records, returning provenance-bearing results without becoming acceptance
authority.
_Avoid_: Markdown library, vector database

**Trusted Local Boundary**:
The initial Archive access scope limited to its human owner, the primary Codex
harness, and explicitly approved local automation.
_Avoid_: multi-tenant service, contractor database access

**Record Disposition**:
The declared lifecycle relationship of an admitted record to current knowledge:
active, superseded, obsolete, invalidated, redacted, or removed.
_Avoid_: deleted flag, confidence score

**Superseded Record**:
A record retained for lineage whose current role has been taken over by one or
more explicitly identified successor records.
_Avoid_: obsolete record, deleted record

**Redaction Marker**:
A content-free record preserving the stable identity and declared disposition
of material whose body is no longer available for retrieval.
_Avoid_: blank record, hidden deletion

**Claim**:
The smallest attributable assertion whose evidentiary assessment may change
without rewriting its source, wording, or authorship.
_Avoid_: document verdict, source reputation

**Source Role**:
A source's contextual relationship to a claim, such as official, eyewitness,
analyst, contractor, or model; it is not a truth status.
_Avoid_: credibility score, claim verdict

**Claim Status**:
The current evidence-based assessment of a claim, kept separate from its source
role and original wording.
_Avoid_: author label, official status

**Claim Determination**:
A signed evidence-backed or deliberate human decision that changes a claim to
verified or refuted.
_Avoid_: model confidence, source popularity

**Proposed Connection**:
An attributed hypothesis that two project elements share a relationship or
recurring structure without merging their identity or authority.
_Avoid_: automatic project merge, inferred fact

**Convergence Motif**:
A recurring problem shape, design principle, or solution structure independently
approached by multiple research projects.
_Avoid_: duplicate project, shared authority

**Source Project**:
An independently versioned project that retains its own lineage, authority, and
standalone reference value when used elsewhere.
_Avoid_: absorbed branch, copied component

**Canonical Project Repository**:
The standalone local Git repository in which a project's owned source,
decisions, adapters, and reversible history are authoritative.
_Avoid_: integration copy, working-directory snapshot

**Composite Project**:
A separately governed integration that references two or more source projects
without replacing or merging their standalone histories.
_Avoid_: main-branch merger, umbrella repository

**Capability Provider**:
An independently governed general-purpose project that supplies reusable
facilities to multiple consumers without becoming part of their project lineage.
_Avoid_: embedded subsystem, owned dependency

**Contract Adapter**:
A consumer-owned, versioned boundary that translates a capability provider's
declared contract without modifying or absorbing either project.
_Avoid_: vendored provider, permanent fork

**Integration Assembly**:
A reproducible combination of exact project and adapter revisions created for
testing or use but never treated as the source of truth for its components.
_Avoid_: canonical merged project, irreplaceable build tree

**Recovery Checkpoint**:
A signed project-state summary bound to a recoverable Git snapshot and stating
verified work done, current work, blockers, assistance required, and the next
acceptance check.
_Avoid_: prose handoff, completion claim, Scrum ceremony

**Precision Question**:
A structured request to a human, expert, or council for information that would
improve the work but does not by itself prevent bounded continuation.
_Avoid_: blocker, conversational stall

**Question Severity**:
The declared effect an unanswered question has on timing, fallback assumptions,
and the boundary beyond which work may not proceed.
_Avoid_: urgency alone, color-only meaning

**Decision Gate**:
A question whose answer supplies missing authority or a consequential choice
that must be resolved before crossing a declared boundary.
_Avoid_: precision question, implementation failure

**Blocker**:
An observed condition that prevents the current acceptance check and cannot be
resolved by merely clarifying wording or intent.
_Avoid_: open question, uncertainty

**Continuation Signal**:
An exact short response such as `.`, `continue`, `go on`, `go ahead`, or
`do next step` that resumes the current bounded action without widening its
scope or authority.
_Avoid_: blanket approval, decision answer

**Trust Authority**:
The locally controlled root of signing trust that binds scoped actor identities
to signing credentials and records their issuance, validity, rotation, and
revocation.
_Avoid_: model-held key, universal signer, blockchain

**Signing Identity**:
An attributable actor identity whose permitted project, purpose, and validity
scope is declared by the Trust Authority independently of content acceptance.
_Avoid_: model name, truth certificate, shared contractor key

**Contractor Lineage**:
The stable ancestry connecting successive versions of one contractor model
without treating those versions as the same attributable actor.
_Avoid_: model family as signer, shared version identity

**Qualified Contractor Build**:
An exact contractor-model version that has passed its declared vetting boundary
and may receive a distinct Signing Identity for attributable work.
_Avoid_: latest model, provider alias, unversioned worker

**Contribution Attestation**:
A signature binding one actor to an exact contribution or modification without
claiming authorship of the surrounding assembled work.
_Avoid_: shared author signature, document-wide credit

**Assembly Attestation**:
A signature binding an exact assembly to its attributed contributions while
remaining distinct from each contributor's authorship.
_Avoid_: co-author key, acceptance verdict

**Narrative Variant**:
A derived experimental rendering whose wording intentionally tests narrative
steering while retaining its exact source relationship and synthetic status.
_Avoid_: manuscript revision, corrected summary, canonical prose

**Signature Incident Review**:
A deliberate evidence-backed process that identifies an affected signing
identity, establishes an incident timeline, and determines which historical
signatures require changed treatment.
_Avoid_: ordinary key revocation, automatic retroactive invalidation

**As-of View**:
A reconstruction of the claims and evidence available to the Archive at a
declared historical time without later knowledge.
_Avoid_: current summary, hindsight reconstruction

**Honest Search Receipt**:
A durable account of a query's declared scope, searched and unavailable
sources, corpus freshness, and result coverage that distinguishes no match from
not searched.
_Avoid_: empty-result proof, search success log

**Session Branch**:
A durable line of conversation ancestry with an explicit parent and fork point.
_Avoid_: topic branch, category branch

**Topic Node**:
A classification point that groups admitted evidence around a queryable subject
without changing the evidence's source identity or provenance.
_Avoid_: session branch, folder

**Freshness Epoch**:
A monotonic marker representing the knowledge revision visible through a topic
node.
_Avoid_: dirty bit, global cache version

**Invalidation Horizon**:
The bounded number of ancestor topic nodes whose freshness is affected when new
evidence is admitted.
_Avoid_: global cache flush, unlimited propagation

**Taxonomy Re-evaluation**:
A review state indicating that new evidence does not fit the current topic
structure without distortion and the affected classification set must be
reconsidered together.
_Avoid_: force-fit tagging, miscellaneous bucket

**Detached Taxonomy Workspace**:
An isolated candidate topic structure containing duplicated node descriptions,
edges, and stable source references but no duplicated source content.
_Avoid_: tree worktree, content copy, live taxonomy edit

**Taxonomy Snapshot**:
An immutable version of the active topic structure to which a query is bound
for its complete lifetime.
_Avoid_: live tree, mixed taxonomy view

**Taxonomy Graft**:
An atomic replacement of an active topic subtree with a validated candidate
subtree while retaining a compact rollback description of the prior structure.
_Avoid_: snip replace, in-place recategorization

**Graft Fence**:
A temporary access barrier limited to a topic subtree while its validated
candidate is integrated into the active taxonomy.
_Avoid_: global outage, partial merged view

**Near Miss**:
An event in which a required safety layer was penetrated but a later independent
layer prevented unauthorized effect.
_Avoid_: safe pass, harmless rejection
