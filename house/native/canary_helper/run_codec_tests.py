"""Link and execute only the pure protocol-codec contract test."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import stat
import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

DEFAULT_CLANG = "/Library/Developer/CommandLineTools/usr/bin/clang"
DEFAULT_SDK = "/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk"
CODESIGN = "/usr/bin/codesign"
MAX_OUTPUT_BYTES = 1_048_576
DEFAULT_COMPILE_TIMEOUT_SECONDS = 30
DEFAULT_INSPECTION_TIMEOUT_SECONDS = 10
PRIVATE_DIRECTORY_ATTEMPTS = 8
PRIVATE_DIRECTORY_PREFIX = ".dream-house-codec."
TEST_EXECUTABLE_NAME = "codec_contract_test"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1_048_576), b""):
            digest.update(block)
    return digest.hexdigest()


def _bounded_output(result: subprocess.CompletedProcess[str]) -> str:
    output = (result.stdout or "") + (result.stderr or "")
    if len(output.encode("utf-8", errors="replace")) > MAX_OUTPUT_BYTES:
        raise RuntimeError("codec test process output exceeded the fixed bound")
    return output


def _positive_timeout(value: int, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise RuntimeError(f"{label} must be a positive integer")
    return value


def _run_process(
    argv: list[str],
    *,
    label: str,
    timeout_seconds: int,
) -> subprocess.CompletedProcess[str]:
    timeout = _positive_timeout(timeout_seconds, f"{label} timeout")
    try:
        return subprocess.run(
            argv,
            check=False,
            capture_output=True,
            text=True,
            env={"LC_ALL": "C"},
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"{label} timed out after {timeout} seconds") from exc


@contextmanager
def _private_output_directory(output_root: str | Path) -> Iterator[tuple[Path, int]]:
    requested_root = Path(output_root)
    requested_info = requested_root.lstat()
    if stat.S_ISLNK(requested_info.st_mode):
        raise RuntimeError("codec output root must not be a symlink")
    if not stat.S_ISDIR(requested_info.st_mode):
        raise RuntimeError("codec output root must be an existing directory")

    canonical_root = requested_root.resolve(strict=True)
    directory_flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    root_descriptor = os.open(canonical_root, directory_flags)
    private_name: str | None = None
    private_descriptor: int | None = None
    cleanup_error: RuntimeError | None = None
    try:
        root_info = os.fstat(root_descriptor)
        if not stat.S_ISDIR(root_info.st_mode):
            raise RuntimeError("codec output root changed away from a directory")
        for _ in range(PRIVATE_DIRECTORY_ATTEMPTS):
            candidate = f"{PRIVATE_DIRECTORY_PREFIX}{secrets.token_hex(16)}"
            try:
                os.mkdir(candidate, 0o700, dir_fd=root_descriptor)
            except FileExistsError:
                continue
            private_name = candidate
            break
        if private_name is None:
            raise RuntimeError("could not reserve a private codec output directory")

        private_descriptor = os.open(
            private_name, directory_flags, dir_fd=root_descriptor
        )
        os.fchmod(private_descriptor, 0o700)
        private_info = os.fstat(private_descriptor)
        private_path = canonical_root / private_name
        path_info = os.stat(private_path, follow_symlinks=False)
        if not stat.S_ISDIR(path_info.st_mode):
            raise RuntimeError("private codec output path is not a directory")
        if (path_info.st_dev, path_info.st_ino) != (
            private_info.st_dev,
            private_info.st_ino,
        ):
            raise RuntimeError("private codec output path identity mismatch")
        if stat.S_IMODE(private_info.st_mode) != 0o700:
            raise RuntimeError("private codec output directory mode is not 0700")
        yield private_path, private_descriptor
    finally:
        if private_descriptor is not None:
            entries = os.listdir(private_descriptor)
            unexpected = [entry for entry in entries if entry != TEST_EXECUTABLE_NAME]
            if unexpected:
                cleanup_error = RuntimeError(
                    f"private codec output contains unexpected entries: {unexpected!r}"
                )
            if TEST_EXECUTABLE_NAME in entries:
                try:
                    os.unlink(TEST_EXECUTABLE_NAME, dir_fd=private_descriptor)
                except OSError as exc:
                    cleanup_error = RuntimeError(
                        "could not remove the exact codec test executable"
                    )
                    cleanup_error.__cause__ = exc
            os.close(private_descriptor)
        if private_name is not None and cleanup_error is None:
            try:
                os.rmdir(private_name, dir_fd=root_descriptor)
            except OSError as exc:
                cleanup_error = RuntimeError(
                    "could not remove the private codec output directory"
                )
                cleanup_error.__cause__ = exc
        os.close(root_descriptor)
        if cleanup_error is not None:
            raise cleanup_error


def _require_regular_executable(directory_descriptor: int) -> None:
    info = os.stat(
        TEST_EXECUTABLE_NAME,
        dir_fd=directory_descriptor,
        follow_symlinks=False,
    )
    if not stat.S_ISREG(info.st_mode):
        raise RuntimeError("codec test output is not a regular file")


def run_codec_tests(
    source_root: str | Path,
    output_root: str | Path,
    *,
    clang: str = DEFAULT_CLANG,
    sdk: str = DEFAULT_SDK,
    timeout_seconds: int = 5,
    compile_timeout_seconds: int = DEFAULT_COMPILE_TIMEOUT_SECONDS,
    inspection_timeout_seconds: int = DEFAULT_INSPECTION_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    source = Path(source_root).resolve(strict=True)
    sdk_root = Path(sdk).resolve(strict=True)
    protocol_source = source / "protocol.c"
    test_source = source / "tests" / "codec_contract_test.c"
    compile_timeout = _positive_timeout(
        compile_timeout_seconds, "codec compile timeout"
    )
    inspection_timeout = _positive_timeout(
        inspection_timeout_seconds, "signature inspection timeout"
    )
    execution_timeout = _positive_timeout(timeout_seconds, "codec execution timeout")

    receipt: dict[str, Any]
    with _private_output_directory(output_root) as (output, output_descriptor):
        executable = output / TEST_EXECUTABLE_NAME
        compile_command = [
            clang,
            "-isysroot",
            str(sdk_root),
            "-std=c11",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-pedantic",
            "-fno-common",
            "-I",
            str(source),
            str(protocol_source),
            str(test_source),
            "-o",
            str(executable),
        ]
        compile_result = _run_process(
            compile_command,
            label="codec test link",
            timeout_seconds=compile_timeout,
        )
        compile_output = _bounded_output(compile_result)
        if compile_result.returncode != 0:
            raise RuntimeError(f"codec test link failed: {compile_output}")
        _require_regular_executable(output_descriptor)

        signature_command = [CODESIGN, "--display", "--verbose=4", str(executable)]
        signature_result = _run_process(
            signature_command,
            label="codec signature inspection",
            timeout_seconds=inspection_timeout,
        )
        signature_output = _bounded_output(signature_result)
        if signature_result.returncode != 0:
            raise RuntimeError("codec test signature metadata inspection failed")
        signature_match = re.search(r"(?m)^Signature=(.+)$", signature_output)
        team_match = re.search(r"(?m)^TeamIdentifier=(.+)$", signature_output)
        signature = signature_match.group(1).strip() if signature_match else "unknown"
        team_identifier = team_match.group(1).strip() if team_match else "not set"
        if signature.lower() != "adhoc" or team_identifier != "not set":
            raise RuntimeError("codec test unexpectedly used an identity-bearing signature")
        _require_regular_executable(output_descriptor)

        run_command = [str(executable)]
        run_result = _run_process(
            run_command,
            label="codec contract test",
            timeout_seconds=execution_timeout,
        )
        run_output = _bounded_output(run_result)
        if run_result.returncode != 0:
            raise RuntimeError(f"codec contract test failed with {run_result.returncode}")
        if run_output:
            raise RuntimeError("codec contract test produced unexpected output")
        _require_regular_executable(output_descriptor)
        receipt = {
            "schema": "dream-house-canary-codec-test-receipt/2",
            "state": "PURE_CODEC_TEST_LINKED_AND_PASSED",
            "protocol_source_sha256": _sha256(protocol_source),
            "test_source_sha256": _sha256(test_source),
            "test_executable_sha256": _sha256(executable),
            "test_executable_signature": signature,
            "test_executable_team_identifier": team_identifier,
            "compile_timeout_seconds": compile_timeout,
            "signature_inspection_timeout_seconds": inspection_timeout,
            "execution_timeout_seconds": execution_timeout,
            "private_output_directory": str(output),
            "private_output_directory_mode": "0700",
            "private_output_cleanup": "COMPLETED_BEFORE_RECEIPT_RETURN",
            "compile_command": compile_command,
            "signature_inspection_command": signature_command,
            "run_command": run_command,
            "run_returncode": run_result.returncode,
            "stdout_bytes": len((run_result.stdout or "").encode()),
            "stderr_bytes": len((run_result.stderr or "").encode()),
            "candidate_link": "NOT_ATTEMPTED",
            "candidate_launch": "NOT_ATTEMPTED",
            "parent_helper_link": "NOT_ATTEMPTED",
            "parent_helper_launch": "NOT_ATTEMPTED",
            "identity_signing": "NOT_ATTEMPTED",
            "keychain": "NOT_ATTEMPTED",
            "network": "NOT_ATTEMPTED",
            "generated_canary": "NOT_ATTEMPTED",
            "real_secret": "NOT_ATTEMPTED",
            "process_environment": {"LC_ALL": "C"},
            "process_count": 3,
            "tool_processes": ["clang/linker", "codesign display", "codec test"],
            "host_pid": os.getpid(),
        }
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the pure codec contract test")
    parser.add_argument("--source-root", default=str(Path(__file__).parent))
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--clang", default=DEFAULT_CLANG)
    parser.add_argument("--sdk", default=DEFAULT_SDK)
    args = parser.parse_args()
    result = run_codec_tests(
        args.source_root,
        args.output_root,
        clang=args.clang,
        sdk=args.sdk,
    )
    Path(args.receipt).write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
