#!/usr/bin/env python3
"""Capture an offline installed-vs-source Codex surface baseline."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_probe(label: str, executable: Path, args: list[str], env: dict[str, str]) -> dict:
    completed = subprocess.run(
        [str(executable), *args],
        check=False,
        capture_output=True,
        env=env,
        timeout=30,
    )
    return {
        "label": label,
        "argv": [executable.name, *args],
        "exit_code": completed.returncode,
        "stdout": completed.stdout.decode("utf-8", errors="replace"),
        "stderr": completed.stderr.decode("utf-8", errors="replace"),
        "combined_sha256": sha256_bytes(completed.stdout + b"\0" + completed.stderr),
    }


def tree_receipt(root: Path) -> dict:
    records = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        records.append(
            {
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    canonical = json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
    return {
        "file_count": len(records),
        "total_bytes": sum(record["bytes"] for record in records),
        "tree_sha256": sha256_bytes(canonical),
        "files": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--installed", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--source-app-server", type=Path, required=True)
    parser.add_argument("--git-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    for path in (args.installed, args.source, args.source_app_server):
        if not path.is_file():
            parser.error(f"missing executable: {path}")

    with tempfile.TemporaryDirectory(prefix="codex-dream-house-home-") as home_dir:
        with tempfile.TemporaryDirectory(prefix="codex-dream-house-schema-") as schema_dir:
            env = os.environ.copy()
            env["CODEX_HOME"] = home_dir
            env["NO_COLOR"] = "1"
            schema_path = Path(schema_dir)

            probes = [
                run_probe("installed_version", args.installed, ["--version"], env),
                run_probe("source_version", args.source, ["--version"], env),
                run_probe("installed_help", args.installed, ["--help"], env),
                run_probe("source_help", args.source, ["--help"], env),
                run_probe("installed_app_server_help", args.installed, ["app-server", "--help"], env),
                run_probe("source_app_server_help", args.source, ["app-server", "--help"], env),
                run_probe("source_direct_app_server_help", args.source_app_server, ["--help"], env),
                run_probe(
                    "source_generate_json_schema",
                    args.source,
                    ["app-server", "generate-json-schema", "--out", str(schema_path)],
                    env,
                ),
            ]

            receipt = {
                "schema": "codex-dream-house-baseline/1",
                "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                "git_commit": args.git_commit,
                "inference_requests": 0,
                "live_codex_home_read": False,
                "temporary_codex_home_preserved": False,
                "binaries": {
                    "installed": {"sha256": sha256_file(args.installed)},
                    "source": {"sha256": sha256_file(args.source)},
                    "source_app_server": {"sha256": sha256_file(args.source_app_server)},
                },
                "probes": probes,
                "generated_json_schema": tree_receipt(schema_path),
            }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    failed = [probe["label"] for probe in receipt["probes"] if probe["exit_code"] != 0]
    print(json.dumps({"output": str(args.output), "failed_probes": failed, "schema_files": receipt["generated_json_schema"]["file_count"]}))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
