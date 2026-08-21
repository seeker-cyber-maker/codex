from __future__ import annotations

import unittest

from house.auto_switcher import DEFAULT_ROUTES, route_task


class AutoSwitcherTests(unittest.TestCase):
    def test_explicit_role_and_deterministic_selection(self) -> None:
        receipt = route_task({"role": "coding", "capabilities": ["code"], "context_tokens": 2000})
        self.assertEqual(receipt["state"], "SELECTED")
        self.assertEqual(receipt["selected"]["id"], "chatgpt-codex-direct")
        self.assertEqual(receipt["profile"], {"model_class": "task", "reasoning_effort": "medium", "omp_policy": "balanced"})
        self.assertEqual(receipt["role_evidence"], "explicit:role")
        self.assertEqual(receipt["dispatch"], "NOT_ATTEMPTED")

    def test_keyword_role_never_selects_disabled_chatgpt_bridge(self) -> None:
        receipt = route_task({"summary": "Please review this patch", "capabilities": ["reasoning"]})
        self.assertEqual(receipt["request"]["role"], "review")
        self.assertIn("disabled", receipt["rejected"]["chatgpt-work-packet"])
        self.assertEqual(receipt["selected"]["id"], "chatgpt-codex-direct")

    def test_local_only_fails_closed_to_chatgpt_default_when_no_local_route_exists(self) -> None:
        receipt = route_task({"summary": "summarize logs", "privacy": "local-only"})
        self.assertEqual(receipt["state"], "FALLBACK")
        self.assertEqual(receipt["selected"]["id"], "chatgpt-codex-direct")
        self.assertIn("privacy", receipt["rejected"]["chatgpt-codex-direct"])

    def test_catalog_can_admit_chatgpt_packet_lane_after_bridge_qualification(self) -> None:
        routes = tuple({**route, "enabled": True, "healthy": True} if route["id"] == "chatgpt-work-packet" else route for route in DEFAULT_ROUTES)
        receipt = route_task({"summary": "summarize this log", "delivery": "chat-packet"}, routes)
        self.assertEqual(receipt["selected"]["id"], "chatgpt-work-packet")
        self.assertEqual(receipt["state"], "SELECTED")

    def test_same_input_has_same_hash(self) -> None:
        task = {"summary": "implement a test", "capabilities": ["code"]}
        self.assertEqual(route_task(task)["decision_sha256"], route_task(task)["decision_sha256"])

    def test_omp_quality_first_crosswalk_escalates_review_and_critical_work(self) -> None:
        review = route_task({"role": "review", "capabilities": ["code", "reasoning"]})
        critical = route_task({"role": "summary", "risk": "critical"})
        self.assertEqual(review["profile"], {"model_class": "plan", "reasoning_effort": "high", "omp_policy": "quality_first"})
        self.assertEqual(critical["profile"], {"model_class": "plan", "reasoning_effort": "xhigh", "omp_policy": "quality_first"})

    def test_pinned_case_type_overrides_keyword_role(self) -> None:
        receipt = route_task({"summary": "summarize a kernel fault", "case_type": "systems_critical"})
        self.assertEqual(receipt["profile"], {"model_class": "plan", "reasoning_effort": "xhigh", "omp_policy": "quality_first"})

    def test_compound_prompt_continues_with_decomposition(self) -> None:
        receipt = route_task({"summary": "do we need research for new features to review in the commercial app for training"})
        self.assertEqual(receipt["request"]["case_type"], "compound")
        self.assertEqual(receipt["detected_case_types"], ["research_synthesis", "app_delivery", "training_governance"])
        self.assertEqual(receipt["profile"], {"model_class": "plan", "reasoning_effort": "high", "omp_policy": "quality_first"})
        self.assertEqual(receipt["next_action"], "DECOMPOSE_WITHOUT_BLOCKING")
