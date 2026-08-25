# Runtime static preflight

Status: `STATIC_COMPATIBILITY_OBSERVED / NO_MODEL_LOAD / NO_INFERENCE`

## Observed runtime

- Python environment: `/Volumes/Models/.venv/bin/python`
- `mlx`: `0.31.2`
- `mlx-lm`: `0.31.3`
- Bundle declared model type: `mistral3`

The installed runtime contains `mlx_lm.models.mistral3`.  Its static loader
imports `mlx_lm.models.<model_type>` after any declared remapping, so the
bundle's declared type resolves to a present local module.  Required config,
index, template, and tokenizer files were also present.

## Ceiling

This proves only static package and file-surface compatibility.  It does not
prove successful model loading, output quality, memory safety, actual template
behavior, or evaluation eligibility.  No weight was deserialized and no model
or provider was invoked.

Before a run, the pre-binding still needs an explicit inference-only authority,
fixed decoding configuration, a reserved output path, and a runtime-load
receipt bound to the exact artifact manifest.
