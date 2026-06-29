from __future__ import annotations



import secrets

from datetime import datetime, timedelta



from sqlalchemy import func, select

from sqlalchemy.ext.asyncio import AsyncSession



from app.core.credits import CreditEstimate

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





def image_quality_for_user(user: User) -> str:

    from app.core.ai_pricing import image_quality_for_plan



    return image_quality_for_plan(effective_plan_id(user))





def _reset_usage_counters(user: User) -> None:

    month = _month_key()

    if user.ai_usage_month != month:

        user.ai_usage_month = month

        user.ai_used_month = 0

        user.photo_used_month = 0

        user.music_used_month = 0

        user.music_separate_used_month = 0

        user.image_gen_used_month = 0

        user.pdf_used_month = 0





def credits_total(user: User) -> int:

    return plan_info(user).limits.ai_credits_monthly





def credits_used(user: User) -> int:

    _reset_usage_counters(user)

    return user.ai_used_month or 0





def credits_bonus(user: User) -> int:

    return user.ai_bonus_balance or 0





def credits_left(user: User) -> int:

    _reset_usage_counters(user)

    pool = max(0, credits_total(user) - credits_used(user))

    return pool + credits_bonus(user)





def max_output_tokens_for_user(user: User) -> int:

    return plan_info(user).limits.max_output_tokens





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





def _music_limit(user: User) -> int | None:
    limits = plan_info(user).limits.music_monthly
    if limits is None:
        return None
    return limits


def _music_separate_limit(user: User) -> int | None:
    limits = plan_info(user).limits.music_separate_monthly
    if limits is None:
        return None
    return limits


def _image_gen_limit(user: User) -> int:

    limits = plan_info(user).limits.image_gen_monthly

    bonus = user.bonus_image_gen or 0

    if limits is None:

        return bonus

    return limits + bonus





async def ensure_user_subscription_fields(session: AsyncSession, user: User) -> User:

    changed = False

    if not user.referral_code:

        user.referral_code = secrets.token_hex(4).upper()

        changed = True

    # Grant signup trial only once: trial_expires_at stays None until first grant.
    # Admin downgrade to free sets trial to a past date — must not re-grant here.
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





def can_use_ai(user: User) -> str | None:

    if credits_left(user) > 0:

        return None

    return "quota_ai_credits"





def format_insufficient_credits(user: User, *, cost: int, lang: str) -> str:

    from app.core.config import settings

    lines = [
        INSUFFICIENT_CREDITS_PREFIX
        + t(
            lang,
            "quota_ai_credits_detail",
            cost=cost,
            left=credits_left(user),
        ),
        "",
        t(lang, "quota_ai_credits_plans_title"),
    ]
    for plan_id in ("student", "basic", "premium", "pro"):
        plan = PLANS[plan_id]
        if plan.usd_monthly:
            price = format_uzs(usd_to_uzs(plan.usd_monthly))
        else:
            price = t(lang, "plan_price_free")
        lines.append(
            t(
                lang,
                "quota_ai_credits_plan_line",
                emoji=plan.emoji,
                name=t(lang, plan.name_key),
                credits=plan.limits.ai_credits_monthly,
                price=price,
            )
        )
    lines.extend(["", t(lang, "quota_ai_credits_packages_title")])
    for pkg in ADDON_PACKAGES:
        if pkg.kind != "ai_credits":
            continue
        lines.append(
            t(
                lang,
                "sub_addon_line",
                name=t(lang, pkg.name_key),
                price=format_uzs(usd_to_uzs(pkg.usd_price)),
            )
        )
    lines.extend(["", t(lang, "quota_ai_credits_pay_title")])
    lines.append(t(lang, "quota_ai_credits_pay_line", method=t(lang, "pay_method_stars")))
    if settings.payment_card_number.strip():
        lines.append(t(lang, "quota_ai_credits_pay_line", method=t(lang, "pay_method_card")))
    lines.extend(["", t(lang, "quota_ai_credits_cta")])
    return "\n".join(lines)


def format_image_gen_blocked(
    user: User,
    *,
    lang: str,
    kind: str,
    used: int = 0,
    limit: int = 0,
) -> str:
    from app.core.config import settings

    if kind == "monthly":
        lines = [t(lang, "quota_image_gen_monthly_detail", used=used, limit=limit)]
    else:
        lines = [t(lang, "quota_image_gen_detail")]
    lines.extend(["", t(lang, "quota_image_gen_plans_title")])
    for plan_id in ("student", "basic", "premium", "pro"):
        plan = PLANS[plan_id]
        images = int(plan.limits.image_gen_monthly or 0)
        if images <= 0:
            continue
        if plan.usd_monthly:
            price = format_uzs(usd_to_uzs(plan.usd_monthly))
        else:
            price = t(lang, "plan_price_free")
        lines.append(
            t(
                lang,
                "quota_image_gen_plan_line",
                emoji=plan.emoji,
                name=t(lang, plan.name_key),
                images=images,
                price=price,
            )
        )
    lines.extend(["", t(lang, "quota_ai_credits_pay_title")])
    lines.append(t(lang, "quota_ai_credits_pay_line", method=t(lang, "pay_method_stars")))
    if settings.payment_card_number.strip():
        lines.append(t(lang, "quota_ai_credits_pay_line", method=t(lang, "pay_method_card")))
    lines.extend(["", t(lang, "quota_ai_credits_cta")])
    return "\n".join(lines)


INSUFFICIENT_CREDITS_PREFIX = "\x00quota_credits\x00"
QUOTA_BLOCK_PREFIX = "\x00quota_block\x00"


def parse_insufficient_credits_reply(text: str) -> tuple[bool, str]:
    if text.startswith(INSUFFICIENT_CREDITS_PREFIX):
        return True, text[len(INSUFFICIENT_CREDITS_PREFIX) :]
    if text.startswith(QUOTA_BLOCK_PREFIX):
        return True, text[len(QUOTA_BLOCK_PREFIX) :]
    return False, text





def check_credits_for_cost(user: User, cost: int, *, lang: str) -> str | None:

    _reset_usage_counters(user)

    if cost <= 0:

        return None

    if credits_left(user) >= cost:

        return None

    return format_insufficient_credits(user, cost=cost, lang=lang)





async def consume_credits(session: AsyncSession, user: User, amount: int) -> None:

    _reset_usage_counters(user)

    amount = max(0, int(amount))

    if amount <= 0:

        return

    bonus = user.ai_bonus_balance or 0

    if bonus >= amount:

        user.ai_bonus_balance = bonus - amount

    elif bonus > 0:

        user.ai_bonus_balance = 0

        user.ai_used_month = (user.ai_used_month or 0) + (amount - bonus)

    else:

        user.ai_used_month = (user.ai_used_month or 0) + amount

    await session.commit()





async def consume_ai_request(

    session: AsyncSession,

    user: User,

    *,

    credits: int,

    model: str | None = None,

) -> None:

    _reset_usage_counters(user)

    tier = _model_tier(model or "")

    if tier == "advanced":

        user.advanced_model_used_month = (user.advanced_model_used_month or 0) + 1

    elif tier == "pro":

        user.pro_model_used_month = (user.pro_model_used_month or 0) + 1

    await consume_credits(session, user, credits)





def ai_model_for_user(user: User, user_message: str = "", *, module_hint: str = "") -> str:

    from app.services.model_router import select_ai_model



    sample = user_message.strip() or "стандартный вопрос по теме модуля"

    return select_ai_model(

        user,

        sample,

        module_hint=module_hint,

        module_id=user.active_module_id,

    )





async def check_ai_quota(

    session: AsyncSession,

    user: User,

    *,

    lang: str,

    estimate: CreditEstimate,

) -> str | None:

    await ensure_user_subscription_fields(session, user)

    return check_credits_for_cost(user, estimate.credits, lang=lang)





from app.core.config import settings

GPT54_MONTHLY_CAP: dict[str, int] = {
    "free": 0,
    "student": 50,
    "basic": 300,
    "premium": 0,
    "pro": 0,
}

GPT55_MONTHLY_CAP: dict[str, int] = {
    "free": 0,
    "student": 0,
    "basic": 0,
    "premium": 30,
    "pro": 300,
}


def _model_tier(model: str) -> str:
    m = (model or "").lower()
    if m == settings.effective_pro_model.lower():
        return "pro"
    if m == settings.effective_advanced_model.lower():
        return "advanced"
    return "base"


def _gpt54_cap(user: User) -> int:
    plan = effective_plan_id(user)
    return GPT54_MONTHLY_CAP.get(plan, 0) + (user.bonus_advanced_model or 0)


def _gpt55_cap(user: User) -> int:
    plan = effective_plan_id(user)
    return GPT55_MONTHLY_CAP.get(plan, 0) + (user.bonus_pro_model or 0)


def check_model_quota(user: User, model: str, *, lang: str) -> str | None:
    tier = _model_tier(model)
    limits = plan_info(user).limits
    _reset_usage_counters(user)

    if tier == "advanced":
        if limits.advanced_model == "none":
            return QUOTA_BLOCK_PREFIX + t(lang, "quota_advanced_model")
        cap = _gpt54_cap(user)
        if cap > 0:
            used = user.advanced_model_used_month or 0
            if used >= cap:
                return QUOTA_BLOCK_PREFIX + t(
                    lang, "quota_advanced_model_monthly", used=used, limit=cap
                )

    if tier == "pro":
        if limits.advanced_model not in ("router", "full"):
            return QUOTA_BLOCK_PREFIX + t(lang, "quota_pro_model")
        cap = _gpt55_cap(user)
        if cap > 0:
            used = user.pro_model_used_month or 0
            if used >= cap:
                return QUOTA_BLOCK_PREFIX + t(lang, "quota_pro_model_monthly", used=used, limit=cap)

    return None





async def consume_photo_analysis(session: AsyncSession, user: User, *, credits: int) -> None:

    _reset_usage_counters(user)

    bonus = user.bonus_photo_analysis or 0

    limits = plan_info(user).limits.photo_analysis_monthly

    if bonus > 0 and (limits is None or (user.photo_used_month or 0) >= (limits or 0)):

        user.bonus_photo_analysis = bonus - 1

    else:

        user.photo_used_month = (user.photo_used_month or 0) + 1

    await consume_credits(session, user, credits)





async def consume_image_generation(session: AsyncSession, user: User, *, credits: int) -> None:

    _reset_usage_counters(user)

    bonus = user.bonus_image_gen or 0

    limits = plan_info(user).limits.image_gen_monthly

    if bonus > 0 and (limits is None or limits == 0 or (user.image_gen_used_month or 0) >= limits):

        user.bonus_image_gen = bonus - 1

    else:

        user.image_gen_used_month = (user.image_gen_used_month or 0) + 1

    await consume_credits(session, user, credits)





def feature_allowed(user: User, feature: str) -> str | None:

    limits = plan_info(user).limits

    if feature == "voice" and not limits.voice:

        return "quota_voice"

    if feature == "music":
        music_limit = _music_limit(user)
        if music_limit == 0:
            return "quota_music"

    if feature == "music_separate":
        sep_limit = _music_separate_limit(user)
        if sep_limit == 0:
            return "quota_music_separate"

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

    if feature == "vault_lock" and not limits.vault_lock:

        return "quota_vault_lock"

    return None





async def check_music_quota(
    session: AsyncSession,
    user: User,
    *,
    lang: str,
    separate: bool = False,
) -> str | None:
    await ensure_user_subscription_fields(session, user)
    blocked = feature_allowed(user, "music")
    if blocked:
        return t(lang, blocked)
    if separate:
        sep_blocked = feature_allowed(user, "music_separate")
        if sep_blocked:
            return t(lang, sep_blocked)
    _reset_usage_counters(user)
    limit = _music_limit(user)
    if limit is not None:
        used = user.music_used_month or 0
        if used >= limit:
            return t(lang, "quota_music_monthly", used=used, limit=limit)
    if separate:
        sep_limit = _music_separate_limit(user)
        if sep_limit is not None:
            sep_used = user.music_separate_used_month or 0
            if sep_used >= sep_limit:
                return t(lang, "quota_music_separate_monthly", used=sep_used, limit=sep_limit)
    return None


async def consume_music_operation(session: AsyncSession, user: User, *, separate: bool = False) -> None:
    _reset_usage_counters(user)
    user.music_used_month = (user.music_used_month or 0) + 1
    if separate:
        user.music_separate_used_month = (user.music_separate_used_month or 0) + 1
    await session.commit()





async def check_photo_analysis_quota(

    session: AsyncSession,

    user: User,

    *,

    lang: str,

    credits: int,

) -> str | None:

    await ensure_user_subscription_fields(session, user)

    blocked = feature_allowed(user, "photo_ai")

    if blocked:

        return t(lang, blocked)

    _reset_usage_counters(user)

    limit = _photo_limit(user)

    if limit is not None:

        used = user.photo_used_month or 0

        if used >= limit:

            return t(lang, "quota_photo_monthly", used=used, limit=limit)

    return check_credits_for_cost(user, credits, lang=lang)





async def check_image_gen_quota(

    session: AsyncSession,

    user: User,

    *,

    lang: str,

    credits: int,

) -> str | None:

    await ensure_user_subscription_fields(session, user)

    blocked = feature_allowed(user, "image_gen")

    if blocked:

        return format_image_gen_blocked(user, lang=lang, kind="plan")

    _reset_usage_counters(user)

    limit = _image_gen_limit(user)

    used = user.image_gen_used_month or 0

    if used >= limit:

        return format_image_gen_blocked(user, lang=lang, kind="monthly", used=used, limit=limit)

    return check_credits_for_cost(user, credits, lang=lang)





async def check_pdf_export_quota(session: AsyncSession, user: User, *, lang: str) -> str | None:

    await ensure_user_subscription_fields(session, user)

    blocked = feature_allowed(user, "pdf_docx")

    if blocked:

        return t(lang, blocked)

    _reset_usage_counters(user)

    limit = plan_info(user).limits.pdf_docx_monthly

    if limit is None:

        return None

    used = user.pdf_used_month or 0

    if used >= limit:

        return t(lang, "quota_pdf_monthly", used=used, limit=limit)

    return None





async def consume_pdf_export(session: AsyncSession, user: User) -> None:

    _reset_usage_counters(user)

    user.pdf_used_month = (user.pdf_used_month or 0) + 1

    await session.commit()





def module_allowed(user: User, module_id: str) -> str | None:

    allowed = plan_info(user).limits.allowed_modules

    if allowed is not None and module_id not in allowed:

        return "quota_student_module"

    return None





async def check_module_access(session: AsyncSession, user: User, module_id: str, *, lang: str) -> str | None:

    await ensure_user_subscription_fields(session, user)

    key = module_allowed(user, module_id)

    if key:

        return t(lang, key, plan=f"{PLANS['student'].emoji} {t(lang, PLANS['student'].name_key)}")

    return None


def check_export_allowed(user: User, *, lang: str) -> str | None:
    if plan_info(user).limits.export_level == "none":
        return t(lang, "quota_export")
    return None


async def check_family_profile_quota(session: AsyncSession, user: User, *, lang: str) -> str | None:
    from app.services.life_data import list_family_profiles

    limit = plan_info(user).limits.family_profiles
    profiles = await list_family_profiles(session, user.id)
    if len(profiles) >= limit:
        return t(lang, "quota_family_profiles", used=len(profiles), limit=limit)
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



    _reset_usage_counters(user)

    stored = normalize_plan_id(user.plan_id or "free")

    effective = effective_plan_id(user)

    info = PLANS[effective]

    stored_info = PLANS.get(stored, PLANS["free"])

    on_signup_trial = (
        stored == "free"
        and effective == "premium"
        and user.trial_expires_at is not None
        and user.trial_expires_at > _utcnow()
    )

    total = credits_total(user)

    used = credits_used(user)

    left = credits_left(user)

    bonus = credits_bonus(user)



    lines = [

        t(lang, "sub_usage_title"),

        "",

    ]

    if on_signup_trial:

        lines.append(
            t(lang, "sub_current_plan", plan=f"{stored_info.emoji} {t(lang, stored_info.name_key)}")
        )

        lines.append(t(lang, "sub_trial_until", date=user.trial_expires_at.strftime("%d.%m.%Y")))

    else:

        lines.append(t(lang, "sub_current_plan", plan=f"{info.emoji} {t(lang, info.name_key)}"))

    lines.append(t(lang, "sub_ai_model", model=model_routing_label(user, lang=lang)))

    if user.plan_expires_at and user.plan_id != "free":

        lines.append(t(lang, "sub_paid_until", date=user.plan_expires_at.strftime("%d.%m.%Y")))

    lines.extend(

        [

            "",

            t(lang, "sub_credits_total", total=total),

            t(lang, "sub_credits_used", used=used),

            t(lang, "sub_credits_left", left=left),

        ]

    )

    if bonus:

        lines.append(t(lang, "sub_credits_bonus", bonus=bonus))

    photo_limit = _photo_limit(user)

    if photo_limit is not None and photo_limit > 0:

        lines.append(t(lang, "sub_photo_monthly", used=user.photo_used_month or 0, limit=photo_limit))

    music_limit = _music_limit(user)
    if music_limit is not None and music_limit > 0:
        lines.append(t(lang, "sub_music_monthly", used=user.music_used_month or 0, limit=music_limit))

    music_sep_limit = _music_separate_limit(user)
    if music_sep_limit is not None and music_sep_limit > 0:
        lines.append(
            t(lang, "sub_music_separate_monthly", used=user.music_separate_used_month or 0, limit=music_sep_limit)
        )

    img_limit = _image_gen_limit(user)

    if img_limit > 0:

        lines.append(t(lang, "sub_image_gen_monthly", used=user.image_gen_used_month or 0, limit=img_limit))

    pdf_limit = plan_info(user).limits.pdf_docx_monthly or 0
    if pdf_limit > 0:
        lines.append(t(lang, "sub_pdf_monthly", used=user.pdf_used_month or 0, limit=pdf_limit))

    gpt54_cap = _gpt54_cap(user)
    if gpt54_cap > 0:
        lines.append(t(lang, "sub_gpt54_monthly", used=user.advanced_model_used_month or 0, limit=gpt54_cap))

    gpt55_cap = _gpt55_cap(user)
    if gpt55_cap > 0:
        lines.append(t(lang, "sub_gpt55_monthly", used=user.pro_model_used_month or 0, limit=gpt55_cap))

    mem_limit = _effective_memory_limit(user)

    if mem_limit is not None:

        lines.append(t(lang, "sub_memory_limit", limit=mem_limit))

    else:

        lines.append(t(lang, "sub_memory_unlimited"))

    lines.append(
        t(lang, "sub_vault_lock_on")
        if plan_info(user).limits.vault_lock
        else t(lang, "sub_vault_lock_off")
    )

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

    credits_line = t(lang, "plan_limit_credits_monthly", n=limits.ai_credits_monthly)

    image_line = (

        t(lang, "plan_limit_image_gen", n=limits.image_gen_monthly or 0)

        if (limits.image_gen_monthly or 0) > 0

        else t(lang, "plan_limit_image_none")

    )

    photo_line = _limit_label(

        limits.photo_analysis_monthly,

        lang=lang,

        unlimited_key="plan_limit_photo_unlimited",

        template_key="plan_limit_photo_monthly",

    )

    music_line = _limit_label(
        limits.music_monthly,
        lang=lang,
        unlimited_key="plan_limit_music_unlimited",
        template_key="plan_limit_music_monthly",
    )

    music_sep_line = _limit_label(
        limits.music_separate_monthly,
        lang=lang,
        unlimited_key="plan_limit_music_sep_unlimited",
        template_key="plan_limit_music_sep_monthly",
    )

    pdf_line = (

        t(lang, "plan_limit_pdf", n=limits.pdf_docx_monthly or 0)

        if (limits.pdf_docx_monthly or 0) > 0

        else t(lang, "plan_limit_pdf_none")

    )

    vault_line = (
        t(lang, "plan_limit_vault_lock")
        if limits.vault_lock
        else t(lang, "plan_limit_vault_basic")
    )

    memory_line = (

        t(lang, "plan_limit_memory_unlimited")

        if limits.memory_facts is None

        else t(lang, "plan_limit_memory", n=limits.memory_facts)

    )

    model_line = t(lang, f"plan_models_{plan_id}")

    parts = [

        f"{plan.emoji} <b>{t(lang, plan.name_key)}</b>",

        price_line,

        "",

        t(lang, plan.desc_key),

        "",

        t(lang, "plan_features_title"),

        f"• {credits_line}",

        f"• {model_line}",

        f"• {image_line}",

        f"• {t(lang, 'plan_feature_voice')}: {'✅' if limits.voice else '❌'}",

        f"• {t(lang, 'plan_feature_photo')}: {photo_line}",

        f"• {t(lang, 'plan_feature_music')}: {music_line}",

        f"• {t(lang, 'plan_feature_music_separate')}: {music_sep_line}",

        f"• {pdf_line}",

        f"• {t(lang, 'plan_feature_memory')}: {memory_line}",

        f"• {vault_line}",

    ]

    if limits.allowed_modules is not None:

        parts.append(f"• {t(lang, 'plan_feature_student_modules')}")

    if limits.household_members > 1:

        parts.append(t(lang, "plan_feature_household", n=limits.household_members))

    else:

        parts.append(f"• {t(lang, 'plan_feature_family')}: ❌")

    if limits.priority:

        parts.append(

            f"• {t(lang, 'plan_feature_priority_max' if limits.max_priority else 'plan_feature_priority')}"

        )

    if limits.allowed_modules:

        parts.append(f"• {t(lang, 'plan_feature_student_modules')}")

    return "\n".join(parts)





def format_packages_list(*, lang: str) -> str:

    lines = [t(lang, "sub_packages_title"), "", t(lang, "sub_packages_addon_title")]

    for pkg in ADDON_PACKAGES:

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





def ai_remaining(user: User) -> tuple[int | None, int | None, int]:

    _reset_usage_counters(user)

    left = credits_left(user)

    return None, left, credits_bonus(user)





def advanced_model_remaining(user: User) -> int:

    return credits_left(user)





def pro_model_remaining(user: User) -> int:

    return credits_left(user)


