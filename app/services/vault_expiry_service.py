from __future__ import annotations

import json
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.i18n import t
from app.models.entities import AlertItem, LifeRecord
from app.services.notifications_service import add_alert_item

VAULT_EXPIRY_SUBMODULES = frozenset({"passport", "policies", "warranty", "documents"})
VAULT_EXPIRY_WARN_DAYS = 14


def merge_meta_expiry(meta_json: str | None, expires_at: datetime | None) -> str | None:
    if not expires_at and not meta_json:
        return meta_json
    try:
        data = json.loads(meta_json or "{}")
    except (json.JSONDecodeError, TypeError):
        data = {}
    if expires_at:
        data["expires_at"] = expires_at.replace(hour=12, minute=0, second=0, microsecond=0).isoformat()
    return json.dumps(data, ensure_ascii=False)


def parse_meta_expiry(meta_json: str | None) -> datetime | None:
    if not meta_json:
        return None
    try:
        raw = json.loads(meta_json).get("expires_at")
        if not raw:
            return None
        return datetime.fromisoformat(str(raw))
    except (json.JSONDecodeError, TypeError, ValueError):
        return None


async def _has_vault_expiry_alert(session: AsyncSession, user_id: int, record_id: int) -> bool:
    marker = f"vault:{record_id}"
    row = (
        await session.execute(
            select(AlertItem.id).where(
                AlertItem.user_id == user_id,
                AlertItem.active.is_(True),
                AlertItem.notes.contains(marker),
            )
        )
    ).first()
    return row is not None


async def schedule_vault_expiry_alert(
    session: AsyncSession,
    *,
    user_id: int,
    record: LifeRecord,
    expires_at: datetime,
    lang: str,
) -> None:
    if await _has_vault_expiry_alert(session, user_id, record.id):
        return
    alert_type = "visa" if record.submodule_id == "passport" else "custom"
    warn_at = expires_at - timedelta(days=VAULT_EXPIRY_WARN_DAYS)
    if warn_at > datetime.utcnow():
        await add_alert_item(
            session,
            user_id=user_id,
            alert_type="custom",
            title=t(lang, "vlt_expiry_warn_title", doc=record.title),
            due_at=warn_at.replace(hour=9, minute=0, second=0, microsecond=0),
            notes=f"vault:{record.id}",
            remind_before_minutes=0,
            profile_id=record.profile_id,
        )
    await add_alert_item(
        session,
        user_id=user_id,
        alert_type=alert_type,
        title=t(lang, "vlt_expiry_due_title", doc=record.title),
        due_at=expires_at.replace(hour=9, minute=0, second=0, microsecond=0),
        notes=f"vault:{record.id}",
        remind_before_minutes=0,
        profile_id=record.profile_id,
    )
