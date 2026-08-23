# After-action review — manual operator-board viewer CLI

## Outcome

`start-operator-board-viewer --output <absolute-completed-export>` is an
explicit keyboard-first command. It uses the verified preparation seam, starts
the existing bounded loopback viewer exactly once, displays the one-time local
URL to the invoking terminal, waits for the terminal receipt, and exits. It
does not launch a browser or iTerm.

## Authority boundary

This is an interim manual operator path, not cryptographic human proof. A model
or process that can invoke the same terminal command could also attempt it;
the command makes no contrary claim. The future YubiKey-backed authority
service is required before treating viewer start as independently authenticated
or delegable.

## Council outcome

The external council run is preserved under `council-runs/`. One reviewer
completed and accepted, one produced a truncated partial response with an
`ACCEPT` verdict, and one provider lane timed out twice. The synthesis records
this as limited independent coverage, not unanimity.
