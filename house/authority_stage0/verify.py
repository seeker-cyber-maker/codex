"""Independent verification helpers for the committed Stage 0 vector."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import serialization

from .canonical import canonical_bytes
from .p256 import verify_digest
from .profile import b64u_decode, decode_strict_signature, verify_vector_record
from .vector_tool import POSITIVE_FIXTURE


def load_record(path: Path = POSITIVE_FIXTURE) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError("positive fixture must be an object")
    return value


def verify_pure(record: dict[str, Any]) -> None:
    result = verify_vector_record(record)
    key = serialization.load_der_public_key(b64u_decode(record["public_spki_der_b64u"]))
    numbers = key.public_numbers()  # type: ignore[union-attr]
    digest = bytes.fromhex(result["canonical_sha256"])
    _, r, s = decode_strict_signature(record["signature_der_b64u"])
    if not verify_digest((numbers.x, numbers.y), digest, r, s):
        raise ValueError("pure-Python P-256 verification failed")


def verify_openssl(record: dict[str, Any], executable: str = "openssl") -> None:
    canonical = canonical_bytes(record["unsigned_object"])
    public_der = b64u_decode(record["public_spki_der_b64u"])
    signature = b64u_decode(record["signature_der_b64u"])
    with tempfile.TemporaryDirectory(prefix="codex-house-stage0-") as directory:
        root = Path(directory)
        der_path = root / "public.der"
        pem_path = root / "public.pem"
        message_path = root / "message.bin"
        signature_path = root / "signature.der"
        der_path.write_bytes(public_der)
        message_path.write_bytes(canonical)
        signature_path.write_bytes(signature)
        subprocess.run(
            [
                executable,
                "pkey",
                "-pubin",
                "-inform",
                "DER",
                "-in",
                str(der_path),
                "-out",
                str(pem_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = subprocess.run(
            [
                executable,
                "dgst",
                "-sha256",
                "-verify",
                str(pem_path),
                "-signature",
                str(signature_path),
                str(message_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        if result.stdout.strip() != "Verified OK":
            raise ValueError(f"unexpected OpenSSL output: {result.stdout!r}")


def main() -> None:
    record = load_record()
    verify_pure(record)
    verify_openssl(record)
    print("cryptography: accepted")
    print("pure-python: accepted")
    print("openssl: accepted")


if __name__ == "__main__":
    main()
