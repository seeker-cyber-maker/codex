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
