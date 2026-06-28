from app.services.module_context import build_module_ai_hint
from app.services.shopping_service import SHOPPING_SUBMODULE_AI, shopping_submodule_description


def test_shopping_submodule_description():
    desc = shopping_submodule_description("compare", "ru")
    assert "сравн" in desc.lower() or "товар" in desc.lower()


def test_shopping_ai_hints():
    assert len(SHOPPING_SUBMODULE_AI) == 4
    assert "deals" in SHOPPING_SUBMODULE_AI
    assert "advice" in SHOPPING_SUBMODULE_AI


def test_module_hint_scoped_to_shopping():
    hint = build_module_ai_hint("shopping", "specs", lang="ru")
    assert "Покупки" in hint or "Xaridlar" in hint
    assert "характеристик" in hint.lower() or "параметр" in hint.lower()
