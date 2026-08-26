from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from house.local_model_evaluation import (
    LocalEvaluationContractError,
    parse_adapter_score,
    render_rubric_prompt,
    require_execution_authority,
    validate_source_only_contract,
)


class LocalEvaluationContractTests(unittest.TestCase):
    def _inputs(self) -> tuple[dict[str, object], dict[str, object], list[object]]:
        root = Path(__file__).parents[1]
        return (
            json.loads((root / "rubric_manifest_v1.json").read_text(encoding="utf-8")),
            json.loads((root / "rubric_fixtures_v1.json").read_text(encoding="utf-8")),
            json.loads((root / "adapter_declarations_v1.json").read_text(encoding="utf-8")),
        )

    def test_contract_is_valid_but_execution_is_blocked(self) -> None:
        manifest, fixtures, adapters = self._inputs()
        report = validate_source_only_contract(manifest, fixtures, adapters)
        self.assertEqual(report.fixture_count, 4)
        self.assertTrue(report.execution_blocked)
        self.assertEqual(
            report.adapter_ids,
            (
                "instructor-bracket-result-v1",
                "chat-json-score-v1",
                "chat-json-score-no-thinking-v1",
            ),
        )
        with self.assertRaisesRegex(LocalEvaluationContractError, "no execution"):
            require_execution_authority(manifest, fixtures, adapters)

    def test_rejects_effect_or_fixture_mutation(self) -> None:
        manifest, fixtures, adapters = self._inputs()
        bad_effect = copy.deepcopy(manifest)
        bad_effect["effects"]["model_load"] = "ATTEMPTED"
        with self.assertRaisesRegex(LocalEvaluationContractError, "not attempted"):
            validate_source_only_contract(bad_effect, fixtures, adapters)
        bad_fixture = copy.deepcopy(fixtures)
        del bad_fixture["fixtures"][0]["criteria"]
        with self.assertRaisesRegex(LocalEvaluationContractError, "schema drift"):
            validate_source_only_contract(manifest, bad_fixture, adapters)

    def test_rejects_model_identity_and_unknown_adapter_surface(self) -> None:
        manifest, fixtures, adapters = self._inputs()
        named_adapter = copy.deepcopy(adapters)
        named_adapter[0]["model_name"] = "must-not-be-a-scoring-feature"
        with self.assertRaisesRegex(LocalEvaluationContractError, "schema drift"):
            validate_source_only_contract(manifest, fixtures, named_adapter)
        bad_parser = copy.deepcopy(adapters)
        bad_parser[1]["output_parser"] = "freeform-prose-v1"
        with self.assertRaisesRegex(LocalEvaluationContractError, "not declared"):
            validate_source_only_contract(manifest, fixtures, bad_parser)

    def test_renders_shared_prompt_without_adapter_identity(self) -> None:
        _manifest, fixtures, _adapters = self._inputs()
        rendered = render_rubric_prompt(fixtures["fixtures"][0])
        self.assertIn("Compute 12 - 3 * 2", rendered)
        self.assertIn("Score 5:", rendered)
        self.assertNotIn("adapter_id", rendered)
        self.assertNotIn("model", rendered.lower())

    def test_closed_adapter_parsers(self) -> None:
        _manifest, _fixtures, adapters = self._inputs()
        bracket, json_adapter, no_thinking_adapter = adapters
        self.assertEqual(parse_adapter_score(bracket, "Feedback. [RESULT] 4"), 4)
        self.assertEqual(parse_adapter_score(json_adapter, '{"score": 5}'), 5)
        with self.assertRaisesRegex(LocalEvaluationContractError, "exactly"):
            parse_adapter_score(json_adapter, '{"score": 5, "notes": "extra"}')
        with self.assertRaisesRegex(LocalEvaluationContractError, "absent"):
            parse_adapter_score(bracket, "score 4")

    def test_renderer_declares_the_selected_adapter_output_shape(self) -> None:
        _manifest, fixtures, adapters = self._inputs()
        bracket, json_adapter, no_thinking_adapter = adapters
        json_prompt = render_rubric_prompt(fixtures["fixtures"][0], json_adapter)
        self.assertIn('exactly {"score": integer}', json_prompt)
        self.assertNotIn("feedback", json_prompt.lower())
        bracket_prompt = render_rubric_prompt(fixtures["fixtures"][0], bracket)
        self.assertIn("[RESULT] (integer)", bracket_prompt)
        no_thinking_prompt = render_rubric_prompt(fixtures["fixtures"][0], no_thinking_adapter)
        self.assertIn('exactly {"score": integer}', no_thinking_prompt)


if __name__ == "__main__":
    unittest.main()
