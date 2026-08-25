"""Independent S1 known-answer and static-containment check.

This validation helper is run evidence, not production code.  It reads only the
accepted public F1 fixture and candidate source, then emits a compact receipt.
"""

from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from house.task_spine.recovery_checkpoint import verify_checkpoint


F1 = ROOT / "house/workflow/runs/20260825T015729Z-recovery-checkpoint-oracle/attempt-a"
SOURCE = ROOT / "house/task_spine/recovery_checkpoint.py"
FIXTURE_SHA256 = "0d52a694cf3e5c681c40faee2ff577fc8ac07c01222c59c6722c0a14ecedc25e"
RECEIPT_SHA256 = "7222f1e7ba1e1b314b8e2620e9405f4fa2df629e7d4389939db7749b918ccf9f"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if sha256(F1 / "fixture.json") != FIXTURE_SHA256:
        raise SystemExit("F1 fixture hash mismatch")
    fixture = json.loads((F1 / "fixture.json").read_text(encoding="utf-8"))
    expected = json.loads((F1 / "expected_receipt.canonical.json").read_text(encoding="utf-8"))
    first = verify_checkpoint(
        fixture["signed_checkpoint_envelope"], fixture["expected_descriptor"], fixture["ledger_summary"]
    )
    second = verify_checkpoint(
        fixture["signed_checkpoint_envelope"], fixture["expected_descriptor"], fixture["ledger_summary"]
    )
    if first != expected or second != expected or first["receipt_sha256"] != RECEIPT_SHA256:
        raise SystemExit("candidate receipt mismatch")
    source = SOURCE.read_text(encoding="utf-8")
    imports = {
        alias.name
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imports |= {
        node.module
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom) and node.module
    }
    forbidden = {"os", "pathlib", "sqlite3", "subprocess", "socket", "time", "datetime"}
    if not imports.isdisjoint(forbidden) or any(
        token in source for token in ("fixture_generator", "derive_test_scalar", "sign_digest", "authority_stage0.p256")
    ):
        raise SystemExit("candidate source containment mismatch")
    print(json.dumps({
        "schema": "dream-house-s1-independent-verification/1",
        "result": "PASS",
        "fixture_sha256": FIXTURE_SHA256,
        "expected_receipt_sha256": RECEIPT_SHA256,
        "candidate_source_sha256": sha256(SOURCE),
        "whole_receipt_equal": True,
        "repeat_equal": True,
        "source_graph_contained": True,
        "authority": "NOT_GRANTED",
        "dispatch": "NOT_ATTEMPTED",
        "hardware": "NOT_ACCESSED",
        "runtime_admission": "NOT_ATTEMPTED"
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
