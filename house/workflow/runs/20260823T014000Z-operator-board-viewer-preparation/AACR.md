# After-action review — operator-board viewer preparation

## Outcome

`prepare_operator_board_viewer()` checks a named completed export through its
existing fail-closed inspector, reads the board bytes once, verifies those bytes
still match the inspected receipt hash, decodes strict UTF-8, and constructs an
unstarted `OneShotLoopbackViewer`.

## Boundary

Preparation neither binds a listener nor issues a capability. It reads only the
caller-named already-complete export and does not update its receipt or any
relay/task state. The returned object can start only through a later explicit
caller action; this run does not authorize or exercise that transition.

## Review note

The viewer wrapper intentionally hides the base viewer's injectable clock and
validator parameters, matching the existing relay viewer's narrowed public
surface. It exposes only host, port, and TTL, whose validations remain in the
qualified base viewer.
