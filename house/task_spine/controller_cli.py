"""Offline CLI for the finite local task inbox/controller."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from .core import TaskSpine
from .inbox import TaskInbox


def _emit(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Exercise the offline Dream House task controller."
    )
    parser.add_argument(
        "--inbox-db", required=True, help="explicit local inbox SQLite path"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    enqueue = commands.add_parser(
        "enqueue", help="idempotently enqueue one raw JSON packet"
    )
    enqueue.add_argument("--enqueue-id", required=True)
    enqueue.add_argument("--input", required=True, help="UTF-8 JSON path")
    lease = commands.add_parser("lease", help="acquire one finite controller lease")
    lease.add_argument("--holder", required=True)
    lease.add_argument("--ttl", type=float, default=30.0)
    drain = commands.add_parser("drain-once", help="process at most one inbox record")
    drain.add_argument(
        "--spine-db", required=True, help="separate task-spine SQLite path"
    )
    drain.add_argument("--holder", required=True)
    drain.add_argument("--token", required=True)
    release = commands.add_parser(
        "release", help="release the current controller lease"
    )
    release.add_argument("--holder", required=True)
    release.add_argument("--token", required=True)
    commands.add_parser("status", help="print ordered inbox state")
    args = parser.parse_args(argv)
    inbox = TaskInbox(Path(args.inbox_db))
    try:
        if args.command == "enqueue":
            try:
                packet = json.loads(Path(args.input).read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                parser.error(f"cannot load inbox submission: {exc}")
            _emit(inbox.enqueue(args.enqueue_id, packet))
            return 0
        if args.command == "lease":
            _emit(inbox.acquire_controller(args.holder, ttl_seconds=args.ttl))
            return 0
        if args.command == "release":
            _emit(inbox.release_controller(args.holder, args.token))
            return 0
        if args.command == "status":
            _emit(inbox.entries())
            return 0
        spine = TaskSpine(Path(args.spine_db))
        try:
            _emit(inbox.drain_once(spine, holder=args.holder, fencing_token=args.token))
            return 0
        finally:
            spine.close()
    finally:
        inbox.close()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
