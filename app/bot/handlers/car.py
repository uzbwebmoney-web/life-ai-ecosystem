from __future__ import annotations

from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards_car import (
    car_ai_kb,
    car_cancel_kb,
    car_compliance_kb,
    car_expenses_kb,
    car_maint_item_kb,
    car_maint_type_kb,
    car_module_kb,
    car_panel_kb,
    car_reminders_kb,
    car_service_kb,
)
from app.bot.states import CarStates
from app.core.i18n import t
from app.core.modules.catalog import MODULE_BY_ID
from app.models.entities import User
from app.services.car_service import (
    CAR_MODULE,
    add_car_compliance,
    add_car_maintenance,
    car_expense_total,
    car_submodule_description,
    deactivate_car_compliance,
    deactivate_car_maintenance,
    format_compliance_line,
    format_expense_line,
    format_maint_line,
    get_car_maintenance,
    list_car_compliance,
    list_car_expenses,
    list_car_maintenance,
    parse_date,
)
from app.services.life_data import add_record, set_active_module

router = Router()


@router.callback_query(F.data == "mod:car")
async def car_module(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    await set_active_module(session, user, "car")
    await callback.message.edit_text(t(lang, "car_module_intro"), reply_markup=car_module_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("sub:car:"))
async def car_submodule(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    sub_id = (callback.data or "").split(":")[2]
    mod = MODULE_BY_ID["car"]
    sub = next((s for s in mod.submodules if s.id == sub_id), None)
    if not sub:
        await callback.answer(t(lang, "not_found"), show_alert=True)
        return
    await set_active_module(session, user, "car", submodule_id=sub_id)

    if sub_id == "service":
        await _show_service(callback.message, user, session, lang, edit=True)
    elif sub_id == "reminders":
        await _show_reminders(callback.message, user, session, lang, edit=True)
    elif sub_id == "compliance":
        await _show_compliance(callback.message, user, session, lang, edit=True)
    elif sub_id == "expenses":
        await _show_expenses(callback.message, user, session, lang, edit=True)
    elif sub_id == "panel_photo":
        text = f"🚗 <b>{sub.title(lang)}</b>\n\n{t(lang, 'car_panel_hint')}"
        await callback.message.edit_text(text, reply_markup=car_panel_kb(lang))
    elif sub_id == "sounds":
        text = f"🚗 <b>{sub.title(lang)}</b>\n\n{t(lang, 'car_sounds_hint')}"
        await callback.message.edit_text(text, reply_markup=car_ai_kb(sub_id, lang))
    else:
        desc = car_submodule_description(sub_id, lang)
        text = f"🚗 <b>{mod.title(lang)}</b> → <b>{sub.title(lang)}</b>\n\n{desc}\n\n{t(lang, 'car_ai_hint')}"
        await callback.message.edit_text(text, reply_markup=car_ai_kb(sub_id, lang))
    await callback.answer()


async def _show_service(target, user: User, session: AsyncSession, lang: str, *, edit: bool = False) -> None:
    items = await list_car_maintenance(session, user.id)
    lines = [t(lang, "car_service_title"), ""]
    if items:
        lines.append(t(lang, "car_service_hint"))
        lines.append("")
        lines.extend(format_maint_line(i, lang) for i in items)
    else:
        lines.append(t(lang, "car_service_empty"))
    text = "\n".join(lines)
    kb = car_service_kb(items, lang)
    if edit:
        await target.edit_text(text, reply_markup=kb)
    else:
        await target.answer(text, reply_markup=kb)


async def _show_reminders(target, user: User, session: AsyncSession, lang: str, *, edit: bool = False) -> None:
    items = await list_car_maintenance(session, user.id)
    lines = [t(lang, "car_reminders_title"), ""]
    upcoming = [i for i in items if i.item_type in ("oil", "filter", "tires")]
    if upcoming:
        lines.extend(format_maint_line(i, lang) for i in upcoming)
    else:
        lines.append(t(lang, "car_reminders_empty"))
    text = "\n".join(lines)
    kb = car_reminders_kb(lang)
    if edit:
        await target.edit_text(text, reply_markup=kb)
    else:
        await target.answer(text, reply_markup=kb)


async def _show_compliance(target, user: User, session: AsyncSession, lang: str, *, edit: bool = False) -> None:
    rows = await list_car_compliance(session, user.id)
    lines = [t(lang, "car_comp_title"), ""]
    if rows:
        lines.extend(format_compliance_line(r, lang) for r in rows)
    else:
        lines.append(t(lang, "car_comp_empty"))
    text = "\n".join(lines)
    kb = car_compliance_kb(rows, lang)
    if edit:
        await target.edit_text(text, reply_markup=kb)
    else:
        await target.answer(text, reply_markup=kb)


async def _show_expenses(target, user: User, session: AsyncSession, lang: str, *, edit: bool = False) -> None:
    records = await list_car_expenses(session, user.id)
    total = await car_expense_total(session, user.id)
    lines = [t(lang, "car_expenses_title"), "", t(lang, "car_expenses_total", total=int(total)), ""]
    if records:
        lines.extend(format_expense_line(r, lang) for r in records)
    else:
        lines.append(t(lang, "car_expenses_empty"))
    text = "\n".join(lines)
    kb = car_expenses_kb(lang)
    if edit:
        await target.edit_text(text, reply_markup=kb)
    else:
        await target.answer(text, reply_markup=kb)


@router.callback_query(F.data == "car:service:list")
async def car_service_list(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    await _show_service(callback.message, user, session, user.language, edit=True)
    await callback.answer()


@router.callback_query(F.data == "car:maint:add")
async def car_maint_add(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.clear()
    await callback.message.answer(t(user.language, "car_maint_pick_type"), reply_markup=car_maint_type_kb(user.language))
    await callback.answer()


@router.callback_query(F.data.startswith("car:maint:quick:"))
async def car_maint_quick(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    item_type = (callback.data or "").split(":")[3]
    lang = user.language
    await state.update_data(car_maint_type=item_type, car_maint_title=t(lang, f"car_maint_{item_type}"))
    await state.set_state(CarStates.waiting_maint_date)
    await callback.message.answer(t(lang, "car_enter_date"), reply_markup=car_cancel_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("car:maint:type:"))
async def car_maint_type(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    item_type = (callback.data or "").split(":")[3]
    lang = user.language
    await state.update_data(car_maint_type=item_type, car_maint_title=t(lang, f"car_maint_{item_type}"))
    await state.set_state(CarStates.waiting_maint_date)
    await callback.message.answer(t(lang, "car_enter_date"), reply_markup=car_cancel_kb(lang))
    await callback.answer()


@router.message(CarStates.waiting_maint_date)
async def car_maint_date(message: Message, state: FSMContext, user: User) -> None:
    lang = user.language
    due = parse_date(message.text or "")
    if not due:
        await message.answer(t(lang, "car_date_error"))
        return
    await state.update_data(car_maint_due=due.isoformat())
    await state.set_state(CarStates.waiting_maint_notes)
    await message.answer(t(lang, "car_enter_notes"), reply_markup=car_cancel_kb(lang))


@router.message(CarStates.waiting_maint_notes)
async def car_maint_save(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    data = await state.get_data()
    notes = (message.text or "").strip()
    if notes == "-":
        notes = ""
    due = datetime.fromisoformat(str(data.get("car_maint_due")))
    item = await add_car_maintenance(
        session,
        user_id=user.id,
        item_type=str(data.get("car_maint_type") or "other"),
        title=str(data.get("car_maint_title") or t(lang, "car_maint_other")),
        due_at=due,
        notes=notes,
        profile_id=user.active_profile_id,
    )
    items = await list_car_maintenance(session, user.id)
    await message.answer(
        f"{t(lang, 'car_maint_saved')}\n\n{format_maint_line(item, lang)}",
        reply_markup=car_service_kb(items, lang),
    )
    await state.clear()


@router.callback_query(F.data.startswith("car:maint:open:"))
async def car_maint_open(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    item_id = int((callback.data or "").split(":")[3])
    item = await get_car_maintenance(session, user.id, item_id)
    if not item:
        await callback.answer(t(lang, "car_not_found"), show_alert=True)
        return
    await callback.message.edit_text(format_maint_line(item, lang), reply_markup=car_maint_item_kb(item_id, lang))
    await callback.answer()


@router.callback_query(F.data.startswith("car:maint:del:"))
async def car_maint_delete(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    item_id = int((callback.data or "").split(":")[3])
    ok = await deactivate_car_maintenance(session, user.id, item_id)
    if not ok:
        await callback.answer(t(lang, "car_not_found"), show_alert=True)
        return
    await _show_service(callback.message, user, session, lang, edit=True)
    await callback.answer(t(lang, "car_deleted"))


@router.callback_query(F.data.startswith("car:comp:add:"))
async def car_comp_add(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    comp_type = (callback.data or "").split(":")[3]
    lang = user.language
    await state.update_data(car_comp_type=comp_type, car_comp_title=t(lang, f"car_comp_{comp_type}"))
    await state.set_state(CarStates.waiting_compliance_date)
    await callback.message.answer(t(lang, "car_comp_enter_date"), reply_markup=car_cancel_kb(lang))
    await callback.answer()


@router.message(CarStates.waiting_compliance_date)
async def car_comp_save(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    expires = parse_date(message.text or "")
    if not expires:
        await message.answer(t(lang, "car_date_error"))
        return
    data = await state.get_data()
    row = await add_car_compliance(
        session,
        user_id=user.id,
        compliance_type=str(data.get("car_comp_type") or "insurance"),
        title=str(data.get("car_comp_title") or ""),
        expires_at=expires,
        profile_id=user.active_profile_id,
    )
    rows = await list_car_compliance(session, user.id)
    await message.answer(
        f"{t(lang, 'car_comp_saved')}\n\n{format_compliance_line(row, lang)}",
        reply_markup=car_compliance_kb(rows, lang),
    )
    await state.clear()


@router.callback_query(F.data.startswith("car:comp:del:"))
async def car_comp_delete(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    row_id = int((callback.data or "").split(":")[3])
    ok = await deactivate_car_compliance(session, user.id, row_id)
    if not ok:
        await callback.answer(t(lang, "car_not_found"), show_alert=True)
        return
    await _show_compliance(callback.message, user, session, lang, edit=True)
    await callback.answer(t(lang, "car_deleted"))


@router.callback_query(F.data == "car:exp:add")
async def car_exp_add(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.set_state(CarStates.waiting_expense_title)
    await callback.message.answer(t(user.language, "car_expense_title_prompt"), reply_markup=car_cancel_kb(user.language))
    await callback.answer()


@router.message(CarStates.waiting_expense_title)
async def car_exp_title(message: Message, state: FSMContext, user: User) -> None:
    title = (message.text or "").strip()
    if len(title) < 2:
        return
    await state.update_data(car_exp_title=title)
    await state.set_state(CarStates.waiting_expense_amount)
    await message.answer(t(user.language, "car_expense_amount_prompt"), reply_markup=car_cancel_kb(user.language))


@router.message(CarStates.waiting_expense_amount)
async def car_exp_amount(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    raw = (message.text or "").replace(" ", "").replace(",", ".").strip()
    try:
        amount = float(raw)
    except ValueError:
        await message.answer(t(lang, "record_amount_error"))
        return
    data = await state.get_data()
    title = str(data.get("car_exp_title") or t(lang, "car_expenses_title"))
    await add_record(
        session,
        user_id=user.id,
        module_id=CAR_MODULE,
        submodule_id="expenses",
        title=title,
        body=title,
        amount=amount,
        currency="UZS",
        profile_id=user.active_profile_id,
    )
    await _show_expenses(message, user, session, lang)
    await message.answer(t(lang, "car_expense_saved"))
    await state.clear()


@router.callback_query(F.data == "car:cancel")
async def car_cancel(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.clear()
    await callback.message.answer(t(user.language, "car_module_intro"), reply_markup=car_module_kb(user.language))
    await callback.answer()
