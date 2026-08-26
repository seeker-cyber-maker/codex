from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from house.term_notation.compatibility import canonical_fixture_projection_sha256
from house.workflow.run_term_local_compatibility import (
    CONDITIONS,
    TermRunError,
    _render_chat_prompt,
    validate_roster_bindings,
    validate_run_manifest,
)


class TermLocalCompatibilityRunnerTests(unittest.TestCase):
    def _run_dir(self) -> Path:
        return Path(__file__).parents[1] / "runs/20260826T001404Z-term-notation-local-compatibility"

    def _manifest(self) -> dict[str, object]:
        return json.loads((self._run_dir() / "RUN_MANIFEST.json").read_text(encoding="utf-8"))

    def _fixtures(self) -> dict[str, object]:
        path = Path(__file__).parents[2] / "term_notation/compatibility_fixtures_v1.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def _bindings(self) -> dict[str, object]:
        return {
            "schema": "dream-house/term-notation-local-roster-bindings/1",
            "run_id": "20260826T001404Z-term-notation-local-compatibility",
            "fixture_projection_sha256": canonical_fixture_projection_sha256(self._fixtures()),
            "bindings": [
                {
                    "opaque_candidate_id": f"local-term-candidate-{number:02d}",
                    "artifact": {
                        "local_provenance_path": f"/Volumes/Test/model-{number}",
                        "files": [{"path": "config.json", "sha256": "0" * 64}],
                    },
                    "runtime": {
                        "tokenizer_config": {"fix_mistral_regex": True} if number == 2 else {},
                        "template_kwargs": {"enable_thinking": False} if number in {3, 5, 6} else ({"reasoning_effort": "low"} if number == 4 else {}),
                    },
                    "static_load": "PASS_LAZY_LOCAL_ONLY",
                }
                for number in range(1, 7)
            ],
        }

    def test_accepts_the_sealed_local_only_manifest(self) -> None:
        self.assertEqual(validate_run_manifest(self._manifest())["status"], "PLAN_SEALED_NO_OUTPUTS_COLLECTED")

    def test_rejects_broadened_effect_authority(self) -> None:
        manifest = copy.deepcopy(self._manifest())
        manifest["authority"] = "WORKER_EXECUTION_AUTHORIZED"
        with self.assertRaisesRegex(TermRunError, "local-only authority"):
            validate_run_manifest(manifest)

    def test_rejects_decoding_or_roster_drift(self) -> None:
        manifest = copy.deepcopy(self._manifest())
        manifest["decoding"]["max_tokens"] = 97
        with self.assertRaisesRegex(TermRunError, "decoding or budget drift"):
            validate_run_manifest(manifest)
        manifest = copy.deepcopy(self._manifest())
        manifest["roster"] = list(reversed(manifest["roster"]))
        with self.assertRaisesRegex(TermRunError, "roster or conditions drift"):
            validate_run_manifest(manifest)

    def test_binds_six_opaque_candidates_without_scoring_names(self) -> None:
        indexed = validate_roster_bindings(self._bindings(), canonical_fixture_projection_sha256(self._fixtures()))
        self.assertEqual(tuple(indexed), tuple(f"local-term-candidate-{number:02d}" for number in range(1, 7)))

    def test_rejects_binding_fingerprint_or_template_expansion(self) -> None:
        bindings = self._bindings()
        bindings["bindings"][0]["artifact"]["files"][0]["sha256"] = "short"
        with self.assertRaisesRegex(TermRunError, "fingerprint hash"):
            validate_roster_bindings(bindings, canonical_fixture_projection_sha256(self._fixtures()))
        bindings = self._bindings()
        bindings["bindings"][0]["runtime"]["template_kwargs"] = {"arbitrary": "prompt control"}
        with self.assertRaisesRegex(TermRunError, "template configuration drift"):
            validate_roster_bindings(bindings, canonical_fixture_projection_sha256(self._fixtures()))
        bindings = self._bindings()
        bindings["bindings"][0]["static_load"] = "NOT_ATTEMPTED"
        with self.assertRaisesRegex(TermRunError, "static local-load receipt"):
            validate_roster_bindings(bindings, canonical_fixture_projection_sha256(self._fixtures()))

    def test_template_renderer_passes_only_prebound_controls(self) -> None:
        class RecordingTokenizer:
            def apply_chat_template(self, messages, **kwargs):
                self.messages = messages
                self.kwargs = kwargs
                return "rendered"

        tokenizer = RecordingTokenizer()
        self.assertEqual(_render_chat_prompt(tokenizer, "TERM? test", {"enable_thinking": False}), "rendered")
        self.assertEqual(tokenizer.kwargs, {"tokenize": False, "add_generation_prompt": True, "enable_thinking": False})
        self.assertEqual(CONDITIONS[-1], "OVERCOMPRESSED_CONTROL")


if __name__ == "__main__":
    unittest.main()
