from __future__ import annotations

from app.core.i18n import t
from app.core.modules.catalog import MODULE_BY_ID

GENERIC_AI_MODULES: frozenset[str] = frozenset({"sport", "fitness"})

GENERIC_SUBMODULE_AI: dict[str, dict[str, str]] = {
    "sport": {
        "analytics": "Футбольная аналитика: тактика, форма команд, ключевые игроки.",
        "stats": "Статистика матчей, игроков, турнирные таблицы — справочно.",
        "matches": "Разбор матчей, ключевые моменты, прогнозы — без гарантий.",
        "teams": "Сравнение команд по составу, форме, статистике.",
        "alerts": "Напоминания о матчах — помогай настроить через органайзер.",
    },
    "fitness": {
        "workouts": "Планы тренировок по целям и уровню подготовки.",
        "progress": "Отслеживание прогресса, мотивация, периодизация.",
        "reminders": "Напоминания о тренировках — советуй использовать органайзер.",
    },
}


def generic_submodule_description(module_id: str, sub_id: str, lang: str) -> str:
    key = f"gen_sub_{module_id}_{sub_id}"
    text = t(lang, key)
    if text != key:
        return text
    return GENERIC_SUBMODULE_AI.get(module_id, {}).get(sub_id, t(lang, "gen_ai_hint"))


def generic_module_intro(module_id: str, lang: str) -> str:
    key = f"gen_{module_id}_intro"
    text = t(lang, key)
    if text != key:
        return text
    mod = MODULE_BY_ID.get(module_id)
    return mod.ai_hint_ru if mod else t(lang, "gen_ai_hint")
