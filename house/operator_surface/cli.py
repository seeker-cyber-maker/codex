"""Keyboard-first, no-dispatch interface to the shared command registry."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from typing import Any

from .registry import RegistryError, builtin_registry
from .task_enqueue import OperatorTaskEnqueueError, enqueue_task

SURFACES = ("agent", "dashboard", "iterm")


def _add_surface(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--surface", choices=SURFACES, help="filter by surface")


def _print_commands(commands: Sequence[Mapping[str, Any]]) -> None:
    if not commands:
        print("No commands matched.")
        return
    for command in commands:
        hotkey = command.get("hotkey") or "-"
        print(
            f"{hotkey:<14} {command['command_id']}\n"
            f"{'':14} {command['title']} — {command['description']}\n"
            f"{'':14} authority={command['authority']}"
        )


def _parse_key_values(
    values: Sequence[str], parser: argparse.ArgumentParser
) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for raw in values:
        name, separator, value = raw.partition("=")
        if not separator or not name or not value:
            parser.error(f"argument must be NAME=VALUE: {raw}")
        if name in parsed:
            parser.error(f"duplicate argument: {name}")
        parsed[name] = value
    return parsed


def _target_from_args(
    args: argparse.Namespace, parser: argparse.ArgumentParser
) -> dict[str, str] | None:
    if bool(args.target_kind) != bool(args.target_id):
        parser.error("--target-kind and --target-id must be supplied together")
    if not args.target_kind:
        return None
    return {"kind": args.target_kind, "id": args.target_id}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codex-house",
        description="Search Dream House commands or prepare a no-dispatch request.",
    )
    subparsers = parser.add_subparsers(dest="operation", required=True)

    list_parser = subparsers.add_parser("list", help="list declared commands")
    _add_surface(list_parser)
    list_parser.add_argument("--json", action="store_true", help="emit manifest JSON")

    search_parser = subparsers.add_parser("search", help="search commands")
    search_parser.add_argument("query", nargs="+", help="terms that must all match")
    _add_surface(search_parser)
    search_parser.add_argument("--json", action="store_true", help="emit result JSON")

    keys_parser = subparsers.add_parser("keys", help="show assigned key bindings")
    _add_surface(keys_parser)
    keys_parser.add_argument("--json", action="store_true", help="emit result JSON")

    prepare_parser = subparsers.add_parser(
        "prepare", help="prepare an unauthorized request"
    )
    prepare_parser.add_argument("command_id")
    prepare_parser.add_argument("--target-kind")
    prepare_parser.add_argument("--target-id")
    prepare_parser.add_argument(
        "--arg", action="append", default=[], metavar="NAME=VALUE"
    )

    submit_parser = subparsers.add_parser(
        "enqueue-task",
        help="validate and queue one task for later controller admission",
    )
    submit_parser.add_argument(
        "--inbox-db", required=True, help="explicit local inbox SQLite path"
    )
    submit_parser.add_argument(
        "--enqueue-id", required=True, help="caller-selected idempotency key"
    )
    submit_parser.add_argument(
        "--requested-by", required=True, help="asserted requester identity"
    )
    submit_parser.add_argument("--title", required=True, help="short task title")
    submit_parser.add_argument(
        "--summary", required=True, help="concrete bounded task objective"
    )
    submit_parser.add_argument(
        "--recipient",
        default="triage",
        choices=("triage", "coder", "reviewer", "specific_model"),
        help="requested task lane; this does not launch a worker",
    )
    submit_parser.add_argument(
        "--recipient-id",
        default="",
        help="required only with --recipient specific_model",
    )
    submit_parser.add_argument(
        "--case-type", default="", help="optional routing-advisory case type"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    registry = builtin_registry()

    if args.operation == "list":
        manifest = registry.manifest(surface=args.surface)
        if args.json:
            print(json.dumps(manifest, indent=2, sort_keys=True))
        else:
            _print_commands(manifest["commands"])
        return 0

    if args.operation == "search":
        commands = registry.search(" ".join(args.query), surface=args.surface)
        if args.json:
            print(json.dumps(commands, indent=2, sort_keys=True))
        else:
            _print_commands(commands)
        return 0 if commands else 1

    if args.operation == "keys":
        commands = [
            command
            for command in registry.manifest(surface=args.surface)["commands"]
            if command["hotkey"] is not None
        ]
        if args.json:
            print(json.dumps(commands, indent=2, sort_keys=True))
        else:
            _print_commands(commands)
        return 0

    if args.operation == "enqueue-task":
        try:
            receipt = enqueue_task(
                args.inbox_db,
                enqueue_id=args.enqueue_id,
                requested_by=args.requested_by,
                title=args.title,
                summary=args.summary,
                recipient=args.recipient,
                recipient_id=args.recipient_id,
                case_type=args.case_type,
            )
        except OperatorTaskEnqueueError as exc:
            parser.error(str(exc))
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0

    try:
        receipt = registry.prepare_request(
            args.command_id,
            target=_target_from_args(args, parser),
            arguments=_parse_key_values(args.arg, parser),
        )
    except RegistryError as exc:
        parser.error(str(exc))
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
