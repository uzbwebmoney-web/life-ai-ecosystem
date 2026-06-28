from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.i18n import t
from app.models.entities import AlertItem
from app.services.notifications_service import alert_type_def


def ecosystem_features_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "btn_notifications"), callback_data="hub:notifications")],
            [InlineKeyboardButton(text=t(lang, "eco_btn_memory"), callback_data="set:memory")],
            [InlineKeyboardButton(text=t(lang, "btn_search"), callback_data="hub:search")],
            [InlineKeyboardButton(text=t(lang, "btn_voice"), callback_data="set:voice")],
            [InlineKeyboardButton(text=t(lang, "btn_language"), callback_data="hub:language")],
            [InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")],
        ]
    )


def _ntf_add_btn(lang: str, alert_type: str) -> InlineKeyboardButton:
    kind = alert_type_def(alert_type)
    return InlineKeyboardButton(
        text=t(lang, f"ntf_add_{alert_type}"),
        callback_data=f"ntf:add:{alert_type}",
    )


def notifications_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                _ntf_add_btn(lang, "movie"),
                _ntf_add_btn(lang, "event"),
            ],
            [
                _ntf_add_btn(lang, "ticket"),
                _ntf_add_btn(lang, "delivery"),
            ],
            [
                _ntf_add_btn(lang, "appointment"),
                _ntf_add_btn(lang, "custom"),
            ],
            [
                _ntf_add_btn(lang, "subscription"),
                _ntf_add_btn(lang, "visa"),
            ],
            [InlineKeyboardButton(text=t(lang, "btn_add_reminder"), callback_data="sub:organizer:reminders")],
            [InlineKeyboardButton(text=t(lang, "ntf_manage_alerts"), callback_data="ntf:menu")],
            [InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")],
        ]
    )


def alerts_list_kb(items: list[AlertItem], lang: str = "ru") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [
            _ntf_add_btn(lang, "movie"),
            _ntf_add_btn(lang, "event"),
        ],
    ]
    for item in items[:10]:
        kind = alert_type_def(item.alert_type)
        label = f"🗑 {kind.icon} {item.title[:22]}"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"ntf:del:{item.id}")])
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:notifications")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def alert_item_kb(item_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "fin_bill_delete"), callback_data=f"ntf:del:{item_id}")],
            [InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="ntf:menu")],
        ]
    )


def scan_followup_kb(lang: str = "ru", *, amount: float | None = None) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if amount:
        rows.append(
            [InlineKeyboardButton(text=t(lang, "scan_btn_expense"), callback_data="scan:expense")]
        )
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
