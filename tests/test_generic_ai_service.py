from app.services.generic_ai_service import GENERIC_AI_MODULES, generic_submodule_description


def test_generic_modules_only_fitness():
    assert GENERIC_AI_MODULES == frozenset({"fitness"})


def test_fitness_submodule_fallback():
    text = generic_submodule_description("fitness", "workouts", "ru")
    assert "трениров" in text.lower() or len(text) > 10
