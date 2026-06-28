from datetime import datetime, timedelta

from app.core.plans import PLANS, format_uzs, usd_to_stars, usd_to_uzs
from app.models.entities import User
from app.services.subscription_service import effective_plan_id, module_allowed


def test_effective_plan_trial():
    user = User(id=1, telegram_id=1, plan_id="free", trial_expires_at=datetime.utcnow() + timedelta(days=3))
    assert effective_plan_id(user) == "premium"


def test_effective_plan_free_after_trial():
    user = User(id=1, telegram_id=1, plan_id="free", trial_expires_at=datetime.utcnow() - timedelta(days=1))
    assert effective_plan_id(user) == "free"


def test_legacy_family_maps_to_premium():
    user = User(
        id=1,
        telegram_id=1,
        plan_id="family",
        plan_expires_at=datetime.utcnow() + timedelta(days=10),
    )
    assert effective_plan_id(user) == "premium"


def test_can_use_ai_with_bonus():
    user = User(id=1, telegram_id=1, ai_bonus_balance=5, ai_used_today=100)
    from app.services.subscription_service import can_use_ai

    assert can_use_ai(user) is None


def test_plan_limits_match_business_table():
    assert PLANS["free"].usd_monthly is None
    assert PLANS["student"].usd_monthly == 2.99
    assert PLANS["basic"].usd_monthly == 7.99
    assert PLANS["premium"].usd_monthly == 14.99
    assert PLANS["pro"].usd_monthly == 29.99

    assert PLANS["student"].limits.advanced_model_monthly == 50
    assert PLANS["basic"].limits.advanced_model_monthly == 300
    assert PLANS["premium"].limits.advanced_model_monthly == 1500
    assert PLANS["pro"].limits.advanced_model_monthly == 5000

    assert PLANS["premium"].limits.pro_model_monthly == 30
    assert PLANS["pro"].limits.pro_model_monthly == 300

    assert PLANS["student"].limits.image_gen_monthly == 5
    assert PLANS["basic"].limits.image_gen_monthly == 30
    assert PLANS["premium"].limits.image_gen_monthly == 100
    assert PLANS["pro"].limits.image_gen_monthly == 500

    assert PLANS["free"].limits.pdf_docx_monthly == 3
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
    assert PLANS["free"].limits.photo_analysis_monthly == 5
    assert PLANS["free"].limits.photo_ai is True


def test_student_module_access():
    user = User(
        id=1,
        telegram_id=1,
        plan_id="student",
        plan_expires_at=datetime.utcnow() + timedelta(days=10),
    )
    assert module_allowed(user, "education") is None
    assert module_allowed(user, "finance") == "quota_student_module"


def test_usd_to_uzs_rounding():
    assert usd_to_uzs(2.99) == 36_000
    assert usd_to_uzs(7.99) == 96_000
    assert usd_to_uzs(14.99) == 180_000
    assert usd_to_uzs(29.99) == 360_000


def test_usd_to_stars_student():
    assert usd_to_stars(2.99) == 200


def test_format_uzs():
    assert "36 000" in format_uzs(36_000)
