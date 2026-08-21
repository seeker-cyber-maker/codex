"""CLI for the offline terminal-companion event projector."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .display_batch import build_display_batch
from .projector import CompanionProjectionError, project_jsonl, project_notifications


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Project exported Codex command notifications."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="JSON array or JSONL exported by an approved capture path",
    )
    parser.add_argument(
        "--jsonl",
        action="store_true",
        help="interpret input as append-only JSONL notifications",
    )
    parser.add_argument(
        "--display-batch",
        action="store_true",
        help="wrap projected cards for a future local iTerm adapter",
    )
    parser.add_argument(
        "--sequence", type=int, help="non-negative display-batch sequence"
    )
    parser.add_argument(
        "--previous-batch-id", help="lowercase SHA-256 id of the previous display batch"
    )
    args = parser.parse_args(argv)
    try:
        source = Path(args.input).read_text(encoding="utf-8")
        cards = (
            project_jsonl(source)
            if args.jsonl
            else project_notifications(json.loads(source))
        )
        if args.display_batch:
            if args.sequence is None:
                parser.error("--display-batch requires --sequence")
            result = build_display_batch(
                cards,
                sequence=args.sequence,
                previous_batch_id=args.previous_batch_id,
            )
        else:
            if args.sequence is not None or args.previous_batch_id is not None:
                parser.error(
                    "--sequence and --previous-batch-id require --display-batch"
                )
            result = cards
        print(json.dumps(result, indent=2, sort_keys=True))
    except (OSError, json.JSONDecodeError, CompanionProjectionError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
