from app.services.generic_ai_service import GENERIC_AI_MODULES, generic_submodule_description


def test_generic_modules_count():
    assert len(GENERIC_AI_MODULES) >= 14


def test_generic_submodule_fallback():
    text = generic_submodule_description("work", "resume", "ru")
    assert "резюме" in text.lower() or len(text) > 10


def test_work_in_generic_set():
    assert "work" in GENERIC_AI_MODULES
    assert "notifications" not in GENERIC_AI_MODULES
