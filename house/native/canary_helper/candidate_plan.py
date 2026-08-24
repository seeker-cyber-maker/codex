"""Validate a source-only canary candidate contract and emit plan data only."""

from __future__ import annotations

import copy
import hashlib
import json
import plistlib
import re
import stat
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import Any

CONTRACT_SCHEMA = "dream-house-canary-candidate-contract/1"
UNRESOLVED_STATE = "SOURCE_ONLY_UNRESOLVED_NO_EXECUTABLE_PLAN"
RESOLVED_STATE = "SOURCE_ONLY_RESOLVED_PLAN_DATA_ONLY"
NOT_READY_STATE = "NOT_READY_UNRESOLVED_NO_OPERATIONS"
PLAN_STATE = "PLAN_DATA_ONLY_NOT_EXECUTED"
MAX_CONTRACT_BYTES = 65_536
MAX_PLAN_BYTES = 65_536
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
IDENTIFIER_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9.-]{2,254}")
VERSION_PATTERN = re.compile(r"[0-9]+(?:\.[0-9]+){0,3}")
MODE_PATTERN = re.compile(r"0[0-7]{3}")
CDHASH_PATTERN = re.compile(r"[0-9a-f]{40}")
TEAM_ID_PATTERN = re.compile(r"[A-Z0-9]{10}")

TOP_LEVEL_KEYS = {
    "schema",
    "state",
    "unresolved_marker",
    "claim_ceiling",
    "package",
    "platform",
    "tools",
    "sources",
    "bundle_inventory",
    "plan_policy",
}
PACKAGE_KEYS = {"root", "version", "build_version", "parent", "helper"}
ARTIFACT_KEYS = {
    "bundle_identifier",
    "display_name",
    "executable_name",
    "relative_path",
    "info_plist_policy",
    "info_plist",
    "entitlements",
    "hardened_runtime",
    "identity",
}
ENTITLEMENT_KEYS = {"relative_path", "sha256", "expected"}
RUNTIME_KEYS = {"required", "codesign_options", "prohibited_entitlements"}
IDENTITY_KEYS = {
    "signing_identity",
    "team_identifier",
    "designated_requirement",
    "cdhash",
    "size",
    "sha256",
}
PLATFORM_KEYS = {
    "architecture",
    "deployment_target",
    "developer_dir",
    "sdk_path",
    "sdk_build",
    "toolchain_build",
}
TOOLS_KEYS = {"clang", "codesign"}
TOOL_KEYS = {"absolute_path", "sha256", "version"}
SOURCE_KEYS = {"relative_path", "role", "mode", "sha256"}
INVENTORY_KEYS = {
    "required_members",
    "signing_generated_members",
    "unexpected_member_policy",
    "symlink_policy",
}
MEMBER_KEYS = {"relative_path", "kind", "mode"}
PLAN_POLICY_KEYS = {
    "max_serialized_bytes",
    "output_root_policy",
    "workspace_policy",
    "operation_order",
    "execution",
}
WORKSPACE_POLICY_KEYS = {
    "reservation",
    "mode",
    "token_bits",
    "max_attempts",
    "no_follow",
    "cleanup",
}
EXPECTED_OPERATION_ORDER = [
    "reserve_private_workspace",
    "write_parent_info_plist",
    "compile_parent",
    "compile_helper",
    "link_helper",
    "link_parent",
    "sign_helper",
    "verify_helper",
    "sign_parent",
    "verify_parent",
    "inventory_bundle",
]
EXPECTED_SOURCE_LAYOUT = [
    ("protocol.c", "shared"),
    ("protocol.h", "header"),
    ("contract.h", "header"),
    ("parent_contract.c", "parent"),
    ("helper_contract.c", "helper"),
    ("parent_main.c", "parent"),
    ("helper_main.c", "helper"),
]
EXPECTED_REQUIRED_MEMBERS = [
    {
        "relative_path": "Contents/Info.plist",
        "kind": "parent_info_plist",
        "mode": "0644",
    },
    {
        "relative_path": "Contents/MacOS/DreamHouseCanaryParent",
        "kind": "parent_macho",
        "mode": "0755",
    },
    {
        "relative_path": "Contents/Helpers/DreamHouseCanaryHelper",
        "kind": "helper_macho",
        "mode": "0755",
    },
]
EXPECTED_PARENT_ENTITLEMENTS = {"com.apple.security.app-sandbox": True}
EXPECTED_HELPER_ENTITLEMENTS = {
    "com.apple.security.app-sandbox": True,
    "com.apple.security.inherit": True,
}
PROHIBITED_ENTITLEMENTS = {
    "com.apple.security.cs.allow-dyld-environment-variables",
    "com.apple.security.cs.allow-jit",
    "com.apple.security.cs.allow-unsigned-executable-memory",
    "com.apple.security.cs.debugger",
    "com.apple.security.cs.disable-library-validation",
    "com.apple.security.get-task-allow",
    "com.apple.security.network.client",
    "com.apple.security.network.server",
}


class CandidatePlanError(ValueError):
    """Raised when plan data cannot be produced from the closed contract."""


def _require_mapping(value: object, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise CandidatePlanError(f"{field} must be an object")
    return value


def _require_exact_keys(value: Mapping[str, Any], expected: set[str], field: str) -> None:
    actual = set(value)
    if actual != expected:
        raise CandidatePlanError(
            f"{field} keys mismatch: missing={sorted(expected - actual)!r} "
            f"unexpected={sorted(actual - expected)!r}"
        )


def _strict_relative_path(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise CandidatePlanError(f"{field} must be a nonempty relative path")
    if "\\" in value or value.startswith("/"):
        raise CandidatePlanError(f"{field} must be a strict POSIX relative path")
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise CandidatePlanError(f"{field} contains an unsafe path component")
    pure = PurePosixPath(value)
    if pure.is_absolute() or str(pure) != value:
        raise CandidatePlanError(f"{field} must not normalize")
    return value


def _require_sha256(value: object, field: str, unresolved: str) -> None:
    if value == unresolved:
        return
    if not isinstance(value, str) or SHA256_PATTERN.fullmatch(value) is None:
        raise CandidatePlanError(f"{field} must be lowercase SHA-256 or unresolved")


def _require_mode(value: object, field: str) -> str:
    if not isinstance(value, str) or MODE_PATTERN.fullmatch(value) is None:
        raise CandidatePlanError(f"{field} must be a four-digit octal mode")
    return value


def _bound_file(source_root: Path, relative: str, expected_hash: str, mode: str) -> bytes:
    path = source_root
    parts = relative.split("/")
    for index, component in enumerate(parts):
        path = path / component
        try:
            metadata = path.lstat()
        except FileNotFoundError as error:
            raise CandidatePlanError(f"bound input is missing: {relative}") from error
        if stat.S_ISLNK(metadata.st_mode):
            raise CandidatePlanError(f"bound input path contains a symlink: {relative}")
        if index < len(parts) - 1 and not stat.S_ISDIR(metadata.st_mode):
            raise CandidatePlanError(f"bound input parent is not a directory: {relative}")
    metadata = path.lstat()
    if not stat.S_ISREG(metadata.st_mode):
        raise CandidatePlanError(f"bound input is not a regular file: {relative}")
    actual_mode = f"{stat.S_IMODE(metadata.st_mode):04o}"
    if actual_mode != mode:
        raise CandidatePlanError(f"bound input mode mismatch: {relative}")
    content = path.read_bytes()
    if hashlib.sha256(content).hexdigest() != expected_hash:
        raise CandidatePlanError(f"bound input SHA-256 mismatch: {relative}")
    return content


def _collect_unresolved(value: object, marker: str, path: str = "$") -> list[str]:
    if value == marker:
        return [path]
    if isinstance(value, Mapping):
        result: list[str] = []
        for key in sorted(value):
            result.extend(_collect_unresolved(value[key], marker, f"{path}.{key}"))
        return result
    if isinstance(value, list):
        result = []
        for index, item in enumerate(value):
            result.extend(_collect_unresolved(item, marker, f"{path}[{index}]"))
        return result
    return []


def _validate_artifact(
    name: str,
    artifact: Mapping[str, Any],
    unresolved: str,
    source_root: Path,
) -> None:
    _require_exact_keys(artifact, ARTIFACT_KEYS, f"package.{name}")
    identifier = artifact["bundle_identifier"]
    if identifier != unresolved and (
        not isinstance(identifier, str)
        or IDENTIFIER_PATTERN.fullmatch(identifier) is None
    ):
        raise CandidatePlanError(f"package.{name}.bundle_identifier is invalid")
    for key in ("display_name", "executable_name"):
        if not isinstance(artifact[key], str) or not artifact[key]:
            raise CandidatePlanError(f"package.{name}.{key} must be nonempty")
    _strict_relative_path(artifact["relative_path"], f"package.{name}.relative_path")

    if name == "parent":
        if artifact["info_plist_policy"] != "REQUIRED_PARENT_APP_PLIST":
            raise CandidatePlanError("parent Info.plist policy mismatch")
        info = _require_mapping(artifact["info_plist"], "package.parent.info_plist")
        required_info_keys = {
            "CFBundleDevelopmentRegion",
            "CFBundleDisplayName",
            "CFBundleExecutable",
            "CFBundleIdentifier",
            "CFBundleInfoDictionaryVersion",
            "CFBundleName",
            "CFBundlePackageType",
            "CFBundleShortVersionString",
            "CFBundleSupportedPlatforms",
            "CFBundleVersion",
            "LSBackgroundOnly",
            "LSMinimumSystemVersion",
        }
        _require_exact_keys(info, required_info_keys, "package.parent.info_plist")
        if info["CFBundleExecutable"] != artifact["executable_name"]:
            raise CandidatePlanError("parent executable and Info.plist disagree")
        if info["CFBundleIdentifier"] != artifact["bundle_identifier"]:
            raise CandidatePlanError("parent identifier and Info.plist disagree")
        if info["CFBundlePackageType"] != "APPL":
            raise CandidatePlanError("parent package type must be APPL")
        expected_static_info = {
            "CFBundleDevelopmentRegion": "en",
            "CFBundleDisplayName": "Dream House Canary Parent",
            "CFBundleInfoDictionaryVersion": "6.0",
            "CFBundleName": "DreamHouseCanaryParent",
            "CFBundlePackageType": "APPL",
            "CFBundleShortVersionString": "0.1.0",
            "CFBundleSupportedPlatforms": ["MacOSX"],
            "CFBundleVersion": "1",
            "LSBackgroundOnly": True,
        }
        for key, expected in expected_static_info.items():
            if info[key] != expected:
                raise CandidatePlanError(f"parent Info.plist field mismatch: {key}")
    elif artifact["info_plist_policy"] != (
        "FORBIDDEN_RAW_MACHO_HELPER_NO_SEPARATE_BUNDLE"
    ) or artifact["info_plist"] is not None:
        raise CandidatePlanError("helper must remain a raw Mach-O without Info.plist")

    entitlements = _require_mapping(
        artifact["entitlements"], f"package.{name}.entitlements"
    )
    _require_exact_keys(entitlements, ENTITLEMENT_KEYS, f"package.{name}.entitlements")
    entitlement_path = _strict_relative_path(
        entitlements["relative_path"], f"package.{name}.entitlements.relative_path"
    )
    _require_sha256(
        entitlements["sha256"], f"package.{name}.entitlements.sha256", unresolved
    )
    expected_entitlements = (
        EXPECTED_PARENT_ENTITLEMENTS if name == "parent" else EXPECTED_HELPER_ENTITLEMENTS
    )
    if entitlements["expected"] != expected_entitlements:
        raise CandidatePlanError(f"package.{name} entitlement set mismatch")
    if entitlements["sha256"] != unresolved:
        content = _bound_file(source_root, entitlement_path, entitlements["sha256"], "0644")
        if plistlib.loads(content) != expected_entitlements:
            raise CandidatePlanError(f"package.{name} entitlement content mismatch")

    runtime = _require_mapping(
        artifact["hardened_runtime"], f"package.{name}.hardened_runtime"
    )
    _require_exact_keys(runtime, RUNTIME_KEYS, f"package.{name}.hardened_runtime")
    if runtime["required"] is not True or runtime["codesign_options"] != ["runtime"]:
        raise CandidatePlanError(f"package.{name} hardened runtime is not exact")
    if set(runtime["prohibited_entitlements"]) != PROHIBITED_ENTITLEMENTS:
        raise CandidatePlanError(f"package.{name} prohibited entitlement set mismatch")

    identity = _require_mapping(artifact["identity"], f"package.{name}.identity")
    _require_exact_keys(identity, IDENTITY_KEYS, f"package.{name}.identity")
    _require_sha256(identity["sha256"], f"package.{name}.identity.sha256", unresolved)
    if identity["signing_identity"] != unresolved and (
        not isinstance(identity["signing_identity"], str)
        or not identity["signing_identity"]
    ):
        raise CandidatePlanError(f"package.{name} signing identity is invalid")
    if identity["team_identifier"] != unresolved and (
        not isinstance(identity["team_identifier"], str)
        or TEAM_ID_PATTERN.fullmatch(identity["team_identifier"]) is None
    ):
        raise CandidatePlanError(f"package.{name} Team ID is invalid")
    if identity["designated_requirement"] != unresolved and (
        not isinstance(identity["designated_requirement"], str)
        or not identity["designated_requirement"]
    ):
        raise CandidatePlanError(f"package.{name} designated requirement is invalid")
    if identity["cdhash"] != unresolved and (
        not isinstance(identity["cdhash"], str)
        or CDHASH_PATTERN.fullmatch(identity["cdhash"]) is None
    ):
        raise CandidatePlanError(f"package.{name} CDHash is invalid")
    if identity["size"] != unresolved and (
        not isinstance(identity["size"], int)
        or isinstance(identity["size"], bool)
        or identity["size"] <= 0
    ):
        raise CandidatePlanError(f"package.{name} size is invalid")
    if (
        identifier != unresolved
        and identity["team_identifier"] != unresolved
        and identity["designated_requirement"] != unresolved
    ):
        expected_requirement = (
            f'identifier "{identifier}" and anchor apple generic and '
            f'certificate leaf[subject.OU] = "{identity["team_identifier"]}"'
        )
        if identity["designated_requirement"] != expected_requirement:
            raise CandidatePlanError(
                f"package.{name} designated requirement is not canonical and "
                "identity-bound"
            )


def validate_candidate_contract(
    contract: Mapping[str, Any], source_root: str | Path
) -> dict[str, Any]:
    """Validate the closed contract and return readiness without operations."""

    _require_exact_keys(contract, TOP_LEVEL_KEYS, "contract")
    if contract["schema"] != CONTRACT_SCHEMA:
        raise CandidatePlanError("candidate contract schema mismatch")
    unresolved = contract["unresolved_marker"]
    if unresolved != "UNRESOLVED":
        raise CandidatePlanError("unresolved marker must be the fixed sentinel")
    if contract["state"] not in {UNRESOLVED_STATE, RESOLVED_STATE}:
        raise CandidatePlanError("candidate contract state is invalid")
    if contract["claim_ceiling"] != (
        "SOURCE_AND_PLAN_DATA_ONLY_NO_CANDIDATE_OR_RUNTIME_QUALIFICATION"
    ):
        raise CandidatePlanError("candidate contract claim ceiling mismatch")

    root_input = Path(source_root)
    if root_input.is_symlink():
        raise CandidatePlanError("source root must not be a symlink")
    root = root_input.resolve(strict=True)
    if not root.is_dir():
        raise CandidatePlanError("source root must be a directory")

    package = _require_mapping(contract["package"], "package")
    _require_exact_keys(package, PACKAGE_KEYS, "package")
    _strict_relative_path(package["root"], "package.root")
    if package["root"] != "DreamHouseCanaryParent.app":
        raise CandidatePlanError("package.root mismatch")
    for key in ("version", "build_version"):
        value = package[key]
        if not isinstance(value, str) or VERSION_PATTERN.fullmatch(value) is None:
            raise CandidatePlanError(f"package.{key} is invalid")
    for name in ("parent", "helper"):
        _validate_artifact(
            name,
            _require_mapping(package[name], f"package.{name}"),
            unresolved,
            root,
        )
    parent = package["parent"]
    helper = package["helper"]
    if parent["info_plist"]["CFBundleShortVersionString"] != package["version"]:
        raise CandidatePlanError("package version and parent Info.plist disagree")
    if parent["info_plist"]["CFBundleVersion"] != package["build_version"]:
        raise CandidatePlanError("package build version and parent Info.plist disagree")
    if (
        parent["display_name"] != "Dream House Canary Parent"
        or parent["executable_name"] != "DreamHouseCanaryParent"
        or parent["relative_path"] != "Contents/MacOS/DreamHouseCanaryParent"
    ):
        raise CandidatePlanError("parent package identity fields mismatch")
    if (
        helper["display_name"] != "Dream House Canary Helper"
        or helper["executable_name"] != "DreamHouseCanaryHelper"
        or helper["relative_path"] != "Contents/Helpers/DreamHouseCanaryHelper"
    ):
        raise CandidatePlanError("helper package identity fields mismatch")
    if (
        parent["bundle_identifier"] != unresolved
        and helper["bundle_identifier"] != unresolved
        and parent["bundle_identifier"] == helper["bundle_identifier"]
    ):
        raise CandidatePlanError("parent and helper bundle identifiers must differ")

    platform = _require_mapping(contract["platform"], "platform")
    _require_exact_keys(platform, PLATFORM_KEYS, "platform")
    if platform["architecture"] != "arm64":
        raise CandidatePlanError("only the declared arm64 architecture is accepted")
    if platform["deployment_target"] != unresolved and (
        not isinstance(platform["deployment_target"], str)
        or VERSION_PATTERN.fullmatch(platform["deployment_target"]) is None
    ):
        raise CandidatePlanError("platform deployment target is invalid")
    if (
        platform["deployment_target"] != unresolved
        and parent["info_plist"]["LSMinimumSystemVersion"]
        != platform["deployment_target"]
    ):
        raise CandidatePlanError(
            "deployment target and parent Info.plist minimum system disagree"
        )
    for key in ("developer_dir", "sdk_path"):
        value = platform[key]
        if value != unresolved and (
            not isinstance(value, str) or not value.startswith("/")
        ):
            raise CandidatePlanError(f"platform.{key} must be absolute")
    for key in ("sdk_build", "toolchain_build"):
        value = platform[key]
        if value != unresolved and (not isinstance(value, str) or not value):
            raise CandidatePlanError(f"platform.{key} must be nonempty")

    tools = _require_mapping(contract["tools"], "tools")
    _require_exact_keys(tools, TOOLS_KEYS, "tools")
    for name in sorted(TOOLS_KEYS):
        tool = _require_mapping(tools[name], f"tools.{name}")
        _require_exact_keys(tool, TOOL_KEYS, f"tools.{name}")
        if tool["absolute_path"] != unresolved and (
            not isinstance(tool["absolute_path"], str)
            or not tool["absolute_path"].startswith("/")
        ):
            raise CandidatePlanError(f"tools.{name}.absolute_path must be absolute")
        _require_sha256(tool["sha256"], f"tools.{name}.sha256", unresolved)
        if tool["version"] != unresolved and (
            not isinstance(tool["version"], str) or not tool["version"]
        ):
            raise CandidatePlanError(f"tools.{name}.version must be nonempty")

    sources = contract["sources"]
    if not isinstance(sources, list) or not sources:
        raise CandidatePlanError("sources must be a nonempty list")
    source_paths: set[str] = set()
    for index, value in enumerate(sources):
        source = _require_mapping(value, f"sources[{index}]")
        _require_exact_keys(source, SOURCE_KEYS, f"sources[{index}]")
        relative = _strict_relative_path(
            source["relative_path"], f"sources[{index}].relative_path"
        )
        if relative in source_paths:
            raise CandidatePlanError(f"duplicate source path: {relative}")
        source_paths.add(relative)
        if source["role"] not in {"shared", "header", "parent", "helper"}:
            raise CandidatePlanError(f"sources[{index}].role is invalid")
        mode = _require_mode(source["mode"], f"sources[{index}].mode")
        _require_sha256(source["sha256"], f"sources[{index}].sha256", unresolved)
        if source["sha256"] != unresolved:
            _bound_file(root, relative, source["sha256"], mode)
    if [
        (source["relative_path"], source["role"]) for source in sources
    ] != EXPECTED_SOURCE_LAYOUT:
        raise CandidatePlanError("source layout or role order mismatch")

    inventory = _require_mapping(contract["bundle_inventory"], "bundle_inventory")
    _require_exact_keys(inventory, INVENTORY_KEYS, "bundle_inventory")
    required_members = inventory["required_members"]
    if not isinstance(required_members, list) or len(required_members) != 3:
        raise CandidatePlanError("bundle inventory must contain exactly three members")
    normalized_members = []
    for index, value in enumerate(required_members):
        member = _require_mapping(value, f"required_members[{index}]")
        _require_exact_keys(member, MEMBER_KEYS, f"required_members[{index}]")
        normalized_members.append(
            {
                "relative_path": _strict_relative_path(
                    member["relative_path"],
                    f"required_members[{index}].relative_path",
                ),
                "kind": member["kind"],
                "mode": _require_mode(
                    member["mode"], f"required_members[{index}].mode"
                ),
            }
        )
    if normalized_members != EXPECTED_REQUIRED_MEMBERS:
        raise CandidatePlanError("bundle required-member specification mismatch")
    if inventory["signing_generated_members"] != [
        "Contents/_CodeSignature/CodeResources"
    ]:
        raise CandidatePlanError("signing-generated member set mismatch")
    if inventory["unexpected_member_policy"] != "REJECT":
        raise CandidatePlanError("unexpected bundle members must be rejected")
    if inventory["symlink_policy"] != "REJECT_ALL_BUNDLE_MEMBER_SYMLINKS":
        raise CandidatePlanError("bundle member symlinks must be rejected")

    policy = _require_mapping(contract["plan_policy"], "plan_policy")
    _require_exact_keys(policy, PLAN_POLICY_KEYS, "plan_policy")
    if policy["max_serialized_bytes"] != MAX_PLAN_BYTES:
        raise CandidatePlanError("plan size bound mismatch")
    if policy["output_root_policy"] != (
        "EXISTING_ABSOLUTE_NON_SYMLINK_DIRECTORY_NO_WRITES"
    ):
        raise CandidatePlanError("output-root policy mismatch")
    workspace_policy = _require_mapping(
        policy["workspace_policy"], "plan_policy.workspace_policy"
    )
    _require_exact_keys(
        workspace_policy, WORKSPACE_POLICY_KEYS, "plan_policy.workspace_policy"
    )
    expected_workspace_policy = {
        "reservation": "ATOMIC_RANDOM_CHILD_UNDER_PINNED_PARENT",
        "mode": "0700",
        "token_bits": 128,
        "max_attempts": 8,
        "no_follow": True,
        "cleanup": "EXACT_DESCRIPTOR_RELATIVE_ONLY_AFTER_TERMINAL_RECEIPT",
    }
    if workspace_policy != expected_workspace_policy:
        raise CandidatePlanError("private workspace policy mismatch")
    if policy["operation_order"] != EXPECTED_OPERATION_ORDER:
        raise CandidatePlanError("operation order mismatch")
    if policy["execution"] != "FORBIDDEN_DATA_ONLY":
        raise CandidatePlanError("plan execution must remain forbidden")

    unresolved_paths = _collect_unresolved(
        {key: value for key, value in contract.items() if key != "unresolved_marker"},
        unresolved,
    )
    expected_state = UNRESOLVED_STATE if unresolved_paths else RESOLVED_STATE
    if contract["state"] != expected_state:
        raise CandidatePlanError("contract state does not match unresolved fields")
    return {
        "schema": "dream-house-canary-candidate-contract-validation/1",
        "state": NOT_READY_STATE if unresolved_paths else "READY_FOR_PLAN_DATA_ONLY",
        "unresolved_paths": unresolved_paths,
        "operations": [],
        "tool_execution": "NOT_ATTEMPTED",
        "candidate_creation": "NOT_ATTEMPTED",
        "candidate_launch": "NOT_ATTEMPTED",
    }


def load_candidate_contract(path: str | Path) -> dict[str, Any]:
    """Load a bounded JSON contract without interpreting it as instructions."""

    contract_path = Path(path)
    if contract_path.is_symlink():
        raise CandidatePlanError("candidate contract path must not be a symlink")
    content = contract_path.read_bytes()
    if len(content) > MAX_CONTRACT_BYTES:
        raise CandidatePlanError("candidate contract exceeds the fixed size bound")
    try:
        value = json.loads(content)
    except json.JSONDecodeError as error:
        raise CandidatePlanError("candidate contract is not valid JSON") from error
    if not isinstance(value, dict):
        raise CandidatePlanError("candidate contract must be a JSON object")
    return value


def _source_groups(contract: Mapping[str, Any]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {"parent": [], "helper": []}
    for source in contract["sources"]:
        if source["relative_path"].endswith(".c"):
            if source["role"] in {"shared", "parent"}:
                groups["parent"].append(source["relative_path"])
            if source["role"] in {"shared", "helper"}:
                groups["helper"].append(source["relative_path"])
    return groups


def generate_candidate_plan(
    contract: Mapping[str, Any], source_root: str | Path, output_root: str | Path
) -> dict[str, Any]:
    """Emit bounded plan data for a fully resolved contract; execute nothing."""

    readiness = validate_candidate_contract(contract, source_root)
    if readiness["state"] != "READY_FOR_PLAN_DATA_ONLY":
        raise CandidatePlanError(
            "candidate contract is unresolved; executable plan data is forbidden"
        )
    output_input = Path(output_root)
    if not output_input.is_absolute():
        raise CandidatePlanError("output root must be absolute")
    if output_input.is_symlink():
        raise CandidatePlanError("output root must not be a symlink")
    output = output_input.resolve(strict=True)
    if not output.is_dir():
        raise CandidatePlanError("output root must be an existing directory")
    output_metadata = output.stat()

    source = Path(source_root).resolve(strict=True)
    package = contract["package"]
    parent = package["parent"]
    helper = package["helper"]
    platform = contract["platform"]
    clang = contract["tools"]["clang"]["absolute_path"]
    codesign = contract["tools"]["codesign"]["absolute_path"]
    workspace = "${PRIVATE_WORKSPACE}"
    bundle = f"{workspace}/{package['root']}"
    parent_path = f"{bundle}/{parent['relative_path']}"
    helper_path = f"{bundle}/{helper['relative_path']}"
    object_root = f"{workspace}/.objects"
    groups = _source_groups(contract)

    common_compile = [
        clang,
        "-isysroot",
        platform["sdk_path"],
        f"-mmacosx-version-min={platform['deployment_target']}",
        "-arch",
        platform["architecture"],
        "-std=c11",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-pedantic",
        "-fno-common",
        "-c",
    ]
    common_link = [
        clang,
        "-isysroot",
        platform["sdk_path"],
        f"-mmacosx-version-min={platform['deployment_target']}",
        "-arch",
        platform["architecture"],
    ]
    compile_commands: dict[str, list[list[str]]] = {"parent": [], "helper": []}
    object_paths: dict[str, list[str]] = {"parent": [], "helper": []}
    for target in ("parent", "helper"):
        for relative in groups[target]:
            object_path = f"{object_root}/{target}/{Path(relative).stem}.o"
            object_paths[target].append(object_path)
            compile_commands[target].append(
                [*common_compile, str(source / relative), "-o", str(object_path)]
            )

    sign_identity = parent["identity"]["signing_identity"]
    if helper["identity"]["signing_identity"] != sign_identity:
        raise CandidatePlanError("parent and helper signing identities must match")
    if helper["identity"]["team_identifier"] != parent["identity"]["team_identifier"]:
        raise CandidatePlanError("parent and helper Team IDs must match")
    operations: list[dict[str, Any]] = [
        {
            "id": "reserve_private_workspace",
            "kind": "workspace_reservation_contract",
            "output_parent": str(output),
            "workspace_ref": workspace,
            "policy": copy.deepcopy(contract["plan_policy"]["workspace_policy"]),
            "pinned_parent": {
                "canonical_path": str(output),
                "device": output_metadata.st_dev,
                "inode": output_metadata.st_ino,
            },
            "receipt_requirement": {
                "state": "ATOMIC_PRIVATE_WORKSPACE_RESERVED",
                "mode": "0700",
                "token_bits_at_least": 128,
                "attempts_at_most": 8,
                "descriptor_relative_cleanup_only": True,
            },
            "execution": "NOT_ATTEMPTED_AND_NOT_IMPLEMENTED",
        },
        {
            "id": "write_parent_info_plist",
            "kind": "write_plist_data",
            "path": f"{bundle}/Contents/Info.plist",
            "content": parent["info_plist"],
        },
        {
            "id": "compile_parent",
            "kind": "argv_batch",
            "argv": compile_commands["parent"],
            "tool_binding": copy.deepcopy(contract["tools"]["clang"]),
            "platform_binding": copy.deepcopy(platform),
        },
        {
            "id": "compile_helper",
            "kind": "argv_batch",
            "argv": compile_commands["helper"],
            "tool_binding": copy.deepcopy(contract["tools"]["clang"]),
            "platform_binding": copy.deepcopy(platform),
        },
        {
            "id": "link_helper",
            "kind": "argv",
            "argv": [*common_link, *object_paths["helper"], "-o", helper_path],
            "tool_binding": copy.deepcopy(contract["tools"]["clang"]),
            "platform_binding": copy.deepcopy(platform),
        },
        {
            "id": "link_parent",
            "kind": "argv",
            "argv": [*common_link, *object_paths["parent"], "-o", parent_path],
            "tool_binding": copy.deepcopy(contract["tools"]["clang"]),
            "platform_binding": copy.deepcopy(platform),
        },
        {
            "id": "sign_helper",
            "kind": "argv",
            "argv": [
                codesign,
                "--force",
                "--sign",
                sign_identity,
                "--options",
                "runtime",
                "--entitlements",
                str(source / helper["entitlements"]["relative_path"]),
                "--identifier",
                helper["bundle_identifier"],
                helper_path,
            ],
            "tool_binding": copy.deepcopy(contract["tools"]["codesign"]),
            "identity_binding": copy.deepcopy(helper["identity"]),
            "entitlement_binding": copy.deepcopy(helper["entitlements"]),
            "hardened_runtime_binding": copy.deepcopy(helper["hardened_runtime"]),
        },
        {
            "id": "verify_helper",
            "kind": "argv",
            "argv": [codesign, "--verify", "--strict", "--verbose=4", helper_path],
            "tool_binding": copy.deepcopy(contract["tools"]["codesign"]),
            "expected_identity": copy.deepcopy(helper["identity"]),
            "expected_entitlements": copy.deepcopy(helper["entitlements"]),
            "expected_hardened_runtime": copy.deepcopy(helper["hardened_runtime"]),
        },
        {
            "id": "sign_parent",
            "kind": "argv",
            "argv": [
                codesign,
                "--force",
                "--sign",
                sign_identity,
                "--options",
                "runtime",
                "--entitlements",
                str(source / parent["entitlements"]["relative_path"]),
                "--identifier",
                parent["bundle_identifier"],
                bundle,
            ],
            "tool_binding": copy.deepcopy(contract["tools"]["codesign"]),
            "identity_binding": copy.deepcopy(parent["identity"]),
            "entitlement_binding": copy.deepcopy(parent["entitlements"]),
            "hardened_runtime_binding": copy.deepcopy(parent["hardened_runtime"]),
        },
        {
            "id": "verify_parent",
            "kind": "argv",
            "argv": [
                codesign,
                "--verify",
                "--deep",
                "--strict",
                "--verbose=4",
                bundle,
            ],
            "tool_binding": copy.deepcopy(contract["tools"]["codesign"]),
            "expected_identity": copy.deepcopy(parent["identity"]),
            "expected_entitlements": copy.deepcopy(parent["entitlements"]),
            "expected_hardened_runtime": copy.deepcopy(parent["hardened_runtime"]),
        },
        {
            "id": "inventory_bundle",
            "kind": "verify_exact_members_data",
            "required_members": copy.deepcopy(
                contract["bundle_inventory"]["required_members"]
            ),
            "signing_generated_members": contract["bundle_inventory"][
                "signing_generated_members"
            ],
            "unexpected_member_policy": "REJECT",
            "symlink_policy": "REJECT_ALL_BUNDLE_MEMBER_SYMLINKS",
        },
    ]
    if [operation["id"] for operation in operations] != EXPECTED_OPERATION_ORDER:
        raise CandidatePlanError("generated operation order mismatch")
    plan = {
        "schema": "dream-house-canary-candidate-plan-data/1",
        "state": PLAN_STATE,
        "claim_ceiling": contract["claim_ceiling"],
        "operations": operations,
        "execution": "NOT_ATTEMPTED_AND_NOT_IMPLEMENTED",
        "candidate_creation": "NOT_ATTEMPTED",
        "candidate_launch": "NOT_ATTEMPTED",
    }
    encoded = json.dumps(plan, sort_keys=True, separators=(",", ":")).encode()
    if len(encoded) > contract["plan_policy"]["max_serialized_bytes"]:
        raise CandidatePlanError("generated plan exceeds the fixed size bound")
    return plan


def load_validate_and_generate(
    contract_path: str | Path,
    source_root: str | Path,
    output_root: str | Path,
) -> dict[str, Any]:
    """Convenience wrapper that remains data-only and has no executor."""

    return generate_candidate_plan(
        load_candidate_contract(contract_path), source_root, output_root
    )
