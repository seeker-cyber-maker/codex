# Authority Stage 0 after-action review

Freezing exact bytes before any hardware work was useful: it separated portable
message/signature behavior from PIV client behavior, key custody, and service
isolation. The profile rejects the ambiguous surfaces most likely to create
cross-language drift: duplicate fields, floats, oversized integers, invalid
Unicode, padded base64url, non-minimal DER, and high-S signatures.

The positive vector is reproducible from a conspicuously public test scalar and
is independently accepted by two installed cryptographic implementations plus
the small pure-Python verifier. Binding tests demonstrate digest and signature
sensitivity without claiming freshness, replay prevention, or durable state.

The deliberate limitation is important: this is a restricted RFC 8785-style
subset, not a general numeric JCS implementation. It says nothing about service
transactions, races, crashes, clocks, filesystems, hostile processes, device
selection, YubiKeys, or recovery. Those uncertainties remain attached to the
later preregistered stages rather than being smuggled into the Stage 0 result.
