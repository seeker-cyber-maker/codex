# Opaque candidate pre-binding

Status: `PREPARED_NOT_AUTHORIZED`

This record binds `local-rubric-candidate-b` to exact canonical files while
keeping its human-readable local path outside the evaluation scoring surface.
The source-only intake found a complete, header-consistent MLX Safetensors
bundle without loading weight payloads.

The record is deliberately a *pre-binding*, not a runnable experiment
manifest.  It lacks a runtime fingerprint, confirmed load compatibility,
decoding parameters, output reservation, and inference authorization.  Until
all of those are independently recorded, the candidate may not load, generate,
dispatch, train, or be promoted.
