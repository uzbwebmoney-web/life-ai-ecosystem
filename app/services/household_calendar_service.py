from __future__ import annotations

from datetime import datetime

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import CalendarEvent, User
from app.services.household_service import get_household_member_user_ids
from app.services.life_data import add_calendar_event
from app.services.recurrence import next_occurrence


async def add_household_event(
    session: AsyncSession,
    user: User,
    *,
    title: str,
    starts_at: datetime,
    event_type: str = "meeting",
    notes: str = "",
    profile_id: int | None = None,
) -> CalendarEvent | None:
    if not user.household_id:
        return await add_calendar_event(
            session,
            user_id=user.id,
            title=title,
            starts_at=starts_at,
            event_type=event_type,
            notes=notes,
            profile_id=profile_id,
        )
    event = CalendarEvent(
        user_id=user.id,
        profile_id=profile_id,
        title=title.strip()[:255],
        starts_at=starts_at,
        event_type=event_type,
        notes=notes,
        household_id=user.household_id,
        shared=True,
    )
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event


async def list_household_calendar_events(
    session: AsyncSession,
    user: User,
    *,
    limit: int = 20,
) -> list[tuple[CalendarEvent, str | None]]:
    """Return (event, author_username) sorted by date."""
    now = datetime.utcnow()
    member_ids = await get_household_member_user_ids(session, user)
    clauses = [CalendarEvent.user_id.in_(member_ids)]
    if user.household_id:
        clauses.append(
            CalendarEvent.household_id == user.household_id,
        )
    rows = (
        await session.execute(
            select(CalendarEvent)
            .where(or_(*clauses))
            .order_by(CalendarEvent.starts_at.asc())
            .limit(limit * 4)
        )
    ).scalars().all()
    upcoming: list[tuple[datetime, CalendarEvent]] = []
    for event in rows:
        effective = next_occurrence(event.starts_at, now, event.recurrence or None)
        if effective >= now:
            upcoming.append((effective, event))
    upcoming.sort(key=lambda pair: pair[0])
    result: list[tuple[CalendarEvent, str | None]] = []
    for _, event in upcoming[:limit]:
        author_user = (
            await session.execute(select(User).where(User.id == event.user_id))
        ).scalar_one_or_none()
        name = None
        if author_user:
            name = author_user.username or str(author_user.telegram_id)
        result.append((event, name))
    return result


def format_household_event_line(event: CalendarEvent, author: str | None, lang: str = "ru") -> str:
    from app.services.organizer_service import format_event_line

    base = format_event_line(event, lang)
    if event.shared and author:
        from app.core.i18n import t

        return f"{base} ({t(lang, 'family_calendar_by', author=author)})"
    return base
