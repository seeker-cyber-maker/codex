from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from house.workflow.run_local_rubric_smoke import SmokeRunError, _render_prompt, _validate_execution_manifest


class RunLocalRubricSmokeTests(unittest.TestCase):
    def _manifest(self) -> dict[str, object]:
        path = (
            Path(__file__).parents[2]
            / "workflow/runs/20260825T225000Z-local-rubric-candidate-b-onecase/EXECUTION_MANIFEST_V2.json"
        )
        return json.loads(path.read_text(encoding="utf-8"))

    def test_accepts_the_sealed_inference_only_manifest(self) -> None:
        manifest = self._manifest()
        self.assertEqual(_validate_execution_manifest(manifest)["state"], "INFERENCE_ONLY_AUTHORIZED")

    def test_rejects_promoting_or_expanding_the_effect_surface(self) -> None:
        manifest = copy.deepcopy(self._manifest())
        manifest["effects"]["candidate_promotion"] = "AUTHORIZED"
        with self.assertRaisesRegex(SmokeRunError, "closed inference-only"):
            _validate_execution_manifest(manifest)

    def test_rejects_decoding_drift(self) -> None:
        manifest = copy.deepcopy(self._manifest())
        manifest["decoding"]["max_tokens"] = 64
        with self.assertRaisesRegex(SmokeRunError, "decoding configuration drift"):
            _validate_execution_manifest(manifest)

    def test_allows_only_the_two_declared_tokenizer_configurations(self) -> None:
        manifest = copy.deepcopy(self._manifest())
        manifest["runtime"]["tokenizer_config"] = {}
        self.assertEqual(_validate_execution_manifest(manifest)["runtime"]["tokenizer_config"], {})
        manifest["runtime"]["tokenizer_config"] = {"unknown": True}
        with self.assertRaisesRegex(SmokeRunError, "runtime tokenizer configuration drift"):
            _validate_execution_manifest(manifest)

    def test_no_thinking_renderer_passes_only_the_declared_template_control(self) -> None:
        class RecordingTokenizer:
            def apply_chat_template(self, messages, **kwargs):
                self.messages = messages
                self.kwargs = kwargs
                return "rendered"

        adapter = self._adapter("chat-json-score-no-thinking-v1")
        fixture = self._fixture()
        tokenizer = RecordingTokenizer()
        self.assertEqual(_render_prompt(adapter, fixture, tokenizer), "rendered")
        self.assertEqual(tokenizer.kwargs, {"tokenize": False, "add_generation_prompt": True, "enable_thinking": False})

    def _fixture(self) -> dict[str, object]:
        path = Path(__file__).parents[2] / "local_model_evaluation/rubric_fixtures_v1.json"
        return json.loads(path.read_text(encoding="utf-8"))["fixtures"][0]

    def _adapter(self, adapter_id: str) -> dict[str, object]:
        path = Path(__file__).parents[2] / "local_model_evaluation/adapter_declarations_v1.json"
        adapters = json.loads(path.read_text(encoding="utf-8"))
        return next(adapter for adapter in adapters if adapter["adapter_id"] == adapter_id)


if __name__ == "__main__":
    unittest.main()
