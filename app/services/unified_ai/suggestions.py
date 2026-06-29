from __future__ import annotations

import re

from dataclasses import dataclass

from app.core.i18n import t
from app.services.proactive_service import ProactiveAction, proactive_kb
from app.services.unified_ai.schemas import UnifiedIntent

_HEALTH_SYMPTOM = re.compile(r"\b(?:болит|боль|pain|simptom|аломат|symptom)\w*\b", re.I)
_APPLIANCE = re.compile(r"\b(?:холодильник|fridge|стирал|washer|техник|appliance)\w*\b", re.I)


def smart_suggestions(
    intent: UnifiedIntent,
    user_message: str,
    ai_answer: str = "",
    lang: str = "ru",
) -> list[ProactiveAction]:
    from app.services.proactive_service import suggest_actions

    text = f"{user_message}\n{ai_answer}".lower()
    actions = suggest_actions(user_message, ai_answer, lang, module_id=None)

    def add(action_id: str, label_key: str, callback: str) -> None:
        if any(a.action_id == action_id for a in actions):
            return
        actions.append(ProactiveAction(action_id, t(lang, label_key), callback))

    if intent.goal == "health" or _HEALTH_SYMPTOM.search(text):
        add("symptom_diary", "uni_act_symptom_diary", "act:symptom_diary")
        add("med_remind", "act_med_remind", "act:med_remind")
        add("doctor_visit", "uni_act_doctor_visit", "act:doctor_visit")

    if intent.goal == "purchase" or _APPLIANCE.search(text):
        add("save_expense", "act_save_expense", "act:save_expense")
        add("save_warranty", "uni_act_warranty", "act:save_warranty")
        add("add_inventory", "uni_act_inventory", "act:add_inventory")

    if intent.goal == "travel_prep" or "travel" in intent.modules:
        add("travel_plan", "act_travel_plan", "act:travel_plan")
        add("travel_passport", "act_travel_passport", "act:travel_passport")
        add("travel_budget", "uni_act_travel_budget", "act:travel_budget")

    if "car" in intent.modules or intent.goal == "reminder":
        add("car_service", "act_car_service", "act:car_service")

    if re.search(r"паспорт|passport", text):
        add("travel_passport", "act_travel_passport", "act:travel_passport")
        add("travel_plan", "uni_act_use_passport", "act:travel_plan")

    seen: set[str] = set()
    unique: list[ProactiveAction] = []
    for action in actions:
        if action.action_id in seen:
            continue
        seen.add(action.action_id)
        unique.append(action)
    return unique[:5]


def should_offer_save(intent: UnifiedIntent, user_message: str, answer: str, *, memory_enabled: bool) -> bool:
    if not memory_enabled:
        return False
    if len(answer) < 80 and len(user_message) < 40:
        return False
    if intent.goal in {"save", "purchase", "travel_prep", "health", "reminder"}:
        return True
    return len(answer) > 200


def unified_reply_kb(
    actions: list[ProactiveAction],
    lang: str,
    *,
    offer_save: bool = False,
) -> "InlineKeyboardMarkup | None":
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    rows: list[list[InlineKeyboardButton]] = []
    if offer_save:
        rows.append(
            [
                InlineKeyboardButton(text=t(lang, "uni_btn_save"), callback_data="uni:save"),
                InlineKeyboardButton(text=t(lang, "uni_btn_dismiss"), callback_data="uni:dismiss"),
            ]
        )
    base = proactive_kb(actions, lang)
    if base:
        rows.extend(base.inline_keyboard)
    elif offer_save:
        rows.append([InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")])
    if not rows:
        return None
    return InlineKeyboardMarkup(inline_keyboard=rows)
