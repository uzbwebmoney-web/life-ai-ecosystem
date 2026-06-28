from app.core.modules.ui_texts import module_example_text, module_hint_text
from app.services.date_parse import parse_datetime_flexible


def test_module_hint_localized():
    assert "симптом" in module_hint_text("health", "ru").lower()
    assert module_hint_text("health", "en")


def test_module_example_localized():
    assert "гемоглобин" in module_example_text("health", "ru")
    assert module_example_text("car", "en")


def test_parse_datetime_flexible_eu():
    dt = parse_datetime_flexible("25.06.2026 09:00")
    assert dt is not None
    assert dt.day == 25
    assert dt.hour == 9


def test_parse_datetime_flexible_iso():
    dt = parse_datetime_flexible("2026-06-25 18:00")
    assert dt is not None
    assert dt.hour == 18
