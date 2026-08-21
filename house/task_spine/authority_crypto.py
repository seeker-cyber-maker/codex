"""Canonical P-256 proof primitives for the offline authority candidate."""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import re
from typing import Any

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

PROOF_SCHEMA = "codex-house-authority-proof/1"
PROOF_RECEIPT_SCHEMA = "codex-house-authority-proof-receipt/1"
AUTHORIZED_ENQUEUE_SCHEMA = "codex-house-authorized-enqueue-receipt/1"
ALGORITHM = "ecdsa-p256-sha256"
KNOWN_ACTIONS = frozenset({"inbox.enqueue", "authority.revoke"})
MAX_PROOF_LIFETIME_SECONDS = 300
MAX_CLOCK_SKEW_SECONDS = 5
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
NONCE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{15,127}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
PROOF_FIELDS = frozenset(
    {
        "schema",
        "algorithm",
        "principal_id",
        "key_id",
        "action",
        "binding_sha256",
        "nonce",
        "issued_at",
        "expires_at",
        "signature_b64",
    }
)


class AuthorityError(RuntimeError):
    """A typed fail-closed authority error."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def canonical(value: Any) -> str:
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
    except (TypeError, ValueError) as exc:
        raise AuthorityError(
            "INVALID_JSON", f"value is not canonical JSON: {exc}"
        ) from exc


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def identifier(value: object, field: str) -> str:
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        raise AuthorityError("INVALID_FIELD", f"{field} is not a valid identifier")
    return value


def public_key_der(public_key: ec.EllipticCurvePublicKey) -> bytes:
    if not isinstance(public_key.curve, ec.SECP256R1):
        raise AuthorityError("UNSUPPORTED_KEY", "public key must use P-256")
    return public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def load_public_key(public_key_bytes: bytes) -> ec.EllipticCurvePublicKey:
    try:
        key = serialization.load_der_public_key(public_key_bytes)
    except (TypeError, ValueError) as exc:
        raise AuthorityError("INVALID_KEY", "public key is not valid DER") from exc
    if not isinstance(key, ec.EllipticCurvePublicKey) or not isinstance(
        key.curve, ec.SECP256R1
    ):
        raise AuthorityError("UNSUPPORTED_KEY", "public key must use P-256")
    return key


def key_id_for_public_key(public_key: ec.EllipticCurvePublicKey) -> str:
    """Return the content-derived identifier for one P-256 public key."""
    return "p256:" + hashlib.sha256(public_key_der(public_key)).hexdigest()


def enqueue_binding(enqueue_id: str, submission: object) -> str:
    """Bind an enqueue proof to its normalized target and canonical payload."""
    return sha256_json(
        {
            "action": "inbox.enqueue",
            "enqueue_id": identifier(enqueue_id, "enqueue_id"),
            "submission_sha256": hashlib.sha256(
                canonical(submission).encode()
            ).hexdigest(),
        }
    )


def revocation_binding(target_key_id: str, reason: str) -> str:
    """Bind a revocation proof to one key and bounded reason."""
    target_key_id = identifier(target_key_id, "target_key_id")
    if not isinstance(reason, str) or not reason.strip() or len(reason.strip()) > 512:
        raise AuthorityError("INVALID_FIELD", "reason must be 1 to 512 characters")
    return sha256_json(
        {
            "action": "authority.revoke",
            "target_key_id": target_key_id,
            "reason": reason.strip(),
        }
    )


def sign_proof(
    private_key: ec.EllipticCurvePrivateKey,
    *,
    principal_id: str,
    action: str,
    binding_sha256: str,
    nonce: str,
    issued_at: int,
    expires_at: int,
) -> dict[str, Any]:
    """Create a proof for tests or a software signer; no key is persisted."""
    if not isinstance(private_key.curve, ec.SECP256R1):
        raise AuthorityError("UNSUPPORTED_KEY", "private key must use P-256")
    unsigned = {
        "schema": PROOF_SCHEMA,
        "algorithm": ALGORITHM,
        "principal_id": identifier(principal_id, "principal_id"),
        "key_id": key_id_for_public_key(private_key.public_key()),
        "action": identifier(action, "action"),
        "binding_sha256": binding_sha256,
        "nonce": nonce,
        "issued_at": issued_at,
        "expires_at": expires_at,
    }
    prepare_unsigned_proof(unsigned)
    signature = private_key.sign(
        canonical(unsigned).encode(), ec.ECDSA(hashes.SHA256())
    )
    return {**unsigned, "signature_b64": base64.b64encode(signature).decode("ascii")}


def prepare_unsigned_proof(unsigned: dict[str, Any]) -> dict[str, Any]:
    if unsigned.get("schema") != PROOF_SCHEMA:
        raise AuthorityError("INVALID_SCHEMA", "invalid authority proof schema")
    if unsigned.get("algorithm") != ALGORITHM:
        raise AuthorityError(
            "INVALID_ALGORITHM", "unsupported authority proof algorithm"
        )
    identifier(unsigned.get("principal_id"), "principal_id")
    identifier(unsigned.get("key_id"), "key_id")
    action = identifier(unsigned.get("action"), "action")
    if action not in KNOWN_ACTIONS:
        raise AuthorityError("INVALID_ACTION", "unknown authority action")
    binding = unsigned.get("binding_sha256")
    if not isinstance(binding, str) or not SHA256_RE.fullmatch(binding):
        raise AuthorityError(
            "INVALID_FIELD", "binding_sha256 must be a lowercase SHA-256"
        )
    nonce = unsigned.get("nonce")
    if not isinstance(nonce, str) or not NONCE_RE.fullmatch(nonce):
        raise AuthorityError(
            "INVALID_FIELD", "nonce must be a 16 to 128 character identifier"
        )
    for field in ("issued_at", "expires_at"):
        if isinstance(unsigned.get(field), bool) or not isinstance(
            unsigned.get(field), int
        ):
            raise AuthorityError(
                "INVALID_FIELD", f"{field} must be an integer timestamp"
            )
        if not 0 <= unsigned[field] <= 9_223_372_036_854_775_807:
            raise AuthorityError(
                "INVALID_FIELD", f"{field} is outside the supported range"
            )
    return unsigned


def decode_signature(signature_b64: str) -> bytes:
    try:
        signature = base64.b64decode(signature_b64, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise AuthorityError("INVALID_SIGNATURE", "signature_b64 is invalid") from exc
    if not 64 <= len(signature) <= 80:
        raise AuthorityError("INVALID_SIGNATURE", "signature length is invalid")
    return signature
