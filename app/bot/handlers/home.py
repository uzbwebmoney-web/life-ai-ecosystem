from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards_home import (
    home_cancel_kb,
    home_expenses_kb,
    home_inventory_item_kb,
    home_inventory_kb,
    home_module_kb,
    home_repair_item_kb,
    home_repair_kb,
    home_shopping_kb,
    home_utilities_kb,
    home_utility_item_kb,
)
from app.bot.states import HomeStates
from app.core.i18n import t
from app.models.entities import User
from app.services.home_service import (
    add_home_expense,
    add_home_utility,
    add_inventory_item,
    add_repair_task,
    add_shopping_item,
    cycle_repair_status,
    deactivate_home_utility,
    deactivate_inventory_item,
    deactivate_repair_task,
    deactivate_shopping_item,
    format_expense_line,
    format_inventory_line,
    format_repair_line,
    format_shopping_line,
    format_utility_line,
    home_expenses_total,
    home_submodule_description,
    list_home_expenses,
    list_home_utilities,
    list_inventory_items,
    list_repair_tasks,
    list_shopping_items,
    parse_amount,
    toggle_shopping_item,
)
from app.services.car_service import parse_date
from app.services.life_data import set_active_module

router = Router()


@router.callback_query(F.data == "mod:home")
async def home_module(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    await set_active_module(session, user, "home")
    await callback.message.edit_text(t(lang, "home_module_intro"), reply_markup=home_module_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("sub:home:"))
async def home_submodule(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    sub_id = (callback.data or "").split(":")[2]
    await set_active_module(session, user, "home", submodule_id=sub_id)
    if sub_id == "utilities":
        await _show_utilities(callback.message, user, session, lang, edit=True)
    elif sub_id == "expenses":
        await _show_expenses(callback.message, user, session, lang, edit=True)
    elif sub_id == "repair":
        await _show_repair(callback.message, user, session, lang, edit=True)
    elif sub_id == "shopping":
        await _show_shopping(callback.message, user, session, lang, edit=True)
    elif sub_id == "inventory":
        await _show_inventory(callback.message, user, session, lang, edit=True)
    await callback.answer()


async def _send(target, text: str, kb, edit: bool) -> None:
    if edit:
        await target.edit_text(text, reply_markup=kb)
    else:
        await target.answer(text, reply_markup=kb)


async def _show_utilities(target, user: User, session: AsyncSession, lang: str, *, edit: bool = False) -> None:
    bills = await list_home_utilities(session, user.id)
    lines = [t(lang, "home_utilities_title"), ""]
    if bills:
        lines.extend(format_utility_line(b) for b in bills)
    else:
        lines.append(t(lang, "home_empty"))
    await _send(target, "\n".join(lines), home_utilities_kb(bills, lang), edit)


async def _show_expenses(target, user: User, session: AsyncSession, lang: str, *, edit: bool = False) -> None:
    records = await list_home_expenses(session, user.id)
    total = await home_expenses_total(session, user.id)
    lines = [t(lang, "home_expenses_title"), "", t(lang, "home_total", total=int(total)), ""]
    if records:
        lines.extend(format_expense_line(r) for r in records[:10])
    else:
        lines.append(t(lang, "home_empty"))
    await _send(target, "\n".join(lines), home_expenses_kb(lang), edit)


async def _show_repair(target, user: User, session: AsyncSession, lang: str, *, edit: bool = False) -> None:
    tasks = await list_repair_tasks(session, user.id)
    lines = [t(lang, "home_repair_title"), ""]
    desc = home_submodule_description("repair", lang)
    if desc:
        lines.append(desc)
        lines.append("")
    if tasks:
        lines.extend(format_repair_line(task, lang) for task in tasks)
    else:
        lines.append(t(lang, "home_empty"))
    await _send(target, "\n".join(lines), home_repair_kb(tasks, lang), edit)


async def _show_shopping(target, user: User, session: AsyncSession, lang: str, *, edit: bool = False) -> None:
    items = await list_shopping_items(session, user.id)
    lines = [t(lang, "home_shopping_title"), ""]
    if items:
        lines.extend(format_shopping_line(i) for i in items)
    else:
        lines.append(t(lang, "home_empty"))
    await _send(target, "\n".join(lines), home_shopping_kb(items, lang), edit)


async def _show_inventory(target, user: User, session: AsyncSession, lang: str, *, edit: bool = False) -> None:
    items = await list_inventory_items(session, user.id)
    lines = [t(lang, "home_inventory_title"), ""]
    if items:
        lines.extend(format_inventory_line(i, lang) for i in items)
    else:
        lines.append(t(lang, "home_empty"))
    await _send(target, "\n".join(lines), home_inventory_kb(items, lang), edit)


@router.callback_query(F.data == "home:util:add")
async def home_util_add(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.set_state(HomeStates.waiting_utility_title)
    await callback.message.answer(t(user.language, "home_utility_title_prompt"), reply_markup=home_cancel_kb(user.language))
    await callback.answer()


@router.message(HomeStates.waiting_utility_title)
async def home_util_title(message: Message, state: FSMContext, user: User) -> None:
    await state.update_data(home_utility_title=(message.text or "").strip())
    await state.set_state(HomeStates.waiting_utility_amount)
    await message.answer(t(user.language, "home_utility_amount_prompt"), reply_markup=home_cancel_kb(user.language))


@router.message(HomeStates.waiting_utility_amount)
async def home_util_amount(message: Message, state: FSMContext, user: User) -> None:
    amount = parse_amount(message.text or "")
    if amount is None:
        await message.answer(t(user.language, "record_amount_error"))
        return
    await state.update_data(home_utility_amount=amount)
    await state.set_state(HomeStates.waiting_utility_date)
    await message.answer(t(user.language, "home_utility_date_prompt"), reply_markup=home_cancel_kb(user.language))


@router.message(HomeStates.waiting_utility_date)
async def home_util_save(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    due = parse_date(message.text or "")
    if not due:
        await message.answer(t(lang, "car_date_error"))
        return
    data = await state.get_data()
    await add_home_utility(
        session,
        user_id=user.id,
        title=str(data.get("home_utility_title") or t(lang, "home_utility_default")),
        amount=float(data.get("home_utility_amount") or 0),
        due_at=due,
        profile_id=user.active_profile_id,
    )
    await message.answer(t(lang, "home_utility_saved"))
    await _show_utilities(message, user, session, lang)
    await state.clear()


@router.callback_query(F.data == "home:util:list")
async def home_util_list(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    await _show_utilities(callback.message, user, session, user.language, edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("home:util:open:"))
async def home_util_open(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    bill_id = int((callback.data or "").split(":")[3])
    bills = await list_home_utilities(session, user.id)
    bill = next((b for b in bills if b.id == bill_id), None)
    if not bill:
        await callback.answer(t(lang, "home_not_found"), show_alert=True)
        return
    await callback.message.edit_text(format_utility_line(bill), reply_markup=home_utility_item_kb(bill_id, lang))
    await callback.answer()


@router.callback_query(F.data.startswith("home:util:del:"))
async def home_util_del(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    bill_id = int((callback.data or "").split(":")[3])
    ok = await deactivate_home_utility(session, user.id, bill_id)
    if not ok:
        await callback.answer(t(lang, "home_not_found"), show_alert=True)
        return
    await _show_utilities(callback.message, user, session, lang, edit=True)
    await callback.answer(t(lang, "home_deleted"))


@router.callback_query(F.data == "home:exp:add")
async def home_exp_add(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.set_state(HomeStates.waiting_expense_title)
    await callback.message.answer(t(user.language, "home_expense_title_prompt"), reply_markup=home_cancel_kb(user.language))
    await callback.answer()


@router.message(HomeStates.waiting_expense_title)
async def home_exp_title(message: Message, state: FSMContext, user: User) -> None:
    await state.update_data(home_expense_title=(message.text or "").strip())
    await state.set_state(HomeStates.waiting_expense_amount)
    await message.answer(t(user.language, "home_expense_amount_prompt"), reply_markup=home_cancel_kb(user.language))


@router.message(HomeStates.waiting_expense_amount)
async def home_exp_save(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    amount = parse_amount(message.text or "")
    if amount is None:
        await message.answer(t(lang, "record_amount_error"))
        return
    data = await state.get_data()
    await add_home_expense(
        session,
        user_id=user.id,
        title=str(data.get("home_expense_title") or t(lang, "home_expense_default")),
        amount=amount,
        profile_id=user.active_profile_id,
    )
    await message.answer(t(lang, "home_expense_saved"))
    await _show_expenses(message, user, session, lang)
    await state.clear()


@router.callback_query(F.data == "home:repair:add")
async def home_repair_add(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.set_state(HomeStates.waiting_repair_title)
    await callback.message.answer(t(user.language, "home_repair_title_prompt"), reply_markup=home_cancel_kb(user.language))
    await callback.answer()


@router.message(HomeStates.waiting_repair_title)
async def home_repair_title_msg(message: Message, state: FSMContext, user: User) -> None:
    await state.update_data(home_repair_title=(message.text or "").strip())
    await state.set_state(HomeStates.waiting_repair_notes)
    await message.answer(t(user.language, "home_repair_notes_prompt"), reply_markup=home_cancel_kb(user.language))


@router.message(HomeStates.waiting_repair_notes)
async def home_repair_save(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    data = await state.get_data()
    notes = (message.text or "").strip()
    if notes == "-":
        notes = ""
    await add_repair_task(
        session,
        user_id=user.id,
        title=str(data.get("home_repair_title") or t(lang, "home_repair_default")),
        notes=notes,
        profile_id=user.active_profile_id,
    )
    await message.answer(t(lang, "home_repair_saved"))
    await _show_repair(message, user, session, lang)
    await state.clear()


@router.callback_query(F.data == "home:repair:list")
async def home_repair_list(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    await _show_repair(callback.message, user, session, user.language, edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("home:repair:open:"))
async def home_repair_open(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    task_id = int((callback.data or "").split(":")[3])
    tasks = await list_repair_tasks(session, user.id)
    task = next((x for x in tasks if x.id == task_id), None)
    if not task:
        await callback.answer(t(lang, "home_not_found"), show_alert=True)
        return
    await callback.message.edit_text(format_repair_line(task, lang), reply_markup=home_repair_item_kb(task_id, lang))
    await callback.answer()


@router.callback_query(F.data.startswith("home:repair:status:"))
async def home_repair_status(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    task_id = int((callback.data or "").split(":")[3])
    task = await cycle_repair_status(session, user.id, task_id)
    if not task:
        await callback.answer(t(lang, "home_not_found"), show_alert=True)
        return
    await _show_repair(callback.message, user, session, lang, edit=True)
    await callback.answer(t(lang, "home_repair_updated"))


@router.callback_query(F.data.startswith("home:repair:del:"))
async def home_repair_del(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    task_id = int((callback.data or "").split(":")[3])
    ok = await deactivate_repair_task(session, user.id, task_id)
    if not ok:
        await callback.answer(t(lang, "home_not_found"), show_alert=True)
        return
    await _show_repair(callback.message, user, session, lang, edit=True)
    await callback.answer(t(lang, "home_deleted"))


@router.callback_query(F.data == "home:shop:add")
async def home_shop_add(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.set_state(HomeStates.waiting_shopping_title)
    await callback.message.answer(t(user.language, "home_shopping_title_prompt"), reply_markup=home_cancel_kb(user.language))
    await callback.answer()


@router.message(HomeStates.waiting_shopping_title)
async def home_shop_save(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    await add_shopping_item(
        session,
        user_id=user.id,
        title=(message.text or "").strip()[:255],
        profile_id=user.active_profile_id,
    )
    await message.answer(t(lang, "home_shopping_saved"))
    await _show_shopping(message, user, session, lang)
    await state.clear()


@router.callback_query(F.data.startswith("home:shop:toggle:"))
async def home_shop_toggle(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    item_id = int((callback.data or "").split(":")[3])
    item = await toggle_shopping_item(session, user.id, item_id)
    if not item:
        await callback.answer(t(lang, "home_not_found"), show_alert=True)
        return
    await _show_shopping(callback.message, user, session, lang, edit=True)
    await callback.answer()


@router.callback_query(F.data == "home:inv:add")
async def home_inv_add(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.set_state(HomeStates.waiting_inventory_title)
    await callback.message.answer(t(user.language, "home_inventory_title_prompt"), reply_markup=home_cancel_kb(user.language))
    await callback.answer()


@router.message(HomeStates.waiting_inventory_title)
async def home_inv_title(message: Message, state: FSMContext, user: User) -> None:
    await state.update_data(home_inventory_title=(message.text or "").strip())
    await state.set_state(HomeStates.waiting_inventory_location)
    await message.answer(t(user.language, "home_inventory_location_prompt"), reply_markup=home_cancel_kb(user.language))


@router.message(HomeStates.waiting_inventory_location)
async def home_inv_location(message: Message, state: FSMContext, user: User) -> None:
    loc = (message.text or "").strip()
    await state.update_data(home_inventory_location="" if loc == "-" else loc)
    await state.set_state(HomeStates.waiting_inventory_qty)
    await message.answer(t(user.language, "home_inventory_qty_prompt"), reply_markup=home_cancel_kb(user.language))


@router.message(HomeStates.waiting_inventory_qty)
async def home_inv_save(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    data = await state.get_data()
    qty = (message.text or "1").strip() or "1"
    await add_inventory_item(
        session,
        user_id=user.id,
        title=str(data.get("home_inventory_title") or t(lang, "home_inventory_default")),
        location=str(data.get("home_inventory_location") or ""),
        quantity=qty,
        profile_id=user.active_profile_id,
    )
    await message.answer(t(lang, "home_inventory_saved"))
    await _show_inventory(message, user, session, lang)
    await state.clear()


@router.callback_query(F.data == "home:inv:list")
async def home_inv_list(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    await _show_inventory(callback.message, user, session, user.language, edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("home:inv:open:"))
async def home_inv_open(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    item_id = int((callback.data or "").split(":")[3])
    items = await list_inventory_items(session, user.id)
    item = next((x for x in items if x.id == item_id), None)
    if not item:
        await callback.answer(t(lang, "home_not_found"), show_alert=True)
        return
    await callback.message.edit_text(format_inventory_line(item, lang), reply_markup=home_inventory_item_kb(item_id, lang))
    await callback.answer()


@router.callback_query(F.data.startswith("home:inv:del:"))
async def home_inv_del(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    item_id = int((callback.data or "").split(":")[3])
    ok = await deactivate_inventory_item(session, user.id, item_id)
    if not ok:
        await callback.answer(t(lang, "home_not_found"), show_alert=True)
        return
    await _show_inventory(callback.message, user, session, lang, edit=True)
    await callback.answer(t(lang, "home_deleted"))


@router.callback_query(F.data == "home:cancel")
async def home_cancel(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.clear()
    await callback.message.answer(t(user.language, "home_module_intro"), reply_markup=home_module_kb(user.language))
    await callback.answer()
