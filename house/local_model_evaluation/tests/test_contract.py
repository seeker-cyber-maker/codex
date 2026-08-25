from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from house.local_model_evaluation import (
    LocalEvaluationContractError,
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
            ("instructor-bracket-result-v1", "chat-json-score-v1"),
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


if __name__ == "__main__":
    unittest.main()
