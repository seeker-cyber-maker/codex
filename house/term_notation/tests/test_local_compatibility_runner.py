from __future__ import annotations

import json
import unittest
from pathlib import Path

from house.term_notation.local_compatibility_runner import CONDITIONS, expected_record, render_condition, score_output


class LocalCompatibilityRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        path = Path(__file__).parents[1] / "compatibility_fixtures_v1.json"
        self.fixture = json.loads(path.read_text(encoding="utf-8"))["fixtures"][0]

    def test_all_conditions_request_one_canonical_term_record(self) -> None:
        expected = expected_record(self.fixture)
        for condition in CONDITIONS:
            rendered = render_condition(condition, self.fixture)
            self.assertIn("TERM_NOTATION/1", rendered)
            self.assertIn(self.fixture["candidate"], rendered)
            if condition == "TERM_FULL_FORM":
                self.assertIn(expected, rendered)

    def test_exact_canonical_output_passes(self) -> None:
        result = score_output(self.fixture, expected_record(self.fixture))
        self.assertEqual(result["parse_ok"], True)
        self.assertEqual(result["exact_fields"], True)

    def test_malformed_and_field_drift_outputs_fail_closed(self) -> None:
        malformed = score_output(self.fixture, "not a TERM record")
        self.assertEqual(malformed["parse_ok"], False)
        altered = expected_record(self.fixture).replace("task-42/result-7", "other-scope")
        drift = score_output(self.fixture, altered)
        self.assertEqual(drift["parse_ok"], True)
        self.assertEqual(drift["exact_fields"], False)
