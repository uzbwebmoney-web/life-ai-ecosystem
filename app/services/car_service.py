from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.i18n import t
from app.models.entities import CarCompliance, CarMaintenanceItem, LifeRecord, User
from app.services.health_service import user_local_now

CAR_MODULE = "car"
MAINT_TYPES = ("oil", "filter", "tires", "service", "other")
COMPLIANCE_TYPES = ("insurance", "inspection")
COMPLIANCE_ALERT_DAYS = (30, 7, 1, 0)


from app.services.date_parse import parse_date_flexible as parse_date


def _date_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


async def add_car_maintenance(
    session: AsyncSession,
    *,
    user_id: int,
    item_type: str,
    title: str,
    due_at: datetime,
    notes: str = "",
    profile_id: int | None = None,
) -> CarMaintenanceItem:
    item = CarMaintenanceItem(
        user_id=user_id,
        profile_id=profile_id,
        item_type=item_type if item_type in MAINT_TYPES else "other",
        title=title.strip()[:255],
        due_at=due_at,
        notes=notes.strip()[:2000],
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def list_car_maintenance(
    session: AsyncSession,
    user_id: int,
    *,
    active_only: bool = True,
    limit: int = 20,
) -> list[CarMaintenanceItem]:
    query = select(CarMaintenanceItem).where(CarMaintenanceItem.user_id == user_id)
    if active_only:
        query = query.where(CarMaintenanceItem.active.is_(True))
    rows = (
        await session.execute(query.order_by(CarMaintenanceItem.due_at.asc()).limit(limit))
    ).scalars().all()
    return list(rows)


async def get_car_maintenance(session: AsyncSession, user_id: int, item_id: int) -> CarMaintenanceItem | None:
    return (
        await session.execute(
            select(CarMaintenanceItem).where(
                CarMaintenanceItem.id == item_id,
                CarMaintenanceItem.user_id == user_id,
                CarMaintenanceItem.active.is_(True),
            )
        )
    ).scalar_one_or_none()


async def deactivate_car_maintenance(session: AsyncSession, user_id: int, item_id: int) -> bool:
    item = await get_car_maintenance(session, user_id, item_id)
    if not item:
        return False
    item.active = False
    await session.commit()
    return True


async def add_car_compliance(
    session: AsyncSession,
    *,
    user_id: int,
    compliance_type: str,
    title: str,
    expires_at: datetime,
    profile_id: int | None = None,
) -> CarCompliance:
    row = CarCompliance(
        user_id=user_id,
        profile_id=profile_id,
        compliance_type=compliance_type if compliance_type in COMPLIANCE_TYPES else "insurance",
        title=title.strip()[:255],
        expires_at=expires_at,
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row


async def list_car_compliance(
    session: AsyncSession,
    user_id: int,
    *,
    active_only: bool = True,
) -> list[CarCompliance]:
    query = select(CarCompliance).where(CarCompliance.user_id == user_id)
    if active_only:
        query = query.where(CarCompliance.active.is_(True))
    rows = (await session.execute(query.order_by(CarCompliance.expires_at.asc()))).scalars().all()
    return list(rows)


async def deactivate_car_compliance(session: AsyncSession, user_id: int, row_id: int) -> bool:
    row = (
        await session.execute(
            select(CarCompliance).where(
                CarCompliance.id == row_id,
                CarCompliance.user_id == user_id,
                CarCompliance.active.is_(True),
            )
        )
    ).scalar_one_or_none()
    if not row:
        return False
    row.active = False
    await session.commit()
    return True


async def list_car_expenses(session: AsyncSession, user_id: int, *, limit: int = 15) -> list[LifeRecord]:
    rows = (
        await session.execute(
            select(LifeRecord)
            .where(LifeRecord.user_id == user_id, LifeRecord.module_id == CAR_MODULE, LifeRecord.submodule_id == "expenses")
            .order_by(LifeRecord.created_at.desc())
            .limit(limit)
        )
    ).scalars().all()
    return list(rows)


async def car_expense_total(session: AsyncSession, user_id: int) -> float:
    total = (
        await session.execute(
            select(func.coalesce(func.sum(LifeRecord.amount), 0.0)).where(
                LifeRecord.user_id == user_id,
                LifeRecord.module_id == CAR_MODULE,
                LifeRecord.submodule_id == "expenses",
            )
        )
    ).scalar_one()
    return float(total or 0)


def format_maint_line(item: CarMaintenanceItem, lang: str = "ru") -> str:
    label = t(lang, f"car_maint_{item.item_type}")
    due = item.due_at.strftime("%d.%m.%Y")
    line = f"• <b>{label}</b> — {item.title}\n  📅 {due}"
    if item.notes:
        line += f"\n  <i>{item.notes[:100]}</i>"
    return line


def format_compliance_line(row: CarCompliance, lang: str = "ru") -> str:
    label = t(lang, f"car_comp_{row.compliance_type}")
    exp = row.expires_at.strftime("%d.%m.%Y")
    return f"• <b>{label}</b> — {row.title}\n  📅 {t(lang, 'car_expires')}: {exp}"


def format_expense_line(record: LifeRecord, lang: str = "ru") -> str:
    amount = int(record.amount) if record.amount and float(record.amount).is_integer() else record.amount
    cur = record.currency or "UZS"
    return f"• {record.created_at.strftime('%d.%m.%Y')} — <b>{record.title}</b>: {amount} {cur}"


def build_maint_reminder_text(item: CarMaintenanceItem, lang: str = "ru") -> str:
    label = t(lang, f"car_maint_{item.item_type}")
    return (
        f"🚗 <b>{t(lang, 'car_maint_reminder_title')}</b>\n\n"
        f"{label}: {item.title}\n"
        f"📅 {t(lang, 'car_due_today')}"
    )


def build_compliance_reminder_text(row: CarCompliance, days_left: int, lang: str = "ru") -> str:
    label = t(lang, f"car_comp_{row.compliance_type}")
    if days_left == 0:
        when = t(lang, "car_expires_today")
    elif days_left == 1:
        when = t(lang, "car_expires_tomorrow")
    else:
        when = t(lang, "car_expires_in_days", days=days_left)
    return (
        f"🚗 <b>{t(lang, 'car_comp_reminder_title')}</b>\n\n"
        f"{label}: {row.title}\n"
        f"📅 {when} ({row.expires_at.strftime('%d.%m.%Y')})"
    )


async def fetch_car_maintenance_due(
    session: AsyncSession,
    *,
    now: datetime | None = None,
) -> list[tuple[CarMaintenanceItem, User]]:
    now = now or datetime.utcnow()
    rows = (
        await session.execute(
            select(CarMaintenanceItem, User)
            .join(User, User.id == CarMaintenanceItem.user_id)
            .where(CarMaintenanceItem.active.is_(True))
        )
    ).all()
    due: list[tuple[CarMaintenanceItem, User]] = []
    for item, user in rows:
        local = user_local_now(user, now)
        if item.due_at.date() != local.date():
            continue
        key = _date_key(local)
        if item.last_notified_date == key:
            continue
        due.append((item, user))
    return due


async def mark_car_maintenance_notified(session: AsyncSession, item_id: int, *, day: str | None = None) -> None:
    await session.execute(
        update(CarMaintenanceItem)
        .where(CarMaintenanceItem.id == item_id)
        .values(last_notified_date=day or _date_key(datetime.utcnow()))
    )
    await session.commit()


async def fetch_car_compliance_due(
    session: AsyncSession,
    *,
    now: datetime | None = None,
) -> list[tuple[CarCompliance, User, int]]:
    now = now or datetime.utcnow()
    rows = (
        await session.execute(
            select(CarCompliance, User)
            .join(User, User.id == CarCompliance.user_id)
            .where(CarCompliance.active.is_(True))
        )
    ).all()
    due: list[tuple[CarCompliance, User, int]] = []
    for row, user in rows:
        local = user_local_now(user, now).date()
        exp = row.expires_at.date()
        days_left = (exp - local).days
        if days_left not in COMPLIANCE_ALERT_DAYS:
            continue
        key = f"{row.id}:{days_left}:{exp.isoformat()}"
        if row.last_notified_key == key:
            continue
        due.append((row, user, days_left))
    return due


async def mark_car_compliance_notified(session: AsyncSession, row_id: int, notify_key: str) -> None:
    await session.execute(
        update(CarCompliance).where(CarCompliance.id == row_id).values(last_notified_key=notify_key)
    )
    await session.commit()


CAR_SUBMODULE_AI: dict[str, str] = {
    "panel_photo": (
        "Пользователь прислал фото панели приборов. Расшифруй индикаторы/ошибки: "
        "что означает, насколько срочно, можно ли ехать, что проверить. Без замены СТО."
    ),
    "sounds": (
        "Пользователь описывает звук автомобиля. Анализируй возможные неисправности: "
        "откуда звук, типичные причины, срочность, что проверить. Задай уточняющие вопросы при необходимости."
    ),
    "service": "Помогай составить график ТО: интервалы замены масла, фильтров, жидкостей, рекомендации по пробегу.",
}


def car_submodule_description(sub_id: str, lang: str) -> str:
    key = f"car_sub_{sub_id}"
    text = t(lang, key)
    return text if text != key else t(lang, "car_ai_hint")
