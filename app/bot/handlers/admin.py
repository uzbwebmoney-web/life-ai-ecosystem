from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards_admin import admin_back_kb, admin_menu_kb
from app.bot.keyboards_payment import admin_order_kb, admin_orders_list_kb
from app.core.config import settings
from app.core.i18n import t
from app.models.entities import PaymentOrder, User
from app.services.admin_service import (
    fetch_admin_stats,
    format_admin_stats_message,
    format_recent_users_message,
    list_recent_users,
)
from app.services.ai_usage_service import fetch_ai_cost_stats, format_ai_cost_stats_message
from app.services.payment_service import (
    approve_payment_order,
    count_pending_orders,
    format_buyer_approved_message,
    format_buyer_rejected_message,
    format_order_admin_card,
    format_orders_list,
    get_payment_order,
    list_pending_orders,
    reject_payment_order,
)

router = Router()


def is_admin(user: User) -> bool:
    return bool(settings.admin_telegram_id_list) and user.telegram_id in settings.admin_telegram_id_list


async def _show_admin_menu(
    target: Message,
    lang: str,
    session: AsyncSession | None = None,
    *,
    edit: bool = False,
) -> None:
    intro = t(lang, "admin_menu_intro")
    if session is not None:
        pending = await count_pending_orders(session)
        if pending:
            intro += "\n\n" + t(lang, "pay_admin_pending_count", count=pending)
    kb = admin_menu_kb(lang)
    if edit:
        await target.edit_text(intro, reply_markup=kb)
    else:
        await target.answer(intro, reply_markup=kb)


@router.message(Command("admin"))
async def cmd_admin(message: Message, user: User, session: AsyncSession) -> None:
    if not is_admin(user):
        return
    await _show_admin_menu(message, user.language, session)


@router.callback_query(F.data == "adm:menu")
async def admin_menu(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    if not is_admin(user):
        await callback.answer()
        return
    await _show_admin_menu(callback.message, user.language, session, edit=True)
    await callback.answer()


@router.callback_query(F.data == "adm:stats")
async def admin_stats(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    if not is_admin(user):
        await callback.answer()
        return
    lang = user.language
    stats = await fetch_admin_stats(session)
    await callback.message.edit_text(
        format_admin_stats_message(stats, lang=lang),
        reply_markup=admin_back_kb(lang),
    )
    await callback.answer(t(lang, "admin_refreshed"))


@router.callback_query(F.data == "adm:users")
async def admin_users(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    if not is_admin(user):
        await callback.answer()
        return
    lang = user.language
    users = await list_recent_users(session)
    await callback.message.edit_text(
        format_recent_users_message(users, lang=lang),
        reply_markup=admin_back_kb(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "adm:costs")
async def admin_costs(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    if not is_admin(user):
        await callback.answer()
        return
    lang = user.language
    stats = await fetch_ai_cost_stats(session)
    await callback.message.edit_text(
        format_ai_cost_stats_message(stats, lang=lang),
        reply_markup=admin_back_kb(lang),
    )
    await callback.answer(t(lang, "admin_refreshed"))


async def _load_order_users(session: AsyncSession, orders: list[PaymentOrder]) -> dict[int, User]:
    if not orders:
        return {}
    user_ids = {o.user_id for o in orders}
    rows = (
        await session.execute(select(User).where(User.id.in_(user_ids)))
    ).scalars().all()
    return {u.id: u for u in rows}


@router.callback_query(F.data == "adm:orders")
async def admin_orders(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    if not is_admin(user):
        await callback.answer()
        return
    lang = user.language
    orders = await list_pending_orders(session)
    users = await _load_order_users(session, orders)
    await callback.message.edit_text(
        format_orders_list(orders, users, lang=lang),
        reply_markup=admin_orders_list_kb(orders, lang),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm:order:"))
async def admin_order_detail(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    if not is_admin(user):
        await callback.answer()
        return
    lang = user.language
    order_id = int((callback.data or "").split(":")[2])
    order = await get_payment_order(session, order_id)
    if not order:
        await callback.answer(t(lang, "pay_order_not_found"), show_alert=True)
        return
    buyer = (
        await session.execute(select(User).where(User.id == order.user_id))
    ).scalar_one_or_none()
    if not buyer:
        await callback.answer(t(lang, "pay_order_not_found"), show_alert=True)
        return
    text = format_order_admin_card(order, buyer, lang=lang)
    await callback.message.edit_text(text, reply_markup=admin_order_kb(order_id, lang))
    if order.receipt_file_id:
        await callback.message.answer_photo(order.receipt_file_id, caption=t(lang, "pay_admin_receipt"))
    await callback.answer()


@router.callback_query(F.data.startswith("adm:payok:"))
async def admin_pay_approve(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
    bot: Bot,
) -> None:
    if not is_admin(user):
        await callback.answer()
        return
    lang = user.language
    order_id = int((callback.data or "").split(":")[2])
    order, buyer = await approve_payment_order(session, order_id, user)
    if not order or not buyer:
        await callback.answer(t(lang, "pay_order_already_processed"), show_alert=True)
        return
    await callback.message.edit_text(
        format_order_admin_card(order, buyer, lang=lang) + "\n\n" + t(lang, "pay_admin_done_approved"),
        reply_markup=admin_back_kb(lang),
    )
    try:
        await bot.send_message(
            buyer.telegram_id,
            format_buyer_approved_message(order, lang=buyer.language),
        )
    except Exception:
        pass
    await callback.answer(t(lang, "pay_admin_approved_toast"))


@router.callback_query(F.data.startswith("adm:payno:"))
async def admin_pay_reject(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
    bot: Bot,
) -> None:
    if not is_admin(user):
        await callback.answer()
        return
    lang = user.language
    order_id = int((callback.data or "").split(":")[2])
    order = await reject_payment_order(session, order_id, user)
    if not order:
        await callback.answer(t(lang, "pay_order_already_processed"), show_alert=True)
        return
    buyer = (
        await session.execute(select(User).where(User.id == order.user_id))
    ).scalar_one_or_none()
    text = t(lang, "pay_admin_done_rejected", order_id=order.id)
    if buyer:
        text = format_order_admin_card(order, buyer, lang=lang) + "\n\n" + text
    await callback.message.edit_text(text, reply_markup=admin_back_kb(lang))
    if buyer:
        try:
            await bot.send_message(buyer.telegram_id, format_buyer_rejected_message(lang=buyer.language))
        except Exception:
            pass
    await callback.answer(t(lang, "pay_admin_rejected_toast"))
