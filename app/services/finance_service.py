from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.i18n import t
from app.models.entities import FinanceBill, FinanceBudget, FinanceGoal, LifeRecord, User
from app.services.car_service import parse_date
from app.services.credit_loans import format_amount
from app.services.health_service import user_local_now
from app.services.life_data import add_record

FINANCE_MODULE = "finance"
EXPENSE_CATEGORIES = ("food", "transport", "home", "health", "fun", "shopping", "bills", "other")


def current_month_key(dt: datetime | None = None) -> str:
    dt = dt or datetime.utcnow()
    return dt.strftime("%Y-%m")


def _date_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


def parse_amount(raw: str) -> float | None:
    try:
        val = float(raw.replace(" ", "").replace(",", ".").strip())
        return val if val > 0 else None
    except ValueError:
        return None


def category_from_record(record: LifeRecord) -> str:
    if not record.meta_json:
        return "other"
    try:
        data = json.loads(record.meta_json)
        cat = str(data.get("category") or "other")
        return cat if cat in EXPENSE_CATEGORIES else "other"
    except json.JSONDecodeError:
        return "other"


async def add_finance_transaction(
    session: AsyncSession,
    *,
    user_id: int,
    tx_type: str,
    title: str,
    amount: float,
    category: str | None = None,
    profile_id: int | None = None,
) -> LifeRecord:
    meta = json.dumps({"category": category or "other"}, ensure_ascii=False) if tx_type == "expense" else None
    return await add_record(
        session,
        user_id=user_id,
        module_id=FINANCE_MODULE,
        submodule_id=tx_type,
        title=title.strip()[:255],
        body=title,
        amount=amount,
        currency="UZS",
        profile_id=profile_id,
        meta_json=meta,
    )


async def list_finance_transactions(
    session: AsyncSession,
    user_id: int,
    tx_type: str,
    *,
    limit: int = 15,
) -> list[LifeRecord]:
    rows = (
        await session.execute(
            select(LifeRecord)
            .where(
                LifeRecord.user_id == user_id,
                LifeRecord.module_id == FINANCE_MODULE,
                LifeRecord.submodule_id == tx_type,
            )
            .order_by(LifeRecord.created_at.desc())
            .limit(limit)
        )
    ).scalars().all()
    return list(rows)


async def finance_total(session: AsyncSession, user_id: int, tx_type: str) -> float:
    total = (
        await session.execute(
            select(func.coalesce(func.sum(LifeRecord.amount), 0.0)).where(
                LifeRecord.user_id == user_id,
                LifeRecord.module_id == FINANCE_MODULE,
                LifeRecord.submodule_id == tx_type,
            )
        )
    ).scalar_one()
    return float(total or 0)


async def expense_by_category(session: AsyncSession, user_id: int, *, month_key: str | None = None) -> dict[str, float]:
    month_key = month_key or current_month_key()
    rows = (
        await session.execute(
            select(LifeRecord).where(
                LifeRecord.user_id == user_id,
                LifeRecord.module_id == FINANCE_MODULE,
                LifeRecord.submodule_id == "expense",
            )
        )
    ).scalars().all()
    totals: dict[str, float] = {c: 0.0 for c in EXPENSE_CATEGORIES}
    for row in rows:
        if row.created_at.strftime("%Y-%m") != month_key:
            continue
        cat = category_from_record(row)
        totals[cat] += float(row.amount or 0)
    return totals


async def add_finance_goal(
    session: AsyncSession,
    *,
    user_id: int,
    title: str,
    target_amount: float,
    current_amount: float = 0.0,
    due_at: datetime | None = None,
    profile_id: int | None = None,
) -> FinanceGoal:
    goal = FinanceGoal(
        user_id=user_id,
        profile_id=profile_id,
        title=title.strip()[:255],
        target_amount=float(target_amount),
        current_amount=float(current_amount),
        due_at=due_at,
    )
    session.add(goal)
    await session.commit()
    await session.refresh(goal)
    return goal


async def list_finance_goals(session: AsyncSession, user_id: int) -> list[FinanceGoal]:
    rows = (
        await session.execute(
            select(FinanceGoal)
            .where(FinanceGoal.user_id == user_id, FinanceGoal.active.is_(True))
            .order_by(FinanceGoal.id.asc())
        )
    ).scalars().all()
    return list(rows)


async def update_goal_progress(session: AsyncSession, user_id: int, goal_id: int, current_amount: float) -> FinanceGoal | None:
    goal = (
        await session.execute(
            select(FinanceGoal).where(
                FinanceGoal.id == goal_id,
                FinanceGoal.user_id == user_id,
                FinanceGoal.active.is_(True),
            )
        )
    ).scalar_one_or_none()
    if not goal:
        return None
    goal.current_amount = float(current_amount)
    await session.commit()
    await session.refresh(goal)
    return goal


async def deactivate_finance_goal(session: AsyncSession, user_id: int, goal_id: int) -> bool:
    goal = (
        await session.execute(
            select(FinanceGoal).where(FinanceGoal.id == goal_id, FinanceGoal.user_id == user_id, FinanceGoal.active.is_(True))
        )
    ).scalar_one_or_none()
    if not goal:
        return False
    goal.active = False
    await session.commit()
    return True


async def set_finance_budget(
    session: AsyncSession,
    *,
    user_id: int,
    category: str,
    limit_amount: float,
    month_key: str | None = None,
    profile_id: int | None = None,
) -> FinanceBudget:
    mk = month_key or current_month_key()
    existing = (
        await session.execute(
            select(FinanceBudget).where(
                FinanceBudget.user_id == user_id,
                FinanceBudget.category == category,
                FinanceBudget.month_key == mk,
                FinanceBudget.active.is_(True),
            )
        )
    ).scalar_one_or_none()
    if existing:
        existing.limit_amount = float(limit_amount)
        await session.commit()
        await session.refresh(existing)
        return existing
    row = FinanceBudget(
        user_id=user_id,
        profile_id=profile_id,
        category=category,
        limit_amount=float(limit_amount),
        month_key=mk,
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row


async def list_finance_budgets(session: AsyncSession, user_id: int, *, month_key: str | None = None) -> list[FinanceBudget]:
    mk = month_key or current_month_key()
    rows = (
        await session.execute(
            select(FinanceBudget).where(
                FinanceBudget.user_id == user_id,
                FinanceBudget.month_key == mk,
                FinanceBudget.active.is_(True),
            )
        )
    ).scalars().all()
    return list(rows)


async def add_finance_bill(
    session: AsyncSession,
    *,
    user_id: int,
    title: str,
    amount: float,
    due_at: datetime,
    profile_id: int | None = None,
) -> FinanceBill:
    bill = FinanceBill(
        user_id=user_id,
        profile_id=profile_id,
        title=title.strip()[:255],
        amount=float(amount),
        due_at=due_at,
    )
    session.add(bill)
    await session.commit()
    await session.refresh(bill)
    return bill


async def list_finance_bills(session: AsyncSession, user_id: int, *, limit: int = 15) -> list[FinanceBill]:
    rows = (
        await session.execute(
            select(FinanceBill)
            .where(FinanceBill.user_id == user_id, FinanceBill.active.is_(True))
            .order_by(FinanceBill.due_at.asc())
            .limit(limit)
        )
    ).scalars().all()
    return list(rows)


async def deactivate_finance_bill(session: AsyncSession, user_id: int, bill_id: int) -> bool:
    bill = (
        await session.execute(
            select(FinanceBill).where(FinanceBill.id == bill_id, FinanceBill.user_id == user_id, FinanceBill.active.is_(True))
        )
    ).scalar_one_or_none()
    if not bill:
        return False
    bill.active = False
    await session.commit()
    return True


def format_tx_line(record: LifeRecord, lang: str = "ru") -> str:
    amount = format_amount(float(record.amount or 0))
    if record.submodule_id == "expense":
        cat = t(lang, f"fin_cat_{category_from_record(record)}")
        return f"• {record.created_at.strftime('%d.%m')} — <b>{record.title}</b>: {amount} ({cat})"
    return f"• {record.created_at.strftime('%d.%m')} — <b>{record.title}</b>: +{amount}"


def format_goal_line(goal: FinanceGoal, lang: str = "ru") -> str:
    pct = min(100, int((goal.current_amount / goal.target_amount) * 100)) if goal.target_amount else 0
    line = (
        f"• <b>{goal.title}</b>\n"
        f"  {format_amount(goal.current_amount)} / {format_amount(goal.target_amount)} ({pct}%)"
    )
    if goal.due_at:
        line += f"\n  📅 {goal.due_at.strftime('%d.%m.%Y')}"
    return line


def format_budget_line(budget: FinanceBudget, spent: float, lang: str = "ru") -> str:
    cat = t(lang, f"fin_cat_{budget.category}")
    pct = int((spent / budget.limit_amount) * 100) if budget.limit_amount else 0
    warn = " ⚠️" if spent > budget.limit_amount else ""
    return f"• {cat}: {format_amount(spent)} / {format_amount(budget.limit_amount)} ({pct}%){warn}"


def format_bill_line(bill: FinanceBill, lang: str = "ru") -> str:
    return f"• {bill.due_at.strftime('%d.%m.%Y')} — <b>{bill.title}</b>: {format_amount(bill.amount)}"


def build_bill_reminder_text(bill: FinanceBill, lang: str = "ru") -> str:
    return (
        f"💰 <b>{t(lang, 'fin_bill_reminder_title')}</b>\n\n"
        f"{bill.title}\n"
        f"{format_amount(bill.amount)}\n"
        f"📅 {t(lang, 'fin_due_today')}"
    )


async def fetch_finance_bills_due(
    session: AsyncSession,
    *,
    now: datetime | None = None,
) -> list[tuple[FinanceBill, User]]:
    now = now or datetime.utcnow()
    rows = (
        await session.execute(
            select(FinanceBill, User).join(User, User.id == FinanceBill.user_id).where(FinanceBill.active.is_(True))
        )
    ).all()
    due: list[tuple[FinanceBill, User]] = []
    for bill, user in rows:
        local = user_local_now(user, now)
        if bill.due_at.date() != local.date():
            continue
        key = _date_key(local)
        if bill.last_notified_date == key:
            continue
        due.append((bill, user))
    return due


async def mark_finance_bill_notified(session: AsyncSession, bill_id: int, *, day: str | None = None) -> None:
    await session.execute(
        update(FinanceBill).where(FinanceBill.id == bill_id).values(last_notified_date=day or _date_key(datetime.utcnow()))
    )
    await session.commit()


FINANCE_SUBMODULE_AI: dict[str, str] = {
    "analysis": "Анализируй расходы по категориям, давай советы по экономии и оптимизации бюджета.",
    "budget": "Помогай планировать месячный бюджет по категориям, давай реалистичные лимиты.",
    "goals": "Помогай ставить финансовые цели и план накоплений.",
}


def finance_submodule_description(sub_id: str, lang: str) -> str:
    key = f"fin_sub_{sub_id}"
    text = t(lang, key)
    return text if text != key else t(lang, "fin_ai_hint")
