# Shared corpus lineage

`rubric_fixtures_v1.json` is a frozen, model-neutral projection of the four
cases in the existing instructor smoke manifest:

- Source: `/Users/tiga/Documents/Codex_Projects/storage-inventory/model-classifier/prometheus_instructor_eval.json`
- Source SHA-256 at projection: `3475008c95a5f367bd80f6ec6b8882bceb0ebad6bead48e44bfaa7c2fe320e28`
- Frozen fixture projection SHA-256: `b8e0c058b5d7981b32db10eab608b93f7da97ad829aca73e1672f0eefab44e04`

The source `id` field is renamed only to the neutral `case_id`; instruction,
candidate response, reference answer, criteria, five-level rubric, expected
scores, and diagnostic terms match exactly.  This was checked before the
projection was sealed.

The source manifest remains the provenance record for the original rubric.
This local copy is the immutable test input for future adapter comparisons and
must be superseded by a new version rather than edited in place.
