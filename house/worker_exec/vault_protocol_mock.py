"""Generated-data-only vault protocol and storage qualification fixtures.

This module is deliberately incapable of reading macOS Keychain, spawning a
process, opening a network connection, or returning stored plaintext.  It is a
protocol/state-machine fixture for the first disposable vault implementation
rung, not a production secret broker.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .context_grammar import canonical_sha256, seal_record

RESOLVE_INTENT_SCHEMA = "codex-house-resolve-intent/1"
LEASE_TICKET_SCHEMA = "codex-house-vault-lease-ticket/1"
CLAIM_RECEIPT_SCHEMA = "codex-house-vault-nonce-claim/1"
MOCK_STORE_SCHEMA = "codex-house-generated-vault-store/1"
CRASH_RECEIPT_SCHEMA = "codex-house-vault-crash-classification/1"
ROTATION_RECEIPT_SCHEMA = "codex-house-generated-vault-rotation/1"

_HASH = re.compile(r"^[0-9a-f]{64}$")
_ID = re.compile(r"^[A-Za-z][A-Za-z0-9._-]{0,127}$")
_REF = re.compile(r"^vr_[a-z0-9]{16,64}$")
_NONCE = re.compile(r"^vn_[a-z0-9]{24,96}$")
_LIVE_SINKS = {"provider_header", "inherited_fd"}
_STATES = (
    "PREPARED",
    "INTENT_DURABLE",
    "SINK_BOUND",
    "DELIVERY_ATTEMPTED",
    "CONSUMED",
    "OUTCOME_DURABLE",
)


class VaultProtocolMockError(ValueError):
    """Raised when the generated-only protocol boundary is violated."""


def _exact_id(value: object, label: str) -> str:
    if type(value) is not str or not _ID.fullmatch(value):
        raise VaultProtocolMockError(f"invalid {label}")
    return value


def _exact_hash(value: object, label: str) -> str:
    if type(value) is not str or not _HASH.fullmatch(value):
        raise VaultProtocolMockError(f"invalid {label}")
    return value


def _exact_ref(value: object) -> str:
    if type(value) is not str or not _REF.fullmatch(value):
        raise VaultProtocolMockError("invalid opaque reference")
    return value


def _exact_nonce(value: object) -> str:
    if type(value) is not str or not _NONCE.fullmatch(value):
        raise VaultProtocolMockError("invalid nonce")
    return value


def _verify_sealed(record: object, label: str) -> dict[str, object]:
    if type(record) is not dict:
        raise VaultProtocolMockError(f"invalid {label}")
    supplied = _exact_hash(record.get("record_sha256"), f"{label} hash")
    unsigned = {key: value for key, value in record.items() if key != "record_sha256"}
    if not hmac.compare_digest(canonical_sha256(unsigned), supplied):
        raise VaultProtocolMockError(f"{label} hash mismatch")
    return record


def create_resolve_intent_v1(
    *,
    operation_id: str,
    plan_sha256: str,
    task_sha256: str,
    worker_sha256: str,
    authority_receipt_sha256: str,
    ref_id: str,
    minimum_revision: int,
    namespace_id: str,
    vault_epoch: int,
    audience: str,
    sink_kind: str,
    sink_instance_sha256: str,
    nonce: str,
    created_at_ms: int,
    ttl_seconds: int,
) -> dict[str, object]:
    """Create a complete, one-use, non-retry resolve-intent record."""

    _exact_id(operation_id, "operation id")
    _exact_hash(plan_sha256, "plan hash")
    _exact_hash(task_sha256, "task hash")
    _exact_hash(worker_sha256, "worker hash")
    _exact_hash(authority_receipt_sha256, "authority receipt hash")
    _exact_ref(ref_id)
    _exact_id(namespace_id, "namespace id")
    _exact_id(audience, "audience")
    _exact_hash(sink_instance_sha256, "sink instance hash")
    _exact_nonce(nonce)
    if sink_kind not in _LIVE_SINKS:
        raise VaultProtocolMockError("sink kind is not qualified in v1")
    if type(minimum_revision) is not int or minimum_revision < 1:
        raise VaultProtocolMockError("invalid minimum revision")
    if type(vault_epoch) is not int or vault_epoch < 1:
        raise VaultProtocolMockError("invalid vault epoch")
    if type(created_at_ms) is not int or created_at_ms < 0:
        raise VaultProtocolMockError("invalid creation time")
    if type(ttl_seconds) is not int or not 1 <= ttl_seconds <= 300:
        raise VaultProtocolMockError("invalid TTL")
    return seal_record(
        {
            "schema": RESOLVE_INTENT_SCHEMA,
            "operation_id": operation_id,
            "plan_sha256": plan_sha256,
            "task_sha256": task_sha256,
            "worker_sha256": worker_sha256,
            "authority_receipt_sha256": authority_receipt_sha256,
            "ref_id": ref_id,
            "minimum_revision": minimum_revision,
            "namespace_id": namespace_id,
            "vault_epoch": vault_epoch,
            "audience": audience,
            "sink_kind": sink_kind,
            "sink_instance_sha256": sink_instance_sha256,
            "nonce": nonce,
            "created_at_ms": created_at_ms,
            "ttl_seconds": ttl_seconds,
            "use_count": 1,
            "retry": "FORBIDDEN",
        }
    )


def verify_resolve_intent_v1(intent: object) -> dict[str, object]:
    value = _verify_sealed(intent, "resolve intent")
    expected = {
        "schema",
        "operation_id",
        "plan_sha256",
        "task_sha256",
        "worker_sha256",
        "authority_receipt_sha256",
        "ref_id",
        "minimum_revision",
        "namespace_id",
        "vault_epoch",
        "audience",
        "sink_kind",
        "sink_instance_sha256",
        "nonce",
        "created_at_ms",
        "ttl_seconds",
        "use_count",
        "retry",
        "record_sha256",
    }
    if set(value) != expected or value["schema"] != RESOLVE_INTENT_SCHEMA:
        raise VaultProtocolMockError("resolve intent fields are not exact")
    rebuilt = create_resolve_intent_v1(
        operation_id=value["operation_id"],
        plan_sha256=value["plan_sha256"],
        task_sha256=value["task_sha256"],
        worker_sha256=value["worker_sha256"],
        authority_receipt_sha256=value["authority_receipt_sha256"],
        ref_id=value["ref_id"],
        minimum_revision=value["minimum_revision"],
        namespace_id=value["namespace_id"],
        vault_epoch=value["vault_epoch"],
        audience=value["audience"],
        sink_kind=value["sink_kind"],
        sink_instance_sha256=value["sink_instance_sha256"],
        nonce=value["nonce"],
        created_at_ms=value["created_at_ms"],
        ttl_seconds=value["ttl_seconds"],
    )
    if value["use_count"] != 1 or value["retry"] != "FORBIDDEN":
        raise VaultProtocolMockError("resolve intent is not one-use")
    if rebuilt != value:
        raise VaultProtocolMockError("resolve intent is not canonical")
    return value


class ZeroizingBuffer:
    """Best-effort mutable buffer used only for generated fixture bytes."""

    def __init__(self, value: bytes | bytearray) -> None:
        self._value = bytearray(value)
        self._cleared = False

    def internal_view(self) -> memoryview:
        if self._cleared:
            raise VaultProtocolMockError("buffer already cleared")
        return memoryview(self._value)

    def clear(self) -> None:
        for index in range(len(self._value)):
            self._value[index] = 0
        self._cleared = True

    @property
    def cleared(self) -> bool:
        return self._cleared

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.clear()


class MockControllerKey:
    """Generated HMAC key for deterministic protocol qualification only."""

    def __init__(self, key: bytes | None = None) -> None:
        self._key = bytearray(key if key is not None else os.urandom(32))
        if len(self._key) != 32:
            raise VaultProtocolMockError("mock controller key must be 32 bytes")

    def sign_ticket(
        self, intent: object, *, issued_at_ms: int, expires_at_ms: int
    ) -> dict[str, object]:
        value = verify_resolve_intent_v1(intent)
        if type(issued_at_ms) is not int or type(expires_at_ms) is not int:
            raise VaultProtocolMockError("invalid ticket time")
        intent_expiry = value["created_at_ms"] + value["ttl_seconds"] * 1000
        if not value["created_at_ms"] <= issued_at_ms < expires_at_ms <= intent_expiry:
            raise VaultProtocolMockError("ticket lifetime exceeds intent")
        unsigned = {
            "schema": LEASE_TICKET_SCHEMA,
            "intent_sha256": value["record_sha256"],
            "nonce": value["nonce"],
            "namespace_id": value["namespace_id"],
            "vault_epoch": value["vault_epoch"],
            "issued_at_ms": issued_at_ms,
            "expires_at_ms": expires_at_ms,
            "use_count": 1,
        }
        signature = hmac.new(
            self._key,
            json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode(),
            hashlib.sha256,
        ).hexdigest()
        return seal_record({**unsigned, "controller_signature": signature})

    def verify_ticket(
        self, intent: object, ticket: object, *, now_ms: int
    ) -> dict[str, object]:
        value = verify_resolve_intent_v1(intent)
        signed = _verify_sealed(ticket, "vault lease ticket")
        expected = {
            "schema",
            "intent_sha256",
            "nonce",
            "namespace_id",
            "vault_epoch",
            "issued_at_ms",
            "expires_at_ms",
            "use_count",
            "controller_signature",
            "record_sha256",
        }
        if set(signed) != expected or signed["schema"] != LEASE_TICKET_SCHEMA:
            raise VaultProtocolMockError("vault lease ticket fields are not exact")
        if (
            type(signed["issued_at_ms"]) is not int
            or type(signed["expires_at_ms"]) is not int
        ):
            raise VaultProtocolMockError("invalid vault lease ticket time")
        if (
            signed["intent_sha256"] != value["record_sha256"]
            or signed["nonce"] != value["nonce"]
            or signed["namespace_id"] != value["namespace_id"]
            or signed["vault_epoch"] != value["vault_epoch"]
            or signed["use_count"] != 1
        ):
            raise VaultProtocolMockError("vault lease ticket binding mismatch")
        if (
            type(now_ms) is not int
            or not signed["issued_at_ms"] <= now_ms < signed["expires_at_ms"]
        ):
            raise VaultProtocolMockError("vault lease ticket expired or not active")
        unsigned = {
            key: item
            for key, item in signed.items()
            if key not in {"controller_signature", "record_sha256"}
        }
        expected_signature = hmac.new(
            self._key,
            json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode(),
            hashlib.sha256,
        ).hexdigest()
        signature = signed["controller_signature"]
        if type(signature) is not str or not hmac.compare_digest(
            signature, expected_signature
        ):
            raise VaultProtocolMockError("invalid controller signature")
        return signed

    def clear(self) -> None:
        for index in range(len(self._key)):
            self._key[index] = 0


@dataclass(frozen=True)
class ResolverPolicyV1:
    operation_id: str
    plan_sha256: str
    task_sha256: str
    worker_sha256: str
    authority_receipt_sha256: str
    ref_id: str
    namespace_id: str
    current_epoch: int
    current_revision: int
    audience: str
    sink_kind: str
    sink_instance_sha256: str
    incident_locked: bool = False


class AtomicNonceLedger:
    """A generated-fixture O_EXCL ledger; it is authority state, not audit."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(self.root, 0o700)

    def claim(self, nonce: str, ticket_sha256: str) -> dict[str, object]:
        _exact_nonce(nonce)
        _exact_hash(ticket_sha256, "ticket hash")
        path = self.root / nonce
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError as exc:
            raise VaultProtocolMockError("nonce already claimed") from exc
        try:
            payload = (ticket_sha256 + "\n").encode("ascii")
            os.write(fd, payload)
            os.fsync(fd)
        finally:
            os.close(fd)
        return seal_record(
            {
                "schema": CLAIM_RECEIPT_SCHEMA,
                "nonce": nonce,
                "ticket_sha256": ticket_sha256,
                "state": "CLAIMED_BEFORE_STORAGE_ACCESS",
            }
        )


def validate_policy_and_claim_v1(
    intent: object,
    ticket: object,
    *,
    controller_key: MockControllerKey,
    policy: ResolverPolicyV1,
    ledger: AtomicNonceLedger,
    now_ms: int,
) -> dict[str, object]:
    """Apply every local deny before atomically claiming the signed nonce."""

    value = verify_resolve_intent_v1(intent)
    signed = controller_key.verify_ticket(value, ticket, now_ms=now_ms)
    checks = {
        "operation_id": policy.operation_id,
        "plan_sha256": policy.plan_sha256,
        "task_sha256": policy.task_sha256,
        "worker_sha256": policy.worker_sha256,
        "authority_receipt_sha256": policy.authority_receipt_sha256,
        "ref_id": policy.ref_id,
        "namespace_id": policy.namespace_id,
        "vault_epoch": policy.current_epoch,
        "audience": policy.audience,
        "sink_kind": policy.sink_kind,
        "sink_instance_sha256": policy.sink_instance_sha256,
    }
    if policy.incident_locked:
        raise VaultProtocolMockError("local incident lock denies consumption")
    for field, expected in checks.items():
        if value[field] != expected:
            raise VaultProtocolMockError(f"local policy denies {field}")
    if value["minimum_revision"] > policy.current_revision:
        raise VaultProtocolMockError("local policy denies stale revision")
    return ledger.claim(value["nonce"], signed["record_sha256"])


class MockKeyringStore:
    """In-memory generated keyring with independent namespace/epoch keys."""

    def __init__(self) -> None:
        self._keys: dict[tuple[str, int], bytearray] = {}

    def generate(self, namespace_id: str, epoch: int) -> None:
        _exact_id(namespace_id, "namespace id")
        if type(epoch) is not int or epoch < 1:
            raise VaultProtocolMockError("invalid key epoch")
        identity = (namespace_id, epoch)
        if identity in self._keys:
            raise VaultProtocolMockError("namespace epoch key already exists")
        self._keys[identity] = bytearray(os.urandom(32))

    def _borrow(self, namespace_id: str, epoch: int) -> ZeroizingBuffer:
        try:
            return ZeroizingBuffer(self._keys[(namespace_id, epoch)])
        except KeyError as exc:
            raise VaultProtocolMockError("namespace epoch key is unavailable") from exc

    def keys_are_distinct_for_test(
        self, left: tuple[str, int], right: tuple[str, int]
    ) -> bool:
        """Test-only structural assertion; it never returns key bytes."""

        return not hmac.compare_digest(self._keys[left], self._keys[right])

    def destroy(self, namespace_id: str, epoch: int) -> None:
        key = self._keys.pop((namespace_id, epoch))
        for index in range(len(key)):
            key[index] = 0


class GeneratedVaultStorage:
    """Temp-root encrypted storage accepting only marked generated fixtures."""

    def __init__(self, root: Path, keyring: MockKeyringStore) -> None:
        self.root = root
        self.keyring = keyring
        self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(self.root, 0o700)

    def _existing_path(self, namespace_id: str, epoch: int, ref_id: str) -> Path:
        _exact_id(namespace_id, "namespace id")
        _exact_ref(ref_id)
        if type(epoch) is not int or epoch < 1:
            raise VaultProtocolMockError("invalid storage epoch")
        return self.root / f"{namespace_id}.epoch-{epoch}" / f"{ref_id}.json"

    def _path(self, namespace_id: str, epoch: int, ref_id: str) -> Path:
        path = self._existing_path(namespace_id, epoch, ref_id)
        namespace = path.parent
        namespace.mkdir(mode=0o700, exist_ok=True)
        os.chmod(namespace, 0o700)
        return path

    def put_generated(
        self,
        *,
        namespace_id: str,
        epoch: int,
        ref_id: str,
        revision: int,
        value: ZeroizingBuffer,
    ) -> Path:
        if type(revision) is not int or revision < 1:
            raise VaultProtocolMockError("invalid storage revision")
        try:
            view = value.internal_view()
            if not bytes(view).startswith(b"GENERATED_CANARY_ONLY:"):
                raise VaultProtocolMockError("storage accepts generated canaries only")
            aad_record = {
                "schema": MOCK_STORE_SCHEMA,
                "namespace_id": namespace_id,
                "epoch": epoch,
                "ref_id": ref_id,
                "revision": revision,
            }
            aad = json.dumps(aad_record, sort_keys=True, separators=(",", ":")).encode()
            nonce = os.urandom(12)
            with self.keyring._borrow(namespace_id, epoch) as key:
                ciphertext = AESGCM(bytes(key.internal_view())).encrypt(
                    nonce, bytes(view), aad
                )
            payload = {
                **aad_record,
                "nonce_b64": base64.b64encode(nonce).decode("ascii"),
                "ciphertext_b64": base64.b64encode(ciphertext).decode("ascii"),
            }
            path = self._path(namespace_id, epoch, ref_id)
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            try:
                os.write(
                    fd,
                    json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(),
                )
                os.fsync(fd)
            finally:
                os.close(fd)
            return path
        finally:
            value.clear()

    def _load_authenticated_generated(
        self, *, namespace_id: str, epoch: int, ref_id: str
    ) -> tuple[dict[str, object], ZeroizingBuffer]:
        path = self._existing_path(namespace_id, epoch, ref_id)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise VaultProtocolMockError("corrupt generated store") from exc
        exact = {
            "schema",
            "namespace_id",
            "epoch",
            "ref_id",
            "revision",
            "nonce_b64",
            "ciphertext_b64",
        }
        if set(payload) != exact or payload.get("schema") != MOCK_STORE_SCHEMA:
            raise VaultProtocolMockError("unsupported or corrupt generated store")
        if (
            payload["namespace_id"] != namespace_id
            or payload["epoch"] != epoch
            or payload["ref_id"] != ref_id
            or type(payload["revision"]) is not int
            or payload["revision"] < 1
        ):
            raise VaultProtocolMockError("generated store identity mismatch")
        aad_record = {
            "schema": payload["schema"],
            "namespace_id": payload["namespace_id"],
            "epoch": payload["epoch"],
            "ref_id": payload["ref_id"],
            "revision": payload["revision"],
        }
        aad = json.dumps(aad_record, sort_keys=True, separators=(",", ":")).encode()
        try:
            nonce = base64.b64decode(payload["nonce_b64"], validate=True)
            ciphertext = base64.b64decode(payload["ciphertext_b64"], validate=True)
            with self.keyring._borrow(namespace_id, epoch) as key:
                plaintext = ZeroizingBuffer(
                    AESGCM(bytes(key.internal_view())).decrypt(nonce, ciphertext, aad)
                )
            if not bytes(plaintext.internal_view()).startswith(
                b"GENERATED_CANARY_ONLY:"
            ):
                plaintext.clear()
                raise VaultProtocolMockError("stored value is not a generated canary")
            return payload, plaintext
        except (InvalidTag, ValueError, TypeError) as exc:
            raise VaultProtocolMockError(
                "generated store authentication failed"
            ) from exc

    def rotate_generated(
        self,
        *,
        namespace_id: str,
        old_epoch: int,
        new_epoch: int,
        ref_id: str,
        old_revision: int,
        new_revision: int,
        new_value: ZeroizingBuffer,
    ) -> dict[str, object]:
        """Consume the proposed value while attempting a generated rotation."""

        try:
            return self._rotate_generated(
                namespace_id=namespace_id,
                old_epoch=old_epoch,
                new_epoch=new_epoch,
                ref_id=ref_id,
                old_revision=old_revision,
                new_revision=new_revision,
                new_value=new_value,
            )
        finally:
            new_value.clear()

    def _rotate_generated(
        self,
        *,
        namespace_id: str,
        old_epoch: int,
        new_epoch: int,
        ref_id: str,
        old_revision: int,
        new_revision: int,
        new_value: ZeroizingBuffer,
    ) -> dict[str, object]:
        """Rotate generated fixture material and retain a non-secret tombstone."""

        if new_epoch <= old_epoch or new_revision <= old_revision:
            raise VaultProtocolMockError("rotation must advance epoch and revision")
        old_path = self._existing_path(namespace_id, old_epoch, ref_id)
        if not old_path.is_file():
            raise VaultProtocolMockError("rotation source is unavailable")
        old_payload, old_plaintext = self._load_authenticated_generated(
            namespace_id=namespace_id,
            epoch=old_epoch,
            ref_id=ref_id,
        )
        old_plaintext.clear()
        if old_payload["revision"] != old_revision:
            new_value.clear()
            raise VaultProtocolMockError("rotation source revision mismatch")
        if not bytes(new_value.internal_view()).startswith(b"GENERATED_CANARY_ONLY:"):
            new_value.clear()
            raise VaultProtocolMockError("storage accepts generated canaries only")

        new_path = self._existing_path(namespace_id, new_epoch, ref_id)
        rotations = self.root / "rotation-tombstones"
        tombstone = rotations / f"{ref_id}.epoch-{old_epoch}-to-{new_epoch}.json"
        if new_path.exists():
            new_value.clear()
            raise FileExistsError(new_path)
        if rotations.exists() and not rotations.is_dir():
            new_value.clear()
            raise FileExistsError(rotations)
        if tombstone.exists():
            new_value.clear()
            raise FileExistsError(tombstone)

        receipt = seal_record(
            {
                "schema": ROTATION_RECEIPT_SCHEMA,
                "namespace_id": namespace_id,
                "ref_id": ref_id,
                "old_epoch": old_epoch,
                "new_epoch": new_epoch,
                "old_revision": old_revision,
                "new_revision": new_revision,
                "old_state": "SUPERSEDED_CIPHERTEXT_RETAINED",
                "old_leases": "INVALIDATED",
            }
        )
        new_key_created = False
        new_path_created = False
        tombstone_created = False
        try:
            self.keyring.generate(namespace_id, new_epoch)
            new_key_created = True
            self.put_generated(
                namespace_id=namespace_id,
                epoch=new_epoch,
                ref_id=ref_id,
                revision=new_revision,
                value=new_value,
            )
            new_path_created = True
            rotations.mkdir(mode=0o700, exist_ok=True)
            os.chmod(rotations, 0o700)
            fd = os.open(tombstone, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            tombstone_created = True
            try:
                os.write(
                    fd,
                    json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode(),
                )
                os.fsync(fd)
            finally:
                os.close(fd)
            self.keyring.destroy(namespace_id, old_epoch)
            return receipt
        except Exception:
            if tombstone_created:
                tombstone.unlink(missing_ok=True)
            if new_path_created or new_path.exists():
                new_path.unlink(missing_ok=True)
                try:
                    new_path.parent.rmdir()
                except OSError:
                    pass
            if new_key_created:
                self.keyring.destroy(namespace_id, new_epoch)
            raise

    def verify_generated_for_test(
        self,
        *,
        namespace_id: str,
        epoch: int,
        ref_id: str,
        expected: bytes,
    ) -> bool:
        """Compare internally and return only a boolean, never plaintext."""

        try:
            _, plaintext = self._load_authenticated_generated(
                namespace_id=namespace_id, epoch=epoch, ref_id=ref_id
            )
            return hmac.compare_digest(plaintext.internal_view(), expected)
        finally:
            if "plaintext" in locals():
                plaintext.clear()


def classify_crash_v1(
    *, last_durable_state: str, state_uncertain: bool = False
) -> dict[str, object]:
    """Apply monotonic exposure precedence to a generated crash fixture."""

    if last_durable_state not in _STATES:
        raise VaultProtocolMockError("invalid durable delivery state")
    attempted = _STATES.index(last_durable_state) >= _STATES.index("DELIVERY_ATTEMPTED")
    if attempted or state_uncertain:
        exposure = "POSSIBLE_EXPOSURE"
        action = "QUARANTINE_LOCK_AND_ROTATE_REQUIRED"
    else:
        exposure = "NOT_EXPOSED"
        action = "EXPIRE_UNUSED_LEASE"
    return seal_record(
        {
            "schema": CRASH_RECEIPT_SCHEMA,
            "last_durable_state": last_durable_state,
            "state_uncertain": state_uncertain,
            "exposure": exposure,
            "required_action": action,
        }
    )


def generated_now_ms() -> int:
    """Convenience for tests and demos; protocol callers should pin time."""

    return time.time_ns() // 1_000_000
