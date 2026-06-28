from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards_payment import payment_cancel_kb
from app.bot.states import PaymentStates
from app.core.config import settings
from app.core.i18n import t
from app.models.entities import User
from app.services.payment_service import (
    create_payment_order,
    format_payment_instructions,
    get_payment_order,
    notify_admins_payment_pending,
    resolve_product,
    submit_receipt,
)

router = Router()


@router.callback_query(F.data == "pay:cancel")
async def pay_cancel(callback: CallbackQuery, user: User, session: AsyncSession, state: FSMContext) -> None:
    lang = user.language
    data = await state.get_data()
    order_id = data.get("payment_order_id")
    if order_id:
        order = await get_payment_order(session, int(order_id), user_id=user.id)
        if order and order.status == "awaiting_receipt":
            order.status = "cancelled"
            await session.commit()
    await state.clear()
    await callback.message.edit_text(t(lang, "pay_cancelled"))
    await callback.answer()


@router.message(StateFilter(PaymentStates.waiting_receipt), F.photo)
async def pay_receipt_photo(
    message: Message,
    bot: Bot,
    user: User,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    lang = user.language
    data = await state.get_data()
    order_id = int(data.get("payment_order_id") or 0)
    if not order_id:
        await state.clear()
        await message.answer(t(lang, "pay_order_not_found"))
        return

    photo = message.photo[-1]
    order = await submit_receipt(session, order_id, user.id, photo.file_id)
    if not order:
        await state.clear()
        await message.answer(t(lang, "pay_order_not_found"))
        return

    await state.clear()
    await message.answer(t(lang, "pay_receipt_received", order_id=order.id))
    await notify_admins_payment_pending(bot, order, user, lang=lang)
