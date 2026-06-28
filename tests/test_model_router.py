from datetime import datetime, timedelta

from app.models.entities import User
from app.services.model_router import QueryComplexity, classify_query_complexity, select_ai_model


def _month() -> str:
    return datetime.utcnow().strftime("%Y-%m")


def _user(plan_id: str, **kwargs) -> User:
    kwargs.setdefault("ai_usage_month", _month())
    return User(
        id=1,
        telegram_id=1,
        plan_id=plan_id,
        plan_expires_at=datetime.utcnow() + timedelta(days=30),
        **kwargs,
    )


def test_classify_simple_greeting():
    assert classify_query_complexity("привет") == QueryComplexity.SIMPLE


def test_classify_expert_legal():
    assert classify_query_complexity(
        "Проанализируй договор аренды и риски для арендатора",
        module_id="legal",
    ) == QueryComplexity.EXPERT


def test_free_always_base():
    user = _user("free", trial_expires_at=datetime.utcnow() - timedelta(days=1))
    model = select_ai_model(user, "Проанализируй стратегию выхода на рынок")
    assert model == "gpt-4o-mini"


def test_basic_complex_uses_advanced_when_cap_available():
    user = _user("basic", advanced_model_used_month=0)
    model = select_ai_model(user, "Сделай глубокий анализ договора и рисков")
    assert model == "gpt-5.4-mini"


def test_basic_simple_uses_base():
    user = _user("basic")
    model = select_ai_model(user, "привет")
    assert model == "gpt-4o-mini"


def test_basic_exhausted_cap_still_uses_advanced():
    user = _user("basic", advanced_model_used_month=300)
    model = select_ai_model(user, "Проанализируй договор и все юридические риски")
    assert model == "gpt-5.4-mini"


def test_premium_router_simple():
    user = _user("premium")
    assert select_ai_model(user, "привет") == "gpt-4o-mini"


def test_pro_router_simple():
    user = _user("pro")
    assert select_ai_model(user, "спасибо") == "gpt-4o-mini"


def test_pro_router_expert():
    user = _user("pro")
    assert (
        select_ai_model(user, "Сравни стратегии и составь business plan с анализом рисков")
        == "gpt-5.5"
    )


def test_pro_router_standard():
    user = _user("pro")
    assert select_ai_model(user, "Как составить план питания на неделю?") == "gpt-5.4-mini"
