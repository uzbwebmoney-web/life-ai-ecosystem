from __future__ import annotations

import re
from dataclasses import dataclass

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.i18n import t

_NO_PROACTIVE_MODULES = frozenset(
    {
        "education",
        "vault",
        "legal",
        "health",
        "finance",
        "car",
        "business",
        "travel",
        "home",
        "shopping",
        "nutrition",
        "organizer",
        "music",
        "family",
    }
)

_TRAVEL_PATTERNS = (
    re.compile(r"\b(?:sayohat|travel|trip|отпуск|поездк)\w*\b", re.I),
    re.compile(r"\b(?:turkey|istanbul|turkiya|стамбул)\b", re.I),
    re.compile(r"\b(?:лечу|uçish|flight|рейс)\b", re.I),
)


@dataclass(frozen=True)
class ProactiveAction:
    action_id: str
    label: str
    callback_data: str


def _travel_mentioned(text: str) -> bool:
    return any(p.search(text) for p in _TRAVEL_PATTERNS)


def suggest_actions(
    user_message: str,
    ai_answer: str = "",
    lang: str = "ru",
    *,
    module_id: str | None = None,
) -> list[ProactiveAction]:
    if module_id in _NO_PROACTIVE_MODULES:
        return []

    text = f"{user_message}\n{ai_answer}".lower()
    actions: list[ProactiveAction] = []

    def add(action_id: str, label_key: str, callback: str) -> None:
        actions.append(ProactiveAction(action_id, t(lang, label_key), callback))

    if any(x in text for x in ("купил машину", "новая машина", "новый авто", "yangi mashina", "bought a car", "new car")):
        add("car_profile", "act_add_car", "act:car_profile")
        add("car_service", "act_car_service", "act:car_service")
        add("car_insurance", "act_car_insurance", "act:car_insurance")

    if any(x in text for x in ("антибиот", "лекарств", "назначил", "dori", "antibiotic", "prescribed")):
        add("med_course", "act_med_course", "act:med_course")
        add("med_remind", "act_med_remind", "act:med_remind")

    if _travel_mentioned(text):
        add("travel_plan", "act_travel_plan", "act:travel_plan")
        add("travel_passport", "act_travel_passport", "act:travel_passport")

    if any(x in text for x in ("аллерг", "allerg", "запомни", "remember")):
        add("save_memory", "act_save_memory", "act:save_memory")

    if any(x in text for x in ("чек", "receipt", "оплат", "счет", "bill", "xarajat", "expense")):
        add("save_expense", "act_save_expense", "act:save_expense")

    if not actions and len(user_message) > 20 and not module_id:
        add("save_memory", "act_save_memory", "act:save_memory")

    seen: set[str] = set()
    unique: list[ProactiveAction] = []
    for action in actions:
        if action.action_id in seen:
            continue
        seen.add(action.action_id)
        unique.append(action)
    return unique[:4]


def proactive_kb(actions: list[ProactiveAction], lang: str) -> InlineKeyboardMarkup | None:
    if not actions:
        return None
    rows = [[InlineKeyboardButton(text=a.label, callback_data=a.callback_data)] for a in actions]
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
