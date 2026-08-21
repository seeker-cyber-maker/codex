"""CLI for the offline terminal-companion event projector."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .projector import CompanionProjectionError, project_notifications


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Project exported Codex command notifications.")
    parser.add_argument("--input", required=True, help="JSON array exported by an approved capture path")
    args = parser.parse_args(argv)
    try:
        source = json.loads(Path(args.input).read_text(encoding="utf-8"))
        print(json.dumps(project_notifications(source), indent=2, sort_keys=True))
    except (OSError, json.JSONDecodeError, CompanionProjectionError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
