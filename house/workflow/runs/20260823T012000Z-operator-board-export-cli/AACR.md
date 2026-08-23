# After-action review — frozen operator-board export CLI

## Outcome

`export-operator-board` accepts exactly two UTF-8 frozen HTML input paths and
one new output path, then returns the existing export receipt. Its command
branch runs before relay construction, so it neither requires nor opens a
relay database.

## Boundary

The CLI is an explicit manual bridge to an existing local no-overwrite writer.
It has no implicit source or destination, does not search for documents, and
does not add viewer, network, provider, worker, task, or authority behavior.
The export receipt remains an integrity record, not proof of authorship or
source correctness.

## Review note

Focused behavioral tests cover the successful three-path invocation and parser
rejection when the required paths are absent. Existing export tests retain the
no-overwrite, incomplete-marker, symlink, and byte-integrity checks.
