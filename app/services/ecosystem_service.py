from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.i18n import t
from app.models.entities import CalendarEvent, LifeRecord, MemoryEntry, Reminder, User
from app.services.car_service import list_car_compliance, list_car_maintenance
from app.services.credit_loans import list_credit_loans_for_users, next_credit_payment_at
from app.services.finance_service import list_finance_bills
from app.services.health_service import list_health_medications, user_local_now
from app.services.home_service import list_home_utilities
from app.services.household_service import effective_data_user_ids
from app.services.life_data import list_calendar_events, list_upcoming_reminders, search_memory, search_records
from app.services.notifications_service import list_alert_items


@dataclass(order=True)
class EcosystemNotification:
    sort_at: datetime
    icon: str = field(compare=False)
    title: str = field(compare=False)
    source: str = field(compare=False)


@dataclass
class UnifiedSearchResult:
    records: list[LifeRecord] = field(default_factory=list)
    memory: list[MemoryEntry] = field(default_factory=list)
    events: list[CalendarEvent] = field(default_factory=list)
    reminders: list[Reminder] = field(default_factory=list)

    def has_any(self) -> bool:
        return bool(self.records or self.memory or self.events or self.reminders)


async def list_unified_notifications(
    session: AsyncSession,
    user_or_id: User | int,
    lang: str,
    *,
    horizon_days: int = 60,
    limit: int = 25,
) -> list[EcosystemNotification]:
    if isinstance(user_or_id, User):
        user = user_or_id
        user_ids = await effective_data_user_ids(session, user)
        local_now = user_local_now(user)
    else:
        user_ids = [user_or_id]
        local_now = datetime.utcnow()
    now = local_now
    horizon = now + timedelta(days=horizon_days)
    items: list[EcosystemNotification] = []
    seen: set[str] = set()

    def add(item: EcosystemNotification) -> None:
        key = f"{item.sort_at.isoformat()}:{item.title}:{item.source}"
        if key in seen:
            return
        seen.add(key)
        items.append(item)

    for uid in user_ids:
        for reminder in await list_upcoming_reminders(session, uid, limit=30):
            if reminder.due_at > horizon:
                continue
            source = t(lang, "eco_src_reminder")
            if reminder.module_id == "organizer":
                source = t(lang, "eco_src_organizer")
            elif reminder.module_id == "health":
                source = t(lang, "eco_src_health")
            add(EcosystemNotification(reminder.due_at, "🔔", reminder.title, source))

        for event in await list_calendar_events(session, uid, limit=30):
            from app.services.recurrence import next_occurrence

            effective = next_occurrence(event.starts_at, now, event.recurrence or None)
            if effective < now or effective > horizon:
                continue
            if event.event_type == "birthday":
                icon, source = "🎂", t(lang, "eco_src_birthday")
            elif event.event_type == "meeting":
                icon, source = "🤝", t(lang, "eco_src_meeting")
            else:
                icon, source = "📅", t(lang, "eco_src_calendar")
            add(EcosystemNotification(effective, icon, event.title, source))

        for med in await list_health_medications(session, uid):
            for time_str in med.reminder_times.split(","):
                time_str = time_str.strip()
                if not time_str:
                    continue
                try:
                    hour, minute = map(int, time_str.split(":"))
                except ValueError:
                    continue
                due = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if due < now:
                    due += timedelta(days=1)
                add(
                    EcosystemNotification(
                        due,
                        "💊",
                        f"{med.name} ({med.dosage or '—'})",
                        t(lang, "eco_src_medicine"),
                    )
                )

        for item in await list_car_maintenance(session, uid):
            if item.due_at < now or item.due_at > horizon:
                continue
            add(EcosystemNotification(item.due_at, "🚗", item.title, t(lang, "eco_src_car_service")))

        for row in await list_car_compliance(session, uid):
            if row.expires_at < now or row.expires_at > horizon:
                continue
            label = row.title or row.compliance_type
            source = t(lang, "eco_src_insurance") if row.compliance_type == "insurance" else t(lang, "eco_src_car_service")
            add(EcosystemNotification(row.expires_at, "🛡", label, source))

        for bill in await list_finance_bills(session, uid):
            if bill.due_at < now or bill.due_at > horizon:
                continue
            add(EcosystemNotification(bill.due_at, "💰", bill.title, t(lang, "eco_src_payment")))

        for bill in await list_home_utilities(session, uid, limit=20):
            if bill.due_at < now or bill.due_at > horizon:
                continue
            add(EcosystemNotification(bill.due_at, "🏠", bill.title, t(lang, "eco_src_utilities")))

        for alert in await list_alert_items(session, uid, limit=20):
            if alert.due_at < now or alert.due_at > horizon:
                continue
            source = t(lang, "eco_src_subscription") if alert.alert_type == "subscription" else t(lang, "eco_src_visa")
            add(EcosystemNotification(alert.due_at, "📋", alert.title, source))

    for loan in await list_credit_loans_for_users(session, user_ids):
        due = next_credit_payment_at(loan, now)
        if due > horizon:
            continue
        add(EcosystemNotification(due, "💳", loan.title, t(lang, "eco_src_credit")))

    items.sort()
    return items[:limit]


async def search_calendar_events(
    session: AsyncSession,
    user_id: int,
    query: str,
    *,
    limit: int = 5,
) -> list[CalendarEvent]:
    pattern = f"%{query.strip()}%"
    rows = (
        await session.execute(
            select(CalendarEvent)
            .where(
                CalendarEvent.user_id == user_id,
                or_(CalendarEvent.title.ilike(pattern), CalendarEvent.notes.ilike(pattern)),
            )
            .order_by(CalendarEvent.starts_at.desc())
            .limit(limit)
        )
    ).scalars().all()
    return list(rows)


async def search_reminders(
    session: AsyncSession,
    user_id: int,
    query: str,
    *,
    limit: int = 5,
) -> list[Reminder]:
    pattern = f"%{query.strip()}%"
    rows = (
        await session.execute(
            select(Reminder)
            .where(
                Reminder.user_id == user_id,
                Reminder.title.ilike(pattern),
            )
            .order_by(Reminder.due_at.desc())
            .limit(limit)
        )
    ).scalars().all()
    return list(rows)


async def unified_search(
    session: AsyncSession,
    user: User,
    query: str,
    *,
    limit: int = 5,
) -> UnifiedSearchResult:
    user_ids = await effective_data_user_ids(session, user)
    records: list[LifeRecord] = []
    memory: list[MemoryEntry] = []
    events: list[CalendarEvent] = []
    reminders: list[Reminder] = []
    seen_r: set[int] = set()
    for uid in user_ids:
        for r in await search_records(session, uid, query, limit=limit):
            if r.id not in seen_r:
                seen_r.add(r.id)
                records.append(r)
        for m in await search_memory(session, uid, query, limit=limit):
            memory.append(m)
        for e in await search_calendar_events(session, uid, query, limit=limit):
            events.append(e)
        for rem in await search_reminders(session, uid, query, limit=limit):
            reminders.append(rem)
    return UnifiedSearchResult(
        records=records[:limit],
        memory=memory[:limit],
        events=events[:limit],
        reminders=reminders[:limit],
    )


def format_unified_search(results: UnifiedSearchResult, lang: str, query: str) -> list[str]:
    lines = [t(lang, "search_results", query=query)]
    if results.records:
        lines.append(f"<b>{t(lang, 'search_records')}</b>")
        for record in results.records[:5]:
            body = f" — {record.body[:80]}" if record.body else ""
            archive = ""
            if record.meta_json and "archive_folder" in record.meta_json:
                archive = " 📁"
            lines.append(f"• [{record.module_id}] {record.title}{archive}{body}")
    if results.events:
        lines.append(f"\n<b>{t(lang, 'eco_search_events')}</b>")
        for event in results.events[:5]:
            lines.append(f"• {event.starts_at.strftime('%d.%m.%Y')} — {event.title} ({event.event_type})")
    if results.reminders:
        lines.append(f"\n<b>{t(lang, 'eco_search_reminders')}</b>")
        for reminder in results.reminders[:5]:
            lines.append(f"• {reminder.due_at.strftime('%d.%m.%Y %H:%M')} — {reminder.title}")
    if results.memory:
        lines.append(f"\n<b>{t(lang, 'search_memory')}</b>")
        for entry in results.memory[:5]:
            lines.append(f"• {entry.content[:120]}")
    if not results.has_any():
        lines.append(t(lang, "search_nothing"))
    return lines


def build_search_ai_context(results: UnifiedSearchResult) -> str:
    parts: list[str] = []
    for record in results.records[:5]:
        parts.append(f"[{record.module_id}] {record.title}: {record.body[:300]}")
    for event in results.events[:3]:
        parts.append(f"[calendar] {event.starts_at.date()} {event.title} ({event.event_type})")
    for reminder in results.reminders[:3]:
        parts.append(f"[reminder] {reminder.due_at} {reminder.title}")
    for entry in results.memory[:3]:
        parts.append(f"[memory] {entry.content[:200]}")
    return "\n".join(parts)


def format_notifications_list(items: list[EcosystemNotification], lang: str) -> str:
    lines = [t(lang, "eco_notifications_title"), ""]
    if not items:
        lines.append(t(lang, "eco_notifications_empty"))
        return "\n".join(lines)
    for item in items:
        when = item.sort_at.strftime("%d.%m.%Y %H:%M")
        lines.append(f"{item.icon} <b>{when}</b> — {item.title}\n  <i>{item.source}</i>")
    return "\n".join(lines)
