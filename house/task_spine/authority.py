"""Offline P-256 trust registry and signed task-enqueue gate.

This module stores public keys and append-only authorization evidence. Private
keys remain with the caller. It is a directly enrolled trust registry, not a
certificate authority and not an OS-enforced process boundary.
"""

from __future__ import annotations

import base64
import hashlib
import json
import sqlite3
import time
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

from .authority_crypto import (
    ALGORITHM,
    AUTHORIZED_ENQUEUE_SCHEMA,
    KNOWN_ACTIONS,
    MAX_CLOCK_SKEW_SECONDS,
    MAX_PROOF_LIFETIME_SECONDS,
    PROOF_FIELDS,
    PROOF_RECEIPT_SCHEMA,
    AuthorityError,
    canonical,
    decode_signature,
    enqueue_binding,
    identifier,
    key_id_for_public_key,
    load_public_key,
    prepare_unsigned_proof,
    public_key_der,
    revocation_binding,
    sha256_json,
)
from .inbox import TaskInbox


class AuthorityRegistry:
    """Append-only directly enrolled public-key trust registry."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self.path = Path(database_path)
        self._clock = time.time if clock is None else clock
        self.db = sqlite3.connect(self.path, timeout=5)
        self.db.row_factory = sqlite3.Row
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS authority_journal (
                sequence INTEGER PRIMARY KEY,
                kind TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                previous_sha256 TEXT,
                event_sha256 TEXT NOT NULL UNIQUE
            )"""
        )
        self.db.commit()

    def close(self) -> None:
        self.db.close()

    def bootstrap_key(
        self,
        principal_id: str,
        public_key: ec.EllipticCurvePublicKey,
        actions: Iterable[str],
        *,
        reason: str,
    ) -> dict[str, Any]:
        """Directly enroll the first public key into an empty registry."""
        principal_id = identifier(principal_id, "principal_id")
        action_list = sorted(set(actions))
        if not action_list or any(
            action not in KNOWN_ACTIONS for action in action_list
        ):
            raise AuthorityError(
                "INVALID_ACTION", "bootstrap actions must be known and non-empty"
            )
        if (
            not isinstance(reason, str)
            or not reason.strip()
            or len(reason.strip()) > 512
        ):
            raise AuthorityError("INVALID_FIELD", "reason must be 1 to 512 characters")
        public_der = public_key_der(public_key)
        key_id = key_id_for_public_key(public_key)
        self.db.execute("BEGIN IMMEDIATE")
        try:
            self.verify_journal()
            if any(
                event["kind"] == "authority.key.bootstrapped"
                for event in self._events()
            ):
                raise AuthorityError(
                    "BOOTSTRAP_CLOSED", "authority registry is already bootstrapped"
                )
            event = self._append_no_commit(
                "authority.key.bootstrapped",
                {
                    "principal_id": principal_id,
                    "key_id": key_id,
                    "algorithm": ALGORITHM,
                    "public_key_der_b64": base64.b64encode(public_der).decode("ascii"),
                    "actions": action_list,
                    "reason": reason.strip(),
                    "ceremony": "EXTERNAL_SETUP_ASSERTED",
                },
            )
            self.db.commit()
            return event
        except Exception:
            self.db.rollback()
            raise

    def authorize(
        self,
        proof: object,
        *,
        expected_action: str,
        expected_binding_sha256: str,
    ) -> dict[str, Any]:
        """Verify and consume one action-bound proof nonce."""
        try:
            self.db.execute("BEGIN IMMEDIATE")
            receipt = self._authorize_no_commit(
                proof,
                expected_action=expected_action,
                expected_binding_sha256=expected_binding_sha256,
            )
            self.db.commit()
            return receipt
        except AuthorityError as exc:
            self.db.rollback()
            self._record_rejection(proof, exc.code)
            raise
        except Exception:
            self.db.rollback()
            raise

    def revoke_key(
        self,
        proof: object,
        *,
        target_key_id: str,
        reason: str,
    ) -> dict[str, Any]:
        """Atomically consume a valid revocation proof and revoke one key."""
        binding = revocation_binding(target_key_id, reason)
        try:
            self.db.execute("BEGIN IMMEDIATE")
            receipt = self._authorize_no_commit(
                proof,
                expected_action="authority.revoke",
                expected_binding_sha256=binding,
            )
            keys = self._key_state()
            target = keys.get(target_key_id)
            if target is None:
                raise AuthorityError("UNKNOWN_KEY", "revocation target is unknown")
            if target["revoked"]:
                raise AuthorityError(
                    "KEY_REVOKED", "revocation target is already revoked"
                )
            event = self._append_no_commit(
                "authority.key.revoked",
                {
                    "target_key_id": target_key_id,
                    "reason": reason.strip(),
                    "authorized_by_key_id": receipt["key_id"],
                    "authorized_by_principal_id": receipt["principal_id"],
                    "proof_receipt_sha256": receipt["receipt_sha256"],
                },
            )
            self.db.commit()
            return event
        except AuthorityError as exc:
            self.db.rollback()
            self._record_rejection(proof, exc.code)
            raise
        except Exception:
            self.db.rollback()
            raise

    def verify_journal(self) -> bool:
        previous: str | None = None
        for event in self._events():
            if event["previous_sha256"] != previous:
                raise AuthorityError(
                    "JOURNAL_INVALID", "authority journal previous hash mismatch"
                )
            unsigned = {
                "schema": "codex-house-authority-event/1",
                "sequence": event["sequence"],
                "kind": event["kind"],
                "payload": event["payload"],
                "previous_sha256": previous,
            }
            if sha256_json(unsigned) != event["event_sha256"]:
                raise AuthorityError(
                    "JOURNAL_INVALID", "authority journal event hash mismatch"
                )
            previous = event["event_sha256"]
        return True

    def journal_events(self, kind: str = "") -> list[dict[str, Any]]:
        events = self._events()
        return [event for event in events if not kind or event["kind"] == kind]

    def key_status(self) -> list[dict[str, Any]]:
        """Return the derived public-key permission and revocation view."""
        self.verify_journal()
        return [
            {
                "principal_id": key["principal_id"],
                "key_id": key_id,
                "algorithm": ALGORITHM,
                "actions": sorted(key["actions"]),
                "revoked": key["revoked"],
                "bootstrapped_sequence": key["bootstrapped_sequence"],
            }
            for key_id, key in sorted(self._key_state().items())
        ]

    def _authorize_no_commit(
        self,
        proof: object,
        *,
        expected_action: str,
        expected_binding_sha256: str,
    ) -> dict[str, Any]:
        self.verify_journal()
        prepared = self._prepare_proof(proof)
        now = int(self._clock())
        if prepared["expires_at"] <= prepared["issued_at"]:
            raise AuthorityError("INVALID_TIME", "proof expiry must follow issuance")
        if prepared["expires_at"] - prepared["issued_at"] > MAX_PROOF_LIFETIME_SECONDS:
            raise AuthorityError("INVALID_TIME", "proof lifetime exceeds five minutes")
        if prepared["issued_at"] > now + MAX_CLOCK_SKEW_SECONDS:
            raise AuthorityError("NOT_YET_VALID", "proof issuance is in the future")
        if prepared["expires_at"] <= now:
            raise AuthorityError("EXPIRED", "proof has expired")
        keys = self._key_state()
        key = keys.get(prepared["key_id"])
        if key is None:
            raise AuthorityError("UNKNOWN_KEY", "proof key is not enrolled")
        if key["revoked"]:
            raise AuthorityError("KEY_REVOKED", "proof key is revoked")
        signature = decode_signature(prepared["signature_b64"])
        unsigned = {
            field: prepared[field] for field in PROOF_FIELDS - {"signature_b64"}
        }
        public_key = load_public_key(key["public_key_der"])
        try:
            public_key.verify(
                signature,
                canonical(unsigned).encode(),
                ec.ECDSA(hashes.SHA256()),
            )
        except InvalidSignature as exc:
            raise AuthorityError(
                "INVALID_SIGNATURE", "proof signature is invalid"
            ) from exc
        if key["principal_id"] != prepared["principal_id"]:
            raise AuthorityError(
                "PRINCIPAL_MISMATCH", "proof principal does not own the key"
            )
        if prepared["action"] not in key["actions"]:
            raise AuthorityError(
                "ACTION_DENIED", "key is not permitted for this action"
            )
        if prepared["action"] != expected_action:
            raise AuthorityError(
                "WRONG_ACTION", "proof action does not match requested action"
            )
        if prepared["binding_sha256"] != expected_binding_sha256:
            raise AuthorityError(
                "WRONG_BINDING", "proof binding does not match requested content"
            )
        if any(
            event["kind"] == "authority.proof.accepted"
            and event["payload"]["nonce"] == prepared["nonce"]
            for event in self._events()
        ):
            raise AuthorityError("REPLAY", "proof nonce was already accepted")
        proof_sha256 = sha256_json(prepared)
        unsigned_receipt = {
            "schema": PROOF_RECEIPT_SCHEMA,
            "state": "ACCEPTED",
            "principal_id": prepared["principal_id"],
            "key_id": prepared["key_id"],
            "action": prepared["action"],
            "binding_sha256": prepared["binding_sha256"],
            "nonce": prepared["nonce"],
            "proof_sha256": proof_sha256,
        }
        receipt = {
            **unsigned_receipt,
            "receipt_sha256": sha256_json(unsigned_receipt),
        }
        self._append_no_commit(
            "authority.proof.accepted",
            {
                "principal_id": prepared["principal_id"],
                "key_id": prepared["key_id"],
                "action": prepared["action"],
                "binding_sha256": prepared["binding_sha256"],
                "nonce": prepared["nonce"],
                "proof_sha256": proof_sha256,
                "receipt": receipt,
            },
        )
        return receipt

    def _prepare_proof(self, proof: object) -> dict[str, Any]:
        if not isinstance(proof, dict):
            raise AuthorityError("INVALID_SCHEMA", "authority proof must be an object")
        unknown = set(proof) - PROOF_FIELDS
        missing = PROOF_FIELDS - set(proof)
        if unknown:
            raise AuthorityError(
                "UNKNOWN_FIELD", "authority proof contains unknown fields"
            )
        if missing:
            raise AuthorityError("MISSING_FIELD", "authority proof is missing fields")
        prepared = dict(proof)
        unsigned = {
            field: prepared[field] for field in PROOF_FIELDS - {"signature_b64"}
        }
        prepare_unsigned_proof(unsigned)
        signature = prepared.get("signature_b64")
        if not isinstance(signature, str) or not signature or len(signature) > 256:
            raise AuthorityError("INVALID_SIGNATURE", "signature_b64 is invalid")
        return prepared

    def _key_state(self) -> dict[str, dict[str, Any]]:
        keys: dict[str, dict[str, Any]] = {}
        for event in self._events():
            payload = event["payload"]
            if event["kind"] == "authority.key.bootstrapped":
                keys[payload["key_id"]] = {
                    "principal_id": payload["principal_id"],
                    "actions": set(payload["actions"]),
                    "public_key_der": base64.b64decode(
                        payload["public_key_der_b64"], validate=True
                    ),
                    "revoked": False,
                    "bootstrapped_sequence": event["sequence"],
                }
            elif (
                event["kind"] == "authority.key.revoked"
                and payload["target_key_id"] in keys
            ):
                keys[payload["target_key_id"]]["revoked"] = True
        return keys

    def _record_rejection(self, proof: object, error_code: str) -> None:
        try:
            fingerprint = sha256_json(proof)
        except AuthorityError:
            fingerprint = hashlib.sha256(type(proof).__name__.encode()).hexdigest()
        self.db.execute("BEGIN IMMEDIATE")
        try:
            self.verify_journal()
            self._append_no_commit(
                "authority.proof.rejected",
                {"error_code": error_code, "proof_fingerprint_sha256": fingerprint},
            )
            self.db.commit()
        except AuthorityError as exc:
            self.db.rollback()
            if exc.code != "JOURNAL_INVALID":
                raise
        except Exception:
            self.db.rollback()
            raise

    def _events(self) -> list[dict[str, Any]]:
        return [
            {
                "sequence": int(row["sequence"]),
                "kind": row["kind"],
                "payload": json.loads(row["payload_json"]),
                "previous_sha256": row["previous_sha256"],
                "event_sha256": row["event_sha256"],
            }
            for row in self.db.execute(
                "SELECT * FROM authority_journal ORDER BY sequence"
            )
        ]

    def _append_no_commit(self, kind: str, payload: dict[str, Any]) -> dict[str, Any]:
        previous_row = self.db.execute(
            "SELECT event_sha256 FROM authority_journal ORDER BY sequence DESC LIMIT 1"
        ).fetchone()
        previous = None if previous_row is None else str(previous_row["event_sha256"])
        sequence = int(
            self.db.execute(
                "SELECT COALESCE(MAX(sequence), 0) + 1 FROM authority_journal"
            ).fetchone()[0]
        )
        unsigned = {
            "schema": "codex-house-authority-event/1",
            "sequence": sequence,
            "kind": kind,
            "payload": payload,
            "previous_sha256": previous,
        }
        event_sha256 = sha256_json(unsigned)
        self.db.execute(
            """INSERT INTO authority_journal(
                sequence, kind, payload_json, previous_sha256, event_sha256
            ) VALUES (?, ?, ?, ?, ?)""",
            (sequence, kind, canonical(payload), previous, event_sha256),
        )
        return {**unsigned, "event_sha256": event_sha256}


class AuthorizedTaskInbox:
    """Signature-gated producer surface over the existing local inbox."""

    def __init__(self, registry: AuthorityRegistry, inbox: TaskInbox) -> None:
        if registry.path.resolve() == inbox.path.resolve():
            raise AuthorityError(
                "INVALID_STORAGE", "authority and inbox databases must be separate"
            )
        self.registry = registry
        self.inbox = inbox

    def enqueue(
        self,
        proof: object,
        *,
        enqueue_id: str,
        submission: object,
    ) -> dict[str, Any]:
        binding = enqueue_binding(enqueue_id, submission)
        authority_receipt = self.registry.authorize(
            proof,
            expected_action="inbox.enqueue",
            expected_binding_sha256=binding,
        )
        inbox_entry = self.inbox.enqueue(enqueue_id, submission)
        unsigned = {
            "schema": AUTHORIZED_ENQUEUE_SCHEMA,
            "state": inbox_entry["state"],
            "enqueue_id": inbox_entry["enqueue_id"],
            "submission_sha256": inbox_entry["submission_sha256"],
            "principal_id": authority_receipt["principal_id"],
            "key_id": authority_receipt["key_id"],
            "authority_receipt_sha256": authority_receipt["receipt_sha256"],
            "dispatch": "NOT_ATTEMPTED",
        }
        return {
            **unsigned,
            "receipt_sha256": sha256_json(unsigned),
            "authority_receipt": authority_receipt,
            "inbox_entry": inbox_entry,
        }
