from app.bot.keyboards import ai_chat_insufficient_kb
from app.models.entities import User
from app.services.subscription_service import (
    _month_key,
    check_credits_for_cost,
    credits_left,
    credits_used,
    format_insufficient_credits,
    parse_insufficient_credits_reply,
)


def _user(**kwargs) -> User:
    defaults = {"id": 1, "telegram_id": 1, "plan_id": "free", "ai_usage_month": _month_key()}
    defaults.update(kwargs)
    return User(**defaults)


def test_credits_left_zero_blocks_request() -> None:
    user = _user(ai_used_month=300)
    assert credits_left(user) == 0
    blocked = check_credits_for_cost(user, cost=1, lang="ru")
    assert blocked is not None
    is_quota, body = parse_insufficient_credits_reply(blocked)
    assert is_quota
    assert "Недостаточно AI-кредитов" in body


def test_credits_left_unchanged_when_blocked() -> None:
    user = _user(ai_used_month=300)
    used_before = credits_used(user)
    check_credits_for_cost(user, cost=3, lang="ru")
    assert credits_used(user) == used_before
    assert credits_left(user) == 0


def test_credits_allow_when_enough() -> None:
    user = _user(ai_used_month=297)
    assert credits_left(user) == 3
    assert check_credits_for_cost(user, cost=3, lang="ru") is None


def test_ai_chat_insufficient_kb_has_payment_and_end() -> None:
    kb = ai_chat_insufficient_kb("ru")
    callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
    assert "sub:plans" in callbacks
    assert "sub:packages" in callbacks
    assert "ai:end" in callbacks


def test_format_insufficient_includes_cost_and_left() -> None:
    user = _user(ai_used_month=300, ai_bonus_balance=0)
    text = format_insufficient_credits(user, cost=3, lang="ru")
    _, body = parse_insufficient_credits_reply(text)
    assert "3" in body
    assert "0" in body
