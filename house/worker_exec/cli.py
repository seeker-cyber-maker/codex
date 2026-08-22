"""Terminal-only preparation surface for sealed no-dispatch worker operations."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .controller import WorkerControllerError, WorkerOperationController
from .operation import WorkerExecError, prepare_operation


def _object_from_json(path: str) -> Mapping[str, object]:
    try:
        value: Any = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("task card JSON cannot be read") from exc
    if not isinstance(value, dict):
        raise TypeError("task card JSON must contain one object")
    return value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codex-house-worker",
        description="Seal one no-dispatch worker operation from a task card.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser(
        "prepare", help="prepare and persist a no-dispatch operation"
    )
    prepare.add_argument("--task-card", required=True, help="canonical task-card JSON")
    prepare.add_argument(
        "--controller-db",
        required=True,
        help="explicit operation-controller SQLite path",
    )
    prepare.add_argument(
        "--operation-id", required=True, help="stable operation idempotency key"
    )
    prepare.add_argument(
        "--workspace", required=True, help="absolute read-only workspace"
    )
    prepare.add_argument(
        "--output-root", required=True, help="absolute controlled output root"
    )
    prepare.add_argument(
        "--codex-path", required=True, help="absolute sealed Codex executable"
    )
    prepare.add_argument(
        "--wall-seconds", type=int, default=600, help="hard cap from 1 to 3600 seconds"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        record = prepare_operation(
            _object_from_json(args.task_card),
            operation_id=args.operation_id,
            workspace=args.workspace,
            output_root=args.output_root,
            codex_path=args.codex_path,
            wall_seconds=args.wall_seconds,
        )
        controller = WorkerOperationController(args.controller_db)
        try:
            entry = controller.prepare(record)
        finally:
            controller.close()
    except (TypeError, ValueError, WorkerExecError, WorkerControllerError) as exc:
        parser.error(str(exc))
    receipt = {
        "schema": "codex-house-worker-operation-prepare-receipt/1",
        "state": entry["state"],
        "operation_id": record["operation_id"],
        "record_sha256": record["record_sha256"],
        "controller_entry": entry["state"],
        "dispatch": "NOT_ATTEMPTED",
        "live_dispatch": record["live_dispatch"],
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
