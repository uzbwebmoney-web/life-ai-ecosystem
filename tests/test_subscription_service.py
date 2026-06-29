from datetime import datetime, timedelta

from app.core.plans import PLANS, format_uzs, usd_to_stars, usd_to_uzs
from app.models.entities import User
from app.services.subscription_service import (
    credits_left,
    credits_total,
    effective_plan_id,
    feature_allowed,
    module_allowed,
)


def test_effective_plan_trial():
    user = User(id=1, telegram_id=1, plan_id="free", trial_expires_at=datetime.utcnow() + timedelta(days=3))
    assert effective_plan_id(user) == "premium"


def test_effective_plan_free_after_trial():
    user = User(id=1, telegram_id=1, plan_id="free", trial_expires_at=datetime.utcnow() - timedelta(days=1))
    assert effective_plan_id(user) == "free"


def test_admin_downgrade_to_free_uses_free_limits():
    user = User(
        id=1,
        telegram_id=1,
        plan_id="free",
        trial_expires_at=datetime.utcnow() - timedelta(days=1),
    )
    assert effective_plan_id(user) == "free"
    assert credits_total(user) == PLANS["free"].limits.ai_credits_monthly


def test_legacy_family_maps_to_premium():
    user = User(
        id=1,
        telegram_id=1,
        plan_id="family",
        plan_expires_at=datetime.utcnow() + timedelta(days=10),
    )
    assert effective_plan_id(user) == "premium"


def test_can_use_ai_with_bonus():
    user = User(id=1, telegram_id=1, ai_bonus_balance=500, ai_used_month=10000)
    from app.services.subscription_service import can_use_ai

    assert can_use_ai(user) is None
    assert credits_left(user) >= 500


def test_plan_limits_match_business_table():
    assert PLANS["free"].usd_monthly is None
    assert PLANS["student"].usd_monthly == 2.99
    assert PLANS["basic"].usd_monthly == 5.99
    assert PLANS["premium"].usd_monthly == 11.99
    assert PLANS["pro"].usd_monthly == 19.99

    assert PLANS["free"].limits.ai_credits_monthly == 300
    assert PLANS["student"].limits.ai_credits_monthly == 1500
    assert PLANS["basic"].limits.ai_credits_monthly == 5000

    assert PLANS["student"].limits.image_gen_monthly == 10
    assert PLANS["basic"].limits.image_gen_monthly == 40
    assert PLANS["premium"].limits.image_gen_monthly == 120
    assert PLANS["pro"].limits.image_gen_monthly == 400

    assert PLANS["free"].limits.pdf_docx_monthly == 0
    assert PLANS["free"].limits.photo_analysis_monthly == 3
    assert PLANS["student"].limits.voice is True
    assert PLANS["premium"].limits.household_members == 5
    assert PLANS["pro"].limits.household_members == 10


def test_plan_advanced_model_modes():
    assert PLANS["free"].limits.advanced_model == "none"
    assert PLANS["student"].limits.advanced_model == "limited"
    assert PLANS["basic"].limits.advanced_model == "limited"
    assert PLANS["premium"].limits.advanced_model == "router"
    assert PLANS["pro"].limits.advanced_model == "router"


def test_free_photo_analysis_limit():
    assert PLANS["free"].limits.photo_analysis_monthly == 3
    assert PLANS["free"].limits.photo_ai is True


def test_vault_lock_by_plan():
    assert PLANS["free"].limits.vault_lock is False
    assert PLANS["student"].limits.vault_lock is True
    assert PLANS["basic"].limits.vault_lock is True
    user = User(id=1, telegram_id=1, plan_id="free")
    assert feature_allowed(user, "vault_lock") == "quota_vault_lock"
    paid = User(id=2, telegram_id=2, plan_id="student")
    assert feature_allowed(paid, "vault_lock") is None


def test_student_module_restrictions():
    user = User(
        id=1,
        telegram_id=1,
        plan_id="student",
        plan_expires_at=datetime.utcnow() + timedelta(days=10),
    )
    assert module_allowed(user, "education") is None
    assert module_allowed(user, "vault") is None
    assert module_allowed(user, "finance") == "quota_student_module"


def test_uzs_and_stars():
    assert usd_to_uzs(2.99) > 0
    assert usd_to_stars(2.99) >= 50


def test_format_insufficient_credits_lists_plans_and_payment():
    from app.services.subscription_service import (
        INSUFFICIENT_CREDITS_PREFIX,
        format_insufficient_credits,
        parse_insufficient_credits_reply,
    )

    user = User(id=1, telegram_id=1, plan_id="free", ai_used_month=300)
    text = format_insufficient_credits(user, cost=3, lang="ru")
    assert text.startswith(INSUFFICIENT_CREDITS_PREFIX)
    assert "Недостаточно AI-кредитов" in text
    assert "Тарифы" in text
    assert "Способы оплаты" in text
    assert "Student" in text or "Студент" in text or PLANS["student"].emoji in text

    is_quota, body = parse_insufficient_credits_reply(text)
    assert is_quota is True
    assert INSUFFICIENT_CREDITS_PREFIX not in body
    assert "Недостаточно AI-кредитов" in body

    is_normal, normal = parse_insufficient_credits_reply("Hello")
    assert is_normal is False
    assert normal == "Hello"


def test_format_image_gen_blocked_lists_plans_and_payment():
    from app.services.subscription_service import format_image_gen_blocked

    user = User(id=1, telegram_id=1, plan_id="free")
    text = format_image_gen_blocked(user, lang="ru", kind="plan")
    assert "Создание картинок недоступно" in text
    assert "Тарифы с генерацией" in text
    assert "Способы оплаты" in text
    assert "Student" in text or PLANS["student"].emoji in text
    assert "/subscription" not in text

    user_student = User(id=2, telegram_id=2, plan_id="student", image_gen_used_month=10)
    monthly = format_image_gen_blocked(user_student, lang="ru", kind="monthly", used=10, limit=10)
    assert "исчерпан" in monthly
    assert "10" in monthly
