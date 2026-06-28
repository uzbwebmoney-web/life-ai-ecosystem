from datetime import datetime, timedelta

from app.core.plans import PLANS, format_uzs, usd_to_stars, usd_to_uzs
from app.models.entities import User
from app.services.subscription_service import (
    credits_left,
    effective_plan_id,
    module_allowed,
)


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


def test_student_all_modules():
    user = User(
        id=1,
        telegram_id=1,
        plan_id="student",
        plan_expires_at=datetime.utcnow() + timedelta(days=10),
    )
    assert module_allowed(user, "education") is None
    assert module_allowed(user, "finance") is None


def test_uzs_and_stars():
    assert usd_to_uzs(2.99) > 0
    assert usd_to_stars(2.99) >= 50
