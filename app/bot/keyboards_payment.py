from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.i18n import t
from app.models.entities import PaymentOrder


def payment_cancel_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="pay:cancel")],
        ]
    )


def admin_order_kb(order_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(lang, "pay_admin_approve"), callback_data=f"adm:payok:{order_id}"),
                InlineKeyboardButton(text=t(lang, "pay_admin_reject"), callback_data=f"adm:payno:{order_id}"),
            ],
            [InlineKeyboardButton(text=t(lang, "admin_btn_orders"), callback_data="adm:orders")],
        ]
    )


def admin_orders_list_kb(orders: list[PaymentOrder], lang: str = "ru") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for order in orders[:10]:
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"#{order.id} — {format_uzs_short(order.amount_uzs)}",
                    callback_data=f"adm:order:{order.id}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text=t(lang, "admin_btn_back"), callback_data="adm:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def format_uzs_short(amount: int) -> str:
    if amount >= 1_000_000:
        return f"{amount // 1_000}k"
    return f"{amount:,}".replace(",", " ")
