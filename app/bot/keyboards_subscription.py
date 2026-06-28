from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.i18n import t
from app.core.plans import ADDON_PACKAGES, PLANS


def subscription_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "sub_btn_usage"), callback_data="sub:usage")],
            [InlineKeyboardButton(text=t(lang, "sub_btn_plans"), callback_data="sub:plans")],
            [InlineKeyboardButton(text=t(lang, "sub_btn_packages"), callback_data="sub:packages")],
            [InlineKeyboardButton(text=t(lang, "sub_btn_referral"), callback_data="sub:referral")],
            [InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")],
        ]
    )


def subscription_plan_kb(lang: str = "ru", *, selected: str | None = None) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for plan_id in ("student", "basic", "premium", "pro"):
        plan = PLANS[plan_id]
        label = f"{plan.emoji} {t(lang, plan.name_key)}"
        if selected == plan_id:
            label = f"✓ {label}"
        rows.append(
            [
                InlineKeyboardButton(text=label, callback_data=f"sub:plan:{plan_id}"),
                InlineKeyboardButton(text=t(lang, "sub_btn_buy"), callback_data=f"sub:buy:{plan_id}"),
            ]
        )
    rows.append([InlineKeyboardButton(text=t(lang, "sub_btn_back"), callback_data="sub:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def packages_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for pkg in ADDON_PACKAGES:
        rows.append(
            [
                InlineKeyboardButton(
                    text=t(lang, pkg.name_key),
                    callback_data=f"sub:buy:{pkg.id}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text=t(lang, "sub_btn_back"), callback_data="sub:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
