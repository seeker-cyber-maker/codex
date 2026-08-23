# After-action review — visible source scope

## Outcome

Accepted as a narrow presentation correction. The prior bundle preserved its
source scope in `bundle.json`, but the viewed HTML could be misread as a blank
system rather than an explicitly unpopulated bootstrap.

## Correction

The two existing projection renderers now add a fixed, validated source-scope
line inside their static main fragments. Because that line participates in the
snapshot and envelope bytes, it is covered by the existing receipt chain.

## Limits

No live source, refresh, output path, source content, authority, or worker
behavior was added. Existing bundles remain untouched and truthful historical
artifacts.
