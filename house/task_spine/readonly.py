"""Read-only task-card projection for caller-named task-spine databases."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

from .core import TaskSpine, TaskSpineError


class TaskSpineReadonlyError(ValueError):
    """A named task-spine database cannot be safely read as a board source."""


def load_task_cards_readonly(
    database_path: str | Path,
) -> tuple[list[dict[str, Any]], str]:
    """Verify and project one existing journal without creating database state."""
    target = Path(database_path)
    if not target.is_absolute():
        raise TaskSpineReadonlyError("task-spine database path must be absolute")
    if not target.is_file() or target.is_symlink():
        raise TaskSpineReadonlyError(
            "task-spine database must be an existing regular file"
        )
    try:
        database = sqlite3.connect(f"{target.as_uri()}?mode=ro", uri=True)
    except sqlite3.Error as exc:
        raise TaskSpineReadonlyError(
            "task-spine database cannot be opened read-only"
        ) from exc

    spine = TaskSpine.__new__(TaskSpine)
    spine.path = target
    spine.db = database
    spine.db.row_factory = sqlite3.Row
    try:
        spine.verify_journal()
        events = spine.journal_events()
        cards = spine.task_cards()
    except (TaskSpineError, sqlite3.Error, json.JSONDecodeError) as exc:
        raise TaskSpineReadonlyError("task-spine journal cannot be read") from exc
    finally:
        spine.close()
    encoded = json.dumps(
        events, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return cards, hashlib.sha256(encoded).hexdigest()
