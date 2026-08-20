---
status: accepted
---

# Prioritize actionable attention in the dashboard

The Human Dashboard Projection opens on an Attention Queue rather than a
project directory, activity feed, or completion report. Its ordering question
is: what requires the human's attention now so safe work can continue? Project,
worker, and chronology remain drill-down facets, not the primary rank.

The dashboard's organizing surface is a receipt-derived Operational Kanban.
Tasks, questions, incidents, assistance requests, and promoted Efficiency
Signals have one canonical card and move through `ready`, `in_progress`,
`waiting`, `blocked`, `needs_attention`, `verifying`, and `done` views according
to structured lifecycle events. Failed, cancelled, superseded, and stale states
remain visible through explicit filters and card history rather than being
folded into `done`.

The Attention Queue is a deterministic projection over those cards, not a
second task list. Notifications link to and emphasize the affected canonical
card. The Primary Action opens that card's decision panel, while compact
successors appear in the `needs_attention` lane and preview strip. Project,
owner, worker, role, and time can form filters or swimlanes without duplicating
the card or changing its underlying state.

Push-button Workflow Recipes live outside the Kanban in a fixed Action Dock.
They launch or control work; they are not task cards, notifications, or draggable
board objects. Pressing a button creates a typed command and receipt, then links
to the created or affected canonical card. The dock remains small, reviewed,
emoji-first, and independent of whichever project or board filter is open.

Items are actionable only when a declared actor can make a decision, supply
missing precision or authority, mitigate an incident, unblock work, or prevent
a deadline or bounded resource consequence. Each actionable card states the
required action, why it is needed, consequence of delay, affected scope,
deadline or expiry, recommended default, fallback continuation, requesting
actor, and evidence or receipt links. It offers the smallest safe push-button
choices, including the ordinary `.` continuation/default action where valid.

The default priority order is:

1. active safety, security, integrity, or irreversible-effect incidents;
2. human-authority gates and blockers that stop otherwise ready work;
3. timed precision questions whose fallback would soon execute or expire;
4. assistance requests requiring the human, an expert, or a council;
5. running work approaching a budget, lease, context, storage, or provider
   boundary;
6. stale tasks, repeated Efficiency Signals, and unresolved ownership gaps;
7. current-work summaries, recent completion, and other informational status.

Within one class, deterministic policy orders by consequence, deadline,
dependency fan-out, age, and stable item identity. A model may summarize or
recommend a rank, but cannot hide an actionable item, lower a deterministic
priority floor, invent urgency, or convert information into a blocker. The
dashboard displays the rule and factors responsible for the rank.

Informational prompts and routine completion notices are grouped into digests
below actionable work. Repetition remains counted and searchable, and an
Attention Budget breach opens the alert-quality investigation defined by the
monitoring policy; reducing annoyance improves routing, grouping, or the source
condition rather than discarding the detector. A newly actionable condition
immediately leaves the digest and enters the appropriate queue class.

Acknowledgement changes presentation, not the underlying task, incident, or
authority state. Snoozing is allowed only when policy permits, records an expiry
and reason, and guarantees deterministic resurfacing before the next
consequence boundary. Completed and superseded items remain available through
project history without occupying the action-first surface.

The home page expands exactly one Primary Action. It contains the complete
decision context and push-button choices while the next small, policy-bounded
set of ranked items appears as compact cards; the initial presentation limit is
four compact successors. The complete queue is one deliberate drill-down away,
with the same ordering receipts and no hidden remainder count.

An actionable critical incident is the Primary Action unless a deterministic
emergency rule requires several incidents to remain co-visible. All active
critical incidents also occupy a pinned incident rail that cannot be scrolled
away, covered by informational content, or removed by changing the project
filter. A pinned item may use an opaque emoji in Obscured Dashboard Mode, but
its severity and need for human attention remain unambiguous.

Resolving, explicitly deferring, or permissibly snoozing the Primary Action
promotes the next eligible item. Merely opening, reading, or navigating away
does not acknowledge it. Stable ordering is preserved until an item state,
deadline, consequence, dependency, or governing rule changes; a model response
alone cannot reshuffle the queue. Every promotion records the prior item and
the deterministic reason the next item became primary.

A human button press or answer records `decision_supplied`; it does not mark the
card `done`. If execution can proceed, the card moves to `in_progress` and then
`verifying` while the outcome remains visible without occupying Primary Action.
Only the declared verifier and completion predicate produce `done`. Execution
failure, verification disagreement, expiry, or a newly required human choice
moves the same card back to `needs_attention` or `blocked` with the new reason;
it never creates a duplicate notification card.

Manual drag is a convenience for proposing an allowed lifecycle transition,
not a direct database edit. The control plane validates the transition against
task state, authority, dependencies, and required receipts. Rejected moves snap
back with an actionable explanation, and no UI gesture can manufacture a
completion, approval, or verified result.
