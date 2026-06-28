from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards_finance import (
    finance_analysis_kb,
    finance_bill_item_kb,
    finance_bills_kb,
    finance_budget_kb,
    finance_cancel_kb,
    finance_category_kb,
    finance_goal_item_kb,
    finance_goals_kb,
    finance_loan_item_kb,
    finance_loans_list_kb,
    finance_loans_kb,
    finance_module_kb,
    finance_tx_kb,
)
from app.bot.states import CreditStates, FinanceStates
from app.core.i18n import t
from app.models.entities import User
from app.services.credit_loans import (
    add_credit_loan,
    deactivate_credit_loan,
    format_amount,
    format_credit_loan_line,
    list_credit_loans,
)
from app.services.finance_service import (
    add_finance_bill,
    add_finance_goal,
    add_finance_transaction,
    current_month_key,
    deactivate_finance_bill,
    deactivate_finance_goal,
    expense_by_category,
    finance_total,
    format_bill_line,
    format_budget_line,
    format_goal_line,
    format_tx_line,
    list_finance_bills,
    list_finance_budgets,
    list_finance_goals,
    list_finance_transactions,
    parse_amount,
    parse_date,
    set_finance_budget,
)
from app.services.life_data import set_active_module

router = Router()


@router.callback_query(F.data == "mod:finance")
async def finance_module(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    await set_active_module(session, user, "finance")
    await callback.message.edit_text(t(lang, "fin_module_intro"), reply_markup=finance_module_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("sub:finance:"))
async def finance_submodule(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    sub_id = (callback.data or "").split(":")[2]
    await set_active_module(session, user, "finance", submodule_id=sub_id)

    if sub_id == "income":
        await _show_income(callback.message, user, session, lang, edit=True)
    elif sub_id == "expense":
        await _show_expense(callback.message, user, session, lang, edit=True)
    elif sub_id == "goals":
        await _show_goals(callback.message, user, session, lang, edit=True)
    elif sub_id == "budget":
        await _show_budget(callback.message, user, session, lang, edit=True)
    elif sub_id == "bills":
        await _show_bills(callback.message, user, session, lang, edit=True)
    elif sub_id == "loans":
        await _show_loans(callback.message, user, session, lang, edit=True)
    elif sub_id == "analysis":
        await _show_analysis(callback.message, user, session, lang, edit=True)
    await callback.answer()


async def _send(target, text: str, kb, edit: bool) -> None:
    if edit:
        await target.edit_text(text, reply_markup=kb)
    else:
        await target.answer(text, reply_markup=kb)


async def _show_income(target, user: User, session: AsyncSession, lang: str, *, edit: bool = False) -> None:
    records = await list_finance_transactions(session, user.id, "income")
    total = await finance_total(session, user.id, "income")
    lines = [t(lang, "fin_income_title"), "", t(lang, "fin_total", total=int(total)), ""]
    if records:
        lines.extend(format_tx_line(r, lang) for r in records[:10])
    else:
        lines.append(t(lang, "fin_empty"))
    await _send(target, "\n".join(lines), finance_tx_kb("income", lang), edit)


async def _show_expense(target, user: User, session: AsyncSession, lang: str, *, edit: bool = False) -> None:
    records = await list_finance_transactions(session, user.id, "expense")
    total = await finance_total(session, user.id, "expense")
    lines = [t(lang, "fin_expense_title"), "", t(lang, "fin_total", total=int(total)), ""]
    if records:
        lines.extend(format_tx_line(r, lang) for r in records[:10])
    else:
        lines.append(t(lang, "fin_empty"))
    await _send(target, "\n".join(lines), finance_tx_kb("expense", lang), edit)


async def _show_goals(target, user: User, session: AsyncSession, lang: str, *, edit: bool = False) -> None:
    goals = await list_finance_goals(session, user.id)
    lines = [t(lang, "fin_goals_title"), ""]
    if goals:
        lines.extend(format_goal_line(g, lang) for g in goals)
    else:
        lines.append(t(lang, "fin_goals_empty"))
    await _send(target, "\n".join(lines), finance_goals_kb(goals, lang), edit)


async def _show_budget(target, user: User, session: AsyncSession, lang: str, *, edit: bool = False) -> None:
    mk = current_month_key()
    budgets = await list_finance_budgets(session, user.id, month_key=mk)
    spent_map = await expense_by_category(session, user.id, month_key=mk)
    lines = [t(lang, "fin_budget_title"), "", t(lang, "fin_budget_month", month=mk), ""]
    if budgets:
        for b in budgets:
            lines.append(format_budget_line(b, spent_map.get(b.category, 0), lang))
    else:
        lines.append(t(lang, "fin_budget_empty"))
    lines.append(f"\n{t(lang, 'fin_budget_hint')}")
    await _send(target, "\n".join(lines), finance_budget_kb(lang), edit)


async def _show_bills(target, user: User, session: AsyncSession, lang: str, *, edit: bool = False) -> None:
    bills = await list_finance_bills(session, user.id)
    lines = [t(lang, "fin_bills_title"), ""]
    if bills:
        lines.extend(format_bill_line(b, lang) for b in bills)
    else:
        lines.append(t(lang, "fin_bills_empty"))
    kb = finance_bills_kb(lang)
    if bills:
        rows: list[list[InlineKeyboardButton]] = [
            [InlineKeyboardButton(text=t(lang, "fin_bill_add"), callback_data="fin:bill:add")]
        ]
        for b in bills[:8]:
            rows.append([InlineKeyboardButton(text=f"💳 {b.title[:26]}", callback_data=f"fin:bill:open:{b.id}")])
        rows.append([InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:finance")])
        kb = InlineKeyboardMarkup(inline_keyboard=rows)
    await _send(target, "\n".join(lines), kb, edit)


async def _show_loans(target, user: User, session: AsyncSession, lang: str, *, edit: bool = False) -> None:
    loans = await list_credit_loans(session, user.id)
    lines = [t(lang, "credits_title"), ""]
    if loans:
        lines.extend(format_credit_loan_line(loan, lang) for loan in loans)
    else:
        lines.append(t(lang, "credits_empty"))
        lines.append("")
        lines.append(t(lang, "credits_hint"))
    lines.append(f"\n{t(lang, 'credits_notify')}")
    kb = finance_loans_list_kb(loans, lang) if loans else finance_loans_kb(lang)
    await _send(target, "\n".join(lines), kb, edit)


async def _show_analysis(target, user: User, session: AsyncSession, lang: str, *, edit: bool = False) -> None:
    mk = current_month_key()
    cats = await expense_by_category(session, user.id, month_key=mk)
    income = await finance_total(session, user.id, "income")
    expense = sum(cats.values())
    lines = [
        t(lang, "fin_analysis_title"),
        "",
        t(lang, "fin_analysis_summary", month=mk, income=int(income), expense=int(expense), balance=int(income - expense)),
        "",
        t(lang, "fin_analysis_by_cat"),
    ]
    for cat, amount in sorted(cats.items(), key=lambda x: -x[1]):
        if amount > 0:
            lines.append(f"• {t(lang, f'fin_cat_{cat}')}: <b>{format_amount(amount)}</b>")
    if expense == 0:
        lines.append(t(lang, "fin_empty"))
    await _send(target, "\n".join(lines), finance_analysis_kb(lang), edit)


@router.callback_query(F.data == "fin:inc:add")
async def fin_inc_add(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.update_data(fin_tx_type="income")
    await state.set_state(FinanceStates.waiting_tx_title)
    await callback.message.answer(t(user.language, "fin_tx_title_prompt"), reply_markup=finance_cancel_kb(user.language))
    await callback.answer()


@router.callback_query(F.data == "fin:exp:add")
async def fin_exp_add(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.update_data(fin_tx_type="expense")
    await callback.message.answer(t(user.language, "fin_pick_category"), reply_markup=finance_category_kb(user.language))
    await callback.answer()


@router.callback_query(F.data.startswith("fin:cat:"))
async def fin_exp_category(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    cat = (callback.data or "").split(":")[2]
    await state.update_data(fin_tx_type="expense", fin_category=cat)
    await state.set_state(FinanceStates.waiting_tx_title)
    await callback.message.answer(t(user.language, "fin_tx_title_prompt"), reply_markup=finance_cancel_kb(user.language))
    await callback.answer()


@router.message(FinanceStates.waiting_tx_title)
async def fin_tx_title(message: Message, state: FSMContext, user: User) -> None:
    title = (message.text or "").strip()
    if len(title) < 2:
        return
    await state.update_data(fin_tx_title=title)
    await state.set_state(FinanceStates.waiting_tx_amount)
    await message.answer(t(user.language, "fin_tx_amount_prompt"), reply_markup=finance_cancel_kb(user.language))


@router.message(FinanceStates.waiting_tx_amount)
async def fin_tx_amount(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    amount = parse_amount(message.text or "")
    if amount is None:
        await message.answer(t(lang, "record_amount_error"))
        return
    data = await state.get_data()
    tx_type = str(data.get("fin_tx_type") or "expense")
    await add_finance_transaction(
        session,
        user_id=user.id,
        tx_type=tx_type,
        title=str(data.get("fin_tx_title") or ""),
        amount=amount,
        category=str(data.get("fin_category") or "other"),
        profile_id=user.active_profile_id,
    )
    await message.answer(t(lang, "fin_tx_saved"))
    if tx_type == "income":
        await _show_income(message, user, session, lang)
    else:
        await _show_expense(message, user, session, lang)
    await state.clear()


@router.callback_query(F.data == "fin:goal:add")
async def fin_goal_add(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.set_state(FinanceStates.waiting_goal_title)
    await callback.message.answer(t(user.language, "fin_goal_title_prompt"), reply_markup=finance_cancel_kb(user.language))
    await callback.answer()


@router.message(FinanceStates.waiting_goal_title)
async def fin_goal_title_msg(message: Message, state: FSMContext, user: User) -> None:
    await state.update_data(fin_goal_title=(message.text or "").strip())
    await state.set_state(FinanceStates.waiting_goal_target)
    await message.answer(t(user.language, "fin_goal_target_prompt"), reply_markup=finance_cancel_kb(user.language))


@router.message(FinanceStates.waiting_goal_target)
async def fin_goal_target_msg(message: Message, state: FSMContext, user: User) -> None:
    amount = parse_amount(message.text or "")
    if amount is None:
        await message.answer(t(user.language, "record_amount_error"))
        return
    await state.update_data(fin_goal_target=amount)
    await state.set_state(FinanceStates.waiting_goal_current)
    await message.answer(t(user.language, "fin_goal_current_prompt"), reply_markup=finance_cancel_kb(user.language))


@router.message(FinanceStates.waiting_goal_current)
async def fin_goal_save(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    data = await state.get_data()
    if data.get("fin_goal_id"):
        from app.services.finance_service import update_goal_progress

        goal = await update_goal_progress(session, user.id, int(data["fin_goal_id"]), parse_amount(message.text or "0") or 0)
        if goal:
            await message.answer(t(lang, "fin_goal_updated"))
        await state.clear()
        await _show_goals(message, user, session, lang)
        return
    raw = (message.text or "0").strip()
    current = parse_amount(raw) if raw not in ("0", "-") else 0.0
    await add_finance_goal(
        session,
        user_id=user.id,
        title=str(data.get("fin_goal_title") or t(lang, "fin_goal_default")),
        target_amount=float(data.get("fin_goal_target") or 0),
        current_amount=float(current or 0),
        profile_id=user.active_profile_id,
    )
    await message.answer(t(lang, "fin_goal_saved"))
    await _show_goals(message, user, session, lang)
    await state.clear()


@router.callback_query(F.data == "fin:goal:list")
async def fin_goal_list(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    await _show_goals(callback.message, user, session, user.language, edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("fin:goal:open:"))
async def fin_goal_open(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    goal_id = int((callback.data or "").split(":")[3])
    goals = await list_finance_goals(session, user.id)
    goal = next((g for g in goals if g.id == goal_id), None)
    if not goal:
        await callback.answer(t(lang, "fin_not_found"), show_alert=True)
        return
    await callback.message.edit_text(format_goal_line(goal, lang), reply_markup=finance_goal_item_kb(goal_id, lang))
    await callback.answer()


@router.callback_query(F.data.startswith("fin:goal:upd:"))
async def fin_goal_update_start(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    goal_id = int((callback.data or "").split(":")[3])
    await state.update_data(fin_goal_id=goal_id)
    await state.set_state(FinanceStates.waiting_goal_current)
    await callback.message.answer(t(user.language, "fin_goal_update_prompt"), reply_markup=finance_cancel_kb(user.language))
    await callback.answer()


@router.callback_query(F.data.startswith("fin:goal:del:"))
async def fin_goal_delete(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    goal_id = int((callback.data or "").split(":")[3])
    ok = await deactivate_finance_goal(session, user.id, goal_id)
    if not ok:
        await callback.answer(t(lang, "fin_not_found"), show_alert=True)
        return
    await _show_goals(callback.message, user, session, lang, edit=True)
    await callback.answer(t(lang, "fin_deleted"))


@router.callback_query(F.data.startswith("fin:budget:"))
async def fin_budget_set(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    cat = (callback.data or "").split(":")[2]
    await state.update_data(fin_budget_cat=cat)
    await state.set_state(FinanceStates.waiting_budget_limit)
    await callback.message.answer(
        t(user.language, "fin_budget_limit_prompt", category=t(user.language, f"fin_cat_{cat}")),
        reply_markup=finance_cancel_kb(user.language),
    )
    await callback.answer()


@router.message(FinanceStates.waiting_budget_limit)
async def fin_budget_save(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    limit = parse_amount(message.text or "")
    if limit is None:
        await message.answer(t(lang, "record_amount_error"))
        return
    data = await state.get_data()
    await set_finance_budget(
        session,
        user_id=user.id,
        category=str(data.get("fin_budget_cat") or "other"),
        limit_amount=limit,
        profile_id=user.active_profile_id,
    )
    await message.answer(t(lang, "fin_budget_saved"))
    await _show_budget(message, user, session, lang)
    await state.clear()


@router.callback_query(F.data == "fin:bill:add")
async def fin_bill_add(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.set_state(FinanceStates.waiting_bill_title)
    await callback.message.answer(t(user.language, "fin_bill_title_prompt"), reply_markup=finance_cancel_kb(user.language))
    await callback.answer()


@router.message(FinanceStates.waiting_bill_title)
async def fin_bill_title_msg(message: Message, state: FSMContext, user: User) -> None:
    await state.update_data(fin_bill_title=(message.text or "").strip())
    await state.set_state(FinanceStates.waiting_bill_amount)
    await message.answer(t(user.language, "fin_bill_amount_prompt"), reply_markup=finance_cancel_kb(user.language))


@router.message(FinanceStates.waiting_bill_amount)
async def fin_bill_amount_msg(message: Message, state: FSMContext, user: User) -> None:
    amount = parse_amount(message.text or "")
    if amount is None:
        await message.answer(t(user.language, "record_amount_error"))
        return
    await state.update_data(fin_bill_amount=amount)
    await state.set_state(FinanceStates.waiting_bill_date)
    await message.answer(t(user.language, "fin_bill_date_prompt"), reply_markup=finance_cancel_kb(user.language))


@router.message(FinanceStates.waiting_bill_date)
async def fin_bill_save(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    due = parse_date(message.text or "")
    if not due:
        await message.answer(t(lang, "car_date_error"))
        return
    data = await state.get_data()
    await add_finance_bill(
        session,
        user_id=user.id,
        title=str(data.get("fin_bill_title") or t(lang, "fin_bill_default")),
        amount=float(data.get("fin_bill_amount") or 0),
        due_at=due,
        profile_id=user.active_profile_id,
    )
    await message.answer(t(lang, "fin_bill_saved"))
    await _show_bills(message, user, session, lang)
    await state.clear()


@router.callback_query(F.data == "fin:bill:list")
async def fin_bill_list(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    await _show_bills(callback.message, user, session, user.language, edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("fin:bill:open:"))
async def fin_bill_open(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    bill_id = int((callback.data or "").split(":")[3])
    bills = await list_finance_bills(session, user.id)
    bill = next((b for b in bills if b.id == bill_id), None)
    if not bill:
        await callback.answer(t(lang, "fin_not_found"), show_alert=True)
        return
    await callback.message.edit_text(format_bill_line(bill, lang), reply_markup=finance_bill_item_kb(bill_id, lang))
    await callback.answer()


@router.callback_query(F.data.startswith("fin:bill:del:"))
async def fin_bill_delete(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    bill_id = int((callback.data or "").split(":")[3])
    ok = await deactivate_finance_bill(session, user.id, bill_id)
    if not ok:
        await callback.answer(t(lang, "fin_not_found"), show_alert=True)
        return
    await _show_bills(callback.message, user, session, lang, edit=True)
    await callback.answer(t(lang, "fin_deleted"))


@router.callback_query(F.data == "fin:loan:add")
async def fin_loan_add(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.set_state(CreditStates.waiting_title)
    await callback.message.answer(t(user.language, "credits_new"), reply_markup=finance_cancel_kb(user.language))
    await callback.answer()


@router.message(CreditStates.waiting_title)
async def fin_loan_title_msg(message: Message, state: FSMContext, user: User) -> None:
    lang = user.language
    title = (message.text or "").strip()
    if len(title) < 2:
        await message.answer(t(lang, "credits_title_short"))
        return
    await state.update_data(credit_title=title)
    await state.set_state(CreditStates.waiting_total)
    await message.answer(t(lang, "credits_total"), reply_markup=finance_cancel_kb(lang))


@router.message(CreditStates.waiting_total)
async def fin_loan_total_msg(message: Message, state: FSMContext, user: User) -> None:
    lang = user.language
    amount = parse_amount(message.text or "")
    if amount is None:
        await message.answer(t(lang, "credits_total_error"))
        return
    if amount <= 0:
        await message.answer(t(lang, "credits_total_positive"))
        return
    await state.update_data(credit_total=amount)
    await state.set_state(CreditStates.waiting_monthly)
    await message.answer(t(lang, "credits_monthly"), reply_markup=finance_cancel_kb(lang))


@router.message(CreditStates.waiting_monthly)
async def fin_loan_monthly_msg(message: Message, state: FSMContext, user: User) -> None:
    lang = user.language
    amount = parse_amount(message.text or "")
    if amount is None:
        await message.answer(t(lang, "credits_monthly_error"))
        return
    if amount <= 0:
        await message.answer(t(lang, "credits_total_positive"))
        return
    await state.update_data(credit_monthly=amount)
    await state.set_state(CreditStates.waiting_day)
    await message.answer(t(lang, "credits_day"), reply_markup=finance_cancel_kb(lang))


@router.message(CreditStates.waiting_day)
async def fin_loan_save(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
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
    info = format_credit_loan_line(loan, lang)
    await message.answer(t(lang, "credits_saved", info=info, day=loan.payment_day))
    await _show_loans(message, user, session, lang)
    await state.clear()


@router.callback_query(F.data == "fin:loan:list")
async def fin_loan_list(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    await _show_loans(callback.message, user, session, user.language, edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("fin:loan:open:"))
async def fin_loan_open(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    loan_id = int((callback.data or "").split(":")[3])
    loans = await list_credit_loans(session, user.id)
    loan = next((item for item in loans if item.id == loan_id), None)
    if not loan:
        await callback.answer(t(lang, "credits_not_found"), show_alert=True)
        return
    await callback.message.edit_text(format_credit_loan_line(loan, lang), reply_markup=finance_loan_item_kb(loan_id, lang))
    await callback.answer()


@router.callback_query(F.data.startswith("fin:loan:del:"))
async def fin_loan_delete(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    loan_id = int((callback.data or "").split(":")[3])
    ok = await deactivate_credit_loan(session, user.id, loan_id)
    if not ok:
        await callback.answer(t(lang, "credits_not_found"), show_alert=True)
        return
    await _show_loans(callback.message, user, session, lang, edit=True)
    await callback.answer(t(lang, "credits_removed"))


@router.callback_query(F.data == "fin:cancel")
async def fin_cancel(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.clear()
    await callback.message.answer(t(user.language, "fin_module_intro"), reply_markup=finance_module_kb(user.language))
    await callback.answer()
