"""Bounded read-only host observations for operation-v2 descriptors.

The observer never invokes Codex, Git, a shell, hooks, plugins, MCP servers, or
providers. It does not read credentials or the ambient environment. A
successful bundle is evidence only and is always ``OBSERVED_NOT_QUALIFIED``.
"""

from __future__ import annotations

import errno
import hashlib
import json
import os
import re
import stat
import time
import unicodedata
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import PurePosixPath

from .cli_contract import CliContractError, validate_cli_contract

REQUEST_SCHEMA = "codex-house-host-observation-request/1"
GRAMMAR_SCHEMA = "codex-house-context-discovery-grammar/1"
POLICY_SCHEMA = "codex-house-host-observation-policy/1"
CLI_CAPTURE_SCHEMA = "codex-house-cli-capture/1"
BUNDLE_SCHEMA = "codex-house-host-observation/1"
RECEIPT_SCHEMA = "codex-house-host-observation-verification/1"

CONTRIBUTOR_CLASSES = (
    "executable",
    "system_config",
    "enterprise_config",
    "user_config",
    "project_config",
    "session_flags",
    "project_instructions",
    "hooks",
    "exec_rules",
    "skills",
    "plugins",
    "applications",
    "mcp",
    "project_inputs",
    "environment",
)
CONFIG_PRECEDENCE = (
    "legacy_mdm",
    "legacy_managed_file",
    "session_flags",
    "project",
    "user_profile",
    "user",
    "enterprise_managed",
    "system",
)
SECRET_BASENAMES = (
    ".env",
    "auth.json",
    "credentials.json",
    "cookies.sqlite",
    "id_ed25519",
    "id_rsa",
)

_HASH = re.compile(r"^[0-9a-f]{64}$")
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")
_ENV_NAME = re.compile(r"^[A-Z][A-Z0-9_]{0,127}$")
_SECRET_ENV = re.compile(r"(?:TOKEN|KEY|SECRET|PASSWORD|COOKIE|AUTH)", re.IGNORECASE)
_SECRET_TEXT = re.compile(
    rb"(?i)(?:token|password|secret|api[_-]?key|authorization)\s*[:=]\s*['\"]?[^\s'\"]{8,}|"
    rb"bearer\s+[A-Za-z0-9._~+/=-]{8,}|BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY"
)


class HostObserverError(ValueError):
    """Raised when a sealed observer input or bundle fails closed."""


class _ObservationFailure(Exception):
    def __init__(self, state: str, code: str, entry_id: str | None = None):
        super().__init__(code)
        self.state = state
        self.code = code
        self.entry_id = entry_id


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _bytes_sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _copy(value: object) -> object:
    return json.loads(_canonical(value))


def _exact(value: object, fields: set[str], label: str) -> dict[str, object]:
    if type(value) is not dict or set(value) != fields:
        raise HostObserverError(f"{label} fields are not exact")
    return value


def _text(value: object, label: str, maximum: int = 4096) -> str:
    if type(value) is not str or not value or value != value.strip():
        raise HostObserverError(f"invalid {label}")
    if "\x00" in value or len(value.encode("utf-8")) > maximum:
        raise HostObserverError(f"invalid {label}")
    return value


def _raw_text(value: object, label: str, maximum: int) -> str:
    if type(value) is not str or not value.strip():
        raise HostObserverError(f"invalid {label}")
    if "\x00" in value or len(value.encode("utf-8")) > maximum:
        raise HostObserverError(f"invalid {label}")
    return value


def _identifier(value: object, label: str) -> str:
    result = _text(value, label, 128)
    if not _ID.fullmatch(result) or "*" in result:
        raise HostObserverError(f"invalid {label}")
    return result


def _digest(value: object, label: str) -> str:
    if type(value) is not str or not _HASH.fullmatch(value):
        raise HostObserverError(f"invalid {label}")
    return value


def _timestamp(value: object, label: str) -> datetime:
    rendered = _text(value, label, 40)
    if not rendered.endswith("Z"):
        raise HostObserverError(f"invalid {label}")
    try:
        parsed = datetime.fromisoformat(f"{rendered[:-1]}+00:00")
    except ValueError as exc:
        raise HostObserverError(f"invalid {label}") from exc
    if parsed.tzinfo != timezone.utc:
        raise HostObserverError(f"invalid {label}")
    return parsed


def _path(value: object, label: str) -> str:
    rendered = _text(value, label)
    pure = PurePosixPath(rendered)
    if (
        not rendered.startswith("/")
        or rendered == "/"
        or "//" in rendered
        or str(pure) != rendered
        or unicodedata.normalize("NFC", rendered) != rendered
        or any(part in {".", ".."} for part in pure.parts)
    ):
        raise HostObserverError(f"invalid {label}")
    return rendered


def _sealed(
    record: object, label: str, hash_field: str = "record_sha256"
) -> dict[str, object]:
    if type(record) is not dict or hash_field not in record:
        raise HostObserverError(f"invalid {label}")
    supplied = _digest(record[hash_field], f"{label} hash")
    unsigned = {key: value for key, value in record.items() if key != hash_field}
    if _sha256(unsigned) != supplied:
        raise HostObserverError(f"{label} hash mismatch")
    return record


def _validate_policy(policy: object) -> dict[str, object]:
    value = _sealed(policy, "observation policy")
    _exact(
        value,
        {
            "schema",
            "policy_id",
            "allowed_contributor_classes",
            "allowed_nonsecret_environment_names",
            "secret_basenames",
            "secret_pattern_version",
            "record_sha256",
        },
        "observation policy",
    )
    if value["schema"] != POLICY_SCHEMA:
        raise HostObserverError("invalid observation policy schema")
    _identifier(value["policy_id"], "policy id")
    if value["allowed_contributor_classes"] != list(CONTRIBUTOR_CLASSES):
        raise HostObserverError("observation policy contributor classes differ")
    names = value["allowed_nonsecret_environment_names"]
    if type(names) is not list or len(names) != len(set(names)):
        raise HostObserverError("invalid nonsecret environment allowlist")
    for name in names:
        if (
            type(name) is not str
            or not _ENV_NAME.fullmatch(name)
            or _SECRET_ENV.search(name)
        ):
            raise HostObserverError("invalid nonsecret environment name")
    if value["secret_basenames"] != list(SECRET_BASENAMES):
        raise HostObserverError("secret basename policy may not be weakened")
    if value["secret_pattern_version"] != "builtin-secret-patterns/1":
        raise HostObserverError("invalid secret pattern version")
    return value


def _validate_capture(capture: object) -> dict[str, object]:
    value = _sealed(capture, "CLI capture", "capture_sha256")
    _exact(
        value,
        {
            "schema",
            "producer_id",
            "version_output",
            "exec_help_output",
            "capture_sha256",
        },
        "CLI capture",
    )
    if value["schema"] != CLI_CAPTURE_SCHEMA:
        raise HostObserverError("invalid CLI capture schema")
    _identifier(value["producer_id"], "CLI capture producer")
    _raw_text(value["version_output"], "CLI version capture", 4096)
    _raw_text(value["exec_help_output"], "CLI help capture", 131_072)
    return value


def _validate_grammar(grammar: object) -> dict[str, object]:
    value = _sealed(grammar, "discovery grammar")
    _exact(
        value,
        {
            "schema",
            "grammar_id",
            "source_revision",
            "config_precedence",
            "project_config_policy",
            "instruction_precedence",
            "instruction_byte_budget",
            "symlink_policy",
            "dynamic_source_policy",
            "contributor_states",
            "entries",
            "session_flags",
            "environment_projection",
            "record_sha256",
        },
        "discovery grammar",
    )
    if value["schema"] != GRAMMAR_SCHEMA:
        raise HostObserverError("invalid discovery grammar schema")
    _identifier(value["grammar_id"], "grammar id")
    _digest(value["source_revision"], "grammar source revision")
    if value["config_precedence"] != list(CONFIG_PRECEDENCE):
        raise HostObserverError("configuration precedence differs")
    if value["project_config_policy"] != "CONTENT_ADDRESSED_REQUIRED":
        raise HostObserverError("project config may not be claimed ignored")
    if value["instruction_precedence"] != [
        "AGENTS.override.md",
        "AGENTS.md",
        "CONFIGURED_FALLBACK",
    ]:
        raise HostObserverError("instruction precedence differs")
    if (
        type(value["instruction_byte_budget"]) is not int
        or not 1 <= value["instruction_byte_budget"] <= 1_000_000
    ):
        raise HostObserverError("invalid instruction byte budget")
    if (
        value["symlink_policy"] != "REFUSE"
        or value["dynamic_source_policy"] != "EXPLICIT_OR_INCOMPLETE"
    ):
        raise HostObserverError("unsafe discovery policy")

    states = _exact(
        value["contributor_states"], set(CONTRIBUTOR_CLASSES), "contributor states"
    )
    asserted = {"session_flags", "environment"}
    for name, state_value in states.items():
        allowed = (
            {"ASSERTED_INPUT_ONLY"} if name in asserted else {"FILE_ENTRIES", "ABSENT"}
        )
        if state_value not in allowed:
            raise HostObserverError(f"invalid contributor state for {name}")

    entries = value["entries"]
    if type(entries) is not list:
        raise HostObserverError("grammar entries must be a list")
    entry_ids: set[str] = set()
    normalized_paths: set[str] = set()
    counts = {name: 0 for name in CONTRIBUTOR_CLASSES}
    for item in entries:
        entry = _exact(
            item,
            {"entry_id", "contributor_class", "path", "expectation", "content_policy"},
            "grammar entry",
        )
        entry_id = _identifier(entry["entry_id"], "entry id")
        contributor = entry["contributor_class"]
        if contributor not in states or contributor in asserted:
            raise HostObserverError("invalid grammar contributor")
        entry_path = _path(entry["path"], "grammar entry path")
        folded = unicodedata.normalize("NFC", entry_path).casefold()
        if entry_id in entry_ids or folded in normalized_paths:
            raise HostObserverError("duplicate or colliding grammar entry")
        entry_ids.add(entry_id)
        normalized_paths.add(folded)
        expectation = entry["expectation"]
        content_policy = entry["content_policy"]
        if expectation == "REGULAR_FILE":
            if content_policy not in {"TEXT_NO_SECRETS", "OPAQUE_EXECUTABLE"}:
                raise HostObserverError("invalid regular-file content policy")
            if content_policy == "OPAQUE_EXECUTABLE" and contributor != "executable":
                raise HostObserverError("opaque bytes are limited to the executable")
        elif expectation == "ABSENT":
            if content_policy != "NONE":
                raise HostObserverError("absent entry has content policy")
        elif expectation == "SECRET_PRESENCE_ONLY":
            if content_policy != "PRESENCE_ONLY":
                raise HostObserverError("sensitive entry has content policy")
        else:
            raise HostObserverError("invalid grammar expectation")
        if states[contributor] == "ABSENT" and expectation != "ABSENT":
            raise HostObserverError("absent contributor has a present entry")
        if states[contributor] == "FILE_ENTRIES" and expectation == "ABSENT":
            raise HostObserverError("file contributor has only an absent candidate")
        counts[contributor] += 1
    for name in set(CONTRIBUTOR_CLASSES) - asserted:
        if counts[name] == 0:
            raise HostObserverError(f"missing contributor entry for {name}")
    if counts["executable"] != 1:
        raise HostObserverError("grammar must contain one executable")

    flags = value["session_flags"]
    if type(flags) is not list or len(flags) != len(set(flags)):
        raise HostObserverError("invalid session flags")
    for flag in flags:
        _text(flag, "session flag", 4096)
    if "--ignore-project-config" in flags:
        raise HostObserverError("unsupported project-config ignore claim")

    projection = value["environment_projection"]
    if type(projection) is not list:
        raise HostObserverError("invalid environment projection")
    projected_names: set[str] = set()
    for item in projection:
        env = _exact(
            item, {"name", "classification", "value", "present"}, "environment entry"
        )
        name = env["name"]
        if (
            type(name) is not str
            or not _ENV_NAME.fullmatch(name)
            or name in projected_names
        ):
            raise HostObserverError("invalid environment name")
        projected_names.add(name)
        if type(env["present"]) is not bool:
            raise HostObserverError("invalid environment presence")
        if _SECRET_ENV.search(name):
            if (
                env["classification"] != "SECRET_PRESENCE_ONLY"
                or env["value"] is not None
            ):
                raise HostObserverError("secret environment value is forbidden")
        elif (
            env["classification"] != "NON_SECRET_ASSERTED"
            or type(env["value"]) is not str
        ):
            raise HostObserverError("invalid nonsecret environment projection")
    return value


def _validate_request(request: object) -> dict[str, object]:
    value = _sealed(request, "observation request")
    _exact(
        value,
        {
            "schema",
            "request_id",
            "operation_id",
            "observed_at_utc",
            "expires_at_utc",
            "cwd",
            "workspace_boundary",
            "codex_home",
            "executable_path",
            "expected_executable_sha256",
            "cli_capture_sha256",
            "discovery_grammar_sha256",
            "observation_policy_sha256",
            "read_roots",
            "limits",
            "record_sha256",
        },
        "observation request",
    )
    if value["schema"] != REQUEST_SCHEMA:
        raise HostObserverError("invalid observation request schema")
    _identifier(value["request_id"], "request id")
    _identifier(value["operation_id"], "operation id")
    if _timestamp(value["observed_at_utc"], "observed_at_utc") >= _timestamp(
        value["expires_at_utc"], "expires_at_utc"
    ):
        raise HostObserverError("invalid observation interval")
    cwd = _path(value["cwd"], "cwd")
    workspace = _path(value["workspace_boundary"], "workspace boundary")
    _path(value["codex_home"], "codex home")
    _path(value["executable_path"], "executable path")
    if not _contains(workspace, cwd):
        raise HostObserverError("cwd escapes workspace boundary")
    _digest(value["expected_executable_sha256"], "expected executable hash")
    _digest(value["cli_capture_sha256"], "CLI capture hash")
    _digest(value["discovery_grammar_sha256"], "discovery grammar hash")
    _digest(value["observation_policy_sha256"], "observation policy hash")
    roots = value["read_roots"]
    if type(roots) is not list or not roots:
        raise HostObserverError("read roots must be non-empty")
    checked_roots = [_path(root, "read root") for root in roots]
    folded_roots = {root.casefold() for root in checked_roots}
    if len(checked_roots) != len(set(checked_roots)) or len(folded_roots) != len(
        checked_roots
    ):
        raise HostObserverError("duplicate read roots")
    limits = _exact(
        value["limits"],
        {
            "max_entries",
            "max_total_bytes",
            "max_file_bytes",
            "max_depth",
            "max_retries",
            "max_duration_ms",
        },
        "observation limits",
    )
    ceilings = {
        "max_entries": 100_000,
        "max_total_bytes": 1_000_000_000,
        "max_file_bytes": 100_000_000,
        "max_depth": 128,
        "max_retries": 2,
        "max_duration_ms": 300_000,
    }
    for name, ceiling in ceilings.items():
        item = limits[name]
        minimum = 0 if name == "max_retries" else 1
        if type(item) is not int or not minimum <= item <= ceiling:
            raise HostObserverError(f"invalid {name}")
    return value


def _contains(root: str, child: str) -> bool:
    root_parts = PurePosixPath(root).parts
    child_parts = PurePosixPath(child).parts
    return child_parts[: len(root_parts)] == root_parts


def _matching_root(path: str, roots: list[str]) -> str:
    matches = [root for root in roots if _contains(root, path)]
    if not matches:
        raise _ObservationFailure(
            "INCOMPLETE_CONTEXT_CLOSURE", "PATH_OUTSIDE_READ_ROOT"
        )
    return max(matches, key=len)


def _metadata(info: os.stat_result) -> dict[str, int]:
    return {
        "device": info.st_dev,
        "inode": info.st_ino,
        "mode": info.st_mode,
        "link_count": info.st_nlink,
        "size": info.st_size,
        "mtime_ns": info.st_mtime_ns,
        "ctime_ns": info.st_ctime_ns,
    }


def _open_absolute_directory(path: str) -> int:
    required = ("O_DIRECTORY", "O_NOFOLLOW", "O_CLOEXEC")
    if any(not hasattr(os, name) for name in required):
        raise _ObservationFailure("OBSERVER_ERROR", "NOFOLLOW_UNAVAILABLE")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    fd = os.open("/", flags)
    try:
        for part in PurePosixPath(path).parts[1:]:
            next_fd = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        return fd
    except BaseException:
        os.close(fd)
        raise


def _open_parent(root: str, path: str) -> tuple[int, str, int]:
    root_fd = _open_absolute_directory(root)
    root_device = os.fstat(root_fd).st_dev
    relative = PurePosixPath(path).relative_to(PurePosixPath(root))
    parts = relative.parts
    if not parts:
        os.close(root_fd)
        raise _ObservationFailure("INCOMPLETE_CONTEXT_CLOSURE", "ROOT_IS_NOT_FILE")
    fd = root_fd
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    try:
        for part in parts[:-1]:
            next_fd = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = next_fd
            if os.fstat(fd).st_dev != root_device:
                raise _ObservationFailure(
                    "INCOMPLETE_CONTEXT_CLOSURE", "MOUNT_CROSSING"
                )
        return fd, parts[-1], len(parts)
    except BaseException:
        os.close(fd)
        raise


def _secret_path(path: str) -> bool:
    return PurePosixPath(path).name.casefold() in {
        name.casefold() for name in SECRET_BASENAMES
    }


class _Budget:
    def __init__(self, limits: Mapping[str, int]):
        self.limits = limits
        self.entries = 0
        self.total_bytes = 0
        self.started_ns = time.monotonic_ns()

    def checkpoint(
        self, *, entry: bool = False, byte_count: int = 0, depth: int = 0
    ) -> None:
        if entry:
            self.entries += 1
        self.total_bytes += byte_count
        elapsed_ms = (time.monotonic_ns() - self.started_ns) // 1_000_000
        if (
            self.entries > self.limits["max_entries"]
            or self.total_bytes > self.limits["max_total_bytes"]
            or depth > self.limits["max_depth"]
            or elapsed_ms > self.limits["max_duration_ms"]
        ):
            raise _ObservationFailure("LIMIT_EXCEEDED", "OBSERVATION_LIMIT_EXCEEDED")


def _presence_record(
    entry: Mapping[str, object], root: str, budget: _Budget
) -> dict[str, object]:
    path = entry["path"]
    try:
        parent_fd, name, depth = _open_parent(root, path)  # type: ignore[arg-type]
    except FileNotFoundError:
        budget.checkpoint(entry=True)
        if entry["expectation"] == "ABSENT":
            return {
                "entry_id": entry["entry_id"],
                "contributor_class": entry["contributor_class"],
                "path": path,
                "expectation": entry["expectation"],
                "status": "CONFIRMED_ABSENT",
                "metadata": None,
                "content_sha256": None,
                "present": False,
            }
        return {
            "entry_id": entry["entry_id"],
            "contributor_class": entry["contributor_class"],
            "path": path,
            "expectation": entry["expectation"],
            "status": "SENSITIVE_PRESENCE_ONLY",
            "metadata": None,
            "content_sha256": None,
            "present": False,
        }
    try:
        budget.checkpoint(entry=True, depth=depth)
        try:
            info = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            present = True
            if stat.S_ISLNK(info.st_mode):
                raise _ObservationFailure(
                    "INCOMPLETE_CONTEXT_CLOSURE", "SYMLINK_REFUSED", entry["entry_id"]
                )  # type: ignore[arg-type]
        except FileNotFoundError:
            present = False
    finally:
        os.close(parent_fd)
    expected_absent = entry["expectation"] == "ABSENT"
    if expected_absent and present:
        raise _ObservationFailure(
            "INCOMPLETE_CONTEXT_CLOSURE", "EXPECTED_ABSENT_PRESENT", entry["entry_id"]
        )  # type: ignore[arg-type]
    status = "CONFIRMED_ABSENT" if expected_absent else "SENSITIVE_PRESENCE_ONLY"
    return {
        "entry_id": entry["entry_id"],
        "contributor_class": entry["contributor_class"],
        "path": path,
        "expectation": entry["expectation"],
        "status": status,
        "metadata": None,
        "content_sha256": None,
        "present": present,
    }


def _read_record(
    entry: Mapping[str, object],
    root: str,
    request: Mapping[str, object],
    budget: _Budget,
) -> dict[str, object]:
    path = entry["path"]
    entry_id = entry["entry_id"]
    if _secret_path(path):  # type: ignore[arg-type]
        raise _ObservationFailure(
            "INCOMPLETE_SECRET_DEPENDENCY", "SECRET_PATH_REFUSED", entry_id
        )  # type: ignore[arg-type]
    parent_fd, name, depth = _open_parent(root, path)  # type: ignore[arg-type]
    file_fd: int | None = None
    try:
        parent_before = _metadata(os.fstat(parent_fd))
        budget.checkpoint(entry=True, depth=depth)
        flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK
        file_fd = os.open(name, flags, dir_fd=parent_fd)
        before = os.fstat(file_fd)
        if not stat.S_ISREG(before.st_mode):
            raise _ObservationFailure(
                "INCOMPLETE_CONTEXT_CLOSURE", "SPECIAL_FILE_REFUSED", entry_id
            )  # type: ignore[arg-type]
        if before.st_dev != os.fstat(parent_fd).st_dev:
            raise _ObservationFailure(
                "INCOMPLETE_CONTEXT_CLOSURE", "MOUNT_CROSSING", entry_id
            )  # type: ignore[arg-type]
        if before.st_nlink != 1:
            raise _ObservationFailure(
                "INCOMPLETE_CONTEXT_CLOSURE", "HARD_LINK_REFUSED", entry_id
            )  # type: ignore[arg-type]
        if before.st_size > request["limits"]["max_file_bytes"]:  # type: ignore[index]
            raise _ObservationFailure("LIMIT_EXCEEDED", "FILE_LIMIT_EXCEEDED", entry_id)  # type: ignore[arg-type]
        chunks: list[bytes] = []
        remaining = request["limits"]["max_file_bytes"] + 1  # type: ignore[index,operator]
        while remaining:
            chunk = os.read(file_fd, min(65_536, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
            budget.checkpoint(byte_count=len(chunk), depth=depth)
        if remaining == 0 and os.read(file_fd, 1):
            raise _ObservationFailure("LIMIT_EXCEEDED", "FILE_LIMIT_EXCEEDED", entry_id)  # type: ignore[arg-type]
        content = b"".join(chunks)
        after = os.fstat(file_fd)
        final_entry = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        parent_after = _metadata(os.fstat(parent_fd))
        if (
            _metadata(before) != _metadata(after)
            or (after.st_dev, after.st_ino) != (final_entry.st_dev, final_entry.st_ino)
            or parent_before != parent_after
        ):
            raise _ObservationFailure(
                "UNSTABLE_RETRY_REQUIRED", "DESCRIPTOR_IDENTITY_CHANGED", entry_id
            )  # type: ignore[arg-type]
        if entry["content_policy"] == "TEXT_NO_SECRETS":
            try:
                content.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise _ObservationFailure(
                    "INCOMPLETE_CONTEXT_CLOSURE", "NON_UTF8_CONTEXT", entry_id
                ) from exc  # type: ignore[arg-type]
            if _SECRET_TEXT.search(content):
                raise _ObservationFailure(
                    "INCOMPLETE_SECRET_DEPENDENCY", "SECRET_CONTENT_REFUSED", entry_id
                )  # type: ignore[arg-type]
        digest = _bytes_sha256(content)
        if (
            entry["contributor_class"] == "executable"
            and digest != request["expected_executable_sha256"]
        ):
            raise _ObservationFailure(
                "INCOMPLETE_CONTEXT_CLOSURE", "EXECUTABLE_HASH_MISMATCH", entry_id
            )  # type: ignore[arg-type]
        return {
            "entry_id": entry_id,
            "contributor_class": entry["contributor_class"],
            "path": path,
            "expectation": entry["expectation"],
            "status": "OBSERVED_REGULAR_FILE",
            "metadata": _metadata(after),
            "content_sha256": digest,
            "present": True,
        }
    except OSError as exc:
        if exc.errno in {errno.ELOOP, errno.ENOTDIR}:
            raise _ObservationFailure(
                "INCOMPLETE_CONTEXT_CLOSURE", "SYMLINK_REFUSED", entry_id
            ) from exc  # type: ignore[arg-type]
        raise
    finally:
        if file_fd is not None:
            os.close(file_fd)
        os.close(parent_fd)


def _descriptor_set(
    request: Mapping[str, object],
    grammar: Mapping[str, object],
    capture: Mapping[str, object],
    observations: list[dict[str, object]],
) -> dict[str, object]:
    executable = next(
        item for item in observations if item["contributor_class"] == "executable"
    )
    try:
        contract = validate_cli_contract(
            executable_sha256=executable["content_sha256"],  # type: ignore[arg-type]
            version_output=capture["version_output"],  # type: ignore[arg-type]
            exec_help_output=capture["exec_help_output"],  # type: ignore[arg-type]
        )
    except CliContractError as exc:
        raise _ObservationFailure(
            "REJECTED_REQUEST", "CLI_CAPTURE_CONTRACT_MISMATCH"
        ) from exc
    workspace_items = [
        item
        for item in observations
        if _contains(request["workspace_boundary"], item["path"])
    ]  # type: ignore[arg-type]
    effective_items = [
        item for item in observations if item["contributor_class"] != "executable"
    ]
    descriptors: dict[str, object] = {
        "executable": {
            "schema": "codex-house-observed-executable/1",
            "path": executable["path"],
            "content_sha256": executable["content_sha256"],
            "metadata": executable["metadata"],
            "state": "NOT_EXECUTED",
        },
        "cli_capture": {
            "schema": "codex-house-observed-cli-capture/1",
            "capture_sha256": capture["capture_sha256"],
            "contract_sha256": contract["contract_sha256"],
            "producer_id": capture["producer_id"],
            "binding_state": "ASSERTED_BINDING_ONLY",
        },
        "workspace": {
            "schema": "codex-house-observed-workspace/1",
            "cwd": request["cwd"],
            "boundary": request["workspace_boundary"],
            "identity_sha256": _sha256(workspace_items),
            "project_config_policy": "CONTENT_ADDRESSED_REQUIRED",
        },
        "effective_context": {
            "schema": "codex-house-effective-context-inventory/1",
            "grammar_sha256": grammar["record_sha256"],
            "inventory_sha256": _sha256(effective_items),
            "config_precedence": _copy(grammar["config_precedence"]),
            "contributor_states": _copy(grammar["contributor_states"]),
            "session_flags": _copy(grammar["session_flags"]),
            "environment_projection": _copy(grammar["environment_projection"]),
            "state": "CONTENT_ADDRESSED_AND_ASSERTED_INPUTS_ONLY",
        },
    }
    return {**descriptors, "descriptors_sha256": _sha256(descriptors)}


def _validate_input_bindings(
    request: Mapping[str, object],
    grammar: Mapping[str, object],
    policy: Mapping[str, object],
    capture: Mapping[str, object],
) -> None:
    bindings = (
        (
            "discovery grammar",
            request["discovery_grammar_sha256"],
            grammar["record_sha256"],
        ),
        (
            "observation policy",
            request["observation_policy_sha256"],
            policy["record_sha256"],
        ),
        ("CLI capture", request["cli_capture_sha256"], capture["capture_sha256"]),
    )
    for label, supplied, expected in bindings:
        if supplied != expected:
            raise HostObserverError(f"request {label} binding mismatch")
    allowed_names = set(policy["allowed_nonsecret_environment_names"])  # type: ignore[arg-type]
    for item in grammar["environment_projection"]:  # type: ignore[union-attr]
        if (
            item["classification"] == "NON_SECRET_ASSERTED"
            and item["name"] not in allowed_names
        ):
            raise HostObserverError("environment projection is not allowed by policy")
    roots = request["read_roots"]
    for entry in grammar["entries"]:  # type: ignore[union-attr]
        if not any(_contains(root, entry["path"]) for root in roots):
            raise HostObserverError("grammar entry escapes request read roots")
    executable_entries = [
        entry
        for entry in grammar["entries"]  # type: ignore[union-attr]
        if entry["contributor_class"] == "executable"
    ]
    if executable_entries[0]["path"] != request["executable_path"]:
        raise HostObserverError("executable path binding mismatch")


def _bundle(
    request: Mapping[str, object],
    grammar: Mapping[str, object],
    policy: Mapping[str, object],
    capture: Mapping[str, object],
    *,
    state: str,
    attempt_count: int,
    observations: list[dict[str, object]],
    descriptors: dict[str, object] | None,
    failures: list[dict[str, object]],
) -> dict[str, object]:
    unsigned = {
        "schema": BUNDLE_SCHEMA,
        "request_id": request["request_id"],
        "operation_id": request["operation_id"],
        "request_sha256": request["record_sha256"],
        "grammar_sha256": grammar["record_sha256"],
        "policy_sha256": policy["record_sha256"],
        "cli_capture_sha256": capture["capture_sha256"],
        "state": state,
        "attempt_count": attempt_count,
        "observations": observations,
        "descriptors": descriptors,
        "failures": failures,
        "dispatch": "NOT_ATTEMPTED",
        "authority": "NOT_GRANTED",
    }
    return {**unsigned, "record_sha256": _sha256(unsigned)}


def observe_host_v1(
    request: Mapping[str, object],
    grammar: Mapping[str, object],
    policy: Mapping[str, object],
    cli_capture: Mapping[str, object],
) -> dict[str, object]:
    """Observe only request-authorized files and return an inert sealed bundle."""

    request_value = _validate_request(request)
    grammar_value = _validate_grammar(grammar)
    policy_value = _validate_policy(policy)
    capture_value = _validate_capture(cli_capture)
    _validate_input_bindings(request_value, grammar_value, policy_value, capture_value)
    roots = request_value["read_roots"]

    attempts = request_value["limits"]["max_retries"] + 1  # type: ignore[index,operator]
    for attempt in range(1, attempts + 1):
        budget = _Budget(request_value["limits"])  # type: ignore[arg-type]
        observations: list[dict[str, object]] = []
        try:
            for entry in grammar_value["entries"]:  # type: ignore[union-attr]
                root = _matching_root(entry["path"], roots)  # type: ignore[arg-type]
                if entry["expectation"] in {"ABSENT", "SECRET_PRESENCE_ONLY"}:
                    observations.append(_presence_record(entry, root, budget))
                else:
                    observations.append(
                        _read_record(entry, root, request_value, budget)
                    )
            instruction_bytes = sum(
                item["metadata"]["size"]
                for item in observations
                if item["contributor_class"] == "project_instructions"
                and item["metadata"] is not None
            )
            if instruction_bytes > grammar_value["instruction_byte_budget"]:
                raise _ObservationFailure(
                    "LIMIT_EXCEEDED", "INSTRUCTION_BUDGET_EXCEEDED"
                )
            descriptors = _descriptor_set(
                request_value, grammar_value, capture_value, observations
            )
            return _bundle(
                request_value,
                grammar_value,
                policy_value,
                capture_value,
                state="OBSERVED_NOT_QUALIFIED",
                attempt_count=attempt,
                observations=observations,
                descriptors=descriptors,
                failures=[],
            )
        except _ObservationFailure as exc:
            if exc.state == "UNSTABLE_RETRY_REQUIRED" and attempt < attempts:
                continue
            failure = {"code": exc.code, "entry_id": exc.entry_id}
            return _bundle(
                request_value,
                grammar_value,
                policy_value,
                capture_value,
                state=exc.state,
                attempt_count=attempt,
                observations=[],
                descriptors=None,
                failures=[failure],
            )
        except FileNotFoundError:
            failure = {"code": "REQUIRED_FILE_MISSING", "entry_id": None}
            return _bundle(
                request_value,
                grammar_value,
                policy_value,
                capture_value,
                state="INCOMPLETE_CONTEXT_CLOSURE",
                attempt_count=attempt,
                observations=[],
                descriptors=None,
                failures=[failure],
            )
        except OSError as exc:
            if exc.errno in {errno.ELOOP, errno.ENOTDIR}:
                state = "INCOMPLETE_CONTEXT_CLOSURE"
                code = "SYMLINK_REFUSED"
            else:
                state = "OBSERVER_ERROR"
                code = f"OS_ERROR_{exc.errno}"
            failure = {"code": code, "entry_id": None}
            return _bundle(
                request_value,
                grammar_value,
                policy_value,
                capture_value,
                state=state,
                attempt_count=attempt,
                observations=[],
                descriptors=None,
                failures=[failure],
            )
    raise AssertionError("bounded attempt loop did not return")


def _verify_observation(
    entry: Mapping[str, object], observed: object
) -> dict[str, object]:
    value = _exact(
        observed,
        {
            "entry_id",
            "contributor_class",
            "path",
            "expectation",
            "status",
            "metadata",
            "content_sha256",
            "present",
        },
        "observation record",
    )
    for field in ("entry_id", "contributor_class", "path", "expectation"):
        if value[field] != entry[field]:
            raise HostObserverError("observation entry binding mismatch")
    if type(value["present"]) is not bool:
        raise HostObserverError("invalid observation presence")
    if entry["expectation"] == "REGULAR_FILE":
        if value["status"] != "OBSERVED_REGULAR_FILE" or value["present"] is not True:
            raise HostObserverError("regular observation state mismatch")
        metadata = _exact(
            value["metadata"],
            {"device", "inode", "mode", "link_count", "size", "mtime_ns", "ctime_ns"},
            "file metadata",
        )
        if any(type(item) is not int or item < 0 for item in metadata.values()):
            raise HostObserverError("invalid file metadata")
        if not stat.S_ISREG(metadata["mode"]) or metadata["link_count"] != 1:
            raise HostObserverError("inadmissible file metadata")
        _digest(value["content_sha256"], "observed content hash")
    else:
        expected_status = (
            "CONFIRMED_ABSENT"
            if entry["expectation"] == "ABSENT"
            else "SENSITIVE_PRESENCE_ONLY"
        )
        if (
            value["status"] != expected_status
            or value["metadata"] is not None
            or value["content_sha256"] is not None
        ):
            raise HostObserverError("presence-only observation mismatch")
        if entry["expectation"] == "ABSENT" and value["present"] is not False:
            raise HostObserverError("absent entry is present")
    return value


def verify_host_observation_v1(
    request: Mapping[str, object],
    grammar: Mapping[str, object],
    policy: Mapping[str, object],
    cli_capture: Mapping[str, object],
    bundle: Mapping[str, object],
) -> dict[str, object]:
    """Purely verify snapshot structure, content hashes, and input bindings."""

    request_value = _validate_request(request)
    grammar_value = _validate_grammar(grammar)
    policy_value = _validate_policy(policy)
    capture_value = _validate_capture(cli_capture)
    _validate_input_bindings(request_value, grammar_value, policy_value, capture_value)
    value = _sealed(bundle, "observation bundle")
    _exact(
        value,
        {
            "schema",
            "request_id",
            "operation_id",
            "request_sha256",
            "grammar_sha256",
            "policy_sha256",
            "cli_capture_sha256",
            "state",
            "attempt_count",
            "observations",
            "descriptors",
            "failures",
            "dispatch",
            "authority",
            "record_sha256",
        },
        "observation bundle",
    )
    expected_bindings = (
        ("schema", BUNDLE_SCHEMA),
        ("request_id", request_value["request_id"]),
        ("operation_id", request_value["operation_id"]),
        ("request_sha256", request_value["record_sha256"]),
        ("grammar_sha256", grammar_value["record_sha256"]),
        ("policy_sha256", policy_value["record_sha256"]),
        ("cli_capture_sha256", capture_value["capture_sha256"]),
        ("dispatch", "NOT_ATTEMPTED"),
        ("authority", "NOT_GRANTED"),
    )
    if any(value[field] != expected for field, expected in expected_bindings):
        raise HostObserverError("observation bundle binding mismatch")
    attempts = value["attempt_count"]
    if (
        type(attempts) is not int
        or not 1 <= attempts <= request_value["limits"]["max_retries"] + 1
    ):  # type: ignore[index,operator]
        raise HostObserverError("invalid observation attempt count")
    if type(value["observations"]) is not list or type(value["failures"]) is not list:
        raise HostObserverError("invalid observation result lists")
    if value["state"] == "OBSERVED_NOT_QUALIFIED":
        if value["failures"] or type(value["descriptors"]) is not dict:
            raise HostObserverError("successful observation contains failure state")
        entries = grammar_value["entries"]
        if len(value["observations"]) != len(entries):  # type: ignore[arg-type]
            raise HostObserverError("observation closure mismatch")
        observations = [
            _verify_observation(entry, observed)
            for entry, observed in zip(entries, value["observations"], strict=True)  # type: ignore[arg-type]
        ]
        try:
            expected_descriptors = _descriptor_set(
                request_value, grammar_value, capture_value, observations
            )
        except _ObservationFailure as exc:
            raise HostObserverError(
                "CLI capture cannot verify a success bundle"
            ) from exc
        if value["descriptors"] != expected_descriptors:
            raise HostObserverError("observation descriptor mismatch")
        state = "HOST_OBSERVATION_VERIFIED_NOT_QUALIFIED"
    elif value["state"] in {
        "INCOMPLETE_CONTEXT_CLOSURE",
        "INCOMPLETE_SECRET_DEPENDENCY",
        "UNSTABLE_RETRY_REQUIRED",
        "LIMIT_EXCEEDED",
        "REJECTED_REQUEST",
        "OBSERVER_ERROR",
    }:
        if (
            value["observations"]
            or value["descriptors"] is not None
            or len(value["failures"]) != 1
        ):
            raise HostObserverError("negative observation exposes partial descriptors")
        failure = _exact(
            value["failures"][0], {"code", "entry_id"}, "observation failure"
        )  # type: ignore[index]
        _text(failure["code"], "failure code", 128)
        if failure["entry_id"] is not None:
            _identifier(failure["entry_id"], "failure entry id")
        state = "HOST_OBSERVATION_FAILURE_VERIFIED"
    else:
        raise HostObserverError("invalid observation terminal state")
    unsigned = {
        "schema": RECEIPT_SCHEMA,
        "state": state,
        "claim_ceiling": "STRUCTURE_CONTENT_AND_BINDINGS_ONLY",
        "observation_sha256": value["record_sha256"],
        "dispatch": "NOT_ATTEMPTED",
        "authority": "NOT_GRANTED",
    }
    return {**unsigned, "receipt_sha256": _sha256(unsigned)}
