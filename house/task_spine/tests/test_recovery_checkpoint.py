"""Known-answer and containment tests for the pure checkpoint verifier."""

from __future__ import annotations

import ast
import base64
import copy
import hashlib
import json
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.utils import (
    decode_dss_signature,
    encode_dss_signature,
)

from house.authority_stage0.canonical import canonical_bytes
from house.authority_stage0.profile import b64u_encode
from house.task_spine.recovery_checkpoint import (
    RecoveryCheckpointError,
    verify_checkpoint,
)


RUN_ROOT = Path(__file__).resolve().parents[2] / "workflow" / "runs"
FIXTURE_PATH = (
    RUN_ROOT / "20260825T015729Z-recovery-checkpoint-oracle" / "attempt-a" / "fixture.json"
)
SOURCE_PATH = Path(__file__).resolve().parents[1] / "recovery_checkpoint.py"
P256_ORDER = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551


def fixture() -> dict[str, object]:
    with FIXTURE_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def inputs() -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    value = fixture()
    return (
        copy.deepcopy(value["signed_checkpoint_envelope"]),
        copy.deepcopy(value["expected_descriptor"]),
        copy.deepcopy(value["ledger_summary"]),
    )


def refresh(value: dict[str, object], field: str) -> None:
    unsigned = dict(value)
    del unsigned[field]
    value[field] = hashlib.sha256(canonical_bytes(unsigned)).hexdigest()


class RecoveryCheckpointTests(unittest.TestCase):
    def assert_refused(self, envelope: object, descriptor: object, summary: object) -> None:
        with self.assertRaises(RecoveryCheckpointError):
            verify_checkpoint(envelope, descriptor, summary)

    def test_f1_whole_receipt_and_repeat(self) -> None:
        envelope, descriptor, summary = inputs()
        expected = fixture()["expected_receipt"]
        first = verify_checkpoint(envelope, descriptor, summary)
        second = verify_checkpoint(envelope, descriptor, summary)
        self.assertEqual(first, expected)
        self.assertEqual(second, expected)
        self.assertEqual(first, second)

    def test_closed_shapes_and_type_bounds_refuse(self) -> None:
        envelope, descriptor, summary = inputs()
        for target, field, value in (
            (envelope, "unknown", "x"),
            (descriptor, "unknown", "x"),
            (summary, "unknown", "x"),
            (envelope["unsigned_checkpoint"], "generation", True),
            (envelope["unsigned_checkpoint"], "entry_count", 65),
            (envelope["unsigned_checkpoint"], "checkpoint_sequence", 0),
            (envelope["unsigned_checkpoint"], "registry_id", "bad space"),
        ):
            changed = copy.deepcopy((envelope, descriptor, summary))
            if target is envelope:
                changed[0][field] = value
            elif target is descriptor:
                changed[1][field] = value
            elif target is summary:
                changed[2][field] = value
            else:
                changed[0]["unsigned_checkpoint"][field] = value
            self.assert_refused(*changed)

    def test_each_closed_object_field_is_required(self) -> None:
        envelope, descriptor, summary = inputs()
        for target_index, original in enumerate((envelope, descriptor, summary)):
            for field in original:
                changed = list(inputs())
                del changed[target_index][field]
                self.assert_refused(*changed)
        for field in envelope["unsigned_checkpoint"]:
            changed = list(inputs())
            del changed[0]["unsigned_checkpoint"][field]
            self.assert_refused(*changed)

    def test_digest_and_cross_object_substitutions_refuse(self) -> None:
        for target_index, path, value in (
            (1, ("descriptor_sha256",), "0" * 64),
            (2, ("summary_sha256",), "0" * 64),
            (0, ("unsigned_checkpoint", "checkpoint_binding_sha256"), "0" * 64),
            (1, ("assertion_sha256",), "0" * 64),
            (1, ("checkpoint_id",), "checkpoint:other"),
            (2, ("fencing_epoch",), 5),
            (0, ("unsigned_checkpoint", "recovery_key_epoch"), 3),
        ):
            changed = list(inputs())
            object_value = changed[target_index]
            for part in path[:-1]:
                object_value = object_value[part]
            object_value[path[-1]] = value
            self.assert_refused(*changed)

    def test_recomputed_descriptor_and_summary_splices_refuse(self) -> None:
        envelope, descriptor, summary = inputs()
        descriptor["checkpoint_id"] = "checkpoint:other"
        refresh(descriptor, "descriptor_sha256")
        self.assert_refused(envelope, descriptor, summary)
        envelope, descriptor, summary = inputs()
        summary["fencing_epoch"] = 5
        refresh(summary, "summary_sha256")
        self.assert_refused(envelope, descriptor, summary)

    def test_predecessor_signature_key_and_domain_refuse(self) -> None:
        for path, value in (
            (("unsigned_checkpoint", "predecessor_checkpoint_sha256"), None),
            (("unsigned_checkpoint", "context"), "wrong"),
            (("signature_der_b64u",), "AA"),
            (("public_spki_der_b64u",), "AA"),
        ):
            changed = list(inputs())
            object_value = changed[0]
            for part in path[:-1]:
                object_value = object_value[part]
            object_value[path[-1]] = value
            self.assert_refused(*changed)

    def test_valid_high_s_signature_refuses(self) -> None:
        envelope, descriptor, summary = inputs()
        encoded = envelope["signature_der_b64u"]
        raw = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
        r, low_s = decode_dss_signature(raw)
        envelope["signature_der_b64u"] = b64u_encode(encode_dss_signature(r, P256_ORDER - low_s))
        descriptor["assertion_sha256"] = hashlib.sha256(canonical_bytes(envelope)).hexdigest()
        refresh(descriptor, "descriptor_sha256")
        self.assert_refused(envelope, descriptor, summary)

    def test_source_graph_has_no_operational_or_fixture_generator_surface(self) -> None:
        tree = ast.parse(SOURCE_PATH.read_text(encoding="utf-8"))
        imported = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported |= {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        forbidden = {"os", "pathlib", "sqlite3", "subprocess", "socket", "time", "datetime"}
        self.assertTrue(imported.isdisjoint(forbidden), imported)
        source = SOURCE_PATH.read_text(encoding="utf-8")
        self.assertNotIn("fixture_generator", source)
        self.assertNotIn("derive_test_scalar", source)
        self.assertNotIn("sign_digest", source)
        self.assertNotIn("authority_stage0.p256", source)


if __name__ == "__main__":
    unittest.main()
