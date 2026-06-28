from __future__ import annotations

from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import back_menu_kb
from app.bot.keyboards_ecosystem import alerts_list_kb, notifications_kb
from app.bot.states import NotificationsStates
from app.core.i18n import t
from app.models.entities import User
from app.services.date_parse import parse_date_flexible, parse_datetime_flexible
from app.services.finance_service import parse_amount
from app.services.notifications_service import (
    ADDABLE_ALERT_TYPES,
    DATE_ONLY_ALERT_TYPES,
    EVENT_ALERT_TYPES,
    add_alert_item,
    alert_type_def,
    delete_alert_item,
    format_alert_line,
    list_alert_items,
)

router = Router()


@router.callback_query(F.data == "ntf:menu")
async def ntf_menu(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    items = await list_alert_items(session, user.id)
    lines = [t(lang, "ntf_list_intro"), ""]
    if items:
        lines.extend(format_alert_line(item, lang) for item in items)
    else:
        lines.append(t(lang, "ntf_empty"))
    await callback.message.edit_text("\n".join(lines), reply_markup=alerts_list_kb(items, lang))
    await callback.answer()


@router.callback_query(F.data.startswith("ntf:add:"))
async def ntf_add_start(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = user.language
    alert_type = (callback.data or "").split(":")[2]
    if alert_type not in ADDABLE_ALERT_TYPES:
        await callback.answer(t(lang, "not_found"), show_alert=True)
        return
    await state.update_data(ntf_type=alert_type)
    await state.set_state(NotificationsStates.waiting_title)
    kind = alert_type_def(alert_type)
    await callback.message.answer(t(lang, kind.title_prompt_key), reply_markup=back_menu_kb(lang))
    await callback.answer()


@router.message(NotificationsStates.waiting_title)
async def ntf_title(message: Message, state: FSMContext, user: User) -> None:
    title = (message.text or "").strip()
    if len(title) < 2:
        await message.answer(t(user.language, "ntf_title_short"))
        return
    await state.update_data(ntf_title=title)
    await state.set_state(NotificationsStates.waiting_due)
    data = await state.get_data()
    alert_type = str(data.get("ntf_type") or "custom")
    prompt = "ntf_due_prompt" if alert_type in DATE_ONLY_ALERT_TYPES else "ntf_datetime_prompt"
    await message.answer(t(user.language, prompt), reply_markup=back_menu_kb(user.language))


@router.message(NotificationsStates.waiting_due)
async def ntf_due(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    data = await state.get_data()
    alert_type = str(data.get("ntf_type") or "custom")
    raw = message.text or ""
    if alert_type in DATE_ONLY_ALERT_TYPES:
        due = parse_date_flexible(raw)
    else:
        due = parse_datetime_flexible(raw)
    if not due:
        await message.answer(t(lang, "ntf_due_error"))
        return
    await state.update_data(ntf_due=due.isoformat())
    if alert_type_def(alert_type).needs_amount:
        await state.set_state(NotificationsStates.waiting_amount)
        await message.answer(t(lang, "ntf_amount_prompt"), reply_markup=back_menu_kb(lang))
        return
    if alert_type in EVENT_ALERT_TYPES:
        await state.set_state(NotificationsStates.waiting_notes)
        await message.answer(t(lang, "ntf_notes_prompt"), reply_markup=back_menu_kb(lang))
        return
    await _save_alert(message, state, user, session, amount=None, notes="")


@router.message(NotificationsStates.waiting_notes)
async def ntf_notes(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    raw = (message.text or "").strip()
    notes = "" if raw in ("-", "—") else raw
    await _save_alert(message, state, user, session, amount=None, notes=notes)


@router.message(NotificationsStates.waiting_amount)
async def ntf_amount(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    raw = (message.text or "").strip()
    amount = None if raw in ("-", "—") else parse_amount(raw)
    if raw not in ("-", "—") and amount is None:
        await message.answer(t(user.language, "ntf_amount_error"))
        return
    await _save_alert(message, state, user, session, amount=amount, notes="")


async def _save_alert(
    message: Message,
    state: FSMContext,
    user: User,
    session: AsyncSession,
    *,
    notes: str,
    amount: float | None,
) -> None:
    lang = user.language
    data = await state.get_data()
    due = datetime.fromisoformat(str(data["ntf_due"]))
    alert_type = str(data.get("ntf_type") or "custom")
    await add_alert_item(
        session,
        user_id=user.id,
        alert_type=alert_type,
        title=str(data.get("ntf_title") or ""),
        due_at=due,
        amount=amount,
        currency="UZS" if amount else None,
        notes=notes,
        profile_id=user.active_profile_id,
    )
    await message.answer(t(lang, "ntf_saved"), reply_markup=notifications_kb(lang))
    await state.clear()


@router.callback_query(F.data.startswith("ntf:del:"))
async def ntf_delete(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    item_id = int((callback.data or "").split(":")[2])
    ok = await delete_alert_item(session, user.id, item_id)
    if not ok:
        await callback.answer(t(lang, "fin_not_found"), show_alert=True)
        return
    await ntf_menu(callback, user, session)
