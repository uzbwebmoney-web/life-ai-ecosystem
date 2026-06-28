from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.i18n import t
from app.models.entities import AlertItem, User
from app.services.health_service import user_local_now

ALERT_TYPES = ("subscription", "visa", "custom")


async def add_alert_item(
    session: AsyncSession,
    *,
    user_id: int,
    alert_type: str,
    title: str,
    due_at: datetime,
    amount: float | None = None,
    currency: str | None = None,
    profile_id: int | None = None,
) -> AlertItem:
    item = AlertItem(
        user_id=user_id,
        profile_id=profile_id,
        alert_type=alert_type,
        title=title.strip()[:255],
        due_at=due_at,
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
    limit: int = 20,
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


async def fetch_alert_items_due(session: AsyncSession, *, now: datetime | None = None) -> list[tuple[AlertItem, User]]:
    now = now or datetime.utcnow()
    rows = (
        await session.execute(
            select(AlertItem, User)
            .join(User, User.id == AlertItem.user_id)
            .where(AlertItem.active.is_(True))
            .order_by(AlertItem.due_at.asc())
            .limit(100)
        )
    ).all()
    due: list[tuple[AlertItem, User]] = []
    for item, user in rows:
        local = user_local_now(user, now)
        if item.due_at.date() > local.date():
            continue
        today = local.date().isoformat()
        if item.last_notified_date == today:
            continue
        due.append((item, user))
    return due


async def mark_alert_notified(session: AsyncSession, item_id: int, *, day: str | None = None) -> None:
    item = (await session.execute(select(AlertItem).where(AlertItem.id == item_id))).scalar_one_or_none()
    if not item:
        return
    item.last_notified_date = day or datetime.utcnow().date().isoformat()
    await session.commit()


def format_alert_line(item: AlertItem, lang: str) -> str:
    when = item.due_at.strftime("%d.%m.%Y")
    extra = ""
    if item.amount is not None:
        cur = item.currency or "UZS"
        extra = f" — {item.amount:,.0f} {cur}".replace(",", " ")
    return f"• {when} — <b>{item.title}</b>{extra}"


def build_alert_reminder_text(item: AlertItem, lang: str) -> str:
    when = item.due_at.strftime("%d.%m.%Y")
    extra = ""
    if item.amount is not None:
        cur = item.currency or "UZS"
        extra = f"\n💰 {item.amount:,.0f} {cur}".replace(",", " ")
    return t(lang, "alert_reminder").format(title=item.title, when=when, extra=extra)
