from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards_payment import payment_cancel_kb
from app.bot.keyboards_subscription import packages_kb, subscription_kb, subscription_plan_kb
from app.core.config import settings
from app.core.i18n import t
from app.core.plans import AI_PACKAGES, PLANS, format_uzs, usd_to_uzs
from app.models.entities import User
from app.bot.states import PaymentStates
from app.services.payment_service import create_payment_order, format_payment_instructions, resolve_product
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
        t(lang, "sub_menu_intro"),
        reply_markup=subscription_kb(lang),
    )


@router.callback_query(F.data == "sub:menu")
async def sub_menu(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    await ensure_fields(callback, user, session)
    await callback.message.edit_text(
        t(user.language, "sub_menu_intro"),
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
    for plan_id in ("free", "basic", "premium", "pro", "family"):
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
async def sub_buy(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    product_id = (callback.data or "").split(":")[2]
    lang = user.language
    try:
        product_type, product_id, amount_uzs = resolve_product(product_id)
    except ValueError:
        await callback.answer(t(lang, "pay_product_invalid"), show_alert=True)
        return

    if not settings.payment_card_number.strip():
        await callback.answer(t(lang, "pay_card_not_configured"), show_alert=True)
        return

    order = await create_payment_order(session, user, product_type, product_id, amount_uzs)
    await state.set_state(PaymentStates.waiting_receipt)
    await state.update_data(payment_order_id=order.id)

    text = format_payment_instructions(
        order,
        lang=lang,
        card_number=settings.payment_card_number.strip(),
        card_holder=settings.payment_card_holder.strip(),
    )
    await callback.message.answer(text, reply_markup=payment_cancel_kb(lang))
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
