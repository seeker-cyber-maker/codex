"""Deterministic static inspection for a future signed native candidate.

This module invokes only Apple's code-signature inspection tool. It never runs,
loads, links, or signals either candidate artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import plistlib
import re
import stat
import subprocess
import tempfile
from collections.abc import Callable, Mapping
from pathlib import Path, PurePosixPath
from typing import Any

POLICY_SCHEMA = "dream-house-canary-signing-policy/2"
QUALIFIED_STATE = "QUALIFIED_STATIC_ARTIFACTS_NO_LAUNCH"
REFUSED_STATE = "NOT_QUALIFIED_NO_LAUNCH"
MAX_TOOL_OUTPUT_BYTES = 1_048_576
MAX_ARTIFACT_BYTES = 67_108_864
CODESIGN_TIMEOUT_SECONDS = 10
CODESIGN = "/usr/bin/codesign"
SYSTEM_VERSION_PLIST = "/System/Library/CoreServices/SystemVersion.plist"

PolicyRunner = Callable[[list[str]], subprocess.CompletedProcess[str]]
PlatformBuildProvider = Callable[[], str]


class ArtifactInspectionError(RuntimeError):
    """Raised internally when a candidate fails the static policy."""


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _default_runner(argv: list[str]) -> subprocess.CompletedProcess[str]:
    if not argv or argv[0] != CODESIGN:
        raise ArtifactInspectionError("only the absolute codesign inspector is allowed")
    try:
        return subprocess.run(
            argv,
            check=False,
            capture_output=True,
            text=True,
            env={"LC_ALL": "C"},
            timeout=CODESIGN_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise ArtifactInspectionError(
            f"codesign timed out after {CODESIGN_TIMEOUT_SECONDS} seconds"
        ) from exc


def _host_platform_build() -> str:
    value = plistlib.loads(Path(SYSTEM_VERSION_PLIST).read_bytes())
    build = value.get("ProductBuildVersion") if isinstance(value, Mapping) else None
    if not isinstance(build, str) or not build.strip():
        raise ArtifactInspectionError("host platform build is unavailable")
    return build.strip()


def _bounded_output(result: subprocess.CompletedProcess[str]) -> str:
    output = (result.stdout or "") + (result.stderr or "")
    if len(output.encode("utf-8", errors="replace")) > MAX_TOOL_OUTPUT_BYTES:
        raise ArtifactInspectionError("codesign output exceeded the fixed bound")
    return output


def _strict_relative_path(relative: object) -> PurePosixPath:
    if not isinstance(relative, str) or not relative:
        raise ArtifactInspectionError("artifact relative_path must be non-empty")
    raw_parts = relative.split("/")
    if relative.startswith("/") or any(
        part in {"", ".", ".."} for part in raw_parts
    ):
        raise ArtifactInspectionError("artifact path must be a strict relative path")
    return PurePosixPath(*raw_parts)


def _open_source(root: Path, relative: object) -> tuple[Path, int, os.stat_result]:
    pure = _strict_relative_path(relative)
    canonical_root = root.resolve(strict=True)
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    root_descriptor = os.open(canonical_root, flags)
    parent_descriptor = root_descriptor
    try:
        for part in pure.parts[:-1]:
            part_info = os.stat(
                part, dir_fd=parent_descriptor, follow_symlinks=False
            )
            if stat.S_ISLNK(part_info.st_mode):
                raise ArtifactInspectionError("artifact path component is a symlink")
            if not stat.S_ISDIR(part_info.st_mode):
                raise ArtifactInspectionError(
                    "artifact parent component is not a directory"
                )
            next_descriptor = os.open(part, flags, dir_fd=parent_descriptor)
            if parent_descriptor != root_descriptor:
                os.close(parent_descriptor)
            parent_descriptor = next_descriptor
        file_flags = (
            os.O_RDONLY
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0)
        )
        file_info = os.stat(
            pure.parts[-1], dir_fd=parent_descriptor, follow_symlinks=False
        )
        if stat.S_ISLNK(file_info.st_mode):
            raise ArtifactInspectionError("artifact path component is a symlink")
        descriptor = os.open(pure.parts[-1], file_flags, dir_fd=parent_descriptor)
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode):
            os.close(descriptor)
            raise ArtifactInspectionError("artifact must be a non-symlink regular file")
        if info.st_size > MAX_ARTIFACT_BYTES:
            os.close(descriptor)
            raise ArtifactInspectionError("artifact exceeds the fixed size bound")
        return canonical_root.joinpath(*pure.parts), descriptor, info
    finally:
        if parent_descriptor != root_descriptor:
            os.close(parent_descriptor)
        os.close(root_descriptor)


def _hash_descriptor(descriptor: int) -> str:
    os.lseek(descriptor, 0, os.SEEK_SET)
    digest = hashlib.sha256()
    while True:
        block = os.read(descriptor, 1_048_576)
        if not block:
            return digest.hexdigest()
        digest.update(block)


def _hash_nofollow(path: Path) -> str:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode):
            raise ArtifactInspectionError("snapshot changed away from a regular file")
        return _hash_descriptor(descriptor)
    finally:
        os.close(descriptor)


def _copy_pinned_descriptor(
    source_descriptor: int,
    source_info: os.stat_result,
    destination: Path,
) -> tuple[str, int]:
    if source_info.st_size > MAX_ARTIFACT_BYTES:
        raise ArtifactInspectionError("artifact exceeds the fixed size bound")
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    destination_descriptor = os.open(destination, flags, 0o500)
    digest = hashlib.sha256()
    copied = 0
    try:
        os.lseek(source_descriptor, 0, os.SEEK_SET)
        while True:
            block = os.read(source_descriptor, 1_048_576)
            if not block:
                break
            copied += len(block)
            if copied > MAX_ARTIFACT_BYTES:
                raise ArtifactInspectionError("artifact grew past the fixed size bound")
            digest.update(block)
            view = memoryview(block)
            while view:
                count = os.write(destination_descriptor, view)
                view = view[count:]
        os.fsync(destination_descriptor)
        os.fchmod(destination_descriptor, 0o500)
    finally:
        os.close(destination_descriptor)
    if copied != source_info.st_size:
        raise ArtifactInspectionError("artifact size changed while creating snapshot")
    return digest.hexdigest(), copied


def _metadata(output: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for key in ("CDHash", "TeamIdentifier", "Signature", "Identifier", "Format"):
        match = re.search(rf"(?m)^{re.escape(key)}=(.+)$", output)
        if match:
            values[key] = match.group(1).strip()
    return values


def _designated_requirement(output: str) -> str:
    match = re.search(r"(?m)^designated =>\s*(.+)$", output)
    if not match:
        raise ArtifactInspectionError("codesign did not report a designated requirement")
    return match.group(1).strip()


def _entitlements(output: str) -> dict[str, object]:
    start = output.find("<?xml")
    end_marker = "</plist>"
    end = output.find(end_marker, start)
    if start < 0 or end < 0:
        raise ArtifactInspectionError("codesign did not report XML entitlements")
    raw = output[start : end + len(end_marker)].encode("utf-8")
    value = plistlib.loads(raw)
    if not isinstance(value, dict):
        raise ArtifactInspectionError("artifact entitlements must be a dictionary")
    return value


def _require_exact_keys(value: Mapping[str, object], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        raise ArtifactInspectionError(
            f"{label} keys differ: missing={sorted(expected - actual)!r} extra={sorted(actual - expected)!r}"
        )


def _inspect_one(
    root: Path,
    snapshot_root: Path,
    name: str,
    spec: Mapping[str, object],
    runner: PolicyRunner,
) -> dict[str, object]:
    _require_exact_keys(
        spec,
        {
            "relative_path",
            "size",
            "sha256",
            "cdhash",
            "team_identifier",
            "designated_requirement",
            "entitlements",
        },
        f"{name} policy",
    )
    for key in ("sha256", "cdhash", "team_identifier", "designated_requirement"):
        if not isinstance(spec[key], str) or not str(spec[key]).strip():
            raise ArtifactInspectionError(f"{name} {key} is not sealed")
    if not isinstance(spec["size"], int) or isinstance(spec["size"], bool):
        raise ArtifactInspectionError(f"{name} size is not sealed")
    if not 0 < spec["size"] <= MAX_ARTIFACT_BYTES:
        raise ArtifactInspectionError(f"{name} size is outside the fixed bound")
    expected_entitlements = spec["entitlements"]
    if not isinstance(expected_entitlements, Mapping):
        raise ArtifactInspectionError(f"{name} entitlements are not a dictionary")

    source_path, source_descriptor, source_info = _open_source(
        root, spec["relative_path"]
    )
    snapshot_directory = snapshot_root / name
    snapshot_directory.mkdir(mode=0o700)
    snapshot_path = snapshot_directory / source_path.name
    try:
        copied_hash, copied_size = _copy_pinned_descriptor(
            source_descriptor, source_info, snapshot_path
        )
    finally:
        os.close(source_descriptor)
    if copied_size != spec["size"]:
        raise ArtifactInspectionError(f"{name} content size mismatch")
    if copied_hash != spec["sha256"]:
        raise ArtifactInspectionError(f"{name} content hash mismatch")
    if _hash_nofollow(snapshot_path) != copied_hash:
        raise ArtifactInspectionError(f"{name} snapshot hash mismatch")

    verify = runner(
        [CODESIGN, "--verify", "--strict", "--verbose=4", str(snapshot_path)]
    )
    _bounded_output(verify)
    if verify.returncode != 0:
        raise ArtifactInspectionError(f"{name} strict code-signature verification failed")

    display = runner([CODESIGN, "--display", "--verbose=4", str(snapshot_path)])
    display_output = _bounded_output(display)
    if display.returncode != 0:
        raise ArtifactInspectionError(f"{name} code-signature metadata inspection failed")
    metadata = _metadata(display_output)
    if not metadata.get("Format", "").startswith("Mach-O"):
        raise ArtifactInspectionError(f"{name} is not a Mach-O artifact")
    if metadata.get("Signature", "").lower() == "adhoc":
        raise ArtifactInspectionError(f"{name} uses an ad hoc signature")
    if metadata.get("TeamIdentifier") in {None, "", "not set"}:
        raise ArtifactInspectionError(f"{name} has no TeamIdentifier")
    if metadata.get("TeamIdentifier") != spec["team_identifier"]:
        raise ArtifactInspectionError(f"{name} TeamIdentifier mismatch")
    if metadata.get("CDHash") != spec["cdhash"]:
        raise ArtifactInspectionError(f"{name} CDHash mismatch")

    requirement_result = runner(
        [CODESIGN, "--display", "--requirements", "-", str(snapshot_path)]
    )
    requirement_output = _bounded_output(requirement_result)
    if requirement_result.returncode != 0:
        raise ArtifactInspectionError(f"{name} requirement inspection failed")
    requirement = _designated_requirement(requirement_output)
    if requirement != spec["designated_requirement"]:
        raise ArtifactInspectionError(f"{name} designated requirement mismatch")

    entitlement_result = runner(
        [
            CODESIGN,
            "--display",
            "--entitlements",
            "-",
            "--xml",
            str(snapshot_path),
        ]
    )
    entitlement_output = _bounded_output(entitlement_result)
    if entitlement_result.returncode != 0:
        raise ArtifactInspectionError(f"{name} entitlement inspection failed")
    entitlements = _entitlements(entitlement_output)
    if _canonical(entitlements) != _canonical(dict(expected_entitlements)):
        raise ArtifactInspectionError(f"{name} entitlement set mismatch")

    if _hash_nofollow(snapshot_path) != copied_hash:
        raise ArtifactInspectionError(f"{name} snapshot changed during inspection")
    after_path, after_descriptor, after_info = _open_source(root, spec["relative_path"])
    try:
        after_hash = _hash_descriptor(after_descriptor)
    finally:
        os.close(after_descriptor)
    if after_path != source_path:
        raise ArtifactInspectionError(f"{name} source path changed during inspection")
    if (after_info.st_dev, after_info.st_ino) != (source_info.st_dev, source_info.st_ino):
        raise ArtifactInspectionError(f"{name} source identity changed during inspection")
    if after_info.st_size != source_info.st_size or after_hash != copied_hash:
        raise ArtifactInspectionError(f"{name} source content changed during inspection")
    return {
        "relative_path": spec["relative_path"],
        "size": copied_size,
        "sha256": copied_hash,
        "inspection_subject": "PRIVATE_PINNED_FD_COPY",
        "snapshot_sha256": copied_hash,
        "cdhash": metadata["CDHash"],
        "team_identifier": metadata["TeamIdentifier"],
        "designated_requirement": requirement,
        "entitlements": entitlements,
    }


def inspect_candidate(
    root: str | Path,
    policy: Mapping[str, object],
    *,
    runner: PolicyRunner = _default_runner,
    platform_build_provider: PlatformBuildProvider = _host_platform_build,
) -> dict[str, Any]:
    """Return a fail-closed static receipt without executing candidate code."""

    receipt: dict[str, Any] = {
        "schema": "dream-house-canary-static-inspection-receipt/1",
        "state": REFUSED_STATE,
        "candidate_launch": "NOT_ATTEMPTED",
        "network": "NOT_ATTEMPTED",
        "keychain": "NOT_ATTEMPTED",
        "real_secret": "NOT_ATTEMPTED",
    }
    try:
        _require_exact_keys(
            policy,
            {"schema", "state", "platform_build", "artifacts"},
            "signing policy",
        )
        if policy["schema"] != POLICY_SCHEMA:
            raise ArtifactInspectionError("unsupported signing policy schema")
        if policy["state"] != "SEALED_CANDIDATE":
            raise ArtifactInspectionError("signing policy is not SEALED_CANDIDATE")
        if not isinstance(policy["platform_build"], str) or not str(policy["platform_build"]).strip():
            raise ArtifactInspectionError("platform_build is not sealed")
        host_platform_build = platform_build_provider()
        if policy["platform_build"] != host_platform_build:
            raise ArtifactInspectionError("platform_build does not match the host")
        artifacts = policy["artifacts"]
        if not isinstance(artifacts, Mapping):
            raise ArtifactInspectionError("artifacts policy is not a dictionary")
        _require_exact_keys(artifacts, {"parent", "helper"}, "artifacts policy")
        parent = artifacts["parent"]
        helper = artifacts["helper"]
        if not isinstance(parent, Mapping) or not isinstance(helper, Mapping):
            raise ArtifactInspectionError("parent/helper policies must be dictionaries")
        with tempfile.TemporaryDirectory(
            prefix="dream-house-canary-inspection."
        ) as snapshot_directory:
            snapshot_root = Path(snapshot_directory)
            snapshot_root.chmod(0o700)
            inspected_parent = _inspect_one(
                Path(root), snapshot_root, "parent", parent, runner
            )
            inspected_helper = _inspect_one(
                Path(root), snapshot_root, "helper", helper, runner
            )
        if inspected_parent["team_identifier"] != inspected_helper["team_identifier"]:
            raise ArtifactInspectionError("parent and helper TeamIdentifiers differ")
        receipt.update(
            {
                "state": QUALIFIED_STATE,
                "platform_build": host_platform_build,
                "inspection_subject": "PRIVATE_PINNED_FD_COPY",
                "policy_sha256": hashlib.sha256(_canonical(policy).encode()).hexdigest(),
                "artifacts": {
                    "parent": inspected_parent,
                    "helper": inspected_helper,
                },
            }
        )
    except (ArtifactInspectionError, OSError, KeyError, TypeError, ValueError) as exc:
        receipt["reason"] = str(exc)
    return receipt


def _load_policy(path: Path) -> Mapping[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise ArtifactInspectionError("signing policy must be a JSON object")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect a sealed native candidate without launching it")
    parser.add_argument("--root", required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        result = inspect_candidate(args.root, _load_policy(Path(args.policy)))
    except (ArtifactInspectionError, OSError, json.JSONDecodeError) as exc:
        result = {
            "schema": "dream-house-canary-static-inspection-receipt/1",
            "state": REFUSED_STATE,
            "candidate_launch": "NOT_ATTEMPTED",
            "reason": str(exc),
        }
    rendered = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    raise SystemExit(0 if result["state"] == QUALIFIED_STATE else 2)


if __name__ == "__main__":
    main()
