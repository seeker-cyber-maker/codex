"""CLI for the offline terminal-companion event projector."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .projector import CompanionProjectionError, project_jsonl, project_notifications


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Project exported Codex command notifications.")
    parser.add_argument("--input", required=True, help="JSON array or JSONL exported by an approved capture path")
    parser.add_argument("--jsonl", action="store_true", help="interpret input as append-only JSONL notifications")
    args = parser.parse_args(argv)
    try:
        source = Path(args.input).read_text(encoding="utf-8")
        cards = project_jsonl(source) if args.jsonl else project_notifications(json.loads(source))
        print(json.dumps(cards, indent=2, sort_keys=True))
    except (OSError, json.JSONDecodeError, CompanionProjectionError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
