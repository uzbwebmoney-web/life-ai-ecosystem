from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.i18n import t


def agent_confirm_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(lang, "agent_btn_confirm"), callback_data="agent:confirm"),
                InlineKeyboardButton(text=t(lang, "agent_btn_cancel"), callback_data="agent:cancel"),
            ]
        ]
    )
