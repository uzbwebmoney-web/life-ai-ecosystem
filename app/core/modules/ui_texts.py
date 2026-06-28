from __future__ import annotations

from app.core.i18n import normalize_lang, t

POPULAR_MODULE_IDS: tuple[str, ...] = ("health", "finance", "car", "ai_assistant")

_MODULE_HINT_KEYS: dict[str, str] = {
    "health": "mod_hint_health",
    "car": "mod_hint_car",
    "finance": "mod_hint_finance",
    "business": "mod_hint_business",
    "legal": "mod_hint_legal",
    "travel": "mod_hint_travel",
    "home": "mod_hint_home",
    "shopping": "mod_hint_shopping",
    "education": "mod_hint_education",
    "nutrition": "mod_hint_nutrition",
    "fitness": "mod_hint_fitness",
    "organizer": "mod_hint_organizer",
    "ai_assistant": "mod_hint_ai_assistant",
    "vault": "mod_hint_vault",
}

_MODULE_EXAMPLE_KEYS: dict[str, str] = {
    "health": "mod_example_health",
    "car": "mod_example_car",
    "finance": "mod_example_finance",
    "business": "mod_example_business",
    "legal": "mod_example_legal",
    "travel": "mod_example_travel",
    "home": "mod_example_home",
    "shopping": "mod_example_shopping",
    "education": "mod_example_education",
    "nutrition": "mod_example_nutrition",
    "fitness": "mod_example_fitness",
    "organizer": "mod_example_organizer",
    "ai_assistant": "mod_example_ai_assistant",
    "vault": "mod_example_vault",
}


def module_hint_text(module_id: str, lang: str | None) -> str:
    key = _MODULE_HINT_KEYS.get(module_id)
    if key:
        return t(lang, key)
    return ""


def module_example_text(module_id: str, lang: str | None) -> str:
    key = _MODULE_EXAMPLE_KEYS.get(module_id)
    if key:
        return t(lang, key)
    return ""
