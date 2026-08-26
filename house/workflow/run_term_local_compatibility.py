#!/usr/bin/env python3
"""Collect one sealed, local-only TERM compatibility receipt.

The runner is intentionally a narrow inference wrapper.  It knows no Dream
House task, ticket, relay, worker, provider, network, training, credential, or
promotion API.  It accepts a pre-bound local artifact only after every declared
file hash matches, renders the frozen fixture/condition matrix, and atomically
writes one opaque-candidate receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import time
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import sys

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from house.term_notation.compatibility import canonical_fixture_projection_sha256
from house.term_notation.local_compatibility_runner import CONDITIONS, render_condition, score_output


RUN_SCHEMA = "dream-house-run-manifest/1"
BINDING_SCHEMA = "dream-house/term-notation-local-roster-bindings/1"
RECEIPT_SCHEMA = "dream-house/term-notation-local-compatibility-receipt/1"
RUN_ID = "20260826T001404Z-term-notation-local-compatibility"
_ROSTER = tuple(f"local-term-candidate-{number:02d}" for number in range(1, 7))
_DECODING = {"temperature": 0.0, "seed": 20260826, "max_tokens": 96, "retries": 0}
_BUDGETS = {
    "candidate_runs": 6,
    "prompt_renders_per_candidate": 40,
    "wall_seconds_per_candidate": 300,
    "concurrency": 1,
    "finalization_replay_reserve": 1,
}
_FORBIDDEN = {
    "provider or network calls",
    "task, ticket, relay, authority, or worker-dispatch effects",
    "training or weight mutation",
    "candidate promotion or routing",
    "credential, secret, or Keychain access",
    "dashboard, hook, or upstream-core modification",
}
_EFFECTS = {
    "local_model_load": "AUTHORIZED",
    "local_file_read": "AUTHORIZED",
    "receipt_write": "AUTHORIZED",
    "provider_call": "FORBIDDEN",
    "network": "FORBIDDEN",
    "task_relay_authority_worker_dispatch": "FORBIDDEN",
    "training_weight_mutation": "FORBIDDEN",
    "candidate_promotion_or_routing": "FORBIDDEN",
    "credential_secret_keychain": "FORBIDDEN",
}


class TermRunError(ValueError):
    """Raised before or during a bounded TERM candidate run."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any] | list[Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, (dict, list)):
        raise TermRunError(f"{path} must contain an object or array")
    return value


def _require_mapping(value: object, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TermRunError(f"{label} must be an object")
    return value


def validate_run_manifest(value: object) -> Mapping[str, Any]:
    """Validate the existing sealed run without allowing a wider effect surface."""

    manifest = _require_mapping(value, "run manifest")
    expected_keys = {
        "schema", "run_id", "starting_head", "profile", "case_type", "model_advisory",
        "authority", "write_scope", "forbidden", "roster", "conditions", "decoding",
        "budgets", "status", "next_gate",
    }
    if set(manifest) != expected_keys:
        raise TermRunError("run manifest schema drift")
    if manifest["schema"] != RUN_SCHEMA or manifest["run_id"] != RUN_ID:
        raise TermRunError("unexpected TERM run identity")
    if manifest["case_type"] != "model_evaluation":
        raise TermRunError("TERM run case type drift")
    if manifest["authority"] != "USER_AUTHORIZED_OFFLINE_LOCAL_OUTPUT_COLLECTION_ONLY":
        raise TermRunError("TERM run authority is not the sealed local-only authority")
    if set(manifest["forbidden"]) != _FORBIDDEN:
        raise TermRunError("TERM run forbidden surface drift")
    if tuple(manifest["roster"]) != _ROSTER or tuple(manifest["conditions"]) != CONDITIONS:
        raise TermRunError("TERM roster or conditions drift")
    if manifest["decoding"] != _DECODING or manifest["budgets"] != _BUDGETS:
        raise TermRunError("TERM decoding or budget drift")
    if manifest["status"] != "PLAN_SEALED_NO_OUTPUTS_COLLECTED":
        raise TermRunError("TERM run is not ready for its first output receipt")
    return manifest


def validate_roster_bindings(value: object, fixture_sha256: str) -> Mapping[str, Mapping[str, Any]]:
    """Validate opaque, model-name-free scoring bindings before any load."""

    document = _require_mapping(value, "roster bindings")
    expected_keys = {"schema", "run_id", "fixture_projection_sha256", "bindings"}
    if set(document) != expected_keys or document["schema"] != BINDING_SCHEMA or document["run_id"] != RUN_ID:
        raise TermRunError("roster bindings schema or run identity drift")
    if document["fixture_projection_sha256"] != fixture_sha256:
        raise TermRunError("roster bindings fixture projection drift")
    bindings = document["bindings"]
    if not isinstance(bindings, list) or len(bindings) != len(_ROSTER):
        raise TermRunError("roster bindings must bind exactly six candidates")
    indexed: dict[str, Mapping[str, Any]] = {}
    for raw in bindings:
        binding = _require_mapping(raw, "candidate binding")
        expected_binding_keys = {"opaque_candidate_id", "artifact", "runtime", "static_load"}
        if set(binding) != expected_binding_keys:
            raise TermRunError("candidate binding schema drift")
        candidate_id = binding["opaque_candidate_id"]
        if candidate_id not in _ROSTER or candidate_id in indexed:
            raise TermRunError("candidate binding identity drift")
        artifact = _require_mapping(binding["artifact"], "artifact binding")
        if set(artifact) != {"local_provenance_path", "files"}:
            raise TermRunError("artifact binding schema drift")
        path_value = artifact["local_provenance_path"]
        files = artifact["files"]
        if not isinstance(path_value, str) or not path_value.startswith("/Volumes/"):
            raise TermRunError("artifact path is not a declared local volume path")
        if not isinstance(files, list) or not files:
            raise TermRunError("artifact binding needs a nonempty fingerprint")
        for item in files:
            file_item = _require_mapping(item, "artifact fingerprint entry")
            if set(file_item) != {"path", "sha256"}:
                raise TermRunError("artifact fingerprint entry schema drift")
            relative = file_item["path"]
            sha256 = file_item["sha256"]
            if not isinstance(relative, str) or Path(relative).is_absolute() or "/" in relative:
                raise TermRunError("artifact fingerprint path is unsafe")
            if not isinstance(sha256, str) or len(sha256) != 64:
                raise TermRunError("artifact fingerprint hash is invalid")
        runtime = _require_mapping(binding["runtime"], "runtime binding")
        if set(runtime) != {"tokenizer_config", "template_kwargs"}:
            raise TermRunError("runtime binding schema drift")
        tokenizer_config = runtime["tokenizer_config"]
        template_kwargs = runtime["template_kwargs"]
        if tokenizer_config not in ({}, {"fix_mistral_regex": True}):
            raise TermRunError("runtime tokenizer configuration drift")
        if template_kwargs not in ({}, {"enable_thinking": False}, {"reasoning_effort": "low"}):
            raise TermRunError("runtime template configuration drift")
        if binding["static_load"] != "PASS_LAZY_LOCAL_ONLY":
            raise TermRunError("candidate lacks the required static local-load receipt")
        indexed[candidate_id] = binding
    if tuple(indexed) != _ROSTER:
        raise TermRunError("candidate binding order drift")
    return indexed


def _verify_artifact(binding: Mapping[str, Any]) -> tuple[Path, list[dict[str, str]]]:
    artifact = _require_mapping(binding["artifact"], "artifact binding")
    root = Path(str(artifact["local_provenance_path"]))
    if not root.is_dir():
        raise TermRunError("bound local artifact is unavailable")
    verified: list[dict[str, str]] = []
    for item in artifact["files"]:
        entry = _require_mapping(item, "artifact fingerprint entry")
        path = root / str(entry["path"])
        if not path.is_file():
            raise TermRunError(f"bound artifact file is unavailable: {entry['path']}")
        actual = _sha256(path)
        if actual != entry["sha256"]:
            raise TermRunError(f"artifact fingerprint mismatch: {entry['path']}")
        verified.append({"path": str(entry["path"]), "sha256": actual})
    return root, verified


def _render_chat_prompt(tokenizer: Any, presentation: str, template_kwargs: Mapping[str, object]) -> str:
    return tokenizer.apply_chat_template(
        [{"role": "user", "content": presentation}],
        tokenize=False,
        add_generation_prompt=True,
        **dict(template_kwargs),
    )


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False) as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def _load_fixtures(path: Path) -> Mapping[str, Any]:
    fixtures = _require_mapping(_load_json(path), "fixture set")
    if tuple(fixtures.get("conditions", [])) != CONDITIONS or not isinstance(fixtures.get("fixtures"), list):
        raise TermRunError("TERM fixture conditions or fixtures drift")
    if len(fixtures["fixtures"]) != 8:
        raise TermRunError("TERM fixture count drift")
    return fixtures


def run_candidate(run_dir: Path, candidate_id: str) -> Mapping[str, Any]:
    """Run at most one bound opaque candidate and return its durable receipt."""

    run_dir = run_dir.resolve()
    manifest_path = run_dir / "RUN_MANIFEST.json"
    bindings_path = run_dir / "ROSTER_BINDINGS.json"
    receipt_path = run_dir / "candidate-receipts" / f"{candidate_id}.json"
    if candidate_id not in _ROSTER:
        raise TermRunError("candidate is outside the sealed roster")
    if receipt_path.exists():
        raise TermRunError("candidate receipt already exists; append-only preservation forbids overwrite")
    manifest = validate_run_manifest(_load_json(manifest_path))
    fixtures = _load_fixtures(_REPO_ROOT / "house/term_notation/compatibility_fixtures_v1.json")
    fixture_sha256 = canonical_fixture_projection_sha256(fixtures)
    bindings = validate_roster_bindings(_load_json(bindings_path), fixture_sha256)
    binding = bindings[candidate_id]
    model_path, verified_files = _verify_artifact(binding)

    # Runtime imports occur only after all static manifests and artifact hashes pass.
    import mlx.core as mx
    from mlx_lm import generate, load
    from mlx_lm.sample_utils import make_sampler

    runtime = _require_mapping(binding["runtime"], "runtime binding")
    mx.random.seed(_DECODING["seed"])
    model, tokenizer = load(str(model_path), lazy=True, tokenizer_config=dict(runtime["tokenizer_config"]))
    sampler = make_sampler(temp=_DECODING["temperature"])
    started = time.monotonic()
    deadline = started + _BUDGETS["wall_seconds_per_candidate"]
    cases: list[dict[str, Any]] = []
    halted_reason: str | None = None
    for fixture in fixtures["fixtures"]:
        for condition in CONDITIONS:
            if time.monotonic() >= deadline:
                halted_reason = "WALL_CAP_REACHED_BEFORE_NEXT_RENDER"
                break
            presentation = render_condition(condition, fixture)
            prompt = _render_chat_prompt(tokenizer, presentation, runtime["template_kwargs"])
            output = generate(model, tokenizer, prompt=prompt, verbose=False, sampler=sampler, max_tokens=_DECODING["max_tokens"])
            score = score_output(fixture, output)
            cases.append({
                "fixture_id": fixture["fixture_id"],
                "condition": condition,
                "presentation": presentation,
                "output": output,
                "score": score,
            })
        if halted_reason is not None:
            break
    elapsed = time.monotonic() - started
    complete = len(cases) == _BUDGETS["prompt_renders_per_candidate"]
    parse_count = sum(bool(case["score"]["parse_ok"]) for case in cases)
    exact_count = sum(bool(case["score"]["exact_fields"]) for case in cases)
    receipt: dict[str, Any] = {
        "schema": RECEIPT_SCHEMA,
        "state": "COMPLETED_INFERENCE_ONLY" if complete else "HALTED_INFERENCE_ONLY",
        "run": {"path": str(manifest_path), "sha256": _sha256(manifest_path)},
        "bindings": {"path": str(bindings_path), "sha256": _sha256(bindings_path)},
        "opaque_candidate_id": candidate_id,
        "artifact_fingerprint_verified": verified_files,
        "runtime": runtime,
        "decoding": _DECODING,
        "effects": _EFFECTS,
        "cases": cases,
        "metrics": {
            "render_count": len(cases),
            "parse_rate": parse_count / len(cases) if cases else 0.0,
            "exact_field_preservation_rate": exact_count / len(cases) if cases else 0.0,
            "wall_time_seconds": elapsed,
        },
        "halted_reason": halted_reason,
        "acceptance_ceiling": "SYNTAX_AND_FIELD_PRESERVATION_ONLY_NO_ROLE_OR_DIALECT_DECISION",
        "disposition": "LOCAL_OUTPUT_EVIDENCE_ONLY_NOT_A_WORKER_QUALIFICATION_OR_ROUTING_DECISION",
    }
    _atomic_json(receipt_path, receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--candidate", required=True, choices=_ROSTER)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    try:
        run_dir.relative_to(_REPO_ROOT)
    except ValueError as error:
        raise SystemExit("run directory must remain within this repository") from error
    receipt = run_candidate(run_dir, args.candidate)
    print(json.dumps({"receipt": str(run_dir / "candidate-receipts" / f"{args.candidate}.json"), "metrics": receipt["metrics"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
