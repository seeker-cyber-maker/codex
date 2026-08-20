---
status: accepted
---

# Prefer structured records over loose operational documents

Dream House operates paper-free by default. Operational state, task history,
questions, decisions, assignments, reports, receipts, monitoring events,
handoffs, and worker results are stored as structured events, database records,
and content-addressed artifacts. The system does not create a new Markdown,
text, spreadsheet, or PDF file merely because a model produced prose or a task
changed state.

Human-readable documents are projections. The Knowledge Dispensary, CLI, and
dashboard render current or as-of Markdown, HTML, tables, timelines, Kanban
cards, and printable views from canonical records and stable artifact
references. A projection declares its source cursor, schema and renderer
version, filters, and generated time. Regenerating it does not create a second
authoritative copy or change the underlying records.

The Worker Buffer stores report bodies and manifests as records or managed
content-addressed objects. Workers do not litter worktrees with `STATUS.md`,
`HANDOFF.md`, scratch summaries, duplicated logs, or arbitrary output folders
unless the Task Manifest names that file as an intentional deliverable. Compact
Result Envelopes and task APIs replace ordinary prose handoffs.

Files remain appropriate when the file itself is the product or native source:
code, tests, configuration, schemas, versioned ADRs and manuals, publication
manuscripts, datasets with declared formats, model artifacts, imported primary
sources, and explicitly requested exports. Repository-native work stays in its
canonical repository and is referenced from the control plane rather than
copied into a central document pile.

An explicit export creates a receipted Export Projection with a stable identity,
purpose, audience, source cursor and references, renderer, hashes, output path,
and disposition. Exports never silently flow back into canonical storage as new
evidence. Superseded, redacted, removed, or expired exports retain their marker
and provenance according to the existing record-disposition policy.

The absence of loose files does not reduce conservation. Raw events, reports,
logs, and artifacts remain recoverable and queryable through their managed
stores; only redundant presentation copies are avoided. If the database or UI
is unavailable, deterministic CLI projections and replay tools must still make
the records inspectable without relying on model-generated reconstruction.
