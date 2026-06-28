from datetime import datetime

from app.models.entities import User
from app.services.admin_user_service import apply_credits_adjustment, parse_admin_credits_input
from app.services.subscription_service import (
    _month_key,
    credits_bonus,
    credits_left,
    credits_total,
)


def test_parse_admin_credits_input():
    assert parse_admin_credits_input("500") == ("add", 500)
    assert parse_admin_credits_input("+500") == ("add", 500)
    assert parse_admin_credits_input("-200") == ("subtract", 200)
    assert parse_admin_credits_input("0") == ("reset", 0)
    assert parse_admin_credits_input("reset") == ("reset", 0)
    assert parse_admin_credits_input("обнулить") == ("reset", 0)
    assert parse_admin_credits_input("abc") is None
    assert parse_admin_credits_input("-0") is None


def test_apply_credits_adjustment_add_to_bonus():
    user = User(id=1, telegram_id=1, plan_id="free", ai_bonus_balance=50)
    apply_credits_adjustment(user, 100, action="add")
    assert user.ai_bonus_balance == 150


def test_apply_credits_adjustment_subtract_from_bonus_first():
    user = User(id=1, telegram_id=1, plan_id="free", ai_bonus_balance=80, ai_used_month=10)
    apply_credits_adjustment(user, 50, action="subtract")
    assert user.ai_bonus_balance == 30
    assert user.ai_used_month == 10


def test_apply_credits_adjustment_subtract_spills_to_usage():
    user = User(
        id=1,
        telegram_id=1,
        plan_id="premium",
        plan_expires_at=datetime.utcnow(),
        ai_bonus_balance=20,
        ai_used_month=100,
    )
    apply_credits_adjustment(user, 50, action="subtract")
    assert user.ai_bonus_balance == 0
    assert user.ai_used_month == 130


def test_apply_credits_adjustment_reset():
    user = User(
        id=1,
        telegram_id=1,
        plan_id="free",
        ai_bonus_balance=97,
        ai_used_month=500,
        ai_usage_month=_month_key(),
    )
    apply_credits_adjustment(user, 0, action="reset")
    assert user.ai_bonus_balance == 0
    assert user.ai_used_month == 0
    assert credits_left(user) == credits_total(user)


def test_apply_credits_adjustment_subtract_only_usage():
    user = User(
        id=1,
        telegram_id=1,
        plan_id="free",
        ai_bonus_balance=0,
        ai_used_month=10,
        ai_usage_month=_month_key(),
    )
    apply_credits_adjustment(user, 5, action="subtract")
    assert user.ai_used_month == 15
    assert credits_left(user) == credits_total(user) - 15
