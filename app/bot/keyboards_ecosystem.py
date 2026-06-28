from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.i18n import t


def ecosystem_features_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "btn_notifications"), callback_data="hub:notifications")],
            [InlineKeyboardButton(text=t(lang, "eco_btn_memory"), callback_data="set:memory")],
            [InlineKeyboardButton(text=t(lang, "btn_search"), callback_data="hub:search")],
            [InlineKeyboardButton(text=t(lang, "btn_voice"), callback_data="set:voice")],
            [InlineKeyboardButton(text=t(lang, "btn_language"), callback_data="hub:language")],
            [InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")],
        ]
    )


def notifications_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "btn_add_reminder"), callback_data="sub:organizer:reminders")],
            [InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")],
        ]
    )
