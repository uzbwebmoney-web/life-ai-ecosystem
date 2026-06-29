from __future__ import annotations

import re

from app.services.agent.intent import should_route_to_agent
from app.services.intent_router import INTENT_KEYWORDS, detect_module
from app.services.unified_ai.schemas import UnifiedIntent

_ACTION_PATTERNS: list[tuple[str, str]] = [
    (r"напомни|remind|eslat", "reminder"),
    (r"сохрани|save|saqlang|запиши|add expense|xarajat", "save"),
    (r"купил|bought|потратил|spent|чек|receipt", "purchase"),
    (r"еду в|поездк|trip to|sayohat|turkey|турци", "travel"),
    (r"болит|symptom|аломат|боль|pain|simptom", "health"),
    (r"найди|where|qayerda|где мой|when|когда", "search"),
    (r"презентац|pptx|таблиц|excel|исследован|research", "research"),
]

_MODULE_CLUSTERS: dict[str, tuple[str, ...]] = {
    "health": ("health", "nutrition", "fitness", "organizer"),
    "purchase": ("finance", "home", "vault", "shopping"),
    "travel": ("travel", "organizer", "finance", "vault"),
    "car": ("car", "organizer", "finance"),
    "receipt": ("vault", "finance", "home"),
}


def _score_modules(text: str) -> dict[str, int]:
    lowered = text.lower()
    scores: dict[str, int] = {}
    for module_id, keywords in INTENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in lowered)
        if score:
            scores[module_id] = score
    primary = detect_module(text)
    if primary:
        scores[primary] = scores.get(primary, 0) + 2
    return scores


def _action_types(text: str) -> list[str]:
    low = text.lower()
    found: list[str] = []
    for pattern, action in _ACTION_PATTERNS:
        if re.search(pattern, low):
            found.append(action)
    return found


def _expand_modules(scores: dict[str, int], actions: list[str]) -> list[str]:
    modules = sorted(scores, key=scores.get, reverse=True)  # type: ignore[arg-type]
    if not modules and actions:
        for action in actions:
            for mod in _MODULE_CLUSTERS.get(action, ()):
                if mod not in modules:
                    modules.append(mod)
    for action in actions:
        for mod in _MODULE_CLUSTERS.get(action, ()):
            if mod not in modules:
                modules.append(mod)
    if not modules:
        modules = ["ai_assistant"]
    return modules[:6]


def analyze_intent(text: str, *, active_module: str | None = None) -> UnifiedIntent:
    t = (text or "").strip()
    actions = _action_types(t)
    scores = _score_modules(t)
    if active_module and active_module in INTENT_KEYWORDS:
        scores[active_module] = scores.get(active_module, 0) + 1
    modules = _expand_modules(scores, actions)

    goal = "chat"
    if "travel" in actions:
        goal = "travel_prep"
    elif "purchase" in actions or re.search(r"холодильник|fridge|техник|appliance", t, re.I):
        goal = "purchase"
    elif "reminder" in actions:
        goal = "reminder"
    elif "search" in actions:
        goal = "search"
    elif "health" in actions:
        goal = "health"
    elif "research" in actions:
        goal = "research"
    elif "save" in actions:
        goal = "save"

    needs_agent = (
        should_route_to_agent(t)
        or goal in {"travel_prep", "purchase", "reminder", "search", "save", "research"}
        or len(actions) >= 2
        or len(modules) >= 2
    )

    return UnifiedIntent(
        goal=goal,
        modules=modules,
        action_types=actions,
        needs_agent=needs_agent,
        confidence=min(1.0, 0.5 + len(scores) * 0.15 + len(actions) * 0.1),
        active_hint=active_module,
    )
