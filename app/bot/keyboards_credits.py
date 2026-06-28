from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.i18n import t
from app.models.entities import CreditLoan


def credits_hub_kb(loans: list[CreditLoan], lang: str = "ru") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=t(lang, "btn_add_credit"), callback_data="credit:add")],
    ]
    for loan in loans[:10]:
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"🗑 {loan.title[:28]}",
                    callback_data=f"credit:del:{loan.id}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def credits_cancel_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="credit:cancel")]]
    )
