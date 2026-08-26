#!/usr/bin/env python3
"""Create one sealed, local-only TERM roster binding document.

This is the intake half of the TERM experiment.  It hashes the local inference
payload and runtime files, performs one lazy local static-load preflight per
opaque candidate, and writes a single append-only binding document.  It never
generates text, sends a provider request, or accesses Dream House control-plane
surfaces.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sys

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from house.term_notation.compatibility import canonical_fixture_projection_sha256
from house.workflow.run_term_local_compatibility import BINDING_SCHEMA, RUN_ID


_CANDIDATES = (
    ("local-term-candidate-01", "/Volumes/Models/trainers/prometheus-7b-v2.0-mlx-bf16", {}, {}),
    ("local-term-candidate-02", "/Volumes/HIKSEMI/omlx/mlx-community/Devstral-Small-2-24B-Instruct-2512-4bit", {"fix_mistral_regex": True}, {}),
    ("local-term-candidate-03", "/Volumes/HIKSEMI/omlx/mlx-community/Qwen3.5-9B-MLX-4bit", {}, {"enable_thinking": False}),
    ("local-term-candidate-04", "/Volumes/HIKSEMI/omlx/mlx-community/gpt-oss-20b-MXFP4-Q8", {}, {"reasoning_effort": "low"}),
    ("local-term-candidate-05", "/Volumes/HIKSEMI/omlx/mlx-community/Qwen3.6-27B-4bit", {}, {"enable_thinking": False}),
    ("local-term-candidate-06", "/Volumes/HIKSEMI/omlx/mlx-community/Qwen3.6-35B-A3B-4bit", {}, {"enable_thinking": False}),
)
_RUNTIME_FILENAMES = {
    "chat_template.jinja",
    "config.json",
    "configuration.json",
    "generation_config.json",
    "model.safetensors.index.json",
    "params.json",
    "preprocessor_config.json",
    "processor_config.json",
    "special_tokens_map.json",
    "tekken.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "video_preprocessor_config.json",
    "vocab.json",
}


class RosterPreparationError(ValueError):
    """Raised when a closed TERM roster cannot be prepared safely."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _artifact_files(root: Path) -> list[dict[str, str]]:
    if not root.is_dir():
        raise RosterPreparationError(f"candidate root is unavailable: {root}")
    selected = sorted(
        path for path in root.iterdir()
        if path.is_file() and (path.suffix == ".safetensors" or path.name in _RUNTIME_FILENAMES)
    )
    if not selected or not any(path.suffix == ".safetensors" for path in selected):
        raise RosterPreparationError(f"candidate lacks local safetensors payload: {root}")
    return [{"path": path.name, "sha256": _sha256(path)} for path in selected]


def _lazy_local_load(root: Path, tokenizer_config: dict[str, object]) -> None:
    # This import and load happen only after the on-disk fingerprint is complete.
    from mlx_lm import load

    model, tokenizer = load(str(root), lazy=True, tokenizer_config=tokenizer_config)
    del model, tokenizer


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False) as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def prepare(output: Path) -> dict[str, Any]:
    """Build one non-overwriting binding document from the frozen six-variant roster."""

    output = output.resolve()
    try:
        output.relative_to(_REPO_ROOT)
    except ValueError as error:
        raise RosterPreparationError("binding output must remain inside this repository") from error
    if output.exists():
        raise RosterPreparationError("binding document already exists; append-only preservation forbids overwrite")
    fixture_path = _REPO_ROOT / "house/term_notation/compatibility_fixtures_v1.json"
    fixtures = json.loads(fixture_path.read_text(encoding="utf-8"))
    bindings = []
    for candidate_id, raw_path, tokenizer_config, template_kwargs in _CANDIDATES:
        root = Path(raw_path)
        files = _artifact_files(root)
        _lazy_local_load(root, tokenizer_config)
        bindings.append({
            "opaque_candidate_id": candidate_id,
            "artifact": {"local_provenance_path": raw_path, "files": files},
            "runtime": {"tokenizer_config": tokenizer_config, "template_kwargs": template_kwargs},
            "static_load": "PASS_LAZY_LOCAL_ONLY",
        })
    document = {
        "schema": BINDING_SCHEMA,
        "run_id": RUN_ID,
        "fixture_projection_sha256": canonical_fixture_projection_sha256(fixtures),
        "bindings": bindings,
    }
    _atomic_json(output, document)
    return document


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    document = prepare(args.output)
    print(json.dumps({"output": str(args.output.resolve()), "candidate_count": len(document["bindings"])}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
