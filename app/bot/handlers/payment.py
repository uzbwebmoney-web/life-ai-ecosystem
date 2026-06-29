from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards_payment import payment_cancel_kb
from app.bot.states import PaymentStates
from app.core.config import settings
from app.core.i18n import t
from app.models.entities import User
from app.services.payment_service import (
    activate_product_purchase,
    build_stars_payload,
    create_payment_order,
    format_payment_instructions,
    get_payment_order,
    notify_admins_payment_pending,
    notify_admins_stars_purchase,
    parse_stars_payload,
    product_label,
    register_stars_payment,
    resolve_product,
    resolve_product_stars,
    submit_receipt,
)

router = Router()


@router.callback_query(F.data.startswith("sub:pay:card:"))
async def pay_card_start(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    product_id = (callback.data or "").split(":")[3]
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


@router.callback_query(F.data.startswith("sub:pay:stars:"))
async def pay_stars_invoice(callback: CallbackQuery, bot: Bot, user: User) -> None:
    product_id = (callback.data or "").split(":")[3]
    lang = user.language
    try:
        product_type, product_id, stars = resolve_product_stars(product_id)
    except ValueError:
        await callback.answer(t(lang, "pay_product_invalid"), show_alert=True)
        return

    product = product_label(product_type, product_id, lang=lang)
    payload = build_stars_payload(product_type, product_id)
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=product,
        description=t(lang, "pay_stars_invoice_desc", product=product),
        payload=payload,
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label=product, amount=stars)],
    )
    await callback.answer()


@router.pre_checkout_query(F.invoice_payload.startswith("st:"))
async def stars_pre_checkout(query: PreCheckoutQuery) -> None:
    parsed = parse_stars_payload(query.invoice_payload)
    if not parsed:
        await query.answer(ok=False, error_message="Invalid product")
        return
    product_type, product_id = parsed
    _, _, expected_stars = resolve_product_stars(product_id)
    if query.total_amount != expected_stars or query.currency != "XTR":
        await query.answer(ok=False, error_message="Invalid amount")
        return
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def stars_payment_success(message: Message, bot: Bot, user: User, session: AsyncSession) -> None:
    payment = message.successful_payment
    if not payment or not (payment.invoice_payload or "").startswith("st:"):
        return

    lang = user.language
    parsed = parse_stars_payload(payment.invoice_payload)
    if not parsed:
        await message.answer(t(lang, "pay_order_not_found"))
        return

    product_type, product_id = parsed
    _, _, expected_stars = resolve_product_stars(product_id)
    if payment.total_amount != expected_stars or payment.currency != "XTR":
        await message.answer(t(lang, "pay_order_not_found"))
        return

    charge_id = payment.telegram_payment_charge_id or payment.provider_payment_charge_id or ""
    if not charge_id:
        await message.answer(t(lang, "pay_order_not_found"))
        return
    if not await register_stars_payment(
        session,
        charge_id=charge_id,
        user_id=user.id,
        product_type=product_type,
        product_id=product_id,
    ):
        await message.answer(t(lang, "pay_already_processed"))
        return

    await activate_product_purchase(session, user, product_type, product_id)
    product = product_label(product_type, product_id, lang=lang)
    await message.answer(t(lang, "pay_approved", product=product))
    await notify_admins_stars_purchase(
        bot,
        user,
        product_type,
        product_id,
        expected_stars,
        lang=lang,
    )


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
