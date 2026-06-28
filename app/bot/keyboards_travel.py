from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.i18n import t
from app.core.modules.catalog import MODULE_BY_ID
from app.services.travel_service import TRAVEL_CURRENCIES


def travel_module_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    mod = MODULE_BY_ID["travel"]
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=sub.title(lang), callback_data=f"sub:travel:{sub.id}")]
        for sub in mod.submodules
    ]
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def travel_ai_kb(module_id: str, sub_id: str, lang: str = "ru") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(text=t(lang, "btn_ask_ai"), callback_data=f"ai:{module_id}:{sub_id}"),
            InlineKeyboardButton(text=t(lang, "btn_add_record"), callback_data=f"rec:{module_id}:{sub_id}"),
        ],
    ]
    if sub_id == "currency":
        rows.insert(0, [InlineKeyboardButton(text=t(lang, "trv_fx_convert"), callback_data="trv:fx:start")])
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:travel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def travel_currency_pick_kb(prefix: str, lang: str = "ru") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for code in TRAVEL_CURRENCIES:
        row.append(InlineKeyboardButton(text=code, callback_data=f"{prefix}:{code}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="trv:fx:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def travel_cancel_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="trv:fx:cancel")]]
    )
