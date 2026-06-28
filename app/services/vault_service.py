from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import LifeRecord
from app.services.life_data import add_record

VAULT_MODULE = "vault"
VAULT_SUBMODULES = ("documents", "passport", "policies", "warranty", "receipts", "notes")
VAULT_FILE_SUBMODULES = ("documents", "passport", "policies", "warranty", "receipts")

SUBMODULE_ICONS: dict[str, str] = {
    "documents": "📄",
    "passport": "🛂",
    "policies": "📋",
    "warranty": "🧾",
    "receipts": "🧾",
    "notes": "📝",
}


async def add_vault_item(
    session: AsyncSession,
    *,
    user_id: int,
    submodule_id: str,
    title: str,
    body: str = "",
    amount: float | None = None,
    profile_id: int | None = None,
) -> LifeRecord:
    return await add_record(
        session,
        user_id=user_id,
        module_id=VAULT_MODULE,
        submodule_id=submodule_id,
        title=title.strip()[:255],
        body=body.strip()[:4000],
        amount=amount,
        currency="UZS" if amount else None,
        profile_id=profile_id,
    )


async def list_vault_items(
    session: AsyncSession,
    user_id: int,
    submodule_id: str,
    *,
    limit: int = 15,
) -> list[LifeRecord]:
    rows = (
        await session.execute(
            select(LifeRecord)
            .where(
                LifeRecord.user_id == user_id,
                LifeRecord.module_id == VAULT_MODULE,
                LifeRecord.submodule_id == submodule_id,
            )
            .order_by(LifeRecord.created_at.desc())
            .limit(limit)
        )
    ).scalars().all()
    return list(rows)


async def delete_vault_item(session: AsyncSession, user_id: int, record_id: int) -> bool:
    record = (
        await session.execute(
            select(LifeRecord).where(
                LifeRecord.id == record_id,
                LifeRecord.user_id == user_id,
                LifeRecord.module_id == VAULT_MODULE,
            )
        )
    ).scalar_one_or_none()
    if not record:
        return False
    await session.delete(record)
    await session.commit()
    return True


def format_vault_line(record: LifeRecord, submodule_id: str) -> str:
    icon = SUBMODULE_ICONS.get(submodule_id, "🔐")
    line = f"{icon} <b>{record.title}</b>"
    if submodule_id == "passport":
        line += " — <i>🔒 данные скрыты</i>"
    elif record.amount:
        line += f" — {record.amount:,.0f} UZS".replace(",", " ")
    elif record.body:
        preview = record.body.replace("\n", " ")[:80]
        if preview.startswith("file_id="):
            line += " — <i>📎 файл</i>"
        else:
            line += f"\n  <i>{preview}</i>"
    return line


def vault_submodule_title_key(sub_id: str) -> str:
    return f"vlt_{sub_id}_title"
