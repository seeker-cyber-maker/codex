"""Compile spawn-disabled C sources to relocatable objects without linking."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

DEFAULT_CLANG = "/Library/Developer/CommandLineTools/usr/bin/clang"
DEFAULT_NM = "/Library/Developer/CommandLineTools/usr/bin/nm"
DEFAULT_SDK = "/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk"
SOURCES = (
    "protocol.c",
    "parent_contract.c",
    "helper_contract.c",
    "parent_main.c",
    "helper_main.c",
)
FORBIDDEN_UNDEFINED = {
    "_connect",
    "_execve",
    "_fork",
    "_getenv",
    "_open",
    "_popen",
    "_posix_spawn",
    "_socket",
    "_system",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1_048_576), b""):
            digest.update(block)
    return digest.hexdigest()


def build_objects(
    source_root: str | Path,
    output_root: str | Path,
    *,
    clang: str = DEFAULT_CLANG,
    nm: str = DEFAULT_NM,
    sdk: str = DEFAULT_SDK,
) -> dict[str, Any]:
    source = Path(source_root).resolve(strict=True)
    output = Path(output_root)
    sdk_root = Path(sdk).resolve(strict=True)
    output.mkdir(parents=True, exist_ok=True)
    commands: list[list[str]] = []
    objects: dict[str, object] = {}
    for name in SOURCES:
        source_path = source / name
        object_path = output / f"{Path(name).stem}.o"
        command = [
            clang,
            "-isysroot",
            str(sdk_root),
            "-std=c11",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-pedantic",
            "-fno-common",
            "-c",
            str(source_path),
            "-o",
            str(object_path),
        ]
        commands.append(command)
        subprocess.run(command, check=True, capture_output=True, text=True)
        nm_command = [nm, "-u", str(object_path)]
        commands.append(nm_command)
        nm_result = subprocess.run(
            nm_command, check=True, capture_output=True, text=True
        )
        undefined = sorted(
            line.strip().split()[-1]
            for line in nm_result.stdout.splitlines()
            if line.strip() and not line.rstrip().endswith(":")
        )
        forbidden = sorted(FORBIDDEN_UNDEFINED.intersection(undefined))
        if forbidden:
            raise RuntimeError(f"{name} imports forbidden symbols: {forbidden!r}")
        objects[name] = {
            "source_sha256": _sha256(source_path),
            "object_sha256": _sha256(object_path),
            "undefined_symbols": undefined,
            "forbidden_symbols": forbidden,
            "executable": bool(object_path.stat().st_mode & 0o111),
        }
    return {
        "schema": "dream-house-canary-object-build-receipt/1",
        "state": "STATIC_OBJECTS_BUILT_NO_LINK_NO_LAUNCH",
        "candidate_launch": "NOT_ATTEMPTED",
        "link": "NOT_ATTEMPTED",
        "toolchain_processes": "CLANG_AND_NM_ONLY",
        "sdk": str(sdk_root),
        "commands": commands,
        "objects": objects,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build relocatable canary-helper objects only")
    parser.add_argument("--source-root", default=str(Path(__file__).parent))
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--clang", default=DEFAULT_CLANG)
    parser.add_argument("--nm", default=DEFAULT_NM)
    parser.add_argument("--sdk", default=DEFAULT_SDK)
    args = parser.parse_args()
    result = build_objects(
        args.source_root,
        args.output_root,
        clang=args.clang,
        nm=args.nm,
        sdk=args.sdk,
    )
    Path(args.receipt).write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
