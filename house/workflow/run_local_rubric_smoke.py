#!/usr/bin/env python3
"""Run one sealed, inference-only local rubric smoke test.

This driver lives outside ``house.local_model_evaluation`` on purpose: the
shared package is pure validation and cannot execute models.  This script only
accepts the closed execution-manifest surface, records a receipt atomically,
and has no Dream House control-plane imports.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import mlx.core as mx
from mlx_lm import generate, load
from mlx_lm.sample_utils import make_sampler

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from house.local_model_evaluation import LocalEvaluationContractError, parse_adapter_score, render_rubric_prompt


EXECUTION_SCHEMA = "dream-house/local-rubric-inference-manifest/1"
_MANIFEST_FIELDS = {
    "schema",
    "state",
    "authority_basis",
    "opaque_candidate_id",
    "prebinding",
    "fixture_set",
    "case_ids",
    "adapter_id",
    "runtime",
    "decoding",
    "effects",
    "acceptance_ceiling",
}
_EFFECTS = {
    "model_load": "AUTHORIZED",
    "provider_call": "FORBIDDEN",
    "training": "FORBIDDEN",
    "worker_dispatch": "FORBIDDEN",
    "candidate_promotion": "FORBIDDEN",
}
class SmokeRunError(ValueError):
    """Raised before model loading when the sealed run contract is invalid."""


def _load_json(path: Path) -> dict[str, Any] | list[Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, (dict, list)):
        raise SmokeRunError(f"{path} must contain a JSON object or array")
    return value


def _repo_path(path_value: object, label: str) -> Path:
    if not isinstance(path_value, str) or not path_value:
        raise SmokeRunError(f"{label} must be nonempty relative text")
    candidate = (_REPO_ROOT / path_value).resolve()
    try:
        candidate.relative_to(_REPO_ROOT)
    except ValueError as error:
        raise SmokeRunError(f"{label} escapes the repository") from error
    return candidate


def _manifest_relative_path(manifest_path: Path, path_value: object, label: str) -> Path:
    if not isinstance(path_value, str) or not path_value:
        raise SmokeRunError(f"{label} must be nonempty relative text")
    candidate = (manifest_path.parent / path_value).resolve()
    try:
        candidate.relative_to(_REPO_ROOT)
    except ValueError as error:
        raise SmokeRunError(f"{label} escapes the repository") from error
    return candidate


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _require_exact_fields(value: object, expected: set[str], label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != expected:
        raise SmokeRunError(f"{label} schema drift")
    return value


def _select_adapter(adapters: object, adapter_id: str) -> Mapping[str, Any]:
    if not isinstance(adapters, list):
        raise SmokeRunError("adapter declarations must be a list")
    matches = [adapter for adapter in adapters if isinstance(adapter, Mapping) and adapter.get("adapter_id") == adapter_id]
    if len(matches) != 1:
        raise SmokeRunError("sealed adapter is absent or ambiguous")
    return matches[0]


def _validate_execution_manifest(manifest: object) -> Mapping[str, Any]:
    value = _require_exact_fields(manifest, _MANIFEST_FIELDS, "execution manifest")
    if value["schema"] != EXECUTION_SCHEMA or value["state"] != "INFERENCE_ONLY_AUTHORIZED":
        raise SmokeRunError("manifest does not grant the required inference-only state")
    if value["effects"] != _EFFECTS:
        raise SmokeRunError("execution effects are not the closed inference-only surface")
    if value["acceptance_ceiling"] != "runtime-and-format-smoke-only":
        raise SmokeRunError("acceptance ceiling is not the sealed smoke-test ceiling")
    decoding = value["decoding"]
    expected_decoding = {"temperature": 0.0, "seed": 20260825, "max_tokens": 32, "retries": 0}
    if decoding != expected_decoding:
        raise SmokeRunError("decoding configuration drift")
    runtime = value["runtime"]
    if not isinstance(runtime, Mapping) or runtime.get("tokenizer_config") != {"fix_mistral_regex": True}:
        raise SmokeRunError("runtime tokenizer configuration drift")
    case_ids = value["case_ids"]
    if not isinstance(case_ids, list) or not case_ids or len(case_ids) != len(set(case_ids)):
        raise SmokeRunError("case_ids must be a unique nonempty list")
    return value


def _verify_binding(binding: Mapping[str, Any]) -> tuple[Path, list[dict[str, str]]]:
    artifact = binding.get("artifact")
    if not isinstance(artifact, Mapping):
        raise SmokeRunError("prebinding artifact is absent")
    model_path_value = artifact.get("local_provenance_path")
    if not isinstance(model_path_value, str) or not model_path_value.startswith("/Volumes/"):
        raise SmokeRunError("prebinding model path is not a declared local volume path")
    model_path = Path(model_path_value)
    files = artifact.get("files")
    if not model_path.is_dir() or not isinstance(files, list) or not files:
        raise SmokeRunError("prebound artifact is unavailable")
    verified: list[dict[str, str]] = []
    for item in files:
        if not isinstance(item, Mapping) or set(item) != {"path", "sha256"}:
            raise SmokeRunError("prebinding file entry drift")
        relative = item["path"]
        expected = item["sha256"]
        if not isinstance(relative, str) or Path(relative).is_absolute() or "/" in relative:
            raise SmokeRunError("prebinding file entry path is unsafe")
        if not isinstance(expected, str) or len(expected) != 64:
            raise SmokeRunError("prebinding file hash is invalid")
        artifact_file = model_path / relative
        actual = _sha256(artifact_file)
        if actual != expected:
            raise SmokeRunError(f"prebinding fingerprint mismatch: {relative}")
        verified.append({"path": relative, "sha256": actual})
    return model_path, verified


def _render_prompt(adapter: Mapping[str, Any], fixture: Mapping[str, Any], tokenizer: Any) -> str:
    prompt = render_rubric_prompt(fixture, adapter)
    if adapter.get("input_renderer") == "chat_template_system_user_v1":
        return tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}], tokenize=False, add_generation_prompt=True
        )
    if adapter.get("input_renderer") == "chat_template_single_user_v1":
        return prompt
    raise SmokeRunError("adapter renderer is not supported by this bounded runner")


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def run(manifest_path: Path, output_path: Path) -> dict[str, Any]:
    manifest = _validate_execution_manifest(_load_json(manifest_path))
    binding_path = _manifest_relative_path(manifest_path, manifest["prebinding"], "prebinding")
    binding = _load_json(binding_path)
    if not isinstance(binding, Mapping):
        raise SmokeRunError("prebinding must be an object")
    if binding.get("opaque_candidate_id") != manifest["opaque_candidate_id"]:
        raise SmokeRunError("candidate binding mismatch")
    if binding.get("state") not in {"PREPARED_NOT_AUTHORIZED", "INFERENCE_ONLY_AUTHORIZED"}:
        raise SmokeRunError("candidate binding state is unavailable")
    model_path, verified_files = _verify_binding(binding)
    fixtures_value = _load_json(_repo_path(manifest["fixture_set"], "fixture_set"))
    adapters_value = _load_json(_REPO_ROOT / "house/local_model_evaluation/adapter_declarations_v1.json")
    if not isinstance(fixtures_value, Mapping):
        raise SmokeRunError("fixture set must be an object")
    adapter = _select_adapter(adapters_value, str(manifest["adapter_id"]))
    fixtures_by_id = {
        fixture.get("case_id"): fixture
        for fixture in fixtures_value.get("fixtures", [])
        if isinstance(fixture, Mapping)
    }
    selected = []
    for case_id in manifest["case_ids"]:
        fixture = fixtures_by_id.get(case_id)
        if fixture is None:
            raise SmokeRunError(f"sealed fixture is absent: {case_id}")
        selected.append(fixture)

    decoding = manifest["decoding"]
    mx.random.seed(decoding["seed"])
    model, tokenizer = load(
        str(model_path), lazy=True, tokenizer_config=dict(manifest["runtime"]["tokenizer_config"])
    )
    sampler = make_sampler(temp=decoding["temperature"])
    cases: list[dict[str, Any]] = []
    for fixture in selected:
        prompt = _render_prompt(adapter, fixture, tokenizer)
        output = generate(
            model,
            tokenizer,
            prompt=prompt,
            verbose=False,
            sampler=sampler,
            max_tokens=decoding["max_tokens"],
        )
        record: dict[str, Any] = {
            "case_id": fixture["case_id"],
            "expected_scores": fixture["expected_scores"],
            "output": output,
        }
        try:
            score = parse_adapter_score(adapter, output)
        except LocalEvaluationContractError as error:
            record.update({"parsed_score": None, "parse_error": str(error), "score_agrees": False})
        else:
            record.update({"parsed_score": score, "parse_error": None, "score_agrees": score in fixture["expected_scores"]})
        cases.append(record)
    parsed_cases = [case for case in cases if case["parsed_score"] is not None]
    result: dict[str, Any] = {
        "schema": "dream-house/local-rubric-inference-receipt/1",
        "state": "COMPLETED_INFERENCE_ONLY",
        "manifest": {"path": str(manifest_path), "sha256": _sha256(manifest_path)},
        "prebinding": {"path": str(binding_path), "sha256": _sha256(binding_path)},
        "opaque_candidate_id": manifest["opaque_candidate_id"],
        "artifact_fingerprint_verified": verified_files,
        "adapter_id": adapter["adapter_id"],
        "runtime": manifest["runtime"],
        "decoding": decoding,
        "cases": cases,
        "metrics": {
            "case_count": len(cases),
            "parse_rate": len(parsed_cases) / len(cases),
            "score_agreement": sum(case["score_agrees"] for case in cases) / len(cases),
        },
        "effects": manifest["effects"],
        "acceptance_ceiling": manifest["acceptance_ceiling"],
        "disposition": "RUNTIME_AND_FORMAT_EVIDENCE_ONLY_NOT_A_WORKER_QUALIFICATION",
    }
    _atomic_json(output_path, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    output_path = args.output.resolve()
    try:
        manifest_path.relative_to(_REPO_ROOT)
        output_path.relative_to(_REPO_ROOT)
    except ValueError as error:
        raise SystemExit("manifest and output must remain within this repository") from error
    result = run(manifest_path, output_path)
    print(json.dumps({"receipt": str(output_path), "metrics": result["metrics"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
