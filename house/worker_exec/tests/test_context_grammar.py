from __future__ import annotations

import builtins
import copy
import os
import socket
import subprocess
import time
import unittest
from unittest.mock import patch

from house.worker_exec import (
    ContextGrammarError,
    compile_context_grammar_v1,
    mock_firewall_failure_is_sterile,
    prepare_mock_launch_binding_v1,
    project_mock_context_v1,
    verify_context_grammar_v1,
)
from house.worker_exec.context_grammar import (
    CONFIG_PRECEDENCE,
    canonical_sha256,
    seal_record,
    verify_safe_projection_v1,
)
from house.worker_exec.context_grammar import (
    ContextGrammarError as ModuleContextGrammarError,
)


class ContextGrammarTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ruleset = seal_record(
            {
                "schema": "codex-house-context-ruleset/1",
                "ruleset_id": "synthetic-ruleset-v1",
                "source_revision": "a" * 64,
                "platform_profile": "synthetic-posix-v1",
                "config_precedence": list(CONFIG_PRECEDENCE),
                "required_contributor_classes": ["config", "instructions", "mcp"],
                "allowed_projection_classes": [
                    "BEHAVIOR_VALUE",
                    "PUBLIC_LOCATOR",
                    "SECRET_REFERENCE",
                    "SENSITIVE_PRESENCE_ONLY",
                    "PUBLIC_CONTENT_ADDRESSABLE",
                ],
            }
        )
        self.fixtures = [
            {
                "contributor_id": "config-1",
                "contributor_class": "config",
                "classification": "BEHAVIOR_VALUE",
                "locator_id": "synthetic:project-root-markers",
                "raw_value": [".git"],
                "content_sha256": None,
                "vault_ref": None,
            },
            {
                "contributor_id": "instructions-1",
                "contributor_class": "instructions",
                "classification": "PUBLIC_CONTENT_ADDRESSABLE",
                "locator_id": "synthetic:agents",
                "raw_value": None,
                "content_sha256": "b" * 64,
                "vault_ref": None,
            },
            {
                "contributor_id": "mcp-1",
                "contributor_class": "mcp",
                "classification": "SECRET_REFERENCE",
                "locator_id": "synthetic:mcp",
                "raw_value": None,
                "content_sha256": None,
                "vault_ref": {
                    "ref_id": "vr_0123456789abcdef",
                    "scope_class": "environment",
                    "required_sink": "provider_header",
                    "revision": 1,
                },
            },
        ]

    def _project(self) -> dict[str, object]:
        return project_mock_context_v1(
            self.ruleset,
            projection_id="projection-1",
            operation_id="operation-1",
            stage="D",
            fixtures=self.fixtures,
            parent_stage_sha256="c" * 64,
        )

    def test_happy_path_compiles_and_verifies_without_runtime_authority(self) -> None:
        projection = self._project()
        grammar = compile_context_grammar_v1(self.ruleset, projection)
        receipt = verify_context_grammar_v1(self.ruleset, projection, grammar)
        self.assertEqual(grammar["state"], "GRAMMAR_DERIVED_NOT_OBSERVED")
        self.assertEqual(grammar["authority"], "NOT_GRANTED")
        self.assertEqual(grammar["execution"], "NOT_QUALIFIED")
        self.assertEqual(receipt["state"], "CONTEXT_GRAMMAR_VERIFIED_NOT_QUALIFIED")
        self.assertEqual(receipt["authenticity"], "UNAUTHENTICATED_BY_PURE_VERIFIER")

    def test_01_low_entropy_secret_is_rejected_without_value_or_hash(self) -> None:
        rejected = "synthetic-low-entropy-secret"
        fixtures = copy.deepcopy(self.fixtures)
        fixtures[0]["raw_value"] = rejected
        projection = project_mock_context_v1(
            self.ruleset,
            projection_id="projection-2",
            operation_id="operation-1",
            stage="B",
            fixtures=fixtures,
        )
        self.assertEqual(projection["state"], "INCOMPLETE_SECRET_DEPENDENCY")
        self.assertTrue(mock_firewall_failure_is_sterile(projection, rejected))
        self.assertNotIn(canonical_sha256(rejected), str(projection))
        with self.assertRaisesRegex(ContextGrammarError, "incomplete projection"):
            compile_context_grammar_v1(self.ruleset, projection)

    def test_02_unknown_class_and_unadmitted_content_fail_closed(self) -> None:
        unknown = copy.deepcopy(self.fixtures)
        unknown[1]["classification"] = "UNCLASSIFIED"
        unknown_projection = project_mock_context_v1(
            self.ruleset,
            projection_id="projection-3",
            operation_id="operation-1",
            stage="D",
            fixtures=unknown,
        )
        self.assertEqual(unknown_projection["state"], "INCOMPLETE_UNKNOWN_KEY")

        private = copy.deepcopy(self.fixtures)
        private[1]["content_sha256"] = None
        private_projection = project_mock_context_v1(
            self.ruleset,
            projection_id="projection-4",
            operation_id="operation-1",
            stage="D",
            fixtures=private,
        )
        self.assertEqual(private_projection["state"], "INCOMPLETE_PRIVATE_TEXT")

    def test_02b_behavior_list_secret_is_rejected_before_projection(self) -> None:
        rejected = ["plain", "synthetic-secret-token"]
        fixtures = copy.deepcopy(self.fixtures)
        fixtures[0]["raw_value"] = rejected
        projection = project_mock_context_v1(
            self.ruleset,
            projection_id="projection-2b",
            operation_id="operation-1",
            stage="B",
            fixtures=fixtures,
        )
        self.assertEqual(projection["state"], "INCOMPLETE_SECRET_DEPENDENCY")
        self.assertTrue(mock_firewall_failure_is_sterile(projection, rejected[1]))

    def test_03_grammar_binding_and_authority_overclaims_are_rejected(self) -> None:
        projection = self._project()
        grammar = compile_context_grammar_v1(self.ruleset, projection)
        changed = copy.deepcopy(grammar)
        changed["authority"] = "GRANTED"
        changed["record_sha256"] = canonical_sha256(
            {key: value for key, value in changed.items() if key != "record_sha256"}
        )
        with self.assertRaisesRegex(ContextGrammarError, "execution authority"):
            verify_context_grammar_v1(self.ruleset, projection, changed)

        changed = copy.deepcopy(grammar)
        changed["projection_sha256"] = "d" * 64
        changed["record_sha256"] = canonical_sha256(
            {key: value for key, value in changed.items() if key != "record_sha256"}
        )
        with self.assertRaisesRegex(ContextGrammarError, "projection binding mismatch"):
            verify_context_grammar_v1(self.ruleset, projection, changed)

    def test_04_pure_verifier_uses_no_ambient_api(self) -> None:
        projection = self._project()
        grammar = compile_context_grammar_v1(self.ruleset, projection)

        def forbidden(*_args: object, **_kwargs: object) -> None:
            raise AssertionError("ambient API used by pure verifier")

        with (
            patch.object(builtins, "open", forbidden),
            patch.object(os, "getenv", forbidden),
            patch.object(socket, "socket", forbidden),
            patch.object(subprocess, "run", forbidden),
            patch.object(time, "time", forbidden),
        ):
            receipt = verify_context_grammar_v1(self.ruleset, projection, grammar)
        self.assertEqual(receipt["authority"], "NOT_GRANTED")

    def test_05_launch_binding_models_toctou_without_launching(self) -> None:
        grammar = compile_context_grammar_v1(self.ruleset, self._project())
        refused = prepare_mock_launch_binding_v1(
            grammar,
            binding_kind="PATH_REOPEN",
            admitted_content_sha256="e" * 64,
            observed_content_sha256="f" * 64,
        )
        immutable = prepare_mock_launch_binding_v1(
            grammar,
            binding_kind="IMMUTABLE_OBJECT",
            admitted_content_sha256="e" * 64,
            observed_content_sha256="e" * 64,
        )
        self.assertEqual(refused["state"], "MOCK_LAUNCH_BINDING_REFUSED")
        self.assertEqual(immutable["execution"], "NOT_ATTEMPTED")

    def test_06_projection_schema_rejects_duplicate_contributor_ids(self) -> None:
        projection = self._project()
        changed = copy.deepcopy(projection)
        changed["contributors"][1]["contributor_id"] = "config-1"
        changed["record_sha256"] = canonical_sha256(
            {key: value for key, value in changed.items() if key != "record_sha256"}
        )
        with self.assertRaisesRegex(ModuleContextGrammarError, "duplicate contributor"):
            verify_safe_projection_v1(changed)
