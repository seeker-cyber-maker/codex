"""Deterministic command inventory shared by agents and human surfaces.

The registry describes and validates requests.  It deliberately has no
dispatcher and grants no authority.  A later controller must independently
authorize any request before an action can occur.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

COMMAND_ID = re.compile(r"^[a-z][a-z0-9]*(?:\.[a-z][a-z0-9_-]*){2,}$")
PARAMETER_NAME = re.compile(r"^[a-z][a-z0-9_]*$")
CORE_NAMESPACE = "codex.house."


class RegistryError(ValueError):
    """Raised when a command declaration or request is ambiguous."""


class TargetRequirement(str, Enum):
    NONE = "NONE"
    EXPLICIT = "EXPLICIT"


@dataclass(frozen=True)
class Parameter:
    name: str
    description: str
    required: bool = False
    default: str | None = None
    choices: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not PARAMETER_NAME.fullmatch(self.name):
            raise RegistryError(f"invalid parameter name: {self.name}")
        if not self.description.strip():
            raise RegistryError(f"parameter description is empty: {self.name}")
        if self.required and self.default is not None:
            raise RegistryError(
                f"required parameter cannot have a default: {self.name}"
            )
        if len(set(self.choices)) != len(self.choices):
            raise RegistryError(f"duplicate choices: {self.name}")
        if (
            self.default is not None
            and self.choices
            and self.default not in self.choices
        ):
            raise RegistryError(f"default is not an allowed choice: {self.name}")

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "required": self.required,
            "default": self.default,
            "choices": list(self.choices),
        }


@dataclass(frozen=True)
class Command:
    command_id: str
    title: str
    description: str
    category: str
    authority: str
    target_requirement: TargetRequirement = TargetRequirement.NONE
    target_kinds: tuple[str, ...] = ()
    parameters: tuple[Parameter, ...] = ()
    hotkey: str | None = None
    surfaces: tuple[str, ...] = ("agent", "dashboard")
    source_ref: str = ""

    def __post_init__(self) -> None:
        if not COMMAND_ID.fullmatch(self.command_id):
            raise RegistryError(f"invalid command id: {self.command_id}")
        for label, value in (
            ("title", self.title),
            ("description", self.description),
            ("category", self.category),
            ("authority", self.authority),
        ):
            if not value.strip():
                raise RegistryError(f"{label} is empty: {self.command_id}")
        if (
            self.target_requirement is TargetRequirement.EXPLICIT
            and not self.target_kinds
        ):
            raise RegistryError(f"explicit target has no kinds: {self.command_id}")
        if self.target_requirement is TargetRequirement.NONE and self.target_kinds:
            raise RegistryError(
                f"target kinds declared for targetless command: {self.command_id}"
            )
        if len(set(self.target_kinds)) != len(self.target_kinds):
            raise RegistryError(f"duplicate target kinds: {self.command_id}")
        names = [parameter.name for parameter in self.parameters]
        if len(names) != len(set(names)):
            raise RegistryError(f"duplicate parameter: {self.command_id}")
        if not self.surfaces or not set(self.surfaces).issubset(
            {"agent", "dashboard", "iterm"}
        ):
            raise RegistryError(f"invalid surfaces: {self.command_id}")

    def as_dict(self) -> dict[str, Any]:
        return {
            "command_id": self.command_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "authority": self.authority,
            "target_requirement": self.target_requirement.value,
            "target_kinds": list(self.target_kinds),
            "parameters": [parameter.as_dict() for parameter in self.parameters],
            "hotkey": self.hotkey,
            "surfaces": list(self.surfaces),
            "source_ref": self.source_ref,
        }


@dataclass
class CommandRegistry:
    """A fail-closed catalog that produces no-dispatch request envelopes."""

    _commands: dict[str, Command] = field(default_factory=dict)

    def register(self, command: Command, *, owner: str) -> None:
        self.register_many((command,), owner=owner)

    def register_many(self, commands: Iterable[Command], *, owner: str) -> None:
        if owner == "core":
            raise RegistryError("core registration is not a public plugin operation")
        self._register_many(tuple(commands), owner=owner, core=False)

    def _register_core_many(self, commands: Iterable[Command]) -> None:
        """Populate the compiled first-party catalog outside the plugin API."""
        self._register_many(tuple(commands), owner="core", core=True)

    def _register_many(
        self, commands: tuple[Command, ...], *, owner: str, core: bool
    ) -> None:
        commands = tuple(commands)
        seen = set(self._commands)
        hotkeys = {
            command.hotkey: command.command_id
            for command in self._commands.values()
            if command.hotkey is not None
        }
        for command in commands:
            if command.command_id in seen:
                raise RegistryError(f"command id collision: {command.command_id}")
            if command.command_id.startswith(CORE_NAMESPACE) and not core:
                raise RegistryError(f"reserved core namespace: {command.command_id}")
            if core and not command.command_id.startswith(CORE_NAMESPACE):
                raise RegistryError(
                    f"core command outside reserved namespace: {command.command_id}"
                )
            if not core and not command.command_id.startswith(owner + "."):
                raise RegistryError(
                    f"command outside owner namespace: {command.command_id}"
                )
            if command.hotkey is not None and command.hotkey in hotkeys:
                raise RegistryError(
                    f"hotkey collision: {command.hotkey} with {hotkeys[command.hotkey]}"
                )
            seen.add(command.command_id)
            if command.hotkey is not None:
                hotkeys[command.hotkey] = command.command_id
        for command in commands:
            self._commands[command.command_id] = command

    def manifest(self, *, surface: str | None = None) -> dict[str, Any]:
        if surface is not None and surface not in {"agent", "dashboard", "iterm"}:
            raise RegistryError(f"unknown surface: {surface}")
        commands = [
            command.as_dict()
            for command in sorted(
                self._commands.values(), key=lambda item: item.command_id
            )
            if surface is None or surface in command.surfaces
        ]
        payload = {
            "schema": "codex-house-command-manifest/1",
            "surface": surface or "all",
            "commands": commands,
            "dispatch": "NOT_IMPLEMENTED",
            "authority": "NOT_GRANTED",
        }
        return {**payload, "manifest_sha256": _digest(payload)}

    def search(self, query: str, *, surface: str | None = None) -> list[dict[str, Any]]:
        terms = tuple(term for term in query.casefold().split() if term)
        manifest = self.manifest(surface=surface)
        if not terms:
            return manifest["commands"]
        matches = []
        for command in manifest["commands"]:
            haystack = " ".join(
                str(command[key])
                for key in ("command_id", "title", "description", "category")
            ).casefold()
            if all(term in haystack for term in terms):
                matches.append(command)
        return matches

    def prepare_request(
        self,
        command_id: str,
        *,
        target: Mapping[str, str] | None = None,
        arguments: Mapping[str, str] | None = None,
    ) -> dict[str, Any]:
        command = self._commands.get(command_id)
        if command is None:
            raise RegistryError(f"unknown command: {command_id}")
        target = dict(target or {})
        arguments = dict(arguments or {})
        self._validate_target(command, target)
        normalized = self._validate_arguments(command, arguments)
        payload = {
            "schema": "codex-house-command-request/1",
            "command_id": command.command_id,
            "target": target or None,
            "arguments": normalized,
            "authority": command.authority,
            "state": "PREPARED_UNAUTHORIZED",
            "dispatch": "NOT_ATTEMPTED",
        }
        return {**payload, "request_sha256": _digest(payload)}

    @staticmethod
    def _validate_target(command: Command, target: dict[str, str]) -> None:
        if command.target_requirement is TargetRequirement.NONE:
            if target:
                raise RegistryError(
                    f"command does not accept a target: {command.command_id}"
                )
            return
        if set(target) != {"kind", "id"}:
            raise RegistryError(
                f"explicit target requires kind and id: {command.command_id}"
            )
        if not isinstance(target["kind"], str) or not isinstance(target["id"], str):
            raise RegistryError("target kind and id must be strings")
        if target["kind"] not in command.target_kinds:
            raise RegistryError(f"invalid target kind: {target['kind']}")
        if not target["id"].strip() or len(target["id"]) > 256:
            raise RegistryError("invalid target id")

    @staticmethod
    def _validate_arguments(
        command: Command, arguments: dict[str, str]
    ) -> dict[str, str]:
        parameters = {parameter.name: parameter for parameter in command.parameters}
        unknown = sorted(set(arguments) - set(parameters))
        if unknown:
            raise RegistryError("unknown arguments: " + ", ".join(unknown))
        normalized: dict[str, str] = {}
        for name, parameter in parameters.items():
            value = arguments.get(name, parameter.default)
            if value is None:
                if parameter.required:
                    raise RegistryError(f"missing required argument: {name}")
                continue
            if not isinstance(value, str) or not value.strip() or len(value) > 4096:
                raise RegistryError(f"invalid argument: {name}")
            if parameter.choices and value not in parameter.choices:
                raise RegistryError(f"invalid choice for {name}: {value}")
            normalized[name] = value
        return normalized


def _digest(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def builtin_registry() -> CommandRegistry:
    """Return the bounded first-party inventory; it does not inspect runtime state."""
    registry = CommandRegistry()
    registry._register_core_many(
        (
            Command(
                command_id="codex.house.task.submit",
                title="Create task",
                description="Prepare a task submission for the single-writer inbox.",
                category="tasks",
                authority="TASK_SUBMISSION_REQUIRED",
                parameters=(
                    Parameter("summary", "Concrete task objective.", required=True),
                    Parameter(
                        "recipient",
                        "Requested recipient or triage lane.",
                        default="triage",
                        choices=("triage", "coder", "reviewer", "specific_model"),
                    ),
                ),
                hotkey="cmd+shift+t",
                source_ref="house/task_spine/submission.py",
            ),
            Command(
                command_id="codex.house.task.inspect",
                title="Inspect task",
                description="Prepare a read-only task status lookup.",
                category="tasks",
                authority="READ_ONLY",
                target_requirement=TargetRequirement.EXPLICIT,
                target_kinds=("task",),
                hotkey="cmd+shift+i",
                source_ref="house/task_spine/core.py",
            ),
            Command(
                command_id="codex.house.context.inspect",
                title="Inspect context branch",
                description="Prepare a read-only lookup of one conserved context branch.",
                category="context",
                authority="READ_ONLY",
                target_requirement=TargetRequirement.EXPLICIT,
                target_kinds=("thread", "context_view"),
                source_ref="house/context_tree/codex_house_context.py",
            ),
            Command(
                command_id="codex.house.companion.preview",
                title="Preview terminal companion",
                description="Prepare a display-only terminal companion preview request.",
                category="terminal",
                authority="DISPLAY_ONLY",
                target_requirement=TargetRequirement.EXPLICIT,
                target_kinds=("display_batch",),
                surfaces=("agent", "dashboard", "iterm"),
                source_ref="house/terminal_companion/webview.py",
            ),
            Command(
                command_id="codex.house.routes.list",
                title="List model routes",
                description="Show automatic and manual-only routes without selecting one.",
                category="routing",
                authority="READ_ONLY",
                source_ref="house/auto_switcher/policy.py",
            ),
        ),
    )
    return registry
