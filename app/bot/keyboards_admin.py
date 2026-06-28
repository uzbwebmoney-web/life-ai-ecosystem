from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.i18n import t


def admin_menu_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "admin_btn_stats"), callback_data="adm:stats")],
            [InlineKeyboardButton(text=t(lang, "admin_btn_users"), callback_data="adm:users")],
            [InlineKeyboardButton(text=t(lang, "admin_btn_orders"), callback_data="adm:orders")],
            [InlineKeyboardButton(text=t(lang, "admin_btn_costs"), callback_data="adm:costs")],
            [
                InlineKeyboardButton(text=t(lang, "admin_btn_refresh"), callback_data="adm:stats"),
                InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu"),
            ],
        ]
    )


def admin_back_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "admin_btn_back"), callback_data="adm:menu")],
        ]
    )
