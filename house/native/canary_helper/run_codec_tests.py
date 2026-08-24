"""Link and execute only the pure protocol-codec contract test."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

DEFAULT_CLANG = "/Library/Developer/CommandLineTools/usr/bin/clang"
DEFAULT_SDK = "/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk"
CODESIGN = "/usr/bin/codesign"
MAX_OUTPUT_BYTES = 1_048_576


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


def run_codec_tests(
    source_root: str | Path,
    output_root: str | Path,
    *,
    clang: str = DEFAULT_CLANG,
    sdk: str = DEFAULT_SDK,
    timeout_seconds: int = 5,
) -> dict[str, Any]:
    source = Path(source_root).resolve(strict=True)
    output = Path(output_root)
    output.mkdir(parents=True, exist_ok=True)
    sdk_root = Path(sdk).resolve(strict=True)
    protocol_source = source / "protocol.c"
    test_source = source / "tests" / "codec_contract_test.c"
    executable = output / "codec_contract_test"
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
    compile_result = subprocess.run(
        compile_command,
        check=False,
        capture_output=True,
        text=True,
        env={"LC_ALL": "C"},
    )
    compile_output = _bounded_output(compile_result)
    if compile_result.returncode != 0:
        raise RuntimeError(f"codec test link failed: {compile_output}")

    signature_command = [CODESIGN, "--display", "--verbose=4", str(executable)]
    signature_result = subprocess.run(
        signature_command,
        check=False,
        capture_output=True,
        text=True,
        env={"LC_ALL": "C"},
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

    run_command = [str(executable)]
    run_result = subprocess.run(
        run_command,
        check=False,
        capture_output=True,
        text=True,
        env={"LC_ALL": "C"},
        timeout=timeout_seconds,
    )
    run_output = _bounded_output(run_result)
    if run_result.returncode != 0:
        raise RuntimeError(f"codec contract test failed with {run_result.returncode}")
    if run_output:
        raise RuntimeError("codec contract test produced unexpected output")
    return {
        "schema": "dream-house-canary-codec-test-receipt/1",
        "state": "PURE_CODEC_TEST_LINKED_AND_PASSED",
        "protocol_source_sha256": _sha256(protocol_source),
        "test_source_sha256": _sha256(test_source),
        "test_executable_sha256": _sha256(executable),
        "test_executable_signature": signature,
        "test_executable_team_identifier": team_identifier,
        "timeout_seconds": timeout_seconds,
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
