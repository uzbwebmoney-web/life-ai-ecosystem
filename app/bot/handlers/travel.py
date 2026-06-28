from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards_travel import travel_ai_kb, travel_cancel_kb, travel_currency_pick_kb, travel_module_kb
from app.bot.states import TravelStates
from app.core.i18n import t
from app.core.modules.catalog import MODULE_BY_ID
from app.models.entities import User
from app.services.life_data import set_active_module
from app.services.travel_service import (
    convert_currency,
    format_currency_amount,
    parse_amount,
    travel_submodule_description,
)

router = Router()


@router.callback_query(F.data == "mod:travel")
async def travel_module(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    await set_active_module(session, user, "travel")
    await callback.message.edit_text(t(lang, "trv_module_intro"), reply_markup=travel_module_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("sub:travel:"))
async def travel_submodule(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    sub_id = (callback.data or "").split(":")[2]
    mod = MODULE_BY_ID["travel"]
    sub = next((s for s in mod.submodules if s.id == sub_id), None)
    if not sub:
        await callback.answer(t(lang, "not_found"), show_alert=True)
        return
    await set_active_module(session, user, "travel", submodule_id=sub_id)
    desc = travel_submodule_description(sub_id, lang)
    text = (
        f"✈️ <b>{mod.title(lang)}</b> → <b>{sub.title(lang)}</b>\n\n"
        f"{desc}\n\n{t(lang, 'trv_ai_hint')}"
    )
    await callback.message.edit_text(text, reply_markup=travel_ai_kb("travel", sub_id, lang))
    await callback.answer()


@router.callback_query(F.data == "trv:fx:start")
async def trv_fx_start(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = user.language
    await state.set_state(TravelStates.waiting_fx_amount)
    await callback.message.answer(t(lang, "trv_fx_amount_prompt"), reply_markup=travel_cancel_kb(lang))
    await callback.answer()


@router.message(TravelStates.waiting_fx_amount)
async def trv_fx_amount(message: Message, state: FSMContext, user: User) -> None:
    lang = user.language
    amount = parse_amount(message.text or "")
    if amount is None:
        await message.answer(t(lang, "record_amount_error"))
        return
    await state.update_data(trv_fx_amount=amount)
    await state.set_state(TravelStates.waiting_fx_from)
    await message.answer(t(lang, "trv_fx_from_prompt"), reply_markup=travel_currency_pick_kb("trv:fx:from", lang))


@router.callback_query(F.data.startswith("trv:fx:from:"))
async def trv_fx_from(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = user.language
    code = (callback.data or "").split(":")[3]
    await state.update_data(trv_fx_from=code)
    await state.set_state(TravelStates.waiting_fx_to)
    await callback.message.answer(t(lang, "trv_fx_to_prompt"), reply_markup=travel_currency_pick_kb("trv:fx:to", lang))
    await callback.answer()


@router.callback_query(F.data.startswith("trv:fx:to:"))
async def trv_fx_to(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = user.language
    to_code = (callback.data or "").split(":")[3]
    data = await state.get_data()
    from_code = str(data.get("trv_fx_from") or "")
    amount = float(data.get("trv_fx_amount") or 0)
    result = convert_currency(amount, from_code, to_code)
    if result is None:
        await callback.answer(t(lang, "trv_fx_error"), show_alert=True)
        return
    text = t(
        lang,
        "trv_fx_result",
        amount=format_currency_amount(amount, from_code),
        result=format_currency_amount(result, to_code),
    )
    text += f"\n\n<i>{t(lang, 'trv_fx_disclaimer')}</i>"
    await callback.message.answer(text, reply_markup=travel_ai_kb("travel", "currency", lang))
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "trv:fx:cancel")
async def trv_fx_cancel(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.clear()
    lang = user.language
    await callback.message.answer(t(lang, "trv_module_intro"), reply_markup=travel_module_kb(lang))
    await callback.answer()
