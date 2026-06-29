from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentStep:
    tool: str
    args: dict[str, Any] = field(default_factory=dict)
    requires_confirm: bool = False
    label: str = ""


@dataclass
class AgentPlan:
    intent: str
    steps: list[AgentStep]
    reply_hint: str = ""
    mode: str = "execute"


@dataclass
class ToolRunResult:
    tool: str
    ok: bool
    message: str
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    text: str = ""
    pending: bool = False
    plan: AgentPlan | None = None
    tool_results: list[ToolRunResult] = field(default_factory=list)
    files: list[tuple[bytes, str, str]] = field(default_factory=list)
    used_ai: bool = False
