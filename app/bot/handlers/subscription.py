from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards_payment import payment_method_kb
from app.bot.keyboards_subscription import packages_kb, subscription_kb, subscription_plan_kb
from app.core.config import settings
from app.core.i18n import t
from app.core.plans import PLANS, TRIAL_DAYS, format_stars, format_uzs, usd_to_stars, usd_to_uzs
from app.models.entities import User
from app.services.payment_service import product_label, resolve_product, resolve_product_stars
from app.services.subscription_service import (
    format_packages_list,
    format_plan_card,
    format_referral_info,
    format_usage_summary,
    ensure_user_subscription_fields,
)

router = Router()


@router.message(Command("subscription", "premium", "tariff"))
async def cmd_subscription(message: Message, user: User, session: AsyncSession) -> None:
    await ensure_user_subscription_fields(session, user)
    lang = user.language
    await message.answer(
        t(lang, "sub_menu_intro", days=TRIAL_DAYS),
        reply_markup=subscription_kb(lang),
    )


@router.callback_query(F.data == "sub:menu")
async def sub_menu(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    await ensure_fields(callback, user, session)
    await callback.message.edit_text(
        t(user.language, "sub_menu_intro", days=TRIAL_DAYS),
        reply_markup=subscription_kb(user.language),
    )
    await callback.answer()


async def ensure_fields(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    await ensure_user_subscription_fields(session, user)


@router.callback_query(F.data == "sub:usage")
async def sub_usage(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    await ensure_fields(callback, user, session)
    lang = user.language
    await callback.message.edit_text(
        format_usage_summary(user, lang=lang),
        reply_markup=subscription_kb(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "sub:plans")
async def sub_plans(callback: CallbackQuery, user: User) -> None:
    lang = user.language
    lines = [t(lang, "sub_plans_title"), ""]
    for plan_id in ("free", "student", "basic", "premium", "pro"):
        plan = PLANS[plan_id]
        if plan.usd_monthly:
            price = format_uzs(usd_to_uzs(plan.usd_monthly))
        else:
            price = t(lang, "plan_price_free")
        lines.append(f"{plan.emoji} <b>{t(lang, plan.name_key)}</b> — {price}")
    lines.append("")
    lines.append(t(lang, "sub_plans_hint"))
    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=subscription_plan_kb(lang),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("sub:plan:"))
async def sub_plan_detail(callback: CallbackQuery, user: User) -> None:
    plan_id = (callback.data or "").split(":")[2]
    if plan_id not in PLANS:
        await callback.answer()
        return
    lang = user.language
    await callback.message.edit_text(
        format_plan_card(plan_id, lang=lang),  # type: ignore[arg-type]
        reply_markup=subscription_plan_kb(lang, selected=plan_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("sub:buy:"))
async def sub_buy(callback: CallbackQuery, user: User) -> None:
    product_id = (callback.data or "").split(":")[2]
    lang = user.language
    try:
        product_type, product_id, amount_uzs = resolve_product(product_id)
        _, _, stars = resolve_product_stars(product_id)
    except ValueError:
        await callback.answer(t(lang, "pay_product_invalid"), show_alert=True)
        return

    product = product_label(product_type, product_id, lang=lang)
    card_available = bool(settings.payment_card_number.strip())
    text = t(
        lang,
        "pay_method_choose",
        product=product,
        uzs=format_uzs(amount_uzs),
        stars=format_stars(stars),
    )
    await callback.message.answer(
        text,
        reply_markup=payment_method_kb(product_id, lang, card_available=card_available),
    )
    await callback.answer()


@router.callback_query(F.data == "sub:packages")
async def sub_packages(callback: CallbackQuery, user: User) -> None:
    lang = user.language
    await callback.message.edit_text(
        format_packages_list(lang=lang),
        reply_markup=packages_kb(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "sub:referral")
async def sub_referral(callback: CallbackQuery, user: User, session: AsyncSession, bot: Bot) -> None:
    await ensure_fields(callback, user, session)
    me = await bot.get_me()
    username = me.username or "bot"
    await callback.message.edit_text(
        format_referral_info(user, username, lang=user.language),
        reply_markup=subscription_kb(user.language),
    )
    await callback.answer()
