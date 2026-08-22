# Handoff

`house/worker_catalog` is the only Dream House-side provider integration at
this point. It accepts a strict catalog of approved specialists and emits an
offline receipt bound to the provider source commit and tree.

The current Daybreak lane has established the intended vocabulary:

- `local.omlx` may be active only after its own provider evidence;
- Qwen3-VL and CreateML are approved specialists but remain
  `not_dispatchable` until dedicated adapters are qualified;
- Needle and ordinary model discovery do not become workers by catalog import.

Do not bind a live file, socket, or mutable oMLX directory to this module. The
next step begins only after the provider lane commits a compatible export.
