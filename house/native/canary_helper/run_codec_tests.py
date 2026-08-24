"""Link and execute only pure codec and entrypoint-contract test programs."""

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
TEST_EXECUTABLE_NAMES = ("codec_contract_test", "entrypoint_contract_test")


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
            unexpected = [entry for entry in entries if entry not in TEST_EXECUTABLE_NAMES]
            if unexpected:
                cleanup_error = RuntimeError(
                    f"private codec output contains unexpected entries: {unexpected!r}"
                )
            for executable_name in TEST_EXECUTABLE_NAMES:
                if executable_name not in entries:
                    continue
                try:
                    os.unlink(executable_name, dir_fd=private_descriptor)
                except OSError as exc:
                    cleanup_error = RuntimeError(
                        "could not remove an exact pure contract test executable"
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


def _require_regular_executable(directory_descriptor: int, name: str) -> None:
    info = os.stat(
        name,
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
    parent_contract_source = source / "parent_contract.c"
    helper_contract_source = source / "helper_contract.c"
    parent_entrypoint_source = source / "parent_main.c"
    helper_entrypoint_source = source / "helper_main.c"
    codec_test_source = source / "tests" / "codec_contract_test.c"
    entrypoint_test_source = source / "tests" / "entrypoint_contract_test.c"
    compile_timeout = _positive_timeout(
        compile_timeout_seconds, "codec compile timeout"
    )
    inspection_timeout = _positive_timeout(
        inspection_timeout_seconds, "signature inspection timeout"
    )
    execution_timeout = _positive_timeout(timeout_seconds, "codec execution timeout")

    receipt: dict[str, Any]
    with _private_output_directory(output_root) as (output, output_descriptor):
        codec_executable = output / TEST_EXECUTABLE_NAMES[0]
        codec_compile_command = [
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
            str(codec_test_source),
            "-o",
            str(codec_executable),
        ]
        codec_compile_result = _run_process(
            codec_compile_command,
            label="codec test link",
            timeout_seconds=compile_timeout,
        )
        codec_compile_output = _bounded_output(codec_compile_result)
        if codec_compile_result.returncode != 0:
            raise RuntimeError(f"codec test link failed: {codec_compile_output}")
        _require_regular_executable(output_descriptor, TEST_EXECUTABLE_NAMES[0])

        codec_signature_command = [CODESIGN, "--display", "--verbose=4", str(codec_executable)]
        codec_signature_result = _run_process(
            codec_signature_command,
            label="codec signature inspection",
            timeout_seconds=inspection_timeout,
        )
        codec_signature_output = _bounded_output(codec_signature_result)
        if codec_signature_result.returncode != 0:
            raise RuntimeError("codec test signature metadata inspection failed")
        signature_match = re.search(r"(?m)^Signature=(.+)$", codec_signature_output)
        team_match = re.search(r"(?m)^TeamIdentifier=(.+)$", codec_signature_output)
        signature = signature_match.group(1).strip() if signature_match else "unknown"
        team_identifier = team_match.group(1).strip() if team_match else "not set"
        if signature.lower() != "adhoc" or team_identifier != "not set":
            raise RuntimeError("codec test unexpectedly used an identity-bearing signature")
        _require_regular_executable(output_descriptor, TEST_EXECUTABLE_NAMES[0])

        codec_run_command = [str(codec_executable)]
        codec_run_result = _run_process(
            codec_run_command,
            label="codec contract test",
            timeout_seconds=execution_timeout,
        )
        codec_run_output = _bounded_output(codec_run_result)
        if codec_run_result.returncode != 0:
            raise RuntimeError(f"codec contract test failed with {codec_run_result.returncode}")
        if codec_run_output:
            raise RuntimeError("codec contract test produced unexpected output")
        _require_regular_executable(output_descriptor, TEST_EXECUTABLE_NAMES[0])

        entrypoint_executable = output / TEST_EXECUTABLE_NAMES[1]
        entrypoint_compile_command = [
            clang, "-isysroot", str(sdk_root), "-std=c11", "-Wall", "-Wextra",
            "-Werror", "-pedantic", "-fno-common", "-DDH_CANARY_ENTRYPOINT_UNIT_TEST",
            "-I", str(source), str(protocol_source), str(parent_contract_source),
            str(helper_contract_source), str(parent_entrypoint_source),
            str(helper_entrypoint_source), str(entrypoint_test_source), "-o",
            str(entrypoint_executable),
        ]
        entrypoint_compile_result = _run_process(
            entrypoint_compile_command,
            label="entrypoint contract test link",
            timeout_seconds=compile_timeout,
        )
        entrypoint_compile_output = _bounded_output(entrypoint_compile_result)
        if entrypoint_compile_result.returncode != 0:
            raise RuntimeError(f"entrypoint contract test link failed: {entrypoint_compile_output}")
        _require_regular_executable(output_descriptor, TEST_EXECUTABLE_NAMES[1])
        entrypoint_signature_command = [
            CODESIGN, "--display", "--verbose=4", str(entrypoint_executable)
        ]
        entrypoint_signature_result = _run_process(
            entrypoint_signature_command,
            label="entrypoint signature inspection",
            timeout_seconds=inspection_timeout,
        )
        entrypoint_signature_output = _bounded_output(entrypoint_signature_result)
        if entrypoint_signature_result.returncode != 0:
            raise RuntimeError("entrypoint test signature metadata inspection failed")
        entrypoint_signature_match = re.search(
            r"(?m)^Signature=(.+)$", entrypoint_signature_output
        )
        entrypoint_team_match = re.search(
            r"(?m)^TeamIdentifier=(.+)$", entrypoint_signature_output
        )
        entrypoint_signature = (
            entrypoint_signature_match.group(1).strip()
            if entrypoint_signature_match
            else "unknown"
        )
        entrypoint_team_identifier = (
            entrypoint_team_match.group(1).strip()
            if entrypoint_team_match
            else "not set"
        )
        if entrypoint_signature.lower() != "adhoc" or entrypoint_team_identifier != "not set":
            raise RuntimeError(
                "entrypoint test unexpectedly used an identity-bearing signature"
            )
        _require_regular_executable(output_descriptor, TEST_EXECUTABLE_NAMES[1])
        entrypoint_run_command = [str(entrypoint_executable)]
        entrypoint_run_result = _run_process(
            entrypoint_run_command,
            label="entrypoint contract test",
            timeout_seconds=execution_timeout,
        )
        entrypoint_run_output = _bounded_output(entrypoint_run_result)
        if entrypoint_run_result.returncode != 0:
            raise RuntimeError(
                f"entrypoint contract test failed with {entrypoint_run_result.returncode}"
            )
        if entrypoint_run_output:
            raise RuntimeError("entrypoint contract test produced unexpected output")
        _require_regular_executable(output_descriptor, TEST_EXECUTABLE_NAMES[1])
        receipt = {
            "schema": "dream-house-canary-contract-test-receipt/3",
            "state": "PURE_CODEC_AND_ENTRYPOINT_TESTS_LINKED_AND_PASSED",
            "protocol_source_sha256": _sha256(protocol_source),
            "codec_test_source_sha256": _sha256(codec_test_source),
            "entrypoint_test_source_sha256": _sha256(entrypoint_test_source),
            "parent_entrypoint_source_sha256": _sha256(parent_entrypoint_source),
            "helper_entrypoint_source_sha256": _sha256(helper_entrypoint_source),
            "test_executable_sha256": _sha256(codec_executable),
            "entrypoint_test_executable_sha256": _sha256(entrypoint_executable),
            "entrypoint_test_executable_signature": entrypoint_signature,
            "entrypoint_test_executable_team_identifier": entrypoint_team_identifier,
            "test_executable_signature": signature,
            "test_executable_team_identifier": team_identifier,
            "compile_timeout_seconds": compile_timeout,
            "signature_inspection_timeout_seconds": inspection_timeout,
            "execution_timeout_seconds": execution_timeout,
            "private_output_directory": str(output),
            "private_output_directory_mode": "0700",
            "private_output_cleanup": "COMPLETED_BEFORE_RECEIPT_RETURN",
            "compile_command": codec_compile_command,
            "signature_inspection_command": codec_signature_command,
            "run_command": codec_run_command,
            "run_returncode": codec_run_result.returncode,
            "stdout_bytes": len((codec_run_result.stdout or "").encode()),
            "stderr_bytes": len((codec_run_result.stderr or "").encode()),
            "entrypoint_compile_command": entrypoint_compile_command,
            "entrypoint_signature_inspection_command": entrypoint_signature_command,
            "entrypoint_run_command": entrypoint_run_command,
            "entrypoint_run_returncode": entrypoint_run_result.returncode,
            "entrypoint_stdout_bytes": len((entrypoint_run_result.stdout or "").encode()),
            "entrypoint_stderr_bytes": len((entrypoint_run_result.stderr or "").encode()),
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
            "process_count": 6,
            "tool_processes": ["clang/linker", "codesign display", "codec test", "clang/linker", "codesign display", "entrypoint test"],
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
