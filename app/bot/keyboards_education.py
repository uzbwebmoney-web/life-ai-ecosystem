from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.i18n import t
from app.core.modules.catalog import MODULE_BY_ID


def education_module_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    mod = MODULE_BY_ID["education"]
    rows = [
        [InlineKeyboardButton(text=sub.title(lang), callback_data=f"sub:education:{sub.id}")]
        for sub in mod.submodules
    ]
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def education_ai_kb(module_id: str, sub_id: str, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(lang, "btn_ask_ai"), callback_data=f"ai:{module_id}:{sub_id}"),
                InlineKeyboardButton(text=t(lang, "btn_add_record"), callback_data=f"rec:{module_id}:{sub_id}"),
            ],
            [InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:education")],
        ]
    )
