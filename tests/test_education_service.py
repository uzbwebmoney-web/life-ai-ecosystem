from app.services.education_service import EDUCATION_SUBMODULE_AI, education_submodule_description
from app.services.module_context import build_module_ai_hint


def test_education_submodule_description():
    desc = education_submodule_description("topics", "ru")
    assert "тем" in desc.lower() or "мавз" in desc.lower() or "прост" in desc.lower()


def test_education_ai_hints():
    assert len(EDUCATION_SUBMODULE_AI) == 5
    assert "homework" in EDUCATION_SUBMODULE_AI
    assert "ошиб" in EDUCATION_SUBMODULE_AI["homework"].lower()


def test_module_hint_scoped_to_education():
    hint = build_module_ai_hint("education", "exams", lang="ru")
    assert "Образование" in hint
    assert "экзамен" in hint.lower() or "подготов" in hint.lower()
