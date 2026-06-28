from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.i18n import t
from app.models.entities import CalendarEvent, OrganizerItem, Reminder
from app.services.life_data import add_calendar_event, add_reminder, list_calendar_events

ORGANIZER_MODULE = "organizer"
EVENT_TYPES = ("meeting", "birthday", "task")


from app.services.date_parse import format_date, format_datetime, parse_datetime_flexible as parse_datetime


async def add_task(
    session: AsyncSession,
    *,
    user_id: int,
    title: str,
    due_at: datetime | None = None,
    profile_id: int | None = None,
) -> OrganizerItem:
    item = OrganizerItem(
        user_id=user_id,
        profile_id=profile_id,
        item_type="task",
        title=title.strip()[:255],
        due_at=due_at,
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def list_tasks(session: AsyncSession, user_id: int) -> list[OrganizerItem]:
    rows = (
        await session.execute(
            select(OrganizerItem)
            .where(
                OrganizerItem.user_id == user_id,
                OrganizerItem.item_type == "task",
                OrganizerItem.active.is_(True),
            )
            .order_by(OrganizerItem.done.asc(), OrganizerItem.due_at.asc().nulls_last(), OrganizerItem.id.asc())
        )
    ).scalars().all()
    return list(rows)


async def toggle_task(session: AsyncSession, user_id: int, item_id: int) -> OrganizerItem | None:
    item = (
        await session.execute(
            select(OrganizerItem).where(
                OrganizerItem.id == item_id,
                OrganizerItem.user_id == user_id,
                OrganizerItem.item_type == "task",
                OrganizerItem.active.is_(True),
            )
        )
    ).scalar_one_or_none()
    if not item:
        return None
    item.done = not item.done
    await session.commit()
    await session.refresh(item)
    return item


def format_task_line(item: OrganizerItem, lang: str = "ru") -> str:
    mark = "✅" if item.done else "⬜"
    line = f"{mark} <b>{item.title}</b>"
    if item.due_at:
        line += f" — {item.due_at.strftime('%d.%m.%Y %H:%M')}"
    return line


async def add_note(
    session: AsyncSession,
    *,
    user_id: int,
    title: str,
    body: str = "",
    profile_id: int | None = None,
) -> OrganizerItem:
    item = OrganizerItem(
        user_id=user_id,
        profile_id=profile_id,
        item_type="note",
        title=title.strip()[:255],
        body=body.strip()[:4000],
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def list_notes(session: AsyncSession, user_id: int, *, limit: int = 15) -> list[OrganizerItem]:
    rows = (
        await session.execute(
            select(OrganizerItem)
            .where(
                OrganizerItem.user_id == user_id,
                OrganizerItem.item_type == "note",
                OrganizerItem.active.is_(True),
            )
            .order_by(OrganizerItem.id.desc())
            .limit(limit)
        )
    ).scalars().all()
    return list(rows)


def format_note_line(item: OrganizerItem) -> str:
    line = f"📝 <b>{item.title}</b>"
    if item.body:
        line += f"\n  <i>{item.body[:100]}</i>"
    return line


async def add_org_event(
    session: AsyncSession,
    *,
    user_id: int,
    title: str,
    starts_at: datetime,
    event_type: str,
    notes: str = "",
    profile_id: int | None = None,
) -> CalendarEvent:
    recurrence = "yearly" if event_type == "birthday" else ""
    return await add_calendar_event(
        session,
        user_id=user_id,
        title=title,
        starts_at=starts_at,
        event_type=event_type,
        notes=notes,
        profile_id=profile_id,
        recurrence=recurrence,
    )


async def list_events_by_type(
    session: AsyncSession,
    user_id: int,
    event_type: str,
    *,
    limit: int = 15,
) -> list[CalendarEvent]:
    from app.services.recurrence import next_occurrence

    now = datetime.utcnow()
    rows = (
        await session.execute(
            select(CalendarEvent)
            .where(
                CalendarEvent.user_id == user_id,
                CalendarEvent.event_type == event_type,
            )
            .order_by(CalendarEvent.starts_at.asc())
            .limit(limit * 3)
        )
    ).scalars().all()
    upcoming: list[tuple[datetime, CalendarEvent]] = []
    for event in rows:
        effective = next_occurrence(event.starts_at, now, event.recurrence or None)
        if effective >= now:
            upcoming.append((effective, event))
    upcoming.sort(key=lambda pair: pair[0])
    return [event for _, event in upcoming[:limit]]


async def list_all_events(session: AsyncSession, user_id: int, *, limit: int = 20) -> list[CalendarEvent]:
    return await list_calendar_events(session, user_id, limit=limit)


def format_event_line(event: CalendarEvent, lang: str = "ru") -> str:
    from app.services.recurrence import next_occurrence

    icon = {"meeting": "🤝", "birthday": "🎂", "task": "📋"}.get(event.event_type, "📅")
    when = next_occurrence(event.starts_at, datetime.utcnow(), event.recurrence or None)
    repeat = " 🔁" if event.recurrence == "yearly" else ""
    return f"{icon} {when.strftime('%d.%m.%Y %H:%M')}{repeat} — <b>{event.title}</b>"


async def add_org_reminder(
    session: AsyncSession,
    *,
    user_id: int,
    title: str,
    due_at: datetime,
    profile_id: int | None = None,
) -> Reminder:
    return await add_reminder(
        session,
        user_id=user_id,
        title=title,
        due_at=due_at,
        module_id=ORGANIZER_MODULE,
        profile_id=profile_id,
    )


async def list_org_reminders(session: AsyncSession, user_id: int, *, limit: int = 15) -> list[Reminder]:
    now = datetime.utcnow()
    rows = (
        await session.execute(
            select(Reminder)
            .where(
                Reminder.user_id == user_id,
                Reminder.module_id == ORGANIZER_MODULE,
                Reminder.sent.is_(False),
                Reminder.due_at >= now,
            )
            .order_by(Reminder.due_at.asc())
            .limit(limit)
        )
    ).scalars().all()
    return list(rows)


def format_reminder_line(reminder: Reminder) -> str:
    return f"🔔 {reminder.due_at.strftime('%d.%m.%Y %H:%M')} — <b>{reminder.title}</b>"
