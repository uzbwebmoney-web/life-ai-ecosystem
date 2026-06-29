from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.i18n import t


def support_user_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "support_btn_exit"), callback_data="sup:exit")],
        ]
    )


def support_continue_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "support_btn_continue"), callback_data="sup:open")],
        ]
    )


def support_admin_reply_kb(user_telegram_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(lang, "support_btn_reply"),
                    callback_data=f"sup:reply:{user_telegram_id}",
                )
            ],
        ]
    )
