from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import back_menu_kb
from app.bot.keyboards_credits import credits_cancel_kb, credits_hub_kb
from app.bot.states import CreditStates
from app.core.i18n import t
from app.models.entities import User
from app.services.credit_loans import (
    add_credit_loan,
    deactivate_credit_loan,
    format_credit_loan_line,
    list_credit_loans,
)

router = Router()


async def _show_credits_hub(target: Message, user: User, session: AsyncSession) -> None:
    lang = user.language
    loans = await list_credit_loans(session, user.id)
    if loans:
        body = "\n\n".join(format_credit_loan_line(loan) for loan in loans)
        text = f"{t(lang, 'credits_my')}\n\n{body}\n\n{t(lang, 'credits_notify')}"
    else:
        text = f"{t(lang, 'credits_title')}\n\n{t(lang, 'credits_empty')}\n\n{t(lang, 'credits_hint')}"
    await target.answer(text, reply_markup=credits_hub_kb(loans, lang))


@router.message(Command("credit"))
async def cmd_credit(message: Message, user: User, session: AsyncSession) -> None:
    await _show_credits_hub(message, user, session)


@router.callback_query(F.data == "credit:add")
async def credit_add_start(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = user.language
    await state.set_state(CreditStates.waiting_title)
    await callback.message.answer(t(lang, "credits_new"), reply_markup=credits_cancel_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "credit:cancel")
async def credit_add_cancel(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = user.language
    await state.clear()
    await callback.message.answer(t(lang, "credits_cancelled"), reply_markup=back_menu_kb(lang))
    await callback.answer()


@router.message(CreditStates.waiting_title)
async def credit_title(message: Message, state: FSMContext, user: User) -> None:
    lang = user.language
    title = (message.text or "").strip()
    if len(title) < 2:
        await message.answer(t(lang, "credits_title_short"))
        return
    await state.update_data(credit_title=title)
    await state.set_state(CreditStates.waiting_total)
    await message.answer(t(lang, "credits_total"), reply_markup=credits_cancel_kb(lang))


@router.message(CreditStates.waiting_total)
async def credit_total(message: Message, state: FSMContext, user: User) -> None:
    lang = user.language
    raw = (message.text or "").replace(" ", "").replace(",", ".").strip()
    try:
        total = float(raw)
    except ValueError:
        await message.answer(t(lang, "credits_total_error"))
        return
    if total <= 0:
        await message.answer(t(lang, "credits_total_positive"))
        return
    await state.update_data(credit_total=total)
    await state.set_state(CreditStates.waiting_monthly)
    await message.answer(t(lang, "credits_monthly"), reply_markup=credits_cancel_kb(lang))


@router.message(CreditStates.waiting_monthly)
async def credit_monthly(message: Message, state: FSMContext, user: User) -> None:
    lang = user.language
    raw = (message.text or "").replace(" ", "").replace(",", ".").strip()
    try:
        monthly = float(raw)
    except ValueError:
        await message.answer(t(lang, "credits_monthly_error"))
        return
    if monthly <= 0:
        await message.answer(t(lang, "credits_total_positive"))
        return
    await state.update_data(credit_monthly=monthly)
    await state.set_state(CreditStates.waiting_day)
    await message.answer(t(lang, "credits_day"), reply_markup=credits_cancel_kb(lang))


@router.message(CreditStates.waiting_day)
async def credit_day(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    raw = (message.text or "").strip()
    if not raw.isdigit():
        await message.answer(t(lang, "credits_day_error"))
        return
    day = int(raw)
    if day < 1 or day > 31:
        await message.answer(t(lang, "credits_day_range"))
        return
    data = await state.get_data()
    loan = await add_credit_loan(
        session,
        user_id=user.id,
        title=str(data.get("credit_title") or t(lang, "default_loan_title")),
        total_amount=float(data.get("credit_total") or 0),
        monthly_payment=float(data.get("credit_monthly") or 0),
        payment_day=day,
        profile_id=user.active_profile_id,
    )
    await message.answer(
        t(lang, "credits_saved", info=format_credit_loan_line(loan), day=day),
        reply_markup=credits_hub_kb(await list_credit_loans(session, user.id), lang),
    )
    await state.clear()


@router.callback_query(F.data.startswith("credit:del:"))
async def credit_delete(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    loan_id = int((callback.data or "").split(":")[2])
    ok = await deactivate_credit_loan(session, user.id, loan_id)
    if not ok:
        await callback.answer(t(lang, "credits_not_found"), show_alert=True)
        return
    loans = await list_credit_loans(session, user.id)
    if loans:
        body = "\n\n".join(format_credit_loan_line(loan) for loan in loans)
        text = f"{t(lang, 'credits_my')}\n\n{body}"
    else:
        text = t(lang, "credits_deleted_all")
    await callback.message.edit_text(text, reply_markup=credits_hub_kb(loans, lang))
    await callback.answer(t(lang, "credits_removed"))
