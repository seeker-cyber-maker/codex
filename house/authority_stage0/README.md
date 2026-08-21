# Authority Stage 0 fixtures

This isolated module implements the preregistered software-only signing-vector
stage. It provides a restricted RFC 8785-style canonical JSON profile, a
public deterministic RFC 6979 P-256 test signer, strict low-S/DER/base64url
verification, and immutable positive and negative fixtures.

It is not imported by the live task-spine authority code. It has no network,
provider, database, service, hardware, or real-key behavior. The published
private scalar is intentionally public and must never be used for authority.

Run the checks from the repository root:

```text
python3 -m house.authority_stage0.vector_tool check
python3 -m house.authority_stage0.verify
python3 -m unittest discover -s house/authority_stage0/tests -p 'test_*.py'
```
