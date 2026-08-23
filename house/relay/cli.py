"""Keyboard-first CLI for the offline Dream House worker relay."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from .core import Relay, RelayError
from .directory import RelayDirectory, RelayDirectoryError
from .operator_board_export import (
    OperatorBoardExportError,
    write_operator_board_export,
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
        OperatorSnapshotInventoryError,
        RelayDirectoryError,
        RelayError,
    ) as exc:
        parser.error(str(exc))
    return 2  # pragma: no cover


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
