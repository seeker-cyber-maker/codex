"""Small no-dispatch command line interface for the route policy."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from .policy import list_routes, route_task, select_manual_route


def _task_from_args(args: argparse.Namespace, parser: argparse.ArgumentParser) -> dict[str, object]:
    raw = args.task_json
    if args.task_file:
        try:
            raw = Path(args.task_file).read_text(encoding="utf-8")
        except OSError as exc:
            parser.error(f"cannot read --task-file: {exc}")
    try:
        task = json.loads(raw)
    except json.JSONDecodeError as exc:
        parser.error(f"task packet is not JSON: {exc.msg}")
    if not isinstance(task, dict):
        parser.error("task packet must be a JSON object")
    return task


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit a deterministic Dream House routing receipt.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--task-json", help="task packet as one JSON object")
    source.add_argument("--task-file", help="UTF-8 JSON task packet path")
    source.add_argument("--list-routes", action="store_true", help="list automatic and manual-only routes")
    source.add_argument("--manual-route", help="resolve one explicit manual route without dispatch")
    args = parser.parse_args(argv)
    if args.list_routes:
        print(json.dumps(list_routes(), indent=2, sort_keys=True))
        return 0
    if args.manual_route:
        try:
            receipt = select_manual_route(args.manual_route)
        except ValueError as exc:
            parser.error(str(exc))
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0
    receipt = route_task(_task_from_args(args, parser))
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised through module invocation
    raise SystemExit(main())
