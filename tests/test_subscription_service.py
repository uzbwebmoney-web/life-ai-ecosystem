from datetime import datetime, timedelta

from app.core.plans import format_uzs, usd_to_stars, usd_to_uzs
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


def test_plan_advanced_model_modes():
    from app.core.plans import PLANS

    assert PLANS["free"].limits.advanced_model == "none"
    assert PLANS["basic"].limits.advanced_model == "limited"
    assert PLANS["basic"].limits.advanced_model_monthly == 50
    assert PLANS["premium"].limits.advanced_model == "full"
    assert PLANS["pro"].limits.advanced_model == "router"
    assert PLANS["student"].limits.advanced_model == "none"


def test_free_photo_analysis_limit():
    from app.core.plans import PLANS

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
    assert usd_to_uzs(4) == 48_000


def test_usd_to_stars_student():
    assert usd_to_stars(2.49) == 200


def test_format_uzs():
    assert "48 000" in format_uzs(48_000)
