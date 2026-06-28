from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import (
    AlertItem,
    CalendarEvent,
    CreditLoan,
    LifeRecord,
    MemoryEntry,
    OrganizerItem,
    Reminder,
    User,
)


def _dt(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


async def build_user_export(session: AsyncSession, user_id: int) -> str:
    user = (await session.execute(select(User).where(User.id == user_id))).scalar_one()
    records = (
        await session.execute(select(LifeRecord).where(LifeRecord.user_id == user_id).order_by(LifeRecord.id))
    ).scalars().all()
    events = (
        await session.execute(select(CalendarEvent).where(CalendarEvent.user_id == user_id).order_by(CalendarEvent.id))
    ).scalars().all()
    reminders = (
        await session.execute(select(Reminder).where(Reminder.user_id == user_id).order_by(Reminder.id))
    ).scalars().all()
    memory = (
        await session.execute(select(MemoryEntry).where(MemoryEntry.user_id == user_id).order_by(MemoryEntry.id))
    ).scalars().all()
    organizer = (
        await session.execute(select(OrganizerItem).where(OrganizerItem.user_id == user_id).order_by(OrganizerItem.id))
    ).scalars().all()
    alerts = (
        await session.execute(select(AlertItem).where(AlertItem.user_id == user_id, AlertItem.active.is_(True)))
    ).scalars().all()
    loans = (
        await session.execute(select(CreditLoan).where(CreditLoan.user_id == user_id, CreditLoan.active.is_(True)))
    ).scalars().all()

    payload = {
        "exported_at": datetime.utcnow().isoformat(),
        "user": {
            "telegram_id": user.telegram_id,
            "language": user.language,
            "memory_enabled": user.memory_enabled,
            "voice_mode": user.voice_mode,
        },
        "records": [
            {
                "module_id": r.module_id,
                "submodule_id": r.submodule_id,
                "title": r.title,
                "body": r.body,
                "amount": r.amount,
                "currency": r.currency,
                "created_at": _dt(r.created_at),
            }
            for r in records
        ],
        "calendar_events": [
            {
                "title": e.title,
                "starts_at": _dt(e.starts_at),
                "event_type": e.event_type,
                "recurrence": e.recurrence,
                "notes": e.notes,
            }
            for e in events
        ],
        "reminders": [{"title": r.title, "due_at": _dt(r.due_at), "module_id": r.module_id} for r in reminders],
        "memory": [{"content": m.content, "module_id": m.module_id, "created_at": _dt(m.created_at)} for m in memory],
        "organizer": [
            {
                "type": o.item_type,
                "title": o.title,
                "body": o.body,
                "due_at": _dt(o.due_at),
                "done": o.done,
            }
            for o in organizer
        ],
        "alerts": [
            {
                "type": a.alert_type,
                "title": a.title,
                "due_at": _dt(a.due_at),
                "amount": a.amount,
                "currency": a.currency,
            }
            for a in alerts
        ],
        "credit_loans": [
            {
                "title": loan.title,
                "total_amount": loan.total_amount,
                "monthly_payment": loan.monthly_payment,
                "payment_day": loan.payment_day,
                "currency": loan.currency,
            }
            for loan in loans
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)
