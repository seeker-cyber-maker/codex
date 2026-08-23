"""Keyboard-first CLI for the offline Dream House worker relay."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from house.task_spine.readonly import TaskSpineReadonlyError, load_task_cards_readonly
from house.terminal_companion import LoopbackViewerError

from .core import Relay, RelayError
from .directory import RelayDirectory, RelayDirectoryError
from .operator_board_bundle import (
    OperatorBoardBundleError,
    write_operator_board_bundle,
)
from .operator_board_export import (
    OperatorBoardExportError,
    write_operator_board_export,
)
from .operator_board_viewer import (
    OperatorBoardViewerError,
    prepare_operator_board_viewer,
)
from .snapshot_inventory import (
    OperatorSnapshotInventoryError,
    inspect_operator_snapshot_inventory,
)


def _emit(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def _load_json(path: str, parser: argparse.ArgumentParser, label: str) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(f"cannot load {label}: {exc}")


def _load_text(path: str, parser: argparse.ArgumentParser, label: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        parser.error(f"cannot load {label}: {exc}")


def _load_absolute_json(
    path: str, parser: argparse.ArgumentParser, label: str
) -> tuple[Any, Path, str]:
    target = Path(path)
    if not target.is_absolute():
        parser.error(f"{label} path must be absolute")
    if not target.is_file() or target.is_symlink():
        parser.error(f"{label} must be an existing regular file")
    try:
        encoded = target.read_bytes()
        return (
            json.loads(encoded.decode("utf-8")),
            target,
            hashlib.sha256(encoded).hexdigest(),
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        parser.error(f"cannot load {label}: {exc}")


def _source_projections(
    args: argparse.Namespace, parser: argparse.ArgumentParser
) -> tuple[list[object], list[object], dict[str, object]]:
    registrations: list[object] = []
    relay_source: dict[str, object] = {
        "state": "NOT_SUPPLIED",
        "path": None,
        "input_sha256": None,
        "count": 0,
    }
    if args.relay_registrations:
        value, path, digest = _load_absolute_json(
            args.relay_registrations, parser, "relay registrations"
        )
        if not isinstance(value, list):
            parser.error("relay registrations must be a JSON array")
        registrations = value
        relay_source = {
            "state": "NAMED_JSON",
            "path": str(path),
            "input_sha256": digest,
            "count": len(registrations),
        }

    task_cards: list[object] = []
    task_source: dict[str, object] = {
        "state": "NOT_SUPPLIED",
        "path": None,
        "journal_sha256": None,
        "count": 0,
    }
    if args.task_spine_db:
        target = Path(args.task_spine_db)
        if not target.is_absolute():
            parser.error("task-spine database path must be absolute")
        try:
            task_cards, journal_sha256 = load_task_cards_readonly(target)
        except TaskSpineReadonlyError as exc:
            parser.error(str(exc))
        task_source = {
            "state": "READ_ONLY_NAMED_DATABASE",
            "path": str(target),
            "journal_sha256": journal_sha256,
            "count": len(task_cards),
        }
    return (
        registrations,
        task_cards,
        {
            "relay_registrations": relay_source,
            "task_spine": task_source,
        },
    )


def _relay(args: argparse.Namespace) -> Relay:
    return Relay(Path(args.relay_db))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Use the offline, no-dispatch Dream House worker relay."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    address = commands.add_parser(
        "directory-address", help="look up one static recipient"
    )
    address.add_argument("--catalog-receipt", required=True)
    address.add_argument("--recipient-id", required=True)
    capability = commands.add_parser(
        "directory-capability", help="list static recipients declaring one capability"
    )
    capability.add_argument("--catalog-receipt", required=True)
    capability.add_argument("--capability", required=True)

    submit = commands.add_parser("submit", help="queue one validated envelope")
    submit.add_argument("--relay-db", required=True)
    submit.add_argument("--input", required=True, help="UTF-8 JSON envelope path")
    status = commands.add_parser("status", help="read one envelope status")
    status.add_argument("--relay-db", required=True)
    status.add_argument("--envelope-id", required=True)
    receive = commands.add_parser("receive", help="record offline recipient retrieval")
    receive.add_argument("--relay-db", required=True)
    receive.add_argument("--recipient-id", required=True)
    receive.add_argument("--limit", type=int, default=1)
    acknowledge = commands.add_parser("acknowledge", help="record one acknowledgement")
    acknowledge.add_argument("--relay-db", required=True)
    acknowledge.add_argument("--recipient-id", required=True)
    acknowledge.add_argument("--envelope-id", required=True)
    acknowledge.add_argument("--message", required=True)
    verify = commands.add_parser("verify-journal", help="verify relay journal hashes")
    verify.add_argument("--relay-db", required=True)
    inventory = commands.add_parser(
        "snapshot-inventory",
        help="inspect explicitly listed frozen snapshot-envelope paths",
    )
    inventory.add_argument(
        "--input",
        required=True,
        help="UTF-8 JSON array of one to 32 absolute envelope paths",
    )
    export_board = commands.add_parser(
        "export-operator-board",
        help="write one frozen operator board to a new explicit output path",
    )
    export_board.add_argument(
        "--operator-snapshot",
        required=True,
        help="UTF-8 frozen operator snapshot HTML path",
    )
    export_board.add_argument(
        "--inventory-board",
        required=True,
        help="UTF-8 frozen snapshot inventory HTML path",
    )
    export_board.add_argument(
        "--output",
        required=True,
        help="new absolute operator-board HTML path",
    )
    build_board = commands.add_parser(
        "build-operator-board",
        help="write one new sealed offline operator-board bundle from named sources",
    )
    build_board.add_argument(
        "--output-dir",
        required=True,
        help="new absolute directory for the complete operator-board bundle",
    )
    build_board.add_argument(
        "--relay-registrations",
        help="optional absolute JSON array of frozen relay-preview registrations",
    )
    build_board.add_argument(
        "--task-spine-db",
        help="optional absolute existing task-spine database opened read-only",
    )
    start_board_viewer = commands.add_parser(
        "start-operator-board-viewer",
        help="manually start one bounded loopback preview for one completed export",
    )
    start_board_viewer.add_argument(
        "--output",
        required=True,
        help="absolute completed operator-board HTML export path",
    )

    args = parser.parse_args(argv)
    try:
        if args.command.startswith("directory-"):
            directory = RelayDirectory(
                _load_json(args.catalog_receipt, parser, "catalog receipt")
            )
            if args.command == "directory-address":
                _emit(directory.address(args.recipient_id))
            else:
                _emit(directory.find_capability(args.capability))
            return 0
        if args.command == "snapshot-inventory":
            _emit(
                inspect_operator_snapshot_inventory(
                    _load_json(args.input, parser, "snapshot-envelope path list")
                )
            )
            return 0
        if args.command == "export-operator-board":
            _emit(
                write_operator_board_export(
                    args.output,
                    _load_text(
                        args.operator_snapshot, parser, "frozen operator snapshot"
                    ),
                    _load_text(args.inventory_board, parser, "frozen inventory board"),
                )
            )
            return 0
        if args.command == "build-operator-board":
            registrations, task_cards, sources = _source_projections(args, parser)
            _emit(
                write_operator_board_bundle(
                    args.output_dir, registrations, task_cards, sources
                )
            )
            return 0
        if args.command == "start-operator-board-viewer":
            viewer = prepare_operator_board_viewer(args.output)
            grant = viewer.start()
            print(f"One-time local URL: {grant.url}", flush=True)
            _emit(viewer.wait())
            return 0

        relay = _relay(args)
        try:
            if args.command == "submit":
                _emit(relay.submit(_load_json(args.input, parser, "relay envelope")))
            elif args.command == "status":
                _emit(relay.get(args.envelope_id))
            elif args.command == "receive":
                _emit(relay.receive(args.recipient_id, limit=args.limit))
            elif args.command == "acknowledge":
                _emit(
                    relay.acknowledge(args.recipient_id, args.envelope_id, args.message)
                )
            else:
                _emit(
                    {
                        "journal_valid": relay.verify_journal(),
                        "runtime_disposition": "NOT_ATTEMPTED",
                    }
                )
            return 0
        finally:
            relay.close()
    except (
        OperatorBoardExportError,
        OperatorBoardBundleError,
        OperatorBoardViewerError,
        OperatorSnapshotInventoryError,
        LoopbackViewerError,
        RelayDirectoryError,
        RelayError,
    ) as exc:
        parser.error(str(exc))
    return 2  # pragma: no cover


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
