"""Strict authority-command vector profile and independent verifier surface."""

from __future__ import annotations

import base64
import binascii
import hashlib
import re
from typing import Any, NoReturn

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import (
    decode_dss_signature,
    encode_dss_signature,
)

from .canonical import CanonicalError, canonical_bytes
from .p256 import N

SCHEMA = "codex-house-authority-command/2"
ALGORITHM = "ecdsa-p256-sha256-jcs-low-s/1"
CONTEXT = "codex-house/authority-command/v2"
VECTOR_SCHEMA = "codex-house-p256-vector/1"
MAX_LIFETIME_SECONDS = 300
INT64_MAX = 2**63 - 1

UNSIGNED_FIELDS = frozenset(
    {
        "schema",
        "algorithm",
        "context",
        "registry_id",
        "generation",
        "deployment_id",
        "policy_sha256",
        "principal_id",
        "key_id",
        "key_epoch",
        "action",
        "binding_sha256",
        "challenge",
        "issued_at",
        "expires_at",
    }
)
HEX32 = re.compile(r"^[0-9a-f]{32}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
KEY_ID = re.compile(r"^p256:[0-9a-f]{64}$")
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$")
B64U = re.compile(r"^[A-Za-z0-9_-]+$")


class ProfileError(ValueError):
    """Typed vector-profile failure."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _fail(code: str, message: str) -> NoReturn:
    raise ProfileError(code, message)


def b64u_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def b64u_decode(value: Any, *, code: str = "PROFILE_B64U") -> bytes:
    if not isinstance(value, str) or not value or not B64U.fullmatch(value):
        _fail(code, "value is not canonical unpadded base64url")
    try:
        decoded = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except (ValueError, binascii.Error) as error:
        raise ProfileError(code, "value is not valid base64url") from error
    if b64u_encode(decoded) != value:
        _fail(code, "value has a non-canonical base64url representation")
    return decoded


def _integer(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        _fail("PROFILE_INTEGER", f"{name} must be an integer")
    if not 0 <= value <= INT64_MAX:
        _fail("PROFILE_INTEGER", f"{name} is outside the supported range")
    return value


def validate_unsigned(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail("PROFILE_OBJECT", "unsigned proof must be an object")
    fields = set(value)
    if fields != UNSIGNED_FIELDS:
        _fail(
            "PROFILE_FIELDS",
            f"unsigned proof fields differ: missing={sorted(UNSIGNED_FIELDS - fields)}, unknown={sorted(fields - UNSIGNED_FIELDS)}",
        )
    if value["schema"] != SCHEMA:
        _fail("PROFILE_SCHEMA", "unsupported proof schema")
    if value["algorithm"] != ALGORITHM:
        _fail("PROFILE_ALGORITHM", "unsupported proof algorithm")
    if value["context"] != CONTEXT:
        _fail("PROFILE_CONTEXT", "unsupported proof domain context")
    for name in ("registry_id", "deployment_id"):
        if not isinstance(value[name], str) or not HEX32.fullmatch(value[name]):
            _fail("PROFILE_ID", f"{name} must be 128-bit lowercase hex")
    for name in ("policy_sha256", "binding_sha256"):
        if not isinstance(value[name], str) or not HEX64.fullmatch(value[name]):
            _fail("PROFILE_DIGEST", f"{name} must be lowercase SHA-256 hex")
    for name in ("principal_id", "action"):
        if not isinstance(value[name], str) or not IDENTIFIER.fullmatch(value[name]):
            _fail("PROFILE_IDENTIFIER", f"{name} is not an admitted identifier")
    if not isinstance(value["key_id"], str) or not KEY_ID.fullmatch(value["key_id"]):
        _fail("PROFILE_KEY_ID", "key_id is not content-derived P-256 identity")
    generation = _integer(value["generation"], "generation")
    key_epoch = _integer(value["key_epoch"], "key_epoch")
    issued_at = _integer(value["issued_at"], "issued_at")
    expires_at = _integer(value["expires_at"], "expires_at")
    if generation == 0 or key_epoch == 0:
        _fail("PROFILE_EPOCH", "generation and key_epoch must be positive")
    if not issued_at < expires_at <= issued_at + MAX_LIFETIME_SECONDS:
        _fail("PROFILE_LIFETIME", "proof lifetime is empty or exceeds five minutes")
    if len(b64u_decode(value["challenge"], code="PROFILE_CHALLENGE")) != 16:
        _fail("PROFILE_CHALLENGE", "challenge must contain exactly 128 bits")
    try:
        canonical_bytes(value)
    except CanonicalError as error:
        raise ProfileError(error.code, str(error)) from error
    return value


def decode_strict_signature(value: Any) -> tuple[bytes, int, int]:
    der = b64u_decode(value, code="PROFILE_SIGNATURE_B64U")
    try:
        r, s = decode_dss_signature(der)
    except (TypeError, ValueError) as error:
        raise ProfileError(
            "PROFILE_SIGNATURE_DER", "signature is not strict DER"
        ) from error
    if encode_dss_signature(r, s) != der:
        _fail("PROFILE_SIGNATURE_DER", "signature DER is not minimally encoded")
    if not 1 <= r < N or not 1 <= s < N:
        _fail("PROFILE_SIGNATURE_RANGE", "signature component is outside P-256 order")
    if s > N // 2:
        _fail("PROFILE_SIGNATURE_HIGH_S", "signature is not normalized to low-S")
    return der, r, s


def load_p256_spki(value: Any) -> tuple[ec.EllipticCurvePublicKey, bytes]:
    der = b64u_decode(value, code="PROFILE_PUBLIC_KEY_B64U")
    try:
        key = serialization.load_der_public_key(der)
    except ValueError as error:
        raise ProfileError(
            "PROFILE_PUBLIC_KEY_DER", "public key is not DER SPKI"
        ) from error
    if not isinstance(key, ec.EllipticCurvePublicKey) or not isinstance(
        key.curve, ec.SECP256R1
    ):
        _fail("PROFILE_PUBLIC_KEY_CURVE", "public key is not P-256")
    canonical = key.public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    if canonical != der:
        _fail("PROFILE_PUBLIC_KEY_DER", "public key DER is not canonical SPKI")
    return key, der


def key_id_for_spki(der: bytes) -> str:
    return f"p256:{hashlib.sha256(der).hexdigest()}"


def verify_vector_record(record: Any) -> dict[str, Any]:
    if not isinstance(record, dict) or record.get("vector_schema") != VECTOR_SCHEMA:
        _fail("VECTOR_SCHEMA", "unsupported vector record")
    unsigned = validate_unsigned(record.get("unsigned_object"))
    canonical = canonical_bytes(unsigned)
    if canonical.hex() != record.get("canonical_utf8_hex"):
        _fail("VECTOR_CANONICAL", "canonical bytes differ from vector")
    digest = hashlib.sha256(canonical).digest()
    if digest.hex() != record.get("sha256_hex"):
        _fail("VECTOR_DIGEST", "SHA-256 differs from vector")
    public_key, spki = load_p256_spki(record.get("public_spki_der_b64u"))
    key_id = key_id_for_spki(spki)
    if record.get("key_id") != key_id or unsigned["key_id"] != key_id:
        _fail("VECTOR_KEY_ID", "content-derived key ID differs from vector")
    signature, r, s = decode_strict_signature(record.get("signature_der_b64u"))
    if record.get("r_hex") != f"{r:064x}" or record.get("s_hex") != f"{s:064x}":
        _fail("VECTOR_COMPONENT", "r/s components differ from DER signature")
    try:
        public_key.verify(signature, canonical, ec.ECDSA(hashes.SHA256()))
    except InvalidSignature as error:
        raise ProfileError(
            "VECTOR_SIGNATURE", "signature verification failed"
        ) from error
    return {
        "vector_id": record.get("vector_id"),
        "canonical_sha256": digest.hex(),
        "key_id": key_id,
        "r": r,
        "s": s,
    }
