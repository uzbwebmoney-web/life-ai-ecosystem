from datetime import datetime, timedelta

from app.core.plans import format_uzs, usd_to_uzs
from app.models.entities import User
from app.services.subscription_service import can_use_ai, effective_plan_id


def test_effective_plan_trial():
    user = User(id=1, telegram_id=1, plan_id="free", trial_expires_at=datetime.utcnow() + timedelta(days=3))
    assert effective_plan_id(user) == "premium"


def test_effective_plan_free_after_trial():
    user = User(id=1, telegram_id=1, plan_id="free", trial_expires_at=datetime.utcnow() - timedelta(days=1))
    assert effective_plan_id(user) == "free"


def test_can_use_ai_with_bonus():
    user = User(id=1, telegram_id=1, ai_bonus_balance=5, ai_used_today=100)
    assert can_use_ai(user) is None


def test_usd_to_uzs_rounding():
    assert usd_to_uzs(4) == 48_000


def test_format_uzs():
    assert "48 000" in format_uzs(48_000)
