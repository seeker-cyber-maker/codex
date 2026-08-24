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
from collections.abc import Callable, Mapping
from pathlib import Path, PurePosixPath
from typing import Any

POLICY_SCHEMA = "dream-house-canary-signing-policy/1"
QUALIFIED_STATE = "QUALIFIED_STATIC_ARTIFACTS_NO_LAUNCH"
REFUSED_STATE = "NOT_QUALIFIED_NO_LAUNCH"
MAX_TOOL_OUTPUT_BYTES = 1_048_576
CODESIGN = "/usr/bin/codesign"

PolicyRunner = Callable[[list[str]], subprocess.CompletedProcess[str]]


class ArtifactInspectionError(RuntimeError):
    """Raised internally when a candidate fails the static policy."""


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _default_runner(argv: list[str]) -> subprocess.CompletedProcess[str]:
    if not argv or argv[0] != CODESIGN:
        raise ArtifactInspectionError("only the absolute codesign inspector is allowed")
    return subprocess.run(
        argv,
        check=False,
        capture_output=True,
        text=True,
        env={"LC_ALL": "C"},
    )


def _bounded_output(result: subprocess.CompletedProcess[str]) -> str:
    output = (result.stdout or "") + (result.stderr or "")
    if len(output.encode("utf-8", errors="replace")) > MAX_TOOL_OUTPUT_BYTES:
        raise ArtifactInspectionError("codesign output exceeded the fixed bound")
    return output


def _strict_regular_file(root: Path, relative: object) -> Path:
    if not isinstance(relative, str) or not relative:
        raise ArtifactInspectionError("artifact relative_path must be non-empty")
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts or "." in pure.parts:
        raise ArtifactInspectionError("artifact path must be a strict relative path")
    root_info = root.lstat()
    if stat.S_ISLNK(root_info.st_mode) or not stat.S_ISDIR(root_info.st_mode):
        raise ArtifactInspectionError("candidate root must be a non-symlink directory")
    candidate = root
    for index, part in enumerate(pure.parts):
        candidate = candidate / part
        info = candidate.lstat()
        if stat.S_ISLNK(info.st_mode):
            raise ArtifactInspectionError("artifact path component is a symlink")
        if index < len(pure.parts) - 1 and not stat.S_ISDIR(info.st_mode):
            raise ArtifactInspectionError("artifact parent component is not a directory")
    if not stat.S_ISREG(info.st_mode):
        raise ArtifactInspectionError("artifact must be a non-symlink regular file")
    return candidate


def _hash_nofollow(path: Path) -> str:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode):
            raise ArtifactInspectionError("artifact changed away from a regular file")
        digest = hashlib.sha256()
        while True:
            block = os.read(descriptor, 1_048_576)
            if not block:
                return digest.hexdigest()
            digest.update(block)
    finally:
        os.close(descriptor)


def _metadata(output: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for key in ("CDHash", "TeamIdentifier", "Signature", "Identifier"):
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
    name: str,
    spec: Mapping[str, object],
    runner: PolicyRunner,
) -> dict[str, object]:
    _require_exact_keys(
        spec,
        {
            "relative_path",
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
    expected_entitlements = spec["entitlements"]
    if not isinstance(expected_entitlements, Mapping):
        raise ArtifactInspectionError(f"{name} entitlements are not a dictionary")

    path = _strict_regular_file(root, spec["relative_path"])
    before = _hash_nofollow(path)
    if before != spec["sha256"]:
        raise ArtifactInspectionError(f"{name} content hash mismatch")

    verify = runner([CODESIGN, "--verify", "--strict", "--verbose=4", str(path)])
    _bounded_output(verify)
    if verify.returncode != 0:
        raise ArtifactInspectionError(f"{name} strict code-signature verification failed")

    display = runner([CODESIGN, "--display", "--verbose=4", str(path)])
    display_output = _bounded_output(display)
    if display.returncode != 0:
        raise ArtifactInspectionError(f"{name} code-signature metadata inspection failed")
    metadata = _metadata(display_output)
    if metadata.get("Signature", "").lower() == "adhoc":
        raise ArtifactInspectionError(f"{name} uses an ad hoc signature")
    if metadata.get("TeamIdentifier") in {None, "", "not set"}:
        raise ArtifactInspectionError(f"{name} has no TeamIdentifier")
    if metadata.get("TeamIdentifier") != spec["team_identifier"]:
        raise ArtifactInspectionError(f"{name} TeamIdentifier mismatch")
    if metadata.get("CDHash") != spec["cdhash"]:
        raise ArtifactInspectionError(f"{name} CDHash mismatch")

    requirement_result = runner([CODESIGN, "--display", "--requirements", "-", str(path)])
    requirement_output = _bounded_output(requirement_result)
    if requirement_result.returncode != 0:
        raise ArtifactInspectionError(f"{name} requirement inspection failed")
    requirement = _designated_requirement(requirement_output)
    if requirement != spec["designated_requirement"]:
        raise ArtifactInspectionError(f"{name} designated requirement mismatch")

    entitlement_result = runner(
        [CODESIGN, "--display", "--entitlements", "-", "--xml", str(path)]
    )
    entitlement_output = _bounded_output(entitlement_result)
    if entitlement_result.returncode != 0:
        raise ArtifactInspectionError(f"{name} entitlement inspection failed")
    entitlements = _entitlements(entitlement_output)
    if _canonical(entitlements) != _canonical(dict(expected_entitlements)):
        raise ArtifactInspectionError(f"{name} entitlement set mismatch")

    after = _hash_nofollow(path)
    if after != before:
        raise ArtifactInspectionError(f"{name} changed during inspection")
    return {
        "relative_path": spec["relative_path"],
        "sha256": before,
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
        artifacts = policy["artifacts"]
        if not isinstance(artifacts, Mapping):
            raise ArtifactInspectionError("artifacts policy is not a dictionary")
        _require_exact_keys(artifacts, {"parent", "helper"}, "artifacts policy")
        parent = artifacts["parent"]
        helper = artifacts["helper"]
        if not isinstance(parent, Mapping) or not isinstance(helper, Mapping):
            raise ArtifactInspectionError("parent/helper policies must be dictionaries")
        inspected_parent = _inspect_one(Path(root), "parent", parent, runner)
        inspected_helper = _inspect_one(Path(root), "helper", helper, runner)
        if inspected_parent["team_identifier"] != inspected_helper["team_identifier"]:
            raise ArtifactInspectionError("parent and helper TeamIdentifiers differ")
        receipt.update(
            {
                "state": QUALIFIED_STATE,
                "platform_build": policy["platform_build"],
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
