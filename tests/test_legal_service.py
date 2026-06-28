from app.services.legal_service import LEGAL_SUBMODULE_AI, legal_submodule_description
from app.services.module_context import build_module_ai_hint


def test_legal_submodule_description():
    desc = legal_submodule_description("checklists", "ru")
    assert "чек" in desc.lower() or "действ" in desc.lower() or "шаг" in desc.lower()


def test_legal_ai_hints():
    assert "questions" in LEGAL_SUBMODULE_AI
    assert "doc_check" in LEGAL_SUBMODULE_AI
    assert len(LEGAL_SUBMODULE_AI) == 5


def test_module_hint_scoped_to_legal_applications():
    hint = build_module_ai_hint("legal", "applications", lang="ru")
    assert "Юридическая помощь" in hint
    assert "заявлен" in hint.lower() or "юрист" in hint.lower()
