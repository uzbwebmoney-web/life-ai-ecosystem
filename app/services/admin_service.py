from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import LifeRecord, MemoryEntry, User


@dataclass
class AdminStats:
    total_users: int = 0
    new_today: int = 0
    new_last_7_days: int = 0
    new_last_30_days: int = 0
    active_last_7_days: int = 0
    onboarding_completed: int = 0
    users_by_language: dict[str, int] = field(default_factory=dict)
    total_records: int = 0
    total_memory_entries: int = 0
    vault_protected_users: int = 0
    generated_at: datetime = field(default_factory=datetime.utcnow)


def _day_start(days_ago: int = 0) -> datetime:
    now = datetime.utcnow()
    day = (now - timedelta(days=days_ago)).replace(hour=0, minute=0, second=0, microsecond=0)
    return day


async def _count_users_since(session: AsyncSession, since: datetime) -> int:
    return (
        await session.execute(select(func.count(User.id)).where(User.created_at >= since))
    ).scalar_one() or 0


async def _count_active_users_since(session: AsyncSession, since: datetime) -> int:
    return (
        await session.execute(
            select(func.count(User.id)).where(
                or_(
                    User.id.in_(select(LifeRecord.user_id).where(LifeRecord.created_at >= since)),
                    User.id.in_(select(MemoryEntry.user_id).where(MemoryEntry.created_at >= since)),
                )
            )
        )
    ).scalar_one() or 0


def parse_admin_telegram_ids(raw: str) -> list[int]:
    ids: list[int] = []
    for part in raw.replace(";", ",").split(","):
        part = part.strip()
        if part.isdigit():
            ids.append(int(part))
    return ids


async def fetch_admin_stats(session: AsyncSession) -> AdminStats:
    today = _day_start()
    week = datetime.utcnow() - timedelta(days=7)
    month = datetime.utcnow() - timedelta(days=30)

    total_users = (await session.execute(select(func.count(User.id)))).scalar_one() or 0
    lang_rows = (
        await session.execute(select(User.language, func.count(User.id)).group_by(User.language))
    ).all()
    users_by_language = {lang or "?": count for lang, count in lang_rows}

    return AdminStats(
        total_users=total_users,
        new_today=await _count_users_since(session, today),
        new_last_7_days=await _count_users_since(session, week),
        new_last_30_days=await _count_users_since(session, month),
        active_last_7_days=await _count_active_users_since(session, week),
        onboarding_completed=(
            await session.execute(select(func.count(User.id)).where(User.onboarding_done.is_(True)))
        ).scalar_one()
        or 0,
        users_by_language=users_by_language,
        total_records=(await session.execute(select(func.count(LifeRecord.id)))).scalar_one() or 0,
        total_memory_entries=(await session.execute(select(func.count(MemoryEntry.id)))).scalar_one() or 0,
        vault_protected_users=(
            await session.execute(
                select(func.count(User.id)).where(User.vault_password_hash.isnot(None), User.vault_password_hash != "")
            )
        ).scalar_one()
        or 0,
        generated_at=datetime.utcnow(),
    )


async def list_recent_users(session: AsyncSession, *, limit: int = 25) -> list[User]:
    rows = (
        await session.execute(select(User).order_by(User.created_at.desc()).limit(limit))
    ).scalars().all()
    return list(rows)


def format_admin_stats_message(stats: AdminStats, *, lang: str = "ru") -> str:
    from app.core.i18n import t

    lang_lines = ", ".join(f"{code}: {count}" for code, count in sorted(stats.users_by_language.items()))
    return (
        f"{t(lang, 'admin_stats_title')}\n\n"
        f"👥 {t(lang, 'admin_total_users')}: <b>{stats.total_users}</b>\n"
        f"🆕 {t(lang, 'admin_new_today')}: <b>{stats.new_today}</b>\n"
        f"📈 {t(lang, 'admin_new_week')}: <b>{stats.new_last_7_days}</b>\n"
        f"📅 {t(lang, 'admin_new_month')}: <b>{stats.new_last_30_days}</b>\n"
        f"⚡ {t(lang, 'admin_active_week')}: <b>{stats.active_last_7_days}</b>\n"
        f"✅ {t(lang, 'admin_onboarding_done')}: <b>{stats.onboarding_completed}</b>\n\n"
        f"📝 {t(lang, 'admin_total_records')}: <b>{stats.total_records}</b>\n"
        f"🧠 {t(lang, 'admin_total_memory')}: <b>{stats.total_memory_entries}</b>\n"
        f"🔐 {t(lang, 'admin_vault_protected')}: <b>{stats.vault_protected_users}</b>\n\n"
        f"🌐 {t(lang, 'admin_by_language')}: {lang_lines or '—'}\n\n"
        f"<i>{stats.generated_at.strftime('%d.%m.%Y %H:%M')} UTC</i>"
    )


def format_recent_users_message(users: list[User], *, lang: str = "ru") -> str:
    from app.core.i18n import t

    lines = [t(lang, "admin_recent_users_title"), ""]
    if not users:
        lines.append(t(lang, "admin_users_empty"))
        return "\n".join(lines)
    for user in users:
        name = f"@{user.username}" if user.username else f"id{user.telegram_id}"
        mark = "✅" if user.onboarding_done else "—"
        lines.append(
            f"• <b>{name}</b> · {user.language} · {user.created_at.strftime('%d.%m.%Y %H:%M')} · {mark}"
        )
    return "\n".join(lines)
