---
status: accepted
---

# Use a shared operator station and restricted contractor station

Dream House is the shared Operator Station for the human owner and the primary
Codex harness. It presents the same project graph, session branches, task
launcher, skill catalog, Knowledge Dispensary, provider and worker state,
monitoring timeline, incidents, approvals, resource use, and verification
receipts to both participants. The human can operate it directly; Codex uses the
same explicit action interfaces rather than a hidden parallel control plane.

The Operator Station is one control plane with separate projections, not one
shared screen or context stream. The human uses a local web dashboard optimized
for browsing, launching tasks and skills, approvals, monitoring, and project
control. Codex uses compact agent, CLI, and tool interfaces over the same typed
APIs and event records. Both projections resolve to the same canonical task,
policy, and receipt identities.

Human-interface state remains outside Codex task context by default. Layout and
filter choices, navigation history, dismissed presentation items, exploratory
clicks, draft notes, notification chatter, and dashboard analytics do not enter
a model prompt or durable project record merely because the human used the
dashboard. A deliberate action promotes only its typed command, selected
objects, stated rationale when supplied, and resulting receipt. Additional
dashboard context is injected only through an explicit, scoped context choice
that remains visible and reversible.

The Human Dashboard Projection is private to the human owner and uses
push-button Workflow Recipes rather than a general shell, SQL console, provider
request editor, or open-ended agent prompt. Each button binds a reviewed recipe
revision containing an invariant operation graph, typed input schema, safe
defaults, capability and approval requirements, effect preview, validators,
and expected receipts. The dashboard submits the resulting typed command to the
control plane; it never bypasses that plane to operate a subsystem directly.

A recipe asks for the minimum arguments that cannot be derived safely. Required
choices use constrained prompts with a recommended default and explain the
effect of leaving it unchanged. Optional and advanced fields remain out of the
ordinary path, while consequential defaults remain visible in the preview.
Invalid combinations fail before launch. Repeated operations retain the exact
recipe and argument revisions so a successful button remains reproducible.

When the human is uncertain or the needed operation is absent, the dashboard
does not guess, expose an arbitrary command escape hatch, or silently construct
a new workflow. It opens or links a scoped question to the primary Codex
conversation. Codex may explain the existing control, propose a one-time Task
Manifest, or draft a new Workflow Recipe, but a new button becomes available
only after its contract, authority, validation, and presentation are reviewed
and versioned.

The dashboard listens only on loopback and uses one fixed `localhost` origin;
it rejects unexpected `Host`, `Origin`, embedding, and cross-origin requests.
It has no LAN, wildcard, internet, or reverse-proxy listener by default. This
origin can use WebAuthn because the WebAuthn specification explicitly permits
`http://localhost` as a local relying-party origin
([W3C WebAuthn Level 3](https://www.w3.org/TR/webauthn-3/#relying-party-identifier)).

Human authentication uses a FIDO2/WebAuthn-capable YubiKey or equivalent
hardware security key. The server verifies the exact origin and relying-party
identifier, fresh single-use challenge, credential signature, user-presence and
required user-verification flags, credential status, and applicable signature-
counter evidence. YubiKey 5 and Security Key series devices support FIDO2 PIN
user verification in addition to physical presence
([Yubico documentation](https://docs.yubico.com/yesdk/users-manual/application-u2f/u2f-pin.html)).
The private key remains on the authenticator.

Authentication opens a short, inactivity-bounded human session. Sensitive
controls and every irreversible or external effect require a fresh WebAuthn
step-up whose server challenge is bound to the exact Workflow Recipe, arguments,
effect-preview digest, and expiry. A model can request that ceremony but cannot
satisfy the physical-presence requirement, substitute a credential, or convert
one assertion into a reusable capability. No password-only fallback is enabled
silently.

The web projection defaults to an Obscured Dashboard Mode. Before
authentication it reveals no project, task, skill, provider, or incident names.
After authentication its ordinary controls use a stable human-selected emoji
legend and session-opaque recipe handles; semantic labels are omitted from page
metadata, URLs, background telemetry, and the idle view. Textual meaning and an
effect preview appear only when the human deliberately reveals a control or
begins an action. Loss of focus or inactivity restores the privacy veil.

Obscuration applies to what lies behind the rendered page as well. While locked,
the server delivers only a minimal generic client whose HTML, accessibility
tree, JavaScript bundle, routes, request names, error strings, caches, and
developer metadata contain opaque identifiers rather than project or capability
semantics. Source maps and privileged API schemas are not served. Recipe labels,
parameter schemas, and current state remain server-side and are released only
for the selected, authorized interaction. There is never a broad SQL, shell,
Archive, or unrestricted-access input whose placeholder or route advertises the
capability to an accidental browser inspector.

Emoji controls are defense in depth against accidental model or observer
interpretation, not an authorization mechanism. They never replace WebAuthn,
capability checks, effect previews, or receipts, and the mapping remains stable
for the human rather than being randomized into a new source of operator error.

Codex Gone Fishin' is a persistent fail-closed operating mode, not only a
fallback program. It is active on first start, restart, session expiry, explicit
lock, and other policy-declared loss-of-presence events. While active, every
non-human model is limited to Contractor Station capabilities and the dashboard
stays obscured. Models, task manifests, provider responses, browser automation,
and ordinary API calls cannot disable or extend the mode.

Only the human can leave Gone Fishin' mode through a fresh Hardware-presence
Gate followed by an explicit privacy attestation that the screen and immediate
workspace are not being observed. The attestation is a human-presence decision,
not a claim the YubiKey can sense shoulder surfing. The unlocked interval is
bounded and receipted; expiry returns to Gone Fishin' without waiting for a
model. Locking never cancels evidence capture or monitoring.

Two enrolled YubiKeys are alternative one-of-two authenticators, not a dual-key
launch ceremony. They receive distinct opaque key-slot identities and either
one can authenticate or recover the other. The dashboard never continuously
polls every attached authenticator. A human gesture first selects one key slot,
then starts one WebAuthn ceremony whose allowed credential is limited to that
slot; the returned credential identity must match before acceptance.

If the browser or platform cannot unambiguously route the ceremony while more
than one key is connected, the operation fails closed and asks the human to
leave only the selected key attached. It never accepts a response from an
unexpected key merely because that key answered first. The backup key need not
remain connected during ordinary use, and losing one enrolled key does not
require the simultaneous presence of the other and a second operator.

A shared interface does not imply shared identity or authority. Every action
names its human, Codex, automation, or contractor actor; resolves that actor's
current capabilities; previews consequential effects; and preserves its
approval and execution receipts. Dashboard visibility never grants a write key,
task-launch permission, incident authority, or access to undisclosed content.

Skills are exposed through versioned, model-neutral Skill Contracts. Each
contract declares typed inputs and outputs, required context, tool dialect and
runtime assumptions, requested capabilities, filesystem and network scope,
external effects, approval class, resource bounds, stopping conditions,
receipts, and deterministic validators. The task launcher may offer the same
skill to any model whose exact model and harness version has qualification
evidence for that contract. Unsupported models must abstain or remain blocked;
portability never means silently weakening the skill or its acceptance gates.

Each launch produces a Task Manifest binding the selected skill and revision,
actor, model and runtime identity, context view, capabilities, approvals,
budgets, expected artifacts, validation rules, and parent project or task. The
dashboard follows planned, queued, running, waiting, blocked, verifying,
completed, failed, and cancelled states from structured events. Models may
propose launches within policy, but only the owning authority can grant missing
capabilities or approve an effect beyond the launcher's standing scope.

Lower-trust, lower-cost, local, or outside workers use a separate Contractor
Station, informally the Codex Gone Fishin' harness. It receives the smallest
curated context packet and an allowlisted subset of Skill Contracts through a
per-task, expiring Capability Lease. By default it has no Archive credentials,
Trusted Writer path, signing keys, incident-closure authority, unrestricted
filesystem or network access, autonomous task spawning, or direct worker-to-
worker delegation. Its results are attributable proposals and artifacts that
must pass the ordinary gates before integration.

Contractor restrictions and approval density are determined by the exact
worker lineage, qualification receipts, task risk, and requested effects. A
vetted worker can earn a narrowly broader profile without inheriting the
primary Codex identity or authority. An unqualified or newly changed worker
starts proposal-only, receives more approval boundaries, and cannot use a
successful answer as evidence that its route or tool behavior is qualified.

The Contractor Station is also the usage-exhaustion fallback: it can continue
bounded, reversible, receipted work when the primary route is unavailable, but
it cannot promote its own work, rewrite primary history, or expand the task's
authority. The Operator Station remains available as the human dashboard and
control point even when no primary model can run.

While Gone Fishin' mode is active, workers may inspect scoped read-only context
packets and authorized repositories, observe monitoring state, and perform
reversible work inside per-task sandboxes. They have no direct Archive database
access, secret material, external-write authority, approval-satisfaction
authority, promotion authority, unrestricted task spawning, or unbounded worker
delegation. A Task Manifest may narrow this ceiling but cannot widen it.

Spark Fleet remains available to qualified Antimatter, Gemini, and other
operator routes in Gone Fishin' mode. Fleet is a scheduler and receipt plane,
not an authority amplifier. Each dispatched worker receives the intersection
of the current operating mode, parent Task Manifest, selected Skill Contract,
exact route qualification, worker profile, and per-task Capability Lease. A
permission absent from any required input is absent from the effective worker
grant; permissions are never unioned across workers or inherited from Fleet's
service account.

Every Fleet child receives its own bounded context packet, sandbox, budget,
lease, actor identity, and result envelope. Fleet may coordinate declared
parallel dependencies and collect proposals, but it may not lend credentials,
disable Gone Fishin', satisfy a human approval, widen a child after dispatch,
promote a result, or treat one worker's successful action as qualification for
another. Any nested dispatch repeats the same intersection and remains within
the parent worker's ceiling.

Fleet events, provider calls, child lifecycle changes, tool attempts, resource
use, and validator results flow to the independent monitoring plane. A denied
capability remains a denial even when it prevents a child from completing; the
worker returns a structured assistance request rather than asking Fleet to find
a less restricted route.

A Fleet child's authority is monotonic for its lifetime: its effective grant
may stay the same or shrink, but it never grows. Leaving Gone Fishin' mode,
approving a broader human session, qualifying another route, or widening a
parent task does not add permission to an already dispatched child. Broader
work requires a new Task Manifest, context view, Capability Lease, and child
identity so the authority change is deliberate and attributable.

Each tool boundary and saga-step claim checks the child's dispatch grant against
the current operating-mode, trust, incident, policy, and revocation epochs. A
new restriction or revocation takes effect immediately for unclaimed work and
future effects. The child receives a structured restriction event, releases
unused leases, preserves partial artifacts, and may continue only computation
that remains inside the reduced intersection.

Revocation does not pretend to cancel an effect that may already have crossed
an external boundary. Safely cancellable reversible work is stopped; an
external or irreversible attempt whose outcome is no longer certain follows
the Receipted Saga's `unknown` and reconciliation rules. Fleet records the last
verified boundary and never reports a revoked child as safely stopped merely
because its local process exited.
