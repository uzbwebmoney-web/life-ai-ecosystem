from app.services.generic_ai_service import GENERIC_AI_MODULES, generic_submodule_description


def test_generic_modules_are_sport_and_fitness():
    assert GENERIC_AI_MODULES == frozenset({"sport", "fitness"})


def test_sport_submodule_fallback():
    text = generic_submodule_description("sport", "analytics", "ru")
    assert "аналит" in text.lower() or "футбол" in text.lower()
