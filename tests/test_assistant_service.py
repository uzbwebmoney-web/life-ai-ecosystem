from app.services.assistant_service import ASSISTANT_SUBMODULE_AI, assistant_submodule_description
from app.services.module_context import build_module_ai_hint


def test_assistant_submodule_description():
    desc = assistant_submodule_description("translate", "ru")
    assert "перевод" in desc.lower() or "tarjima" in desc.lower() or "translate" in desc.lower()


def test_assistant_ai_hints():
    assert len(ASSISTANT_SUBMODULE_AI) == 7
    assert "questions" in ASSISTANT_SUBMODULE_AI
    assert "images" in ASSISTANT_SUBMODULE_AI
    assert "код" in ASSISTANT_SUBMODULE_AI["code"].lower() or "program" in ASSISTANT_SUBMODULE_AI["code"].lower()


def test_module_hint_scoped_to_assistant():
    hint = build_module_ai_hint("ai_assistant", "code", lang="ru")
    assert "Моя жизнь" in hint
    assert "ассистент" in hint.lower() or "AI" in hint
    assert "программ" in hint.lower() or "код" in hint.lower()
