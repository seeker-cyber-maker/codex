"""Small test-only P-256/RFC 6979 implementation for fixed fixtures."""

from __future__ import annotations

import hashlib
import hmac
from typing import TypeAlias

P = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
A = P - 3
B = 0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B
GX = 0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296
GY = 0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5
N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
G = (GX, GY)

Point: TypeAlias = tuple[int, int] | None


def inverse(value: int, modulus: int) -> int:
    if value % modulus == 0:
        raise ValueError("inverse does not exist")
    return pow(value, -1, modulus)


def point_add(left: Point, right: Point) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if left == right:
        slope = ((3 * x1 * x1 + A) * inverse(2 * y1, P)) % P
    else:
        slope = ((y2 - y1) * inverse(x2 - x1, P)) % P
    x3 = (slope * slope - x1 - x2) % P
    y3 = (slope * (x1 - x3) - y1) % P
    return x3, y3


def scalar_multiply(scalar: int, point: Point = G) -> Point:
    if not 0 <= scalar < N:
        raise ValueError("scalar is outside P-256 order")
    result: Point = None
    addend = point
    while scalar:
        if scalar & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        scalar >>= 1
    return result


def derive_test_scalar(label: bytes) -> int:
    """Derive a public, deterministic, explicitly non-production scalar."""

    return int.from_bytes(hashlib.sha256(label).digest(), "big") % (N - 1) + 1


def _int2octets(value: int) -> bytes:
    return value.to_bytes(32, "big")


def _bits2octets(digest: bytes) -> bytes:
    return _int2octets(int.from_bytes(digest, "big") % N)


def rfc6979_nonce(private_scalar: int, digest: bytes) -> int:
    """Return the RFC 6979 HMAC-SHA256 nonce for P-256."""

    if not 1 <= private_scalar < N or len(digest) != 32:
        raise ValueError("invalid P-256 scalar or SHA-256 digest")
    value = b"\x01" * 32
    key = b"\x00" * 32
    material = _int2octets(private_scalar) + _bits2octets(digest)
    key = hmac.new(key, value + b"\x00" + material, hashlib.sha256).digest()
    value = hmac.new(key, value, hashlib.sha256).digest()
    key = hmac.new(key, value + b"\x01" + material, hashlib.sha256).digest()
    value = hmac.new(key, value, hashlib.sha256).digest()
    while True:
        candidate = b""
        while len(candidate) < 32:
            value = hmac.new(key, value, hashlib.sha256).digest()
            candidate += value
        nonce = int.from_bytes(candidate[:32], "big")
        if 1 <= nonce < N:
            return nonce
        key = hmac.new(key, value + b"\x00", hashlib.sha256).digest()
        value = hmac.new(key, value, hashlib.sha256).digest()


def sign_digest(private_scalar: int, digest: bytes) -> tuple[int, int]:
    """Create a deterministic low-S P-256 signature over a SHA-256 digest."""

    nonce = rfc6979_nonce(private_scalar, digest)
    point = scalar_multiply(nonce)
    if point is None:
        raise AssertionError("valid nonce produced point at infinity")
    r = point[0] % N
    z = int.from_bytes(digest, "big")
    s = (inverse(nonce, N) * (z + r * private_scalar)) % N
    if r == 0 or s == 0:
        raise AssertionError("invalid zero ECDSA component")
    if s > N // 2:
        s = N - s
    return r, s


def verify_digest(public_point: Point, digest: bytes, r: int, s: int) -> bool:
    """Verify one P-256 signature without the cryptography verifier."""

    if public_point is None or len(digest) != 32:
        return False
    if not 1 <= r < N or not 1 <= s <= N // 2:
        return False
    z = int.from_bytes(digest, "big")
    factor = inverse(s, N)
    point = point_add(
        scalar_multiply((z * factor) % N),
        scalar_multiply((r * factor) % N, public_point),
    )
    return point is not None and point[0] % N == r


def _der_integer(value: int) -> bytes:
    if value <= 0:
        raise ValueError("DER ECDSA integers must be positive")
    encoded = value.to_bytes((value.bit_length() + 7) // 8, "big")
    if encoded[0] & 0x80:
        encoded = b"\x00" + encoded
    return b"\x02" + bytes([len(encoded)]) + encoded


def encode_der_signature(r: int, s: int) -> bytes:
    body = _der_integer(r) + _der_integer(s)
    if len(body) >= 128:
        raise ValueError("unexpected long-form P-256 signature")
    return b"\x30" + bytes([len(body)]) + body
