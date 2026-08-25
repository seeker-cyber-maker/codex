from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from house.workflow.run_local_rubric_smoke import SmokeRunError, _validate_execution_manifest


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


if __name__ == "__main__":
    unittest.main()
