from __future__ import annotations

from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.states import NotificationsStates
from app.core.i18n import t
from app.core.modules.catalog import MODULE_BY_ID
from app.models.entities import User
from app.services.life_data import set_active_module
from app.services.notifications_service import (
    add_alert_item,
    format_alert_line,
    list_alert_items,
)
from app.services.organizer_service import parse_datetime

router = Router()

_LINKS: dict[str, str] = {
    "medicine": "mod:health",
    "car_service": "mod:car",
    "utilities": "mod:home",
    "loans": "mod:finance",
}


def notifications_module_kb(lang: str) -> InlineKeyboardMarkup:
    mod = MODULE_BY_ID["notifications"]
    rows: list[list[InlineKeyboardButton]] = []
    for sub in mod.submodules:
        cb = _LINKS.get(sub.id, f"sub:notifications:{sub.id}")
        rows.append([InlineKeyboardButton(text=sub.title(lang), callback_data=cb)])
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def notifications_sub_kb(sub_id: str, lang: str) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=t(lang, "ntf_add"), callback_data=f"ntf:add:{sub_id}")],
    ]
    if sub_id in ("subscriptions", "visas"):
        rows.append([InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:notifications")])
    else:
        link = _LINKS.get(sub_id, "mod:notifications")
        rows.append([InlineKeyboardButton(text=t(lang, "ntf_open_module"), callback_data=link)])
        rows.append([InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:notifications")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def notifications_cancel_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="ntf:cancel")]]
    )


@router.callback_query(F.data == "mod:notifications")
async def notifications_module(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    await set_active_module(session, user, "notifications")
    await callback.message.edit_text(t(lang, "ntf_module_intro"), reply_markup=notifications_module_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("sub:notifications:"))
async def notifications_sub(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    sub_id = (callback.data or "").split(":")[2]
    mod = MODULE_BY_ID["notifications"]
    sub = next((s for s in mod.submodules if s.id == sub_id), None)
    if not sub:
        await callback.answer(t(lang, "not_found"), show_alert=True)
        return
    await set_active_module(session, user, "notifications", submodule_id=sub_id)
    alert_type = "subscription" if sub_id == "subscriptions" else "visa" if sub_id == "visas" else sub_id
    lines = [f"🔔 <b>{sub.title(lang)}</b>", "", t(lang, "ntf_sub_hint")]
    if sub_id in ("subscriptions", "visas"):
        items = await list_alert_items(session, user.id, alert_type=alert_type)
        if items:
            lines.append("")
            lines.extend(format_alert_line(i, lang) for i in items)
        else:
            lines.append("")
            lines.append(t(lang, "ntf_empty"))
    await callback.message.edit_text("\n".join(lines), reply_markup=notifications_sub_kb(sub_id, lang))
    await callback.answer()


@router.callback_query(F.data.startswith("ntf:add:"))
async def ntf_add_start(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = user.language
    sub_id = (callback.data or "").split(":")[2]
    if sub_id not in ("subscriptions", "visas"):
        await callback.answer(t(lang, "ntf_add_only_data"), show_alert=True)
        return
    alert_type = "subscription" if sub_id == "subscriptions" else "visa"
    await state.update_data(ntf_type=alert_type, ntf_sub=sub_id)
    await state.set_state(NotificationsStates.waiting_title)
    await callback.message.answer(t(lang, "ntf_title_prompt"), reply_markup=notifications_cancel_kb(lang))
    await callback.answer()


@router.message(NotificationsStates.waiting_title)
async def ntf_title(message: Message, state: FSMContext, user: User) -> None:
    lang = user.language
    title = (message.text or "").strip()
    if len(title) < 2:
        await message.answer(t(lang, "ntf_title_short"))
        return
    await state.update_data(ntf_title=title)
    await state.set_state(NotificationsStates.waiting_due)
    await message.answer(t(lang, "ntf_due_prompt"), reply_markup=notifications_cancel_kb(lang))


@router.message(NotificationsStates.waiting_due)
async def ntf_due(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    due = parse_datetime((message.text or "").strip())
    if not due:
        await message.answer(t(lang, "ntf_due_error"))
        return
    data = await state.get_data()
    alert_type = str(data.get("ntf_type") or "subscription")
    if alert_type == "subscription":
        await state.update_data(ntf_due=due.isoformat())
        await state.set_state(NotificationsStates.waiting_amount)
        await message.answer(t(lang, "ntf_amount_prompt"), reply_markup=notifications_cancel_kb(lang))
        return
    await _save_alert(message, state, user, session, due, amount=None)


@router.message(NotificationsStates.waiting_amount)
async def ntf_amount(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    raw = (message.text or "").strip()
    amount = None
    if raw not in ("-", ""):
        try:
            amount = float(raw.replace(",", "."))
        except ValueError:
            await message.answer(t(lang, "ntf_amount_error"))
            return
    data = await state.get_data()
    due = datetime.fromisoformat(str(data.get("ntf_due")))
    await _save_alert(message, state, user, session, due, amount=amount)


async def _save_alert(
    message: Message,
    state: FSMContext,
    user: User,
    session: AsyncSession,
    due: datetime,
    *,
    amount: float | None,
) -> None:
    lang = user.language
    data = await state.get_data()
    alert_type = str(data.get("ntf_type") or "subscription")
    title = str(data.get("ntf_title") or "Alert")
    await add_alert_item(
        session,
        user_id=user.id,
        alert_type=alert_type,
        title=title,
        due_at=due,
        amount=amount,
        currency="UZS" if amount else None,
        profile_id=user.active_profile_id,
    )
    await message.answer(t(lang, "ntf_saved"))
    await state.clear()


@router.callback_query(F.data == "ntf:cancel")
async def ntf_cancel(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.clear()
    await callback.message.answer(t(user.language, "ntf_module_intro"), reply_markup=notifications_module_kb(user.language))
    await callback.answer()
