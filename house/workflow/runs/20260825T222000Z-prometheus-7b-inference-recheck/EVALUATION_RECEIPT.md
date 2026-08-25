# Prometheus 7B BF16 inference recheck

Status: `PASS / INFERENCE_ONLY / NOT_TERM_WORKER_QUALIFICATION`

## Purpose

Recheck the known Prometheus rubric-instructor adapter after coordinating with
the `-Training` task.  This is an isolated local inference smoke test.  It
does not train weights, create a worker lane, dispatch a task, or qualify TERM
notation interoperability.

## Bound inputs

- Model: `/Volumes/Models/trainers/prometheus-7b-v2.0-mlx-bf16`
- Evaluator: `/Users/tiga/Documents/Codex_Projects/storage-inventory/model-classifier/run_prometheus_mlx_instructor_eval.py`
- Frozen manifest: `/Users/tiga/Documents/Codex_Projects/storage-inventory/model-classifier/prometheus_instructor_eval.json`
- Output: `prometheus-instructor-eval.json`
- Output SHA-256: `6f2122fb3f93f6dfe2fe0e2fbf49fe20302fc79fded04ee22936a0aaf4ddf928`

## Result

The complete four-case suite passed its declared thresholds:

- Parse rate: `1.00` (minimum `1.00`)
- Score agreement: `0.75` (minimum `0.75`)
- Diagnostic-term rate: `1.00` (minimum `0.75`)
- Peak MLX memory: `14.713 GB`

## Admission boundary

The test confirms only that the existing Prometheus-specific rubric adapter
currently loads and produces parseable output under its frozen manifest.
Other local models need their own prompt/rendering and result-parser adapters,
then the same manifest can be reused as a shared test corpus.  TERM
compatibility remains `NOT_READY_NO_DISPATCH` until it has a separately sealed
model roster, manifest, evaluator, and authorization.
