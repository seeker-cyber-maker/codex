from __future__ import annotations

import contextlib
import io
import json
import unittest

from house.auto_switcher import DEFAULT_ROUTES, route_task
from house.auto_switcher.cli import main


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

    def test_omp_native_auto_thinking_is_distinct_from_role_selection(self) -> None:
        receipt = route_task({"summary": "design the architecture"})
        self.assertEqual(receipt["profile"]["model_class"], "plan")
        self.assertEqual(receipt["omp_compat"], {
            "mode": "ADVISORY_NO_DISPATCH",
            "native_thinking_level": "auto",
            "effort_advisory": "high",
            "requested_model_role": "plan",
            "effective_model_role": "plan",
            "prewalk": "DISABLED",
            "retry_fallback": "ENABLED_NO_CHAIN",
            "context_promotion": "DISABLED",
        })

    def test_qualified_omp_prewalk_hands_off_only_after_the_first_write(self) -> None:
        pending = route_task({
            "summary": "design the architecture",
            "omp_prewalk_enabled": True,
            "plan_sealed": True,
        })
        completed = route_task({
            "summary": "design the architecture",
            "omp_prewalk_enabled": True,
            "plan_sealed": True,
            "first_write_completed": True,
        })
        self.assertEqual(pending["omp_compat"]["effective_model_role"], "plan")
        self.assertEqual(pending["omp_compat"]["prewalk"], "ARMED_WAITING_FOR_FIRST_WRITE")
        self.assertEqual(completed["omp_compat"]["effective_model_role"], "smol")
        self.assertEqual(completed["omp_compat"]["prewalk"], "HANDOFF_TO_SMOL_AFTER_FIRST_WRITE")

    def test_cli_emits_a_hash_bound_no_dispatch_receipt(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = main(["--task-json", '{"summary":"design the architecture"}'])
        receipt = json.loads(output.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(receipt["dispatch"], "NOT_ATTEMPTED")
        self.assertEqual(receipt["omp_compat"]["native_thinking_level"], "auto")
        self.assertIn("decision_sha256", receipt)

    def test_recurring_work_modes_are_conservative_and_deterministic(self) -> None:
        cases = (
            ("recover lost chats from the forensic records", "incident_recovery", "plan", "high"),
            ("reproduce result through the exact oracle", "verifier_benchmark", "plan", "high"),
            ("inspect an untrusted file without executing it", "artifact_intake", "task", "medium"),
            ("migrate files and deduplicate files in the junkyard", "storage_lifecycle", "task", "medium"),
            ("debug the provider bridge OAuth route", "provider_bridge_debug", "plan", "high"),
            ("run a health check and report quota status", "service_operations", "smol", "low"),
            ("perform claim review for contradictory evidence", "evidence_review", "plan", "high"),
            ("perform model qualification for the local worker", "model_evaluation", "task", "medium"),
            ("ingest archive into the knowledge dispensary", "knowledge_integration", "plan", "high"),
            ("test prompt injection and sandbox escape containment", "security_containment", "plan", "xhigh"),
        )
        for summary, case_type, model_class, effort in cases:
            with self.subTest(case_type=case_type):
                receipt = route_task({"summary": summary})
                self.assertEqual(receipt["request"]["case_type"], case_type)
                self.assertEqual(receipt["profile"]["model_class"], model_class)
                self.assertEqual(receipt["profile"]["reasoning_effort"], effort)
