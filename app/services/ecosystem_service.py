from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.i18n import t
from app.models.entities import CalendarEvent, CreditLoan, LifeRecord, MemoryEntry, Reminder
from app.services.car_service import list_car_compliance, list_car_maintenance
from app.services.credit_loans import list_credit_loans
from app.services.finance_service import list_finance_bills
from app.services.health_service import list_health_medications
from app.services.home_service import list_home_utilities
from app.services.life_data import list_calendar_events, list_upcoming_reminders, search_memory, search_records


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


def _next_credit_payment(loan: CreditLoan, now: datetime) -> datetime:
    day = max(1, min(31, int(loan.payment_day)))
    year, month = now.year, now.month
    if now.day > day:
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
    import calendar

    last = calendar.monthrange(year, month)[1]
    return datetime(year, month, min(day, last), 9, 0)


async def list_unified_notifications(
    session: AsyncSession,
    user_id: int,
    lang: str,
    *,
    horizon_days: int = 60,
    limit: int = 25,
) -> list[EcosystemNotification]:
    now = datetime.utcnow()
    horizon = now + timedelta(days=horizon_days)
    items: list[EcosystemNotification] = []

    for reminder in await list_upcoming_reminders(session, user_id, limit=30):
        if reminder.due_at > horizon:
            continue
        source = t(lang, "eco_src_reminder")
        if reminder.module_id == "organizer":
            source = t(lang, "eco_src_organizer")
        elif reminder.module_id == "health":
            source = t(lang, "eco_src_health")
        items.append(
            EcosystemNotification(reminder.due_at, "🔔", reminder.title, source)
        )

    for event in await list_calendar_events(session, user_id, limit=30):
        if event.starts_at < now or event.starts_at > horizon:
            continue
        if event.event_type == "birthday":
            icon, source = "🎂", t(lang, "eco_src_birthday")
        elif event.event_type == "meeting":
            icon, source = "🤝", t(lang, "eco_src_meeting")
        else:
            icon, source = "📅", t(lang, "eco_src_calendar")
        items.append(EcosystemNotification(event.starts_at, icon, event.title, source))

    for med in await list_health_medications(session, user_id):
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
            items.append(
                EcosystemNotification(
                    due,
                    "💊",
                    f"{med.name} ({med.dosage or '—'})",
                    t(lang, "eco_src_medicine"),
                )
            )

    for item in await list_car_maintenance(session, user_id):
        if item.due_at < now or item.due_at > horizon:
            continue
        items.append(
            EcosystemNotification(item.due_at, "🚗", item.title, t(lang, "eco_src_car_service"))
        )

    for row in await list_car_compliance(session, user_id):
        if row.expires_at < now or row.expires_at > horizon:
            continue
        label = row.title or row.compliance_type
        if row.compliance_type == "insurance":
            source = t(lang, "eco_src_insurance")
        else:
            source = t(lang, "eco_src_car_service")
        items.append(
            EcosystemNotification(
                row.expires_at,
                "🛡",
                label,
                source,
            )
        )

    for bill in await list_finance_bills(session, user_id):
        if bill.due_at < now or bill.due_at > horizon:
            continue
        items.append(
            EcosystemNotification(bill.due_at, "💰", bill.title, t(lang, "eco_src_payment"))
        )

    for bill in await list_home_utilities(session, user_id, limit=20):
        if bill.due_at < now or bill.due_at > horizon:
            continue
        items.append(
            EcosystemNotification(bill.due_at, "🏠", bill.title, t(lang, "eco_src_utilities"))
        )

    for loan in await list_credit_loans(session, user_id):
        due = _next_credit_payment(loan, now)
        if due > horizon:
            continue
        items.append(
            EcosystemNotification(
                due,
                "💳",
                f"{loan.title} — {loan.monthly_payment:,.0f} {loan.currency}".replace(",", " "),
                t(lang, "eco_src_credit"),
            )
        )

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
    user_id: int,
    query: str,
    *,
    limit: int = 5,
) -> UnifiedSearchResult:
    return UnifiedSearchResult(
        records=await search_records(session, user_id, query, limit=limit),
        memory=await search_memory(session, user_id, query, limit=limit),
        events=await search_calendar_events(session, user_id, query, limit=limit),
        reminders=await search_reminders(session, user_id, query, limit=limit),
    )


def format_unified_search(results: UnifiedSearchResult, lang: str, query: str) -> list[str]:
    lines = [t(lang, "search_results", query=query)]
    if results.records:
        lines.append(f"<b>{t(lang, 'search_records')}</b>")
        for record in results.records[:5]:
            body = f" — {record.body[:80]}" if record.body else ""
            lines.append(f"• [{record.module_id}/{record.submodule_id}] {record.title}{body}")
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
