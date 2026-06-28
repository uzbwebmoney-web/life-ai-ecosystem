from __future__ import annotations

import logging
from datetime import datetime

import httpx
from aiogram import Bot
from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import CalendarEvent, CreditLoan, FamilyProfile, LifeRecord, MemoryEntry, Reminder, User

logger = logging.getLogger(__name__)


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
    *,
    language_code: str | None = None,
) -> User:
    user = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one_or_none()
    if user:
        if username and user.username != username:
            user.username = username
            await session.commit()
        return user
    from app.core.i18n import normalize_lang

    default_lang = normalize_lang(language_code)
    user = User(telegram_id=telegram_id, username=username, language=default_lang)
    session.add(user)
    await session.flush()
    profile = FamilyProfile(user_id=user.id, name="Я", relation="self", is_default=True)
    session.add(profile)
    await session.flush()
    user.active_profile_id = profile.id
    from app.services.subscription_service import ensure_user_subscription_fields

    await session.commit()
    await session.refresh(user)
    await ensure_user_subscription_fields(session, user)
    return user


async def get_active_profile(session: AsyncSession, user: User) -> FamilyProfile | None:
    if not user.active_profile_id:
        return None
    return (
        await session.execute(select(FamilyProfile).where(FamilyProfile.id == user.active_profile_id))
    ).scalar_one_or_none()


async def list_family_profiles(session: AsyncSession, user_id: int) -> list[FamilyProfile]:
    rows = (
        await session.execute(
            select(FamilyProfile).where(FamilyProfile.user_id == user_id).order_by(FamilyProfile.id.asc())
        )
    ).scalars().all()
    return list(rows)


async def add_family_profile(session: AsyncSession, user_id: int, name: str, relation: str) -> FamilyProfile:
    profile = FamilyProfile(user_id=user_id, name=name.strip()[:128], relation=relation.strip()[:64])
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return profile


async def switch_active_profile(session: AsyncSession, user: User, profile_id: int) -> bool:
    profile = (
        await session.execute(
            select(FamilyProfile).where(FamilyProfile.id == profile_id, FamilyProfile.user_id == user.id)
        )
    ).scalar_one_or_none()
    if not profile:
        return False
    user.active_profile_id = profile.id
    await session.commit()
    return True


async def toggle_memory(session: AsyncSession, user: User) -> bool:
    user.memory_enabled = not user.memory_enabled
    await session.commit()
    return user.memory_enabled


async def set_active_module(
    session: AsyncSession,
    user: User,
    module_id: str,
    *,
    submodule_id: str | None = None,
) -> None:
    user.active_module_id = module_id
    user.active_submodule_id = submodule_id
    await session.commit()


async def clear_active_module(session: AsyncSession, user: User) -> None:
    user.active_module_id = None
    user.active_submodule_id = None
    await session.commit()


async def set_user_language(session: AsyncSession, user: User, language: str) -> str:
    from app.core.i18n import normalize_lang

    user.language = normalize_lang(language)
    await session.commit()
    return user.language


async def toggle_voice_mode(session: AsyncSession, user: User) -> bool:
    user.voice_mode = not user.voice_mode
    await session.commit()
    return user.voice_mode


async def complete_onboarding(session: AsyncSession, user: User) -> None:
    user.onboarding_done = True
    user.welcome_pending = False
    await session.commit()


async def mark_welcome_pending(session: AsyncSession, user: User) -> None:
    user.welcome_pending = True
    await session.commit()


async def add_record(
    session: AsyncSession,
    *,
    user_id: int,
    module_id: str,
    submodule_id: str,
    title: str,
    body: str = "",
    amount: float | None = None,
    currency: str | None = None,
    profile_id: int | None = None,
    meta_json: str | None = None,
) -> LifeRecord:
    record = LifeRecord(
        user_id=user_id,
        profile_id=profile_id,
        module_id=module_id,
        submodule_id=submodule_id,
        title=title,
        body=body,
        amount=amount,
        currency=currency,
        meta_json=meta_json,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


async def add_calendar_event(
    session: AsyncSession,
    *,
    user_id: int,
    title: str,
    starts_at: datetime,
    event_type: str = "meeting",
    notes: str = "",
    profile_id: int | None = None,
    recurrence: str = "",
) -> CalendarEvent:
    event = CalendarEvent(
        user_id=user_id,
        profile_id=profile_id,
        title=title,
        starts_at=starts_at,
        event_type=event_type,
        notes=notes,
        recurrence=recurrence,
    )
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event


async def list_calendar_events(session: AsyncSession, user_id: int, *, limit: int = 15) -> list[CalendarEvent]:
    from app.services.recurrence import next_occurrence

    now = datetime.utcnow()
    rows = (
        await session.execute(
            select(CalendarEvent)
            .where(CalendarEvent.user_id == user_id)
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


async def search_records(session: AsyncSession, user_id: int, query: str, *, limit: int = 10) -> list[LifeRecord]:
    pattern = f"%{query.strip()}%"
    rows = (
        await session.execute(
            select(LifeRecord)
            .where(
                LifeRecord.user_id == user_id,
                or_(
                    LifeRecord.title.ilike(pattern),
                    LifeRecord.body.ilike(pattern),
                    LifeRecord.module_id.ilike(pattern),
                    LifeRecord.submodule_id.ilike(pattern),
                    LifeRecord.meta_json.ilike(pattern),
                ),
            )
            .order_by(LifeRecord.created_at.desc())
            .limit(limit)
        )
    ).scalars().all()
    return list(rows)


async def add_memory(
    session: AsyncSession,
    user_id: int,
    content: str,
    module_id: str | None = None,
    profile_id: int | None = None,
    *,
    user: User | None = None,
    lang: str = "ru",
) -> MemoryEntry | None:
    if user is not None:
        from app.services.subscription_service import check_memory_quota

        err = await check_memory_quota(session, user, lang=lang)
        if err:
            return None
    entry = MemoryEntry(user_id=user_id, content=content, module_id=module_id, profile_id=profile_id)
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return entry


async def search_memory(session: AsyncSession, user_id: int, query: str, *, limit: int = 10) -> list[MemoryEntry]:
    pattern = f"%{query.strip()}%"
    rows = (
        await session.execute(
            select(MemoryEntry)
            .where(MemoryEntry.user_id == user_id, MemoryEntry.content.ilike(pattern))
            .order_by(MemoryEntry.created_at.desc())
            .limit(limit)
        )
    ).scalars().all()
    return list(rows)


async def add_reminder(
    session: AsyncSession,
    *,
    user_id: int,
    title: str,
    due_at: datetime,
    module_id: str = "notifications",
    profile_id: int | None = None,
    user: User | None = None,
    lang: str = "ru",
) -> Reminder | None:
    if user is not None:
        from app.services.subscription_service import check_reminder_quota

        err = await check_reminder_quota(session, user, lang=lang)
        if err:
            return None
    reminder = Reminder(
        user_id=user_id,
        title=title,
        due_at=due_at,
        module_id=module_id,
        profile_id=profile_id,
    )
    session.add(reminder)
    await session.commit()
    await session.refresh(reminder)
    return reminder


async def list_upcoming_reminders(session: AsyncSession, user_id: int, *, limit: int = 10) -> list[Reminder]:
    now = datetime.utcnow()
    rows = (
        await session.execute(
            select(Reminder)
            .where(Reminder.user_id == user_id, Reminder.sent.is_(False), Reminder.due_at >= now)
            .order_by(Reminder.due_at.asc())
            .limit(limit)
        )
    ).scalars().all()
    return list(rows)


async def fetch_due_reminders(session: AsyncSession, *, limit: int = 50) -> list[tuple[Reminder, User]]:
    now = datetime.utcnow()
    rows = (
        await session.execute(
            select(Reminder, User)
            .join(User, User.id == Reminder.user_id)
            .where(Reminder.sent.is_(False), Reminder.due_at <= now)
            .order_by(Reminder.due_at.asc())
            .limit(limit)
        )
    ).all()
    return [(r, u) for r, u in rows]


async def mark_reminder_sent(session: AsyncSession, reminder_id: int) -> None:
    await session.execute(update(Reminder).where(Reminder.id == reminder_id).values(sent=True))
    await session.commit()


async def dashboard_stats(session: AsyncSession, user_id: int) -> dict[str, int | float]:
    records = int(
        (await session.execute(select(func.count(LifeRecord.id)).where(LifeRecord.user_id == user_id))).scalar_one() or 0
    )
    reminders = int(
        (
            await session.execute(
                select(func.count(Reminder.id)).where(Reminder.user_id == user_id, Reminder.sent.is_(False))
            )
        ).scalar_one()
        or 0
    )
    memory = int(
        (await session.execute(select(func.count(MemoryEntry.id)).where(MemoryEntry.user_id == user_id))).scalar_one() or 0
    )
    events = int(
        (await session.execute(select(func.count(CalendarEvent.id)).where(CalendarEvent.user_id == user_id))).scalar_one()
        or 0
    )
    profiles = int(
        (await session.execute(select(func.count(FamilyProfile.id)).where(FamilyProfile.user_id == user_id))).scalar_one()
        or 0
    )
    credits = int(
        (
            await session.execute(
                select(func.count(CreditLoan.id)).where(CreditLoan.user_id == user_id, CreditLoan.active.is_(True))
            )
        ).scalar_one()
        or 0
    )
    income = (
        await session.execute(
            select(func.coalesce(func.sum(LifeRecord.amount), 0.0)).where(
                LifeRecord.user_id == user_id,
                LifeRecord.module_id == "finance",
                LifeRecord.submodule_id == "income",
            )
        )
    ).scalar_one()
    expense = (
        await session.execute(
            select(func.coalesce(func.sum(LifeRecord.amount), 0.0)).where(
                LifeRecord.user_id == user_id,
                LifeRecord.module_id == "finance",
                LifeRecord.submodule_id == "expense",
            )
        )
    ).scalar_one()
    return {
        "records": records,
        "reminders": reminders,
        "memory": memory,
        "events": events,
        "profiles": profiles,
        "credits": credits,
        "income": float(income or 0),
        "expense": float(expense or 0),
    }
