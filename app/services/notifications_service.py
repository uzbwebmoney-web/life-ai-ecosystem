from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.i18n import t
from app.models.entities import AlertItem, User
from app.services.health_service import user_local_now


@dataclass(frozen=True)
class AlertTypeDef:
    id: str
    icon: str
    date_only: bool
    default_before_min: int
    needs_amount: bool
    title_prompt_key: str


ALERT_TYPES: dict[str, AlertTypeDef] = {
    "subscription": AlertTypeDef("subscription", "📺", True, 0, True, "ntf_title_subscription"),
    "visa": AlertTypeDef("visa", "🛂", True, 0, False, "ntf_title_visa"),
    "movie": AlertTypeDef("movie", "🎬", False, 30, False, "ntf_title_movie"),
    "event": AlertTypeDef("event", "🎉", False, 60, False, "ntf_title_event"),
    "ticket": AlertTypeDef("ticket", "✈️", False, 120, False, "ntf_title_ticket"),
    "delivery": AlertTypeDef("delivery", "📦", False, 15, False, "ntf_title_delivery"),
    "appointment": AlertTypeDef("appointment", "📆", False, 60, False, "ntf_title_appointment"),
    "custom": AlertTypeDef("custom", "🔔", False, 30, False, "ntf_title_custom"),
}

ADDABLE_ALERT_TYPES = tuple(ALERT_TYPES.keys())
DATE_ONLY_ALERT_TYPES = {k for k, v in ALERT_TYPES.items() if v.date_only}
EVENT_ALERT_TYPES = {k for k, v in ALERT_TYPES.items() if not v.date_only}


def alert_type_def(alert_type: str) -> AlertTypeDef:
    return ALERT_TYPES.get(alert_type, ALERT_TYPES["custom"])


def alert_source_key(alert_type: str) -> str:
    key = f"eco_src_{alert_type}"
    return key if alert_type in ALERT_TYPES else "eco_src_custom"


async def add_alert_item(
    session: AsyncSession,
    *,
    user_id: int,
    alert_type: str,
    title: str,
    due_at: datetime,
    amount: float | None = None,
    currency: str | None = None,
    notes: str = "",
    remind_before_minutes: int | None = None,
    profile_id: int | None = None,
) -> AlertItem:
    kind = alert_type_def(alert_type)
    before = kind.default_before_min if remind_before_minutes is None else remind_before_minutes
    item = AlertItem(
        user_id=user_id,
        profile_id=profile_id,
        alert_type=kind.id,
        title=title.strip()[:255],
        due_at=due_at,
        notes=notes.strip()[:2000],
        remind_before_minutes=before,
        amount=amount,
        currency=currency,
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def list_alert_items(
    session: AsyncSession,
    user_id: int,
    *,
    alert_type: str | None = None,
    limit: int = 30,
) -> list[AlertItem]:
    q = select(AlertItem).where(AlertItem.user_id == user_id, AlertItem.active.is_(True))
    if alert_type:
        q = q.where(AlertItem.alert_type == alert_type)
    rows = (await session.execute(q.order_by(AlertItem.due_at.asc()).limit(limit))).scalars().all()
    return list(rows)


async def delete_alert_item(session: AsyncSession, user_id: int, item_id: int) -> bool:
    item = (
        await session.execute(
            select(AlertItem).where(AlertItem.id == item_id, AlertItem.user_id == user_id, AlertItem.active.is_(True))
        )
    ).scalar_one_or_none()
    if not item:
        return False
    item.active = False
    await session.commit()
    return True


def _effective_remind_at(item: AlertItem) -> datetime:
    if item.alert_type in DATE_ONLY_ALERT_TYPES:
        return item.due_at.replace(hour=9, minute=0, second=0, microsecond=0)
    minutes = item.remind_before_minutes or alert_type_def(item.alert_type).default_before_min
    return item.due_at - timedelta(minutes=minutes)


async def fetch_alert_items_due(session: AsyncSession, *, now: datetime | None = None) -> list[tuple[AlertItem, User]]:
    now = now or datetime.utcnow()
    rows = (
        await session.execute(
            select(AlertItem, User)
            .join(User, User.id == AlertItem.user_id)
            .where(AlertItem.active.is_(True), AlertItem.sent.is_(False))
            .order_by(AlertItem.due_at.asc())
            .limit(100)
        )
    ).all()
    due: list[tuple[AlertItem, User]] = []
    for item, user in rows:
        local = user_local_now(user, now)
        if item.alert_type in DATE_ONLY_ALERT_TYPES:
            if item.due_at.date() > local.date():
                continue
            today = local.date().isoformat()
            if item.last_notified_date == today:
                continue
        else:
            remind_at = _effective_remind_at(item)
            remind_local = user_local_now(user, remind_at)
            if local < remind_local:
                continue
        due.append((item, user))
    return due


async def mark_alert_notified(session: AsyncSession, item_id: int, *, day: str | None = None) -> None:
    item = (await session.execute(select(AlertItem).where(AlertItem.id == item_id))).scalar_one_or_none()
    if not item:
        return
    if item.alert_type in DATE_ONLY_ALERT_TYPES:
        item.last_notified_date = day or datetime.utcnow().date().isoformat()
    else:
        item.sent = True
    await session.commit()


def format_alert_line(item: AlertItem, lang: str) -> str:
    kind = alert_type_def(item.alert_type)
    if item.alert_type in DATE_ONLY_ALERT_TYPES:
        when = item.due_at.strftime("%d.%m.%Y")
    else:
        when = item.due_at.strftime("%d.%m.%Y %H:%M")
    extra = ""
    if item.amount is not None:
        cur = item.currency or "UZS"
        extra = f" — {item.amount:,.0f} {cur}".replace(",", " ")
    elif item.notes:
        extra = f" — <i>{item.notes[:40]}</i>"
    return f"• {kind.icon} {when} — <b>{item.title}</b>{extra}"


def build_alert_reminder_text(item: AlertItem, lang: str) -> str:
    kind = alert_type_def(item.alert_type)
    if item.alert_type in DATE_ONLY_ALERT_TYPES:
        when = item.due_at.strftime("%d.%m.%Y")
    else:
        when = item.due_at.strftime("%d.%m.%Y %H:%M")
    extra_parts: list[str] = []
    if item.notes:
        extra_parts.append(f"\n📝 {item.notes[:500]}")
    if item.amount is not None:
        cur = item.currency or "UZS"
        extra_parts.append(f"\n💰 {item.amount:,.0f} {cur}".replace(",", " "))
    extra = "".join(extra_parts)
    msg_key = f"alert_reminder_{kind.id}"
    template = t(lang, msg_key)
    if template == msg_key:
        template = t(lang, "alert_reminder")
    return template.format(title=item.title, when=when, extra=extra)
