from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.i18n import t
from app.core.plans import PLANS
from app.services.admin_user_service import ADMIN_PLAN_IDS


def admin_menu_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "admin_btn_stats"), callback_data="adm:stats")],
            [InlineKeyboardButton(text=t(lang, "admin_btn_users"), callback_data="adm:users")],
            [InlineKeyboardButton(text=t(lang, "admin_btn_search_user"), callback_data="adm:search")],
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


def admin_user_search_results_kb(users: list, lang: str = "ru") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for user in users[:10]:
        label = f"#{user.id} · @{user.username}" if user.username else f"#{user.id} · tg{user.telegram_id}"
        rows.append(
            [InlineKeyboardButton(text=label[:60], callback_data=f"adm:user:{user.id}")]
        )
    rows.append([InlineKeyboardButton(text=t(lang, "admin_btn_search_again"), callback_data="adm:search")])
    rows.append([InlineKeyboardButton(text=t(lang, "admin_btn_back"), callback_data="adm:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def admin_user_kb(user_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    plan_rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for plan_id in ADMIN_PLAN_IDS:
        plan = PLANS[plan_id]
        row.append(
            InlineKeyboardButton(
                text=f"{plan.emoji} {t(lang, plan.name_key)[:12]}",
                callback_data=f"adm:uplan:{user_id}:{plan_id}",
            )
        )
        if len(row) == 2:
            plan_rows.append(row)
            row = []
    if row:
        plan_rows.append(row)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            *plan_rows,
            [
                InlineKeyboardButton(text=t(lang, "admin_user_btn_extend_plan"), callback_data=f"adm:uextplan:{user_id}"),
                InlineKeyboardButton(text=t(lang, "admin_user_btn_extend_trial"), callback_data=f"adm:uextrial:{user_id}"),
            ],
            [
                InlineKeyboardButton(text=t(lang, "admin_user_btn_reset_usage"), callback_data=f"adm:ureset:{user_id}"),
                InlineKeyboardButton(text=t(lang, "admin_user_btn_bonus_100"), callback_data=f"adm:ubonus100:{user_id}"),
            ],
            [
                InlineKeyboardButton(text=t(lang, "admin_user_btn_bonus_custom"), callback_data=f"adm:ubonus:{user_id}"),
                InlineKeyboardButton(text=t(lang, "admin_user_btn_refresh"), callback_data=f"adm:urefresh:{user_id}"),
            ],
            [InlineKeyboardButton(text=t(lang, "admin_btn_search_again"), callback_data="adm:search")],
            [InlineKeyboardButton(text=t(lang, "admin_btn_back"), callback_data="adm:menu")],
        ]
    )
