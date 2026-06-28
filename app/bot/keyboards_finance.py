from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.i18n import t
from app.core.modules.catalog import MODULE_BY_ID
from app.models.entities import FinanceGoal, CreditLoan
from app.services.finance_service import EXPENSE_CATEGORIES


def finance_module_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    mod = MODULE_BY_ID["finance"]
    rows = [
        [InlineKeyboardButton(text=sub.title(lang), callback_data=f"sub:finance:{sub.id}")]
        for sub in mod.submodules
    ]
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def finance_tx_kb(tx_type: str, lang: str = "ru") -> InlineKeyboardMarkup:
    add_cb = "fin:inc:add" if tx_type == "income" else "fin:exp:add"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "fin_add_tx"), callback_data=add_cb)],
            [InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:finance")],
        ]
    )


def finance_category_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=t(lang, f"fin_cat_{cat}"), callback_data=f"fin:cat:{cat}")]
        for cat in EXPENSE_CATEGORIES
    ]
    rows.append([InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="fin:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def finance_goals_kb(goals: list[FinanceGoal], lang: str = "ru") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=t(lang, "fin_goal_add"), callback_data="fin:goal:add")],
    ]
    for goal in goals[:10]:
        rows.append(
            [InlineKeyboardButton(text=f"🎯 {goal.title[:28]}", callback_data=f"fin:goal:open:{goal.id}")]
        )
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:finance")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def finance_goal_item_kb(goal_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "fin_goal_update"), callback_data=f"fin:goal:upd:{goal_id}")],
            [InlineKeyboardButton(text=t(lang, "fin_goal_delete"), callback_data=f"fin:goal:del:{goal_id}")],
            [InlineKeyboardButton(text=t(lang, "fin_back_goals"), callback_data="fin:goal:list")],
        ]
    )


def finance_budget_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=t(lang, f"fin_cat_{cat}"), callback_data=f"fin:budget:{cat}")]
        for cat in EXPENSE_CATEGORIES
    ]
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:finance")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def finance_bills_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "fin_bill_add"), callback_data="fin:bill:add")],
            [InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:finance")],
        ]
    )


def finance_bill_item_kb(bill_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "fin_bill_delete"), callback_data=f"fin:bill:del:{bill_id}")],
            [InlineKeyboardButton(text=t(lang, "fin_back_bills"), callback_data="fin:bill:list")],
        ]
    )


def finance_loans_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "btn_add_credit"), callback_data="fin:loan:add")],
            [InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:finance")],
        ]
    )


def finance_loans_list_kb(loans: list[CreditLoan], lang: str = "ru") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=t(lang, "btn_add_credit"), callback_data="fin:loan:add")],
    ]
    for loan in loans[:8]:
        rows.append(
            [InlineKeyboardButton(text=f"💳 {loan.title[:26]}", callback_data=f"fin:loan:open:{loan.id}")]
        )
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:finance")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def finance_loan_item_kb(loan_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    from app.services.credit_loans import credit_loan_item_kb

    return credit_loan_item_kb(loan_id, lang)


def finance_analysis_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "btn_ask_ai"), callback_data="ai:finance:analysis")],
            [InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:finance")],
        ]
    )


def finance_cancel_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="fin:cancel")]]
    )
