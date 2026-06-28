from __future__ import annotations

import secrets
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.i18n import t
from app.core.plans import (
    AI_PACKAGES,
    PLANS,
    REFERRAL_AI_BONUS,
    TRIAL_DAYS,
    WELCOME_AI_BONUS,
    PlanId,
    format_uzs,
    usd_to_uzs,
)
from app.models.entities import LifeRecord, MemoryEntry, Reminder, User
from app.services.vault_service import VAULT_MODULE


def _utcnow() -> datetime:
    return datetime.utcnow()


def _month_key(when: datetime | None = None) -> str:
    when = when or _utcnow()
    return when.strftime("%Y-%m")


def _day_key(when: datetime | None = None) -> str:
    when = when or _utcnow()
    return when.strftime("%Y-%m-%d")


def effective_plan_id(user: User) -> PlanId:
    now = _utcnow()
    if user.plan_id in PLANS and user.plan_id != "free":
        if user.plan_expires_at is None or user.plan_expires_at > now:
            return user.plan_id  # type: ignore[return-value]
    if user.trial_expires_at and user.trial_expires_at > now:
        return "premium"
    return "free"


def plan_info(user: User):
    return PLANS[effective_plan_id(user)]


def _reset_usage_counters(user: User) -> None:
    day = _day_key()
    month = _month_key()
    if user.ai_usage_day != day:
        user.ai_usage_day = day
        user.ai_used_today = 0
    if user.ai_usage_month != month:
        user.ai_usage_month = month
        user.ai_used_month = 0


async def ensure_user_subscription_fields(session: AsyncSession, user: User) -> User:
    changed = False
    if not user.referral_code:
        user.referral_code = secrets.token_hex(4).upper()
        changed = True
    if user.trial_expires_at is None and user.plan_id == "free" and not user.plan_expires_at:
        user.trial_expires_at = _utcnow() + timedelta(days=TRIAL_DAYS)
        user.ai_bonus_balance = (user.ai_bonus_balance or 0) + WELCOME_AI_BONUS
        changed = True
    if changed:
        await session.commit()
        await session.refresh(user)
    return user


async def apply_referral(session: AsyncSession, user: User, code: str) -> bool:
    code = code.strip().upper()
    if not code or user.referred_by_user_id:
        return False
    referrer = (
        await session.execute(select(User).where(User.referral_code == code))
    ).scalar_one_or_none()
    if not referrer or referrer.id == user.id:
        return False
    user.referred_by_user_id = referrer.id
    user.ai_bonus_balance = (user.ai_bonus_balance or 0) + REFERRAL_AI_BONUS
    referrer.ai_bonus_balance = (referrer.ai_bonus_balance or 0) + REFERRAL_AI_BONUS
    await session.commit()
    return True


def ai_remaining(user: User) -> tuple[int | None, int | None, int]:
    """Returns daily_left, monthly_left, bonus_balance."""
    _reset_usage_counters(user)
    info = plan_info(user)
    limits = info.limits
    bonus = user.ai_bonus_balance or 0
    daily_left = None
    if limits.ai_daily is not None:
        daily_left = max(0, limits.ai_daily - (user.ai_used_today or 0))
    monthly_left = None
    if limits.ai_monthly is not None:
        monthly_left = max(0, limits.ai_monthly - (user.ai_used_month or 0))
    return daily_left, monthly_left, bonus


def can_use_ai(user: User) -> str | None:
    _reset_usage_counters(user)
    daily_left, monthly_left, bonus = ai_remaining(user)
    if bonus > 0:
        return None
    if daily_left is not None and daily_left <= 0:
        return "quota_ai_daily"
    if monthly_left is not None and monthly_left <= 0:
        return "quota_ai_monthly"
    return None


async def consume_ai_request(session: AsyncSession, user: User) -> None:
    _reset_usage_counters(user)
    if (user.ai_bonus_balance or 0) > 0:
        user.ai_bonus_balance -= 1
    else:
        user.ai_used_today = (user.ai_used_today or 0) + 1
        user.ai_used_month = (user.ai_used_month or 0) + 1
    await session.commit()


async def check_ai_quota(session: AsyncSession, user: User, *, lang: str) -> str | None:
    await ensure_user_subscription_fields(session, user)
    key = can_use_ai(user)
    if not key:
        return None
    info = plan_info(user)
    daily_left, monthly_left, bonus = ai_remaining(user)
    return t(
        lang,
        key,
        plan= t(lang, info.name_key),
        daily=daily_left or 0,
        monthly=monthly_left or 0,
        bonus=bonus,
    )


def feature_allowed(user: User, feature: str) -> str | None:
    limits = plan_info(user).limits
    if feature == "voice" and not limits.voice:
        return "quota_voice"
    if feature == "photo_ai" and not limits.photo_ai:
        return "quota_photo_ai"
    return None


async def count_reminders(session: AsyncSession, user_id: int) -> int:
    return (
        await session.execute(select(func.count(Reminder.id)).where(Reminder.user_id == user_id))
    ).scalar_one() or 0


async def check_reminder_quota(session: AsyncSession, user: User, *, lang: str) -> str | None:
    limit = plan_info(user).limits.reminders
    if limit is None:
        return None
    count = await count_reminders(session, user.id)
    if count >= limit:
        return t(lang, "quota_reminders", limit=limit, used=count)
    return None


async def count_memory_entries(session: AsyncSession, user_id: int) -> int:
    return (
        await session.execute(select(func.count(MemoryEntry.id)).where(MemoryEntry.user_id == user_id))
    ).scalar_one() or 0


async def check_memory_quota(session: AsyncSession, user: User, *, lang: str) -> str | None:
    limit = plan_info(user).limits.memory_facts
    if limit is None:
        return None
    count = await count_memory_entries(session, user.id)
    if count >= limit:
        return t(lang, "quota_memory", limit=limit, used=count)
    return None


async def estimate_storage_mb(session: AsyncSession, user_id: int) -> float:
    rows = (
        await session.execute(
            select(LifeRecord.body, LifeRecord.meta_json, LifeRecord.title).where(
                LifeRecord.user_id == user_id,
                LifeRecord.module_id == VAULT_MODULE,
            )
        )
    ).all()
    total_bytes = sum(len((b or "").encode()) + len((m or "").encode()) + len((t or "").encode()) for b, m, t in rows)
    return total_bytes / (1024 * 1024)


async def check_storage_quota(session: AsyncSession, user: User, *, lang: str) -> str | None:
    limit_mb = plan_info(user).limits.storage_mb
    used = await estimate_storage_mb(session, user.id)
    if used >= limit_mb:
        return t(lang, "quota_storage", limit=limit_mb, used=f"{used:.1f}")
    return None


def ai_model_for_user(user: User) -> str:
    from app.core.config import settings

    if plan_info(user).limits.premium_model and settings.premium_openai_model.strip():
        return settings.premium_openai_model
    return settings.openai_model


def format_usage_summary(user: User, *, lang: str) -> str:
    info = plan_info(user)
    _reset_usage_counters(user)
    daily_left, monthly_left, bonus = ai_remaining(user)
    lines = [
        t(lang, "sub_usage_title"),
        "",
        t(lang, "sub_current_plan", plan=f"{info.emoji} {t(lang, info.name_key)}"),
    ]
    if user.trial_expires_at and user.trial_expires_at > _utcnow() and effective_plan_id(user) == "premium":
        lines.append(
            t(lang, "sub_trial_until", date=user.trial_expires_at.strftime("%d.%m.%Y"))
        )
    if user.plan_expires_at and user.plan_id != "free":
        lines.append(t(lang, "sub_paid_until", date=user.plan_expires_at.strftime("%d.%m.%Y")))
    lines.append("")
    if info.limits.ai_daily is not None:
        used = user.ai_used_today or 0
        lines.append(t(lang, "sub_ai_daily", used=used, limit=info.limits.ai_daily))
    if info.limits.ai_monthly is not None:
        used = user.ai_used_month or 0
        lines.append(t(lang, "sub_ai_monthly", used=used, limit=info.limits.ai_monthly))
    if bonus:
        lines.append(t(lang, "sub_ai_bonus", bonus=bonus))
    lines.append(t(lang, "sub_storage_limit", limit=info.limits.storage_mb))
    if info.limits.memory_facts is not None:
        lines.append(t(lang, "sub_memory_limit", limit=info.limits.memory_facts))
    else:
        lines.append(t(lang, "sub_memory_unlimited"))
    return "\n".join(lines)


def format_plan_card(plan_id: PlanId, *, lang: str) -> str:
    plan = PLANS[plan_id]
    price_line = t(lang, "plan_price_free")
    if plan.usd_monthly:
        uzs = usd_to_uzs(plan.usd_monthly)
        price_line = t(lang, "plan_price_monthly", price=format_uzs(uzs), usd=f"{plan.usd_monthly:g}")
    limits = plan.limits
    ai_line = t(lang, "plan_limit_ai_daily", n=limits.ai_daily) if limits.ai_daily else t(
        lang, "plan_limit_ai_monthly", n=limits.ai_monthly or 0
    )
    reminder_line = (
        t(lang, "plan_limit_reminders_unlimited")
        if limits.reminders is None
        else t(lang, "plan_limit_reminders", n=limits.reminders)
    )
    storage_gb = limits.storage_mb / 1024 if limits.storage_mb >= 1024 else None
    storage_line = (
        t(lang, "plan_limit_storage_gb", n=f"{storage_gb:g}")
        if storage_gb
        else t(lang, "plan_limit_storage_mb", n=limits.storage_mb)
    )
    return (
        f"{plan.emoji} <b>{t(lang, plan.name_key)}</b>\n"
        f"{price_line}\n\n"
        f"{t(lang, plan.desc_key)}\n\n"
        f"• {ai_line}\n"
        f"• {reminder_line}\n"
        f"• {storage_line}\n"
        f"• {t(lang, 'plan_all_modules')}\n"
        + (f"• {t(lang, 'plan_feature_voice')}\n" if limits.voice else "")
        + (f"• {t(lang, 'plan_feature_photo')}\n" if limits.photo_ai else "")
        + (f"• {t(lang, 'plan_feature_priority')}\n" if limits.priority else "")
        + (f"• {t(lang, 'plan_feature_premium_model')}\n" if limits.premium_model else "")
    )


def format_packages_list(*, lang: str) -> str:
    lines = [t(lang, "sub_packages_title"), ""]
    for pkg in AI_PACKAGES:
        lines.append(
            t(
                lang,
                "sub_package_line",
                name=t(lang, pkg.name_key),
                requests=pkg.requests,
                price=format_uzs(usd_to_uzs(pkg.usd_price)),
            )
        )
    lines.append("")
    lines.append(t(lang, "sub_packages_hint"))
    return "\n".join(lines)


def referral_link(bot_username: str, user: User) -> str:
    code = user.referral_code or ""
    return f"https://t.me/{bot_username}?start=ref_{code}"


def format_referral_info(user: User, bot_username: str, *, lang: str) -> str:
    link = referral_link(bot_username, user)
    return t(
        lang,
        "sub_referral_info",
        bonus=REFERRAL_AI_BONUS,
        link=link,
        code=user.referral_code or "—",
    )
