from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.i18n import t
from app.core.modules.catalog import MODULE_BY_ID
from app.models.entities import HealthMedication


def health_module_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    mod = MODULE_BY_ID["health"]
    rows: list[list[InlineKeyboardButton]] = []
    for sub in mod.submodules:
        rows.append(
            [InlineKeyboardButton(text=sub.title(lang), callback_data=f"sub:health:{sub.id}")]
        )
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def health_ai_kb(module_id: str, sub_id: str, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(lang, "btn_ask_ai"), callback_data=f"ai:{module_id}:{sub_id}"),
                InlineKeyboardButton(text=t(lang, "btn_add_record"), callback_data=f"rec:{module_id}:{sub_id}"),
            ],
            [InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:health")],
        ]
    )


def health_diary_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(lang, "health_add_pressure"), callback_data="health:metric:pressure"),
                InlineKeyboardButton(text=t(lang, "health_add_sugar"), callback_data="health:metric:sugar"),
            ],
            [InlineKeyboardButton(text=t(lang, "health_add_weight"), callback_data="health:metric:weight")],
            [InlineKeyboardButton(text=t(lang, "health_view_all"), callback_data="health:diary:all")],
            [InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:health")],
        ]
    )


def health_meds_kb(meds: list[HealthMedication], lang: str = "ru") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=t(lang, "health_med_add"), callback_data="health:med:add")],
    ]
    for med in meds[:15]:
        rows.append(
            [InlineKeyboardButton(text=f"💊 {med.name[:30]}", callback_data=f"health:med:open:{med.id}")]
        )
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:health")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def health_med_item_kb(med_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(lang, "health_med_edit_name"), callback_data=f"health:med:edit:name:{med_id}"),
                InlineKeyboardButton(text=t(lang, "health_med_edit_dose"), callback_data=f"health:med:edit:dose:{med_id}"),
            ],
            [InlineKeyboardButton(text=t(lang, "health_med_edit_times"), callback_data=f"health:med:edit:times:{med_id}")],
            [InlineKeyboardButton(text=t(lang, "health_med_delete"), callback_data=f"health:med:del:{med_id}")],
            [InlineKeyboardButton(text=t(lang, "health_med_back_list"), callback_data="health:med:list")],
        ]
    )


def health_visits_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "health_visit_add"), callback_data="health:visit:add")],
            [InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:health")],
        ]
    )


def health_docs_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "health_doc_add"), callback_data="health:doc:add")],
            [InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:health")],
        ]
    )


def health_cancel_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="health:cancel")]]
    )


def med_reminder_kb(med_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(lang, "health_med_btn_taken"), callback_data=f"health:med:taken:{med_id}"),
                InlineKeyboardButton(text=t(lang, "health_med_btn_skip"), callback_data=f"health:med:skip:{med_id}"),
            ],
        ]
    )


def med_snooze_kb(med_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(lang, "health_med_snooze_15"), callback_data=f"health:med:snooze:{med_id}:15"),
                InlineKeyboardButton(text=t(lang, "health_med_snooze_30"), callback_data=f"health:med:snooze:{med_id}:30"),
            ],
            [
                InlineKeyboardButton(text=t(lang, "health_med_snooze_60"), callback_data=f"health:med:snooze:{med_id}:60"),
                InlineKeyboardButton(text=t(lang, "health_med_snooze_120"), callback_data=f"health:med:snooze:{med_id}:120"),
            ],
            [InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="health:med:snooze:cancel")],
        ]
    )
