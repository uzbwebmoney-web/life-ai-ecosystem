from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards_admin import admin_back_kb, admin_menu_kb, admin_user_kb, admin_user_search_results_kb
from app.bot.keyboards_payment import admin_order_kb, admin_orders_list_kb
from app.bot.message_ui import safe_edit_text
from app.bot.states import AdminStates
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
from app.core.plans import PLANS, normalize_plan_id
from app.services.admin_user_service import (
    admin_add_ai_bonus,
    admin_apply_credits_input,
    admin_extend_plan,
    admin_extend_trial,
    admin_reset_credits,
    admin_reset_usage,
    admin_set_user_plan,
    format_admin_user_card,
    format_user_search_results,
    get_user_by_id,
    search_users,
)
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
        await safe_edit_text(target, intro, reply_markup=kb)
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
    await safe_edit_text(
        callback.message,
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
    await safe_edit_text(
        callback.message,
        format_recent_users_message(users, lang=lang),
        reply_markup=admin_back_kb(lang),
    )
    await callback.answer()


async def _show_user_card(
    target: Message,
    session: AsyncSession,
    user_id: int,
    lang: str,
    *,
    edit: bool = False,
) -> bool:
    target_user = await get_user_by_id(session, user_id)
    if not target_user:
        return False
    await session.refresh(target_user)
    text = await format_admin_user_card(session, target_user, lang=lang)
    kb = admin_user_kb(user_id, lang)
    if edit:
        await safe_edit_text(target, text, reply_markup=kb)
    else:
        await target.answer(text, reply_markup=kb)
    return True


@router.callback_query(F.data == "adm:search")
async def admin_search_start(callback: CallbackQuery, user: User, state: FSMContext) -> None:
    if not is_admin(user):
        await callback.answer()
        return
    lang = user.language
    await state.set_state(AdminStates.waiting_user_search)
    await safe_edit_text(callback.message, t(lang, "admin_user_search_prompt"), reply_markup=admin_back_kb(lang))
    await callback.answer()


@router.message(AdminStates.waiting_user_search)
async def admin_search_query(message: Message, user: User, session: AsyncSession, state: FSMContext) -> None:
    if not is_admin(user):
        return
    lang = user.language
    query = (message.text or "").strip()
    users = await search_users(session, query)
    await state.clear()
    if not users:
        await message.answer(t(lang, "admin_user_not_found"), reply_markup=admin_back_kb(lang))
        return
    if len(users) == 1:
        await _show_user_card(message, session, users[0].id, lang)
        return
    await message.answer(
        format_user_search_results(users, lang=lang),
        reply_markup=admin_user_search_results_kb(users, lang),
    )


@router.callback_query(F.data.startswith("adm:user:"))
async def admin_user_open(callback: CallbackQuery, user: User, session: AsyncSession, state: FSMContext) -> None:
    if not is_admin(user):
        await callback.answer()
        return
    await state.clear()
    lang = user.language
    user_id = int((callback.data or "").split(":")[2])
    ok = await _show_user_card(callback.message, session, user_id, lang, edit=True)
    if not ok:
        await callback.answer(t(lang, "admin_user_not_found"), show_alert=True)
        return
    await callback.answer()


@router.callback_query(F.data.startswith("adm:urefresh:"))
async def admin_user_refresh(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    if not is_admin(user):
        await callback.answer()
        return
    lang = user.language
    user_id = int((callback.data or "").split(":")[2])
    ok = await _show_user_card(callback.message, session, user_id, lang, edit=True)
    if not ok:
        await callback.answer(t(lang, "admin_user_not_found"), show_alert=True)
        return
    await callback.answer(t(lang, "admin_refreshed"))


@router.callback_query(F.data.startswith("adm:uplan:"))
async def admin_user_set_plan(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    if not is_admin(user):
        await callback.answer()
        return
    lang = user.language
    parts = (callback.data or "").split(":")
    user_id = int(parts[2])
    plan_id = parts[3]
    plan_key = normalize_plan_id(plan_id)
    updated = await admin_set_user_plan(session, user_id, plan_key, days=30)
    if not updated:
        await callback.answer(t(lang, "admin_user_not_found"), show_alert=True)
        return
    plan_name = t(lang, PLANS[plan_key].name_key) if plan_key in PLANS else plan_key
    await _show_user_card(callback.message, session, user_id, lang, edit=True)
    await callback.answer(t(lang, "admin_user_plan_set", plan=plan_name))


@router.callback_query(F.data.startswith("adm:uextplan:"))
async def admin_user_extend_plan(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    if not is_admin(user):
        await callback.answer()
        return
    lang = user.language
    user_id = int((callback.data or "").split(":")[2])
    updated = await admin_extend_plan(session, user_id, days=30)
    if not updated:
        await callback.answer(t(lang, "admin_user_extend_plan_fail"), show_alert=True)
        return
    await _show_user_card(callback.message, session, user_id, lang, edit=True)
    await callback.answer(t(lang, "admin_user_extend_plan_ok"))


@router.callback_query(F.data.startswith("adm:uextrial:"))
async def admin_user_extend_trial(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    if not is_admin(user):
        await callback.answer()
        return
    lang = user.language
    user_id = int((callback.data or "").split(":")[2])
    updated = await admin_extend_trial(session, user_id, days=7)
    if not updated:
        await callback.answer(t(lang, "admin_user_not_found"), show_alert=True)
        return
    await _show_user_card(callback.message, session, user_id, lang, edit=True)
    await callback.answer(t(lang, "admin_user_extend_trial_ok"))


@router.callback_query(F.data.startswith("adm:ureset:"))
async def admin_user_reset_usage(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    if not is_admin(user):
        await callback.answer()
        return
    lang = user.language
    user_id = int((callback.data or "").split(":")[2])
    updated = await admin_reset_usage(session, user_id)
    if not updated:
        await callback.answer(t(lang, "admin_user_not_found"), show_alert=True)
        return
    await _show_user_card(callback.message, session, user_id, lang, edit=True)
    await callback.answer(t(lang, "admin_user_reset_ok"))


@router.callback_query(F.data.startswith("adm:ucredits0:"))
async def admin_user_reset_credits(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    if not is_admin(user):
        await callback.answer()
        return
    lang = user.language
    user_id = int((callback.data or "").split(":")[2])
    updated = await admin_reset_credits(session, user_id)
    if not updated:
        await callback.answer(t(lang, "admin_user_not_found"), show_alert=True)
        return
    await _show_user_card(callback.message, session, user_id, lang, edit=True)
    await callback.answer(t(lang, "admin_user_credits_reset_ok"))


@router.callback_query(F.data.startswith("adm:ubonus100:"))
async def admin_user_bonus_100(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    if not is_admin(user):
        await callback.answer()
        return
    lang = user.language
    user_id = int((callback.data or "").split(":")[2])
    updated = await admin_add_ai_bonus(session, user_id, 100)
    if not updated:
        await callback.answer(t(lang, "admin_user_not_found"), show_alert=True)
        return
    await _show_user_card(callback.message, session, user_id, lang, edit=True)
    await callback.answer(t(lang, "admin_user_credits_add_ok", amount=100))


@router.callback_query(F.data.startswith("adm:ucredits:"))
async def admin_user_credits_start(callback: CallbackQuery, user: User, state: FSMContext) -> None:
    if not is_admin(user):
        await callback.answer()
        return
    lang = user.language
    user_id = int((callback.data or "").split(":")[2])
    await state.set_state(AdminStates.waiting_credits_adjust)
    await state.update_data(admin_credits_user_id=user_id)
    await callback.message.answer(t(lang, "admin_user_credits_prompt"), reply_markup=admin_back_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("adm:ubonus:"))
async def admin_user_bonus_start(callback: CallbackQuery, user: User, state: FSMContext) -> None:
    if not is_admin(user):
        await callback.answer()
        return
    lang = user.language
    user_id = int((callback.data or "").split(":")[2])
    await state.set_state(AdminStates.waiting_credits_adjust)
    await state.update_data(admin_credits_user_id=user_id)
    await callback.message.answer(t(lang, "admin_user_credits_prompt"), reply_markup=admin_back_kb(lang))
    await callback.answer()


@router.message(AdminStates.waiting_bonus_amount)
@router.message(AdminStates.waiting_credits_adjust)
async def admin_user_credits_save(message: Message, user: User, session: AsyncSession, state: FSMContext) -> None:
    if not is_admin(user):
        return
    lang = user.language
    data = await state.get_data()
    user_id = int(data.get("admin_credits_user_id") or data.get("admin_bonus_user_id") or 0)
    raw = (message.text or "").strip()
    updated, action, amount = await admin_apply_credits_input(session, user_id, raw)
    await state.clear()
    if action is None or not updated:
        await message.answer(t(lang, "admin_user_credits_invalid"))
        return
    if action == "reset":
        toast = t(lang, "admin_user_credits_reset_ok")
    elif action == "subtract":
        toast = t(lang, "admin_user_credits_sub_ok", amount=amount)
    else:
        toast = t(lang, "admin_user_credits_add_ok", amount=amount)
    await message.answer(toast)
    await _show_user_card(message, session, user_id, lang)


@router.callback_query(F.data == "adm:costs")
async def admin_costs(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    if not is_admin(user):
        await callback.answer()
        return
    lang = user.language
    stats = await fetch_ai_cost_stats(session)
    await safe_edit_text(
        callback.message,
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
    await safe_edit_text(
        callback.message,
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
    await safe_edit_text(callback.message, text, reply_markup=admin_order_kb(order_id, lang))
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
    await safe_edit_text(
        callback.message,
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
    await safe_edit_text(callback.message, text, reply_markup=admin_back_kb(lang))
    if buyer:
        try:
            await bot.send_message(buyer.telegram_id, format_buyer_rejected_message(lang=buyer.language))
        except Exception:
            pass
    await callback.answer(t(lang, "pay_admin_rejected_toast"))
