from __future__ import annotations

import unittest

from house.operator_surface import (
    Command,
    CommandRegistry,
    Parameter,
    RegistryError,
    TargetRequirement,
    builtin_registry,
)


class CommandRegistryTests(unittest.TestCase):
    def test_manifest_is_deterministic_and_no_dispatch(self) -> None:
        first = builtin_registry().manifest()
        second = builtin_registry().manifest()
        self.assertEqual(first, second)
        self.assertEqual(first["dispatch"], "NOT_IMPLEMENTED")
        self.assertEqual(first["authority"], "NOT_GRANTED")
        self.assertEqual(len(first["manifest_sha256"]), 64)

    def test_same_registry_drives_agent_dashboard_and_iterm_surfaces(self) -> None:
        registry = builtin_registry()
        agent = {
            item["command_id"]
            for item in registry.manifest(surface="agent")["commands"]
        }
        dashboard = {
            item["command_id"]
            for item in registry.manifest(surface="dashboard")["commands"]
        }
        iterm = {
            item["command_id"]
            for item in registry.manifest(surface="iterm")["commands"]
        }
        self.assertEqual(agent, dashboard)
        self.assertEqual(
            iterm,
            {"codex.house.companion.preview", "codex.house.relay.preview"},
        )

    def test_search_uses_inventory_without_mutating_it(self) -> None:
        registry = builtin_registry()
        matches = registry.search("terminal preview")
        self.assertEqual(
            [item["command_id"] for item in matches],
            ["codex.house.companion.preview", "codex.house.relay.preview"],
        )
        self.assertEqual(registry.manifest(), builtin_registry().manifest())

    def test_explicit_target_prevents_ambient_focus_race(self) -> None:
        registry = builtin_registry()
        with self.assertRaisesRegex(RegistryError, "requires kind and id"):
            registry.prepare_request("codex.house.task.inspect")
        receipt = registry.prepare_request(
            "codex.house.task.inspect",
            target={"kind": "task", "id": "task-123"},
        )
        self.assertEqual(receipt["target"], {"kind": "task", "id": "task-123"})
        self.assertEqual(receipt["state"], "PREPARED_UNAUTHORIZED")
        self.assertEqual(receipt["dispatch"], "NOT_ATTEMPTED")

    def test_targetless_command_rejects_target(self) -> None:
        with self.assertRaisesRegex(RegistryError, "does not accept a target"):
            builtin_registry().prepare_request(
                "codex.house.routes.list",
                target={"kind": "task", "id": "task-123"},
            )

    def test_argument_defaults_and_choices_are_validated(self) -> None:
        registry = builtin_registry()
        receipt = registry.prepare_request(
            "codex.house.task.submit",
            arguments={
                "title": "Review registry",
                "summary": "Review the operator registry",
            },
        )
        self.assertEqual(receipt["arguments"]["recipient"], "triage")
        with self.assertRaisesRegex(RegistryError, "invalid choice"):
            registry.prepare_request(
                "codex.house.task.submit",
                arguments={
                    "title": "x",
                    "summary": "x",
                    "recipient": "unrestricted",
                },
            )

    def test_missing_and_unknown_arguments_fail_closed(self) -> None:
        registry = builtin_registry()
        with self.assertRaisesRegex(RegistryError, "missing required"):
            registry.prepare_request("codex.house.task.submit")
        with self.assertRaisesRegex(RegistryError, "unknown arguments"):
            registry.prepare_request(
                "codex.house.task.submit",
                arguments={"title": "x", "summary": "x", "shell": "rm"},
            )

    def test_reserved_core_namespace_rejects_plugins(self) -> None:
        registry = CommandRegistry()
        command = Command(
            command_id="codex.house.plugin.escape",
            title="Bad plugin",
            description="Attempts to enter the core namespace.",
            category="test",
            authority="NONE",
        )
        with self.assertRaisesRegex(RegistryError, "reserved core namespace"):
            registry.register(command, owner="plugin.example")

    def test_public_registration_cannot_spoof_core_owner(self) -> None:
        registry = CommandRegistry()
        command = Command(
            command_id="codex.house.plugin.spoof",
            title="Spoof core",
            description="Attempts to claim the compiled core owner.",
            category="test",
            authority="NONE",
        )
        with self.assertRaisesRegex(RegistryError, "not a public plugin operation"):
            registry.register(command, owner="core")

    def test_plugin_namespace_is_allowed_but_collision_fails(self) -> None:
        registry = CommandRegistry()
        command = Command(
            command_id="plugin.example.inspect",
            title="Inspect example",
            description="Read an example fixture.",
            category="test",
            authority="READ_ONLY",
        )
        registry.register(command, owner="plugin.example")
        with self.assertRaisesRegex(RegistryError, "collision"):
            registry.register(command, owner="plugin.example")

    def test_plugin_cannot_register_in_another_plugin_namespace(self) -> None:
        registry = CommandRegistry()
        command = Command(
            command_id="plugin.victim.inspect",
            title="Inspect victim",
            description="Attempts to claim another plugin namespace.",
            category="test",
            authority="READ_ONLY",
        )
        with self.assertRaisesRegex(RegistryError, "outside owner namespace"):
            registry.register(command, owner="plugin.attacker")

    def test_duplicate_hotkey_fails_atomically(self) -> None:
        registry = CommandRegistry()
        first = Command(
            command_id="plugin.example.first",
            title="First",
            description="First command.",
            category="test",
            authority="READ_ONLY",
            hotkey="cmd+x",
        )
        second = Command(
            command_id="plugin.example.second",
            title="Second",
            description="Second command.",
            category="test",
            authority="READ_ONLY",
            hotkey="cmd+x",
        )
        with self.assertRaisesRegex(RegistryError, "hotkey collision"):
            registry.register_many((first, second), owner="plugin.example")
        self.assertEqual(registry.manifest()["commands"], [])

    def test_batch_registration_is_atomic_on_collision(self) -> None:
        registry = CommandRegistry()
        valid = Command(
            command_id="plugin.example.first",
            title="First",
            description="First command.",
            category="test",
            authority="READ_ONLY",
        )
        forbidden = Command(
            command_id="codex.house.plugin.second",
            title="Second",
            description="Second command.",
            category="test",
            authority="READ_ONLY",
        )
        with self.assertRaises(RegistryError):
            registry.register_many((valid, forbidden), owner="plugin.example")
        self.assertEqual(registry.manifest()["commands"], [])

    def test_declaration_rejects_inconsistent_target_and_parameters(self) -> None:
        with self.assertRaisesRegex(RegistryError, "explicit target has no kinds"):
            Command(
                command_id="plugin.example.target",
                title="Target",
                description="Missing target kinds.",
                category="test",
                authority="READ_ONLY",
                target_requirement=TargetRequirement.EXPLICIT,
            )
        with self.assertRaisesRegex(RegistryError, "duplicate parameter"):
            Command(
                command_id="plugin.example.parameters",
                title="Parameters",
                description="Duplicate parameters.",
                category="test",
                authority="READ_ONLY",
                parameters=(Parameter("name", "First."), Parameter("name", "Second.")),
            )

    def test_non_string_target_fails_as_registry_error(self) -> None:
        with self.assertRaisesRegex(RegistryError, "must be strings"):
            builtin_registry().prepare_request(
                "codex.house.task.inspect",
                target={"kind": "task", "id": 123},  # type: ignore[dict-item]
            )

    def test_prepared_request_hash_is_deterministic(self) -> None:
        registry = builtin_registry()
        first = registry.prepare_request("codex.house.routes.list")
        second = registry.prepare_request("codex.house.routes.list")
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
