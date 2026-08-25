# F1 bounded verifier-closure delta 2

Round-one council packet:
`86680f088b8f25a822ff6af800512468a309d2c8af3ecad21fba0754f87d3ccf`

The adversarial reviewer found that V1 reconstructed required values but did
not reject unknown object fields. Preserve V1 unchanged as
`independent_verify_v1.py` and add a new `independent_verify.py` wrapper that:

- rejects duplicate JSON keys;
- enforces exact field sets for the fixture and every nested contract object;
- enforces exact provenance, intermediate, artifact-manifest, and disclosure
  schemas; and
- calls unchanged V1 only after schema closure passes.

The wrapper may parse and hash the explicitly public test-key disclosure solely
to enforce its closed schema, warning, and artifact manifest. It must not use
the disclosed scalar or label for key derivation, signing, or verification.
Cryptographic verification remains public-SPKI-only in V1 and OpenSSL.

Authorize exactly two V2 verification runs over the already frozen A/B outputs
and one final council round. Do not regenerate fixture outputs, change the
generator, edit production source, or widen any operational authority.
