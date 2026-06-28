from __future__ import annotations

import secrets
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.i18n import t
from app.core.plans import (
    ADDON_PACKAGES,
    PLANS,
    REFERRAL_AI_BONUS,
    TRIAL_DAYS,
    WELCOME_AI_BONUS,
    PlanId,
    format_uzs,
    normalize_plan_id,
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
    raw = normalize_plan_id(user.plan_id or "free")
    if raw in PLANS and raw != "free":
        if user.plan_expires_at is None or user.plan_expires_at > now:
            return raw  # type: ignore[return-value]
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
        user.photo_used_month = 0
        user.image_gen_used_month = 0
        user.pdf_used_month = 0
        user.advanced_model_used_month = 0


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
    _reset_usage_counters(user)
    limits = plan_info(user).limits
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


def _effective_memory_limit(user: User) -> int | None:
    limits = plan_info(user).limits.memory_facts
    bonus = user.bonus_memory_facts or 0
    if limits is None:
        return None
    return limits + bonus


def _effective_storage_limit_mb(user: User) -> int:
    return plan_info(user).limits.storage_mb + (user.bonus_storage_mb or 0)


def _photo_limit(user: User) -> int | None:
    limits = plan_info(user).limits.photo_analysis_monthly
    bonus = user.bonus_photo_analysis or 0
    if limits is None:
        return None
    if limits == 0:
        return 0 if bonus <= 0 else bonus
    return limits + bonus


def _image_gen_limit(user: User) -> int:
    limits = plan_info(user).limits.image_gen_monthly
    bonus = user.bonus_image_gen or 0
    if limits is None:
        return bonus
    return limits + bonus


async def consume_ai_request(session: AsyncSession, user: User, *, model: str | None = None) -> None:
    from app.core.config import settings

    _reset_usage_counters(user)
    if (user.ai_bonus_balance or 0) > 0:
        user.ai_bonus_balance -= 1
    else:
        user.ai_used_today = (user.ai_used_today or 0) + 1
        user.ai_used_month = (user.ai_used_month or 0) + 1
    if model == settings.effective_advanced_model:
        user.advanced_model_used_month = (user.advanced_model_used_month or 0) + 1
    await session.commit()


def ai_model_for_user(user: User, user_message: str = "", *, module_hint: str = "") -> str:
    """Pick model for a concrete request (defaults to a typical standard query)."""
    from app.services.model_router import select_ai_model

    sample = user_message.strip() or "стандартный вопрос по теме модуля"
    return select_ai_model(
        user,
        sample,
        module_hint=module_hint,
        module_id=user.active_module_id,
    )


async def consume_photo_analysis(session: AsyncSession, user: User) -> None:
    _reset_usage_counters(user)
    bonus = user.bonus_photo_analysis or 0
    limits = plan_info(user).limits.photo_analysis_monthly
    if bonus > 0 and (limits is None or (user.photo_used_month or 0) >= (limits or 0)):
        user.bonus_photo_analysis = bonus - 1
    else:
        user.photo_used_month = (user.photo_used_month or 0) + 1
    await session.commit()


async def consume_image_generation(session: AsyncSession, user: User) -> None:
    _reset_usage_counters(user)
    bonus = user.bonus_image_gen or 0
    limits = plan_info(user).limits.image_gen_monthly
    if bonus > 0 and (limits is None or limits == 0 or (user.image_gen_used_month or 0) >= limits):
        user.bonus_image_gen = bonus - 1
    else:
        user.image_gen_used_month = (user.image_gen_used_month or 0) + 1
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
        plan=t(lang, info.name_key),
        daily=daily_left or 0,
        monthly=monthly_left or 0,
        bonus=bonus,
    )


def feature_allowed(user: User, feature: str) -> str | None:
    limits = plan_info(user).limits
    if feature == "voice" and not limits.voice:
        return "quota_voice"
    if feature == "photo_ai":
        photo_limit = _photo_limit(user)
        if photo_limit == 0:
            return "quota_photo_ai"
    if feature == "ocr" and not limits.ocr:
        return "quota_ocr"
    if feature == "doc_translate" and not limits.doc_translate:
        return "quota_doc_translate"
    if feature == "image_gen":
        if _image_gen_limit(user) <= 0:
            return "quota_image_gen"
    if feature == "pdf_docx":
        if limits.pdf_docx_monthly == 0:
            return "quota_pdf"
    return None


async def check_photo_analysis_quota(session: AsyncSession, user: User, *, lang: str) -> str | None:
    await ensure_user_subscription_fields(session, user)
    blocked = feature_allowed(user, "photo_ai")
    if blocked:
        return t(lang, blocked)
    _reset_usage_counters(user)
    limit = _photo_limit(user)
    if limit is None:
        return None
    used = user.photo_used_month or 0
    if used >= limit:
        return t(lang, "quota_photo_monthly", used=used, limit=limit)
    return None


async def check_image_gen_quota(session: AsyncSession, user: User, *, lang: str) -> str | None:
    await ensure_user_subscription_fields(session, user)
    blocked = feature_allowed(user, "image_gen")
    if blocked:
        return t(lang, blocked)
    _reset_usage_counters(user)
    limit = _image_gen_limit(user)
    used = user.image_gen_used_month or 0
    if used >= limit:
        return t(lang, "quota_image_gen_monthly", used=used, limit=limit)
    return None


def module_allowed(user: User, module_id: str) -> str | None:
    allowed = plan_info(user).limits.allowed_modules
    if allowed is not None and module_id not in allowed:
        return "quota_student_module"
    return None


async def check_module_access(session: AsyncSession, user: User, module_id: str, *, lang: str) -> str | None:
    await ensure_user_subscription_fields(session, user)
    key = module_allowed(user, module_id)
    if key:
        return t(lang, key, plan=t(lang, plan_info(user).name_key))
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
    limit = _effective_memory_limit(user)
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
    limit_mb = _effective_storage_limit_mb(user)
    used = await estimate_storage_mb(session, user.id)
    if used >= limit_mb:
        return t(lang, "quota_storage", limit=limit_mb, used=f"{used:.1f}")
    return None


def format_usage_summary(user: User, *, lang: str) -> str:
    from app.services.model_router import model_routing_label

    info = plan_info(user)
    _reset_usage_counters(user)
    daily_left, monthly_left, bonus = ai_remaining(user)
    limits = info.limits
    lines = [
        t(lang, "sub_usage_title"),
        "",
        t(lang, "sub_current_plan", plan=f"{info.emoji} {t(lang, info.name_key)}"),
        t(lang, "sub_ai_model", model=model_routing_label(user, lang=lang)),
    ]
    if user.trial_expires_at and user.trial_expires_at > _utcnow() and effective_plan_id(user) == "premium":
        lines.append(t(lang, "sub_trial_until", date=user.trial_expires_at.strftime("%d.%m.%Y")))
    if user.plan_expires_at and user.plan_id != "free":
        lines.append(t(lang, "sub_paid_until", date=user.plan_expires_at.strftime("%d.%m.%Y")))
    lines.append("")
    if limits.ai_daily is not None:
        lines.append(t(lang, "sub_ai_daily", used=user.ai_used_today or 0, limit=limits.ai_daily))
    if limits.ai_monthly is not None:
        lines.append(t(lang, "sub_ai_monthly", used=user.ai_used_month or 0, limit=limits.ai_monthly))
    if bonus:
        lines.append(t(lang, "sub_ai_bonus", bonus=bonus))
    photo_limit = _photo_limit(user)
    if photo_limit is not None and photo_limit > 0:
        lines.append(
            t(lang, "sub_photo_monthly", used=user.photo_used_month or 0, limit=photo_limit)
        )
    img_limit = _image_gen_limit(user)
    if img_limit > 0:
        lines.append(
            t(lang, "sub_image_gen_monthly", used=user.image_gen_used_month or 0, limit=img_limit)
        )
    mem_limit = _effective_memory_limit(user)
    if mem_limit is not None:
        lines.append(t(lang, "sub_memory_limit", limit=mem_limit))
    else:
        lines.append(t(lang, "sub_memory_unlimited"))
    lines.append(t(lang, "sub_storage_limit", limit=_effective_storage_limit_mb(user)))
    return "\n".join(lines)


def _limit_label(value: int | None, *, lang: str, unlimited_key: str, template_key: str) -> str:
    if value is None:
        return t(lang, unlimited_key)
    if value == 0:
        return "❌"
    return t(lang, template_key, n=value)


def format_plan_card(plan_id: PlanId, *, lang: str) -> str:
    plan = PLANS[plan_id]
    price_line = t(lang, "plan_price_free")
    if plan.usd_monthly:
        uzs = usd_to_uzs(plan.usd_monthly)
        price_line = t(lang, "plan_price_monthly", price=format_uzs(uzs), usd=f"{plan.usd_monthly:g}")
    limits = plan.limits
    ai_line = (
        t(lang, "plan_limit_ai_daily", n=limits.ai_daily)
        if limits.ai_daily
        else t(lang, "plan_limit_ai_monthly", n=limits.ai_monthly or 0)
    )
    if limits.ai_monthly and limits.ai_monthly >= 999_999:
        ai_line = t(lang, "plan_limit_ai_unlimited")
    photo_line = _limit_label(
        limits.photo_analysis_monthly,
        lang=lang,
        unlimited_key="plan_limit_photo_unlimited",
        template_key="plan_limit_photo_monthly",
    )
    if limits.advanced_model == "limited":
        model_line = t(
            lang,
            "plan_model_limited",
            cap=limits.advanced_model_monthly or 0,
            model="GPT-5.4 mini",
        )
    elif limits.advanced_model == "full":
        model_line = t(lang, "plan_model_full", model="GPT-5.4 mini")
    elif limits.advanced_model == "router":
        model_line = t(lang, "plan_model_router_short")
    else:
        model_line = t(lang, "plan_model_none")
    storage_gb = limits.storage_mb / 1024 if limits.storage_mb >= 1024 else None
    storage_line = (
        t(lang, "plan_limit_storage_gb", n=f"{storage_gb:g}")
        if storage_gb
        else t(lang, "plan_limit_storage_mb", n=limits.storage_mb)
    )
    memory_line = (
        t(lang, "plan_limit_memory_unlimited")
        if limits.memory_facts is None
        else t(lang, "plan_limit_memory", n=limits.memory_facts)
    )
    parts = [
        f"{plan.emoji} <b>{t(lang, plan.name_key)}</b>",
        price_line,
        "",
        t(lang, plan.desc_key),
        "",
        t(lang, "plan_features_title"),
        f"• {ai_line}",
        f"• {t(lang, 'plan_feature_model')}: {model_line}",
        f"• {t(lang, 'plan_feature_photo')}: {photo_line}",
        f"• {t(lang, 'plan_feature_memory')}: {memory_line}",
        f"• {storage_line}",
    ]
    if limits.voice:
        parts.append(f"• {t(lang, 'plan_feature_voice')}")
    if limits.image_gen_monthly:
        parts.append(
            f"• {t(lang, 'plan_limit_image_gen', n=limits.image_gen_monthly)}"
        )
    if limits.household_members > 1:
        parts.append(
            t(lang, "plan_feature_household", n=limits.household_members)
        )
    if limits.priority:
        parts.append(
            f"• {t(lang, 'plan_feature_priority_max' if limits.max_priority else 'plan_feature_priority')}"
        )
    if limits.allowed_modules:
        parts.append(f"• {t(lang, 'plan_feature_student_modules')}")
    return "\n".join(parts)


def format_packages_list(*, lang: str) -> str:
    lines = [t(lang, "sub_packages_title"), "", t(lang, "sub_packages_ai_title")]
    for pkg in ADDON_PACKAGES:
        if pkg.kind != "ai_requests":
            continue
        lines.append(
            t(
                lang,
                "sub_package_line",
                name=t(lang, pkg.name_key),
                requests=pkg.amount,
                price=format_uzs(usd_to_uzs(pkg.usd_price)),
            )
        )
    lines.extend(["", t(lang, "sub_packages_addon_title")])
    for pkg in ADDON_PACKAGES:
        if pkg.kind == "ai_requests":
            continue
        lines.append(
            t(
                lang,
                "sub_addon_line",
                name=t(lang, pkg.name_key),
                price=format_uzs(usd_to_uzs(pkg.usd_price)),
            )
        )
    lines.extend(["", t(lang, "sub_packages_hint")])
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
