# Handoff

`house/worker_exec/mock_admission.py` contains only canonical, sealed
`MOCK_ONLY` runtime-profile and authority fixtures.  It does not import a
subprocess, environment, configuration, callback, executable, model, provider,
or egress path.  Its validation result is `NOT_ATTEMPTED`.

The council corrected an important future boundary: task-card `specific_model`
metadata cannot select a real execution model.  A later qualified runtime
profile and separately authenticated, single-use human authority must bind and
agree on it before a real runner can be proposed.
