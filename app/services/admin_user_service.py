from __future__ import annotations

import html
import re
from datetime import datetime, timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.i18n import t
from app.core.plans import PLANS, PlanId, normalize_plan_id
from app.models.entities import AiUsageLog, LifeRecord, MemoryEntry, Reminder, User
from app.services.subscription_service import (
    _effective_memory_limit,
    _effective_storage_limit_mb,
    _photo_limit,
    _reset_usage_counters,
    count_memory_entries,
    count_reminders,
    credits_bonus,
    credits_left,
    credits_total,
    credits_used,
    effective_plan_id,
    estimate_storage_mb,
    format_usage_summary,
    plan_info,
)

_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,32}$")


def parse_user_search_query(raw: str) -> tuple[str, str | int]:
    text = (raw or "").strip()
    if not text:
        return "empty", ""
    if text.startswith("@"):
        text = text[1:]
    if text.isdigit():
        return "numeric", int(text)
    if _USERNAME_RE.match(text):
        return "username", text.lower()
    return "unknown", text


async def search_users(session: AsyncSession, query: str, *, limit: int = 10) -> list[User]:
    kind, value = parse_user_search_query(query)
    if kind == "empty":
        return []
    if kind == "numeric":
        num = int(value)
        row = (
            await session.execute(
                select(User).where(or_(User.id == num, User.telegram_id == num)).limit(limit)
            )
        ).scalar_one_or_none()
        return [row] if row else []
    if kind == "username":
        username = str(value).lower()
        rows = (
            await session.execute(
                select(User)
                .where(func.lower(User.username) == username)
                .order_by(User.created_at.desc())
                .limit(limit)
            )
        ).scalars().all()
        if rows:
            return list(rows)
        rows = (
            await session.execute(
                select(User)
                .where(User.username.ilike(f"%{username}%"))
                .order_by(User.created_at.desc())
                .limit(limit)
            )
        ).scalars().all()
        return list(rows)
    return []


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    return (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()


def _username_label(user: User) -> str:
    if user.username:
        return f"@{user.username}"
    return "—"


def _utc_offset_label(minutes: int | None) -> str:
    value = 300 if minutes is None else int(minutes)
    sign = "+" if value >= 0 else "-"
    total = abs(value)
    hours, mins = divmod(total, 60)
    return f"UTC{sign}{hours:02d}:{mins:02d}"


async def _user_openai_cost_30d(session: AsyncSession, user_id: int) -> float:
    from app.core.ai_pricing import MODEL_PRICING, IMAGE_QUALITY_USD, normalize_model_key
    from app.models.entities import AiUsageLog

    since = datetime.utcnow() - timedelta(days=30)
    rows = (
        await session.execute(
            select(AiUsageLog).where(
                AiUsageLog.user_id == user_id,
                AiUsageLog.created_at >= since,
            )
        )
    ).scalars().all()
    total = 0.0
    for row in rows:
        key = normalize_model_key(row.model or "")
        if row.image_count:
            q = row.image_quality or "medium"
            total += IMAGE_QUALITY_USD.get(q, 0.042) * (row.image_count or 1)
            continue
        rates = MODEL_PRICING.get(key, MODEL_PRICING["gpt-4o-mini"])
        total += (row.prompt_tokens or 0) / 1_000_000 * rates[0]
        total += (row.completion_tokens or 0) / 1_000_000 * rates[1]
    return total


async def _ai_requests_30d(session: AsyncSession, user_id: int) -> int:
    since = datetime.utcnow() - timedelta(days=30)
    return (
        await session.execute(
            select(func.count(AiUsageLog.id)).where(
                AiUsageLog.user_id == user_id,
                AiUsageLog.created_at >= since,
            )
        )
    ).scalar_one() or 0


async def _records_count(session: AsyncSession, user_id: int) -> int:
    return (
        await session.execute(select(func.count(LifeRecord.id)).where(LifeRecord.user_id == user_id))
    ).scalar_one() or 0


async def format_admin_user_card(session: AsyncSession, user: User, *, lang: str = "ru") -> str:
    _reset_usage_counters(user)
    eff = effective_plan_id(user)
    eff_info = PLANS[eff]
    stored_plan = normalize_plan_id(user.plan_id or "free")
    stored_info = PLANS.get(stored_plan)  # type: ignore[arg-type]
    stored_name = t(lang, stored_info.name_key) if stored_info else stored_plan

    reminders_count = await count_reminders(session, user.id)
    memory_count = await count_memory_entries(session, user.id)
    storage_used = await estimate_storage_mb(session, user.id)
    ai_30d = await _ai_requests_30d(session, user.id)
    records_count = await _records_count(session, user.id)

    reminder_limit = plan_info(user).limits.reminders
    mem_limit = _effective_memory_limit(user)
    storage_limit = _effective_storage_limit_mb(user)

    lines = [
        t(lang, "admin_user_card_title", user_id=user.id),
        "",
        t(
            lang,
            "admin_user_card_identity",
            telegram_id=user.telegram_id,
            username=html.escape(_username_label(user)),
            lang_code=(user.language or "ru").upper(),
            utc_offset=_utc_offset_label(user.utc_offset_minutes),
        ),
        t(
            lang,
            "admin_user_card_dates",
            created=user.created_at.strftime("%d.%m.%Y %H:%M"),
            onboarding="✅" if user.onboarding_done else "❌",
        ),
        "",
        t(
            lang,
            "admin_user_card_plan",
            stored=stored_name,
            effective=f"{eff_info.emoji} {t(lang, eff_info.name_key)}",
        ),
    ]
    if user.trial_expires_at:
        trial_mark = "✅" if user.trial_expires_at > datetime.utcnow() else "❌"
        lines.append(
            t(
                lang,
                "admin_user_card_trial",
                date=user.trial_expires_at.strftime("%d.%m.%Y"),
                mark=trial_mark,
            )
        )
    if user.plan_expires_at and stored_plan != "free":
        paid_mark = "✅" if user.plan_expires_at > datetime.utcnow() else "❌"
        lines.append(
            t(
                lang,
                "admin_user_card_paid_until",
                date=user.plan_expires_at.strftime("%d.%m.%Y %H:%M"),
                mark=paid_mark,
            )
        )
    lines.extend(["", t(lang, "admin_user_card_usage_header"), format_usage_summary(user, lang=lang)])
    lines.extend(
        [
            "",
            t(lang, "admin_user_card_extra"),
            t(
                lang,
                "admin_user_card_reminders",
                used=reminders_count,
                limit=reminder_limit if reminder_limit is not None else "∞",
            ),
            t(
                lang,
                "admin_user_card_memory",
                used=memory_count,
                limit=mem_limit if mem_limit is not None else "∞",
            ),
            t(
                lang,
                "admin_user_card_storage",
                used=f"{storage_used:.1f}",
                limit=storage_limit,
            ),
            t(lang, "admin_user_card_records", count=records_count),
            t(lang, "admin_user_card_ai_30d", count=ai_30d),
        ]
    )
    if user.referral_code:
        lines.append(t(lang, "admin_user_card_referral", code=user.referral_code))
    if user.referred_by_user_id:
        lines.append(t(lang, "admin_user_card_referred_by", user_id=user.referred_by_user_id))
    openai_cost = await _user_openai_cost_30d(session, user.id)
    plan = plan_info(user)
    revenue_est = (plan.usd_monthly or 0.0)
    margin = revenue_est - openai_cost
    lines.append(
        t(
            lang,
            "admin_user_credits_profit",
            openai_usd=openai_cost,
            credits_used=credits_used(user),
            margin=margin,
        )
    )
    lines.append(
        f"💎 {credits_total(user)} / {credits_used(user)} / {credits_left(user)} "
        f"(всего/исп./ост.) · bonus {credits_bonus(user)}"
    )
    return "\n".join(lines)


def format_user_search_results(users: list[User], *, lang: str = "ru") -> str:
    if not users:
        return t(lang, "admin_user_not_found")
    if len(users) == 1:
        return t(lang, "admin_user_found_one")
    lines = [t(lang, "admin_user_found_many", count=len(users)), ""]
    for user in users:
        name = _username_label(user)
        lines.append(f"• <b>#{user.id}</b> · {name} · tg <code>{user.telegram_id}</code>")
    return "\n".join(lines)


async def admin_set_user_plan(
    session: AsyncSession,
    user_id: int,
    plan_id: str,
    *,
    days: int = 30,
) -> User | None:
    user = await get_user_by_id(session, user_id)
    if not user:
        return None
    plan_key = normalize_plan_id(plan_id)
    if plan_key not in PLANS:
        return None
    user.plan_id = plan_key
    if plan_key == "free":
        user.plan_expires_at = None
        # Past date (not None) — otherwise ensure_user_subscription_fields re-grants signup trial.
        user.trial_expires_at = datetime.utcnow() - timedelta(days=1)
    else:
        user.plan_expires_at = datetime.utcnow() + timedelta(days=max(1, days))
        user.trial_expires_at = None
    await session.commit()
    await session.refresh(user)
    return user


async def admin_extend_plan(session: AsyncSession, user_id: int, *, days: int = 30) -> User | None:
    user = await get_user_by_id(session, user_id)
    if not user:
        return None
    if normalize_plan_id(user.plan_id or "free") == "free":
        return None
    base = user.plan_expires_at if user.plan_expires_at and user.plan_expires_at > datetime.utcnow() else datetime.utcnow()
    user.plan_expires_at = base + timedelta(days=max(1, days))
    await session.commit()
    await session.refresh(user)
    return user


async def admin_extend_trial(session: AsyncSession, user_id: int, *, days: int = 7) -> User | None:
    user = await get_user_by_id(session, user_id)
    if not user:
        return None
    base = user.trial_expires_at if user.trial_expires_at and user.trial_expires_at > datetime.utcnow() else datetime.utcnow()
    user.trial_expires_at = base + timedelta(days=max(1, days))
    await session.commit()
    await session.refresh(user)
    return user


async def admin_reset_usage(session: AsyncSession, user_id: int) -> User | None:
    user = await get_user_by_id(session, user_id)
    if not user:
        return None
    user.ai_used_today = 0
    user.ai_used_month = 0
    user.photo_used_month = 0
    user.image_gen_used_month = 0
    user.pdf_used_month = 0
    user.advanced_model_used_month = 0
    user.pro_model_used_month = 0
    user.ai_usage_day = None
    user.ai_usage_month = None
    await session.commit()
    await session.refresh(user)
    return user


async def admin_add_ai_bonus(session: AsyncSession, user_id: int, amount: int) -> User | None:
    user = await get_user_by_id(session, user_id)
    if not user:
        return None
    user.ai_bonus_balance = max(0, (user.ai_bonus_balance or 0) + max(0, amount))
    await session.commit()
    await session.refresh(user)
    return user


ADMIN_PLAN_IDS: tuple[PlanId, ...] = ("free", "student", "basic", "premium", "pro")
