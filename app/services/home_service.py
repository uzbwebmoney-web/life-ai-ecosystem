from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.i18n import t
from app.models.entities import HomeInventoryItem, HomeRepairTask, HomeShoppingItem, HomeUtilityBill, LifeRecord, User
from app.services.car_service import parse_date
from app.services.credit_loans import format_amount
from app.services.health_service import user_local_now
from app.services.life_data import add_record

HOME_MODULE = "home"
REPAIR_STATUSES = ("planned", "in_progress", "done")
STATUS_CYCLE = {"planned": "in_progress", "in_progress": "done", "done": "planned"}


def _date_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


def parse_amount(raw: str) -> float | None:
    try:
        val = float(raw.replace(" ", "").replace(",", ".").strip())
        return val if val > 0 else None
    except ValueError:
        return None


async def add_home_expense(
    session: AsyncSession,
    *,
    user_id: int,
    title: str,
    amount: float,
    profile_id: int | None = None,
) -> LifeRecord:
    return await add_record(
        session,
        user_id=user_id,
        module_id=HOME_MODULE,
        submodule_id="expenses",
        title=title.strip()[:255],
        body=title,
        amount=amount,
        currency="UZS",
        profile_id=profile_id,
    )


async def list_home_expenses(session: AsyncSession, user_id: int, *, limit: int = 15) -> list[LifeRecord]:
    rows = (
        await session.execute(
            select(LifeRecord)
            .where(
                LifeRecord.user_id == user_id,
                LifeRecord.module_id == HOME_MODULE,
                LifeRecord.submodule_id == "expenses",
            )
            .order_by(LifeRecord.created_at.desc())
            .limit(limit)
        )
    ).scalars().all()
    return list(rows)


async def home_expenses_total(session: AsyncSession, user_id: int) -> float:
    total = (
        await session.execute(
            select(func.coalesce(func.sum(LifeRecord.amount), 0.0)).where(
                LifeRecord.user_id == user_id,
                LifeRecord.module_id == HOME_MODULE,
                LifeRecord.submodule_id == "expenses",
            )
        )
    ).scalar_one()
    return float(total or 0)


def format_expense_line(record: LifeRecord) -> str:
    amount = format_amount(float(record.amount or 0))
    return f"• {record.created_at.strftime('%d.%m')} — <b>{record.title}</b>: {amount}"


async def add_home_utility(
    session: AsyncSession,
    *,
    user_id: int,
    title: str,
    amount: float,
    due_at: datetime,
    profile_id: int | None = None,
) -> HomeUtilityBill:
    bill = HomeUtilityBill(
        user_id=user_id,
        profile_id=profile_id,
        title=title.strip()[:255],
        amount=float(amount),
        due_at=due_at,
    )
    session.add(bill)
    await session.commit()
    await session.refresh(bill)
    return bill


async def list_home_utilities(session: AsyncSession, user_id: int, *, limit: int = 15) -> list[HomeUtilityBill]:
    rows = (
        await session.execute(
            select(HomeUtilityBill)
            .where(HomeUtilityBill.user_id == user_id, HomeUtilityBill.active.is_(True))
            .order_by(HomeUtilityBill.due_at.asc())
            .limit(limit)
        )
    ).scalars().all()
    return list(rows)


async def deactivate_home_utility(session: AsyncSession, user_id: int, bill_id: int) -> bool:
    bill = (
        await session.execute(
            select(HomeUtilityBill).where(
                HomeUtilityBill.id == bill_id,
                HomeUtilityBill.user_id == user_id,
                HomeUtilityBill.active.is_(True),
            )
        )
    ).scalar_one_or_none()
    if not bill:
        return False
    bill.active = False
    await session.commit()
    return True


def format_utility_line(bill: HomeUtilityBill) -> str:
    return f"• {bill.due_at.strftime('%d.%m.%Y')} — <b>{bill.title}</b>: {format_amount(bill.amount)}"


def build_utility_reminder_text(bill: HomeUtilityBill, lang: str = "ru") -> str:
    return (
        f"🏠 <b>{t(lang, 'home_utility_reminder_title')}</b>\n\n"
        f"{bill.title}\n"
        f"{format_amount(bill.amount)}\n"
        f"📅 {t(lang, 'home_due_today')}"
    )


async def fetch_home_utilities_due(
    session: AsyncSession,
    *,
    now: datetime | None = None,
) -> list[tuple[HomeUtilityBill, User]]:
    now = now or datetime.utcnow()
    rows = (
        await session.execute(
            select(HomeUtilityBill, User)
            .join(User, User.id == HomeUtilityBill.user_id)
            .where(HomeUtilityBill.active.is_(True))
        )
    ).all()
    due: list[tuple[HomeUtilityBill, User]] = []
    for bill, user in rows:
        local = user_local_now(user, now)
        if bill.due_at.date() != local.date():
            continue
        key = _date_key(local)
        if bill.last_notified_date == key:
            continue
        due.append((bill, user))
    return due


async def mark_home_utility_notified(session: AsyncSession, bill_id: int, *, day: str | None = None) -> None:
    await session.execute(
        update(HomeUtilityBill)
        .where(HomeUtilityBill.id == bill_id)
        .values(last_notified_date=day or _date_key(datetime.utcnow()))
    )
    await session.commit()


async def add_repair_task(
    session: AsyncSession,
    *,
    user_id: int,
    title: str,
    notes: str = "",
    profile_id: int | None = None,
) -> HomeRepairTask:
    task = HomeRepairTask(
        user_id=user_id,
        profile_id=profile_id,
        title=title.strip()[:255],
        notes=notes.strip()[:2000],
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def list_repair_tasks(session: AsyncSession, user_id: int) -> list[HomeRepairTask]:
    rows = (
        await session.execute(
            select(HomeRepairTask)
            .where(HomeRepairTask.user_id == user_id, HomeRepairTask.active.is_(True))
            .order_by(HomeRepairTask.id.asc())
        )
    ).scalars().all()
    return list(rows)


async def cycle_repair_status(session: AsyncSession, user_id: int, task_id: int) -> HomeRepairTask | None:
    task = (
        await session.execute(
            select(HomeRepairTask).where(
                HomeRepairTask.id == task_id,
                HomeRepairTask.user_id == user_id,
                HomeRepairTask.active.is_(True),
            )
        )
    ).scalar_one_or_none()
    if not task:
        return None
    task.status = STATUS_CYCLE.get(task.status, "planned")
    await session.commit()
    await session.refresh(task)
    return task


async def deactivate_repair_task(session: AsyncSession, user_id: int, task_id: int) -> bool:
    task = (
        await session.execute(
            select(HomeRepairTask).where(
                HomeRepairTask.id == task_id,
                HomeRepairTask.user_id == user_id,
                HomeRepairTask.active.is_(True),
            )
        )
    ).scalar_one_or_none()
    if not task:
        return False
    task.active = False
    await session.commit()
    return True


def format_repair_line(task: HomeRepairTask, lang: str = "ru") -> str:
    icon = {"planned": "📋", "in_progress": "🔨", "done": "✅"}.get(task.status, "📋")
    status = t(lang, f"home_repair_{task.status}")
    line = f"{icon} <b>{task.title}</b> — {status}"
    if task.notes:
        line += f"\n  <i>{task.notes[:80]}</i>"
    return line


async def add_shopping_item(
    session: AsyncSession,
    *,
    user_id: int,
    title: str,
    profile_id: int | None = None,
) -> HomeShoppingItem:
    item = HomeShoppingItem(user_id=user_id, profile_id=profile_id, title=title.strip()[:255])
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def list_shopping_items(session: AsyncSession, user_id: int) -> list[HomeShoppingItem]:
    rows = (
        await session.execute(
            select(HomeShoppingItem)
            .where(HomeShoppingItem.user_id == user_id, HomeShoppingItem.active.is_(True))
            .order_by(HomeShoppingItem.done.asc(), HomeShoppingItem.id.asc())
        )
    ).scalars().all()
    return list(rows)


async def toggle_shopping_item(session: AsyncSession, user_id: int, item_id: int) -> HomeShoppingItem | None:
    item = (
        await session.execute(
            select(HomeShoppingItem).where(
                HomeShoppingItem.id == item_id,
                HomeShoppingItem.user_id == user_id,
                HomeShoppingItem.active.is_(True),
            )
        )
    ).scalar_one_or_none()
    if not item:
        return None
    item.done = not item.done
    await session.commit()
    await session.refresh(item)
    return item


async def deactivate_shopping_item(session: AsyncSession, user_id: int, item_id: int) -> bool:
    item = (
        await session.execute(
            select(HomeShoppingItem).where(
                HomeShoppingItem.id == item_id,
                HomeShoppingItem.user_id == user_id,
                HomeShoppingItem.active.is_(True),
            )
        )
    ).scalar_one_or_none()
    if not item:
        return False
    item.active = False
    await session.commit()
    return True


def format_shopping_line(item: HomeShoppingItem) -> str:
    mark = "✅" if item.done else "⬜"
    return f"{mark} {item.title}"


async def add_inventory_item(
    session: AsyncSession,
    *,
    user_id: int,
    title: str,
    location: str = "",
    quantity: str = "1",
    profile_id: int | None = None,
) -> HomeInventoryItem:
    item = HomeInventoryItem(
        user_id=user_id,
        profile_id=profile_id,
        title=title.strip()[:255],
        location=location.strip()[:128],
        quantity=quantity.strip()[:32] or "1",
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def list_inventory_items(session: AsyncSession, user_id: int) -> list[HomeInventoryItem]:
    rows = (
        await session.execute(
            select(HomeInventoryItem)
            .where(HomeInventoryItem.user_id == user_id, HomeInventoryItem.active.is_(True))
            .order_by(HomeInventoryItem.location.asc(), HomeInventoryItem.title.asc())
        )
    ).scalars().all()
    return list(rows)


async def deactivate_inventory_item(session: AsyncSession, user_id: int, item_id: int) -> bool:
    item = (
        await session.execute(
            select(HomeInventoryItem).where(
                HomeInventoryItem.id == item_id,
                HomeInventoryItem.user_id == user_id,
                HomeInventoryItem.active.is_(True),
            )
        )
    ).scalar_one_or_none()
    if not item:
        return False
    item.active = False
    await session.commit()
    return True


def format_inventory_line(item: HomeInventoryItem, lang: str = "ru") -> str:
    loc = item.location or t(lang, "home_inv_no_location")
    return f"• <b>{item.title}</b> × {item.quantity}\n  📍 {loc}"


HOME_SUBMODULE_AI: dict[str, str] = {
    "repair": "Помогай планировать ремонт: этапы, материалы, порядок работ, ориентировочный бюджет.",
}


def home_submodule_description(sub_id: str, lang: str) -> str:
    key = f"home_sub_{sub_id}"
    text = t(lang, key)
    return text if text != key else ""
