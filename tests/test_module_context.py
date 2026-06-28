from app.services.intent_router import detect_module, module_hint
from app.services.module_context import active_module_label, build_module_ai_hint


def test_detect_health_intent():
    assert detect_module("у меня болит голова и температура") == "health"


def test_detect_finance_intent():
    assert detect_module("сколько я потратил на подписки") == "finance"


def test_module_hint_scoped_to_legal():
    hint = module_hint("legal", "applications", lang="ru")
    assert "Юридическая помощь" in hint
    assert "заявлен" in hint.lower() or "Генерация" in hint
    assert "юриста" in hint.lower()


def test_module_hint_scoped_to_health():
    hint = build_module_ai_hint("health", lang="ru")
    assert "Здоровье" in hint
    assert "диагноз" in hint.lower() or "лечен" in hint.lower()


def test_active_module_label():
    assert "Здоровье" in active_module_label("health", "symptoms", lang="ru")
    assert "→" in active_module_label("health", "symptoms", lang="ru")
    assert "Health" in active_module_label("health", "symptoms", lang="en")
