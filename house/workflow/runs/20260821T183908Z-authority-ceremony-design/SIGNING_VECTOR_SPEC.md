# Portable P-256 signing-vector specification

This document specifies future fixtures. It does not generate a key or assert
YubiKey compatibility.

## Algorithm profile

Proposed algorithm identifier:

`ecdsa-p256-sha256-jcs-low-s/1`

- Curve: NIST P-256 / secp256r1.
- Digest: SHA-256.
- Signed message: UTF-8 bytes of the canonical unsigned object.
- JSON canonicalization: RFC 8785 JSON Canonicalization Scheme after strict
  schema and type validation.
- Signature wire form: strict ASN.1 DER ECDSA `(r,s)`, then unpadded base64url.
- Malleability rule: normalize `s` to the lower half of the P-256 group order;
  verifiers reject a non-low-S wire signature even if mathematically valid.
- Public-key wire form: SubjectPublicKeyInfo DER, unpadded base64url.
- Key ID: `p256:` plus lowercase SHA-256 hex of the SPKI DER.

The implementation MUST reject duplicate JSON keys before canonicalization,
unknown fields, floats and non-finite numbers, integers outside signed 64-bit
range, invalid UTF-8, lone surrogates, non-ASCII identifiers, padded or
non-canonical base64url, non-minimal DER integers, zero/out-of-range `r` or `s`,
wrong curves, and trailing DER bytes.

Task content is signed by digest. The submission-digest algorithm is separately
versioned and MUST use strict schema validation plus RFC 8785. Proof fields
remain ASCII identifiers, lowercase hex digests, booleans, or signed 64-bit
integers so hardware and cross-language signers do not interpret arbitrary task
prose.

## Domain separation and freshness

Every signed object MUST include:

- `schema` and `algorithm`;
- `context`, such as `codex-house/authority-command/v2`;
- registry ID/generation, deployment ID, and policy digest;
- principal, key ID/epoch, action, and binding digest;
- a 128-bit unpadded-base64url challenge issued and reserved by the service;
- integer issuance and expiry times with a maximum five-minute lifetime.

The service-issued challenge is one-use and state-bound. Caller-chosen nonces
may remain request metadata but are not the replay authority. If wall time moves
back beyond the declared skew or precedes the service's durable maximum accepted
time, the service enters `CLOCK_UNTRUSTED` and stops mutation until recovery.

## Vector record

Each future vector is one immutable JSON document containing:

```json
{
  "vector_schema": "codex-house-p256-vector/1",
  "vector_id": "stable-name",
  "disposition": "accept or reject",
  "unsigned_object": {},
  "canonical_utf8_hex": "...",
  "sha256_hex": "...",
  "public_spki_der_b64u": "...",
  "key_id": "p256:...",
  "signature_der_b64u": "...",
  "r_hex": "...",
  "s_hex": "...",
  "expected_error": null,
  "provenance": {
    "generator": "exact tool and version",
    "independent_verifiers": [],
    "hardware": null
  }
}
```

Files also carry SHA-256 inventory hashes. A published software vector MAY
include an explicitly non-production test private scalar so independent
implementations can reproduce an RFC 6979 deterministic signature. A hardware
vector MUST NOT export a private key; it proves verification of one observed
signature rather than reproduction of identical ECDSA randomness.

## Required positive vectors

1. Fixed software vector with published test-only private scalar and exact
   RFC 6979 signature.
2. Independent verification by at least two implementations that do not share
   the candidate's signing helper.
3. Canonicalization vectors covering field-order changes, escaped characters,
   Unicode strings in signed content digests, and signed-int64 boundaries.
4. Binding vector proving any change to action, registry, generation, policy,
   key epoch, challenge, target, or content changes the digest.
5. Later, separately authorized PIV vector that exports only public material and
   an observed touch-confirmed signature from one explicitly selected slot.

## Required negative vectors

- unknown/missing/duplicate field;
- invalid UTF-8, lone surrogate, float, NaN, infinity, or oversized integer;
- padded, alternate-alphabet, or non-canonical base64url;
- wrong schema, algorithm, domain, deployment, registry, generation, key epoch,
  action, binding, challenge, time, curve, or public key;
- expired, future, overlong, replayed, unreserved, or already-consumed challenge;
- malformed DER, trailing DER, negative/non-minimal integer, zero/out-of-range
  `r` or `s`, and mathematically valid high-S form;
- changed submission with unchanged claimed digest;
- signature from the other owner key when the selected key ID is bound.

## Interoperability gate

No hardware ceremony implementation may be promoted until:

- all fixed vectors verify identically in the service and an independent tool;
- the independent tool rejects every negative vector with the expected class;
- the chosen PIV client demonstrates public-key retrieval and touch-confirmed
  signing without private-key export in a separately authorized hardware test;
- device/slot ambiguity and removal during signing fail closed;
- the vector inventory, tool versions, source revision, and raw public outputs
  are hash-sealed.

Library or hardware documentation may inform implementation, but only observed
vectors and independent replay establish compatibility for the tested versions.
