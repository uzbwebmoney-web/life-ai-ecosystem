from __future__ import annotations

import calendar
from datetime import datetime

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.i18n import t
from app.models.entities import CreditLoan, User
from app.services.health_service import user_local_now


def _month_key(dt: datetime | None = None) -> str:
    dt = dt or datetime.utcnow()
    return dt.strftime("%Y-%m")


def loan_remaining(loan: CreditLoan) -> float:
    if loan.remaining_amount is not None:
        return max(0.0, float(loan.remaining_amount))
    return float(loan.total_amount)


def payment_day_matches_today(payment_day: int, today: datetime | None = None) -> bool:
    today = today or datetime.utcnow()
    day = max(1, min(31, int(payment_day)))
    last_day = calendar.monthrange(today.year, today.month)[1]
    effective_day = min(day, last_day)
    return today.day == effective_day


def next_credit_payment_at(loan: CreditLoan, local_now: datetime) -> datetime:
    day = max(1, min(31, int(loan.payment_day)))
    last_day = calendar.monthrange(local_now.year, local_now.month)[1]
    effective_day = min(day, last_day)
    due = local_now.replace(hour=9, minute=0, second=0, microsecond=0, day=effective_day)
    if due < local_now:
        if local_now.month == 12:
            year, month = local_now.year + 1, 1
        else:
            year, month = local_now.year, local_now.month + 1
        last_day = calendar.monthrange(year, month)[1]
        effective_day = min(day, last_day)
        due = due.replace(year=year, month=month, day=effective_day)
    return due


def format_amount(value: float, currency: str = "UZS") -> str:
    rounded = int(value) if float(value).is_integer() else value
    return f"{rounded:,}".replace(",", " ") + f" {currency}"


async def add_credit_loan(
    session: AsyncSession,
    *,
    user_id: int,
    title: str,
    total_amount: float,
    monthly_payment: float,
    payment_day: int,
    currency: str = "UZS",
    profile_id: int | None = None,
) -> CreditLoan:
    total = float(total_amount)
    loan = CreditLoan(
        user_id=user_id,
        profile_id=profile_id,
        title=title.strip()[:255],
        total_amount=total,
        remaining_amount=total,
        monthly_payment=float(monthly_payment),
        payment_day=max(1, min(31, int(payment_day))),
        currency=currency.upper()[:8] or "UZS",
    )
    session.add(loan)
    await session.commit()
    await session.refresh(loan)
    return loan


async def get_credit_loan(session: AsyncSession, user_id: int, loan_id: int) -> CreditLoan | None:
    return (
        await session.execute(
            select(CreditLoan).where(
                CreditLoan.id == loan_id,
                CreditLoan.user_id == user_id,
                CreditLoan.active.is_(True),
            )
        )
    ).scalar_one_or_none()


async def list_credit_loans(session: AsyncSession, user_id: int, *, active_only: bool = True) -> list[CreditLoan]:
    query = select(CreditLoan).where(CreditLoan.user_id == user_id)
    if active_only:
        query = query.where(CreditLoan.active.is_(True))
    rows = (await session.execute(query.order_by(CreditLoan.payment_day.asc(), CreditLoan.id.asc()))).scalars().all()
    return list(rows)


async def list_credit_loans_for_users(
    session: AsyncSession,
    user_ids: list[int],
    *,
    active_only: bool = True,
) -> list[CreditLoan]:
    if not user_ids:
        return []
    query = select(CreditLoan).where(CreditLoan.user_id.in_(user_ids))
    if active_only:
        query = query.where(CreditLoan.active.is_(True))
    rows = (await session.execute(query.order_by(CreditLoan.payment_day.asc(), CreditLoan.id.asc()))).scalars().all()
    return list(rows)


async def apply_credit_payment(
    session: AsyncSession,
    user_id: int,
    loan_id: int,
    paid_amount: float,
) -> CreditLoan | None:
    loan = await get_credit_loan(session, user_id, loan_id)
    if not loan:
        return None
    remaining = max(0.0, loan_remaining(loan) - float(paid_amount))
    loan.remaining_amount = remaining
    if remaining <= 0:
        loan.active = False
    await session.commit()
    await session.refresh(loan)
    return loan


async def deactivate_credit_loan(session: AsyncSession, user_id: int, loan_id: int) -> bool:
    loan = await get_credit_loan(session, user_id, loan_id)
    if not loan:
        return False
    loan.active = False
    await session.commit()
    return True


async def fetch_credit_reminders_due(session: AsyncSession, *, now: datetime | None = None) -> list[tuple[CreditLoan, User]]:
    now = now or datetime.utcnow()
    rows = (
        await session.execute(
            select(CreditLoan, User)
            .join(User, User.id == CreditLoan.user_id)
            .where(CreditLoan.active.is_(True))
        )
    ).all()
    due: list[tuple[CreditLoan, User]] = []
    for loan, user in rows:
        local = user_local_now(user, now)
        month = _month_key(local)
        if loan.last_notified_month == month:
            continue
        if payment_day_matches_today(loan.payment_day, local):
            due.append((loan, user))
    return due


async def mark_credit_notified(session: AsyncSession, loan_id: int, *, month: str | None = None) -> None:
    await session.execute(
        update(CreditLoan)
        .where(CreditLoan.id == loan_id)
        .values(last_notified_month=month or _month_key())
    )
    await session.commit()


def format_credit_loan_line(loan: CreditLoan, lang: str = "ru") -> str:
    remaining = loan_remaining(loan)
    return t(lang, "credits_line").format(
        title=loan.title,
        total=format_amount(loan.total_amount, loan.currency),
        remaining=format_amount(remaining, loan.currency),
        monthly=format_amount(loan.monthly_payment, loan.currency),
        day=loan.payment_day,
    )


def build_credit_reminder_text(loan: CreditLoan, lang: str = "ru") -> str:
    remaining = loan_remaining(loan)
    return t(lang, "credits_reminder").format(
        title=loan.title,
        total=format_amount(loan.total_amount, loan.currency),
        remaining=format_amount(remaining, loan.currency),
        monthly=format_amount(loan.monthly_payment, loan.currency),
        day=loan.payment_day,
    )


def credit_reminder_kb(loan_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(lang, "credits_btn_log_payment"),
                    callback_data=f"fin:loan:pay:{loan_id}",
                )
            ],
        ]
    )


def credit_loan_item_kb(loan_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(lang, "credits_btn_log_payment"),
                    callback_data=f"fin:loan:pay:{loan_id}",
                )
            ],
            [InlineKeyboardButton(text=t(lang, "fin_loan_delete"), callback_data=f"fin:loan:del:{loan_id}")],
            [InlineKeyboardButton(text=t(lang, "fin_back_loans"), callback_data="fin:loan:list")],
        ]
    )
