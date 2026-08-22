# After-action council review — relay preview registration contract

## Outcome

The operator registry was reused instead of inventing a second dashboard action
catalog. The relay descriptor binds that shared display-only command to a
document hash, keeping the operator/UI seam comparable to every other prepared
request.

## Correction during implementation

The new command correctly expanded the generic terminal-preview search and the
iTerm surface manifest. Two old singleton assertions were updated after the
failure proved they encoded pre-expansion behavior; search semantics themselves
were unchanged.

## Boundary

This remains an offline descriptor. Browser launch, iTerm registration,
capability issuance, viewer start, authority, and all write/worker paths stay
outside the accepted slice.
