---
status: accepted
---

# Make Codex ergonomics the first implementation objective

After the architecture specification is sufficiently stable, Dream House's
first implementation objective is to make the primary Codex comfortable and
remove measured friction from the official Codex harness while adding the
missing shared operator features for the human. Provider expansion, local-model
training, and broad contractor autonomy do not displace this objective.

The executable foundation remains the pinned official `openai/codex` CLI and
app-server source. New control-plane, dashboard, context, task, monitoring,
receipt, and Knowledge Dispensary features begin in the downstream `house/`
namespace and communicate through typed upstream seams. An upstream-core change
is admitted only when a downstream adapter cannot meet a measured requirement;
it stays small, independently tested, ledgered, reversible, and suitable for
rebase or upstream contribution.

Friction is captured as evidence rather than inferred from taste. Candidate
gaps include repetitive context reconstruction, lossy compaction, scattered
logs, hidden tool progress, repeated precision questions, manual task and model
routing, fragile command construction, missing continuation state, and unclear
usage or incident visibility. Each implementation slice binds one observed gap,
current baseline, desired interaction, acceptance fixture, upstream merge
surface, rollback, and measured change in interruption, manual steps, latency,
token use, failures, or recovery effort.

The primary Codex agent and the human dashboard use the same canonical events
and commands through separate projections. Human convenience must not inject UI
noise into model context; Codex convenience must not hide state or authority
from the human. A feature is incomplete when it improves one projection by
creating unreceipted work, duplicated state, or new archaeology for the other.

Nimbalyst is a possible donor for backend, routing, or operational ideas, but
its interface is explicitly not the Dream House interaction target. Before any
reuse, pin its exact repository, revision, license, and a narrow capability or
fixture. Reimplement or adapt only the useful seam behind Dream House contracts;
do not import its UI, taxonomy, authority assumptions, or repository wholesale.

The first build slice after specification therefore selects the smallest
high-frequency friction that can be improved without an upstream-core patch,
proves the improvement offline, and records whether the seam remains mergeable.
Later slices may cross into core only with the Patch Ledger evidence required by
the existing upstream-first baseline.
