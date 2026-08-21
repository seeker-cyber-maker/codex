"""Compact offline CLI for the v0 task-spine fixture."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .core import TaskSpine


def _emit(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Exercise the offline Dream House task spine.")
    parser.add_argument("--db", required=True, help="explicit SQLite database path; native Codex state is never used")
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo", help="create and admit one offline candidate fixture")
    demo.add_argument("--summary", default="review this provenance claim")
    commands.add_parser("rebuild", help="rebuild and print the read model from the canonical journal")
    args = parser.parse_args(argv)
    spine = TaskSpine(Path(args.db))
    try:
        if args.command == "rebuild":
            _emit(spine.rebuild_read_model())
            return 0
        spine.create_work_item("demo-work", "Offline task-spine demonstration")
        spine.create_task_packet("demo-task", "demo-work", args.summary)
        spine.append_worker_buffer("demo-buffer", "demo-task", "demo-record", "Offline fixture report")
        spine.seal_worker_buffer("demo-buffer")
        spine.seal_result_envelope("demo-envelope", "demo-task", "demo-buffer", "fixture:report", "complete")
        spine.create_import_proposal("demo-proposal", "demo-task", "demo-envelope")
        authorization = spine.authorize_import("demo-proposal", "demo-lead")
        spine.admit_candidate("demo-proposal", actor="trusted_writer", admission_basis_sha256=authorization["event_sha256"])
        _emit(spine.rebuild_read_model())
        return 0
    finally:
        spine.close()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
