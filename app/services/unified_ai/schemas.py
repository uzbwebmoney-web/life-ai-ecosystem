from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class UnifiedIntent:
    goal: str
    modules: list[str]
    action_types: list[str]
    needs_agent: bool
    confidence: float = 1.0
    active_hint: str | None = None


@dataclass
class UnifiedResult:
    handled: bool = True
    used_agent: bool = False
