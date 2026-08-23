"""Offline, authority-neutral worker rendezvous relay."""

from .core import Relay, RelayError
from .dashboard_viewer import prepare_relay_dashboard_viewer
from .directory import RelayDirectory, RelayDirectoryError
from .operator_board import OperatorBoardError, render_operator_board_html
from .operator_inventory_view import (
    OperatorSnapshotInventoryViewError,
    render_operator_snapshot_inventory_html,
)
from .operator_preview import RelayPreviewCardError, render_relay_preview_card_html
from .operator_registration import build_relay_preview_registration
from .operator_snapshot import OperatorSnapshotError, render_operator_snapshot_html
from .preview_index import RelayPreviewIndexError, render_relay_preview_index_html
from .snapshot_descriptor import (
    OperatorSnapshotDescriptorError,
    build_operator_snapshot_descriptor,
    inspect_operator_snapshot_descriptor,
    verify_operator_snapshot_descriptor,
)
from .snapshot_envelope import (
    OperatorSnapshotEnvelopeError,
    inspect_operator_snapshot_envelope,
    write_operator_snapshot_envelope,
)
from .snapshot_inventory import (
    OperatorSnapshotInventoryError,
    inspect_operator_snapshot_inventory,
)
from .task_card_index import TaskCardIndexError, render_task_card_index_html

__all__ = [
    "OperatorBoardError",
    "OperatorSnapshotDescriptorError",
    "OperatorSnapshotEnvelopeError",
    "OperatorSnapshotError",
    "OperatorSnapshotInventoryError",
    "OperatorSnapshotInventoryViewError",
    "Relay",
    "RelayDirectory",
    "RelayDirectoryError",
    "RelayError",
    "RelayPreviewCardError",
    "RelayPreviewIndexError",
    "TaskCardIndexError",
    "build_operator_snapshot_descriptor",
    "build_relay_preview_registration",
    "inspect_operator_snapshot_descriptor",
    "inspect_operator_snapshot_envelope",
    "inspect_operator_snapshot_inventory",
    "prepare_relay_dashboard_viewer",
    "render_operator_board_html",
    "render_operator_snapshot_html",
    "render_operator_snapshot_inventory_html",
    "render_relay_preview_card_html",
    "render_relay_preview_index_html",
    "render_task_card_index_html",
    "verify_operator_snapshot_descriptor",
    "write_operator_snapshot_envelope",
]
